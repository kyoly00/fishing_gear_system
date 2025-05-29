import os
import json
import glob
import csv
import math
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_netCDF_CF_generic
import matplotlib as mpl
from env_api import fetch_all_khoa, fetch_khoa_uv, fetch_era5

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
mpl.rcParams['axes.unicode_minus'] = False

# ─────────────────────────────────────────────────────
# 상수 정의
# ─────────────────────────────────────────────────────
TARGET_SEQ       = [3,0,3,1,3]                 # 시퀀스 탐색용

# ─────────────────────────────────────────────────────
# 1) 시퀀스 탐색용 헬퍼
# ─────────────────────────────────────────────────────
def find_sequence_groups(behaviors, target=TARGET_SEQ):
    # 연속 중복 제거 후 그룹 시퀀스에서 부분열 위치 탐색
    grp = [behaviors[0]]
    for b in behaviors[1:]:
        if b != grp[-1]:
            grp.append(b)
    n,m = len(grp), len(target)
    for i in range(n-m+1):
        if grp[i:i+m] == target:
            return i, i+m
    return None

def load_df(df):
    # 컬럼 이름을 맞춰줌
    df = df.rename(columns={
        'longitude': 'lon',
        'latitude': 'lat'
    })

    # 시간 형식 변환 및 정렬
    df['time_stamp'] = pd.to_datetime(df['time_stamp'])
    return df.sort_values('time_stamp', ignore_index=True)

def locate_sequence(df):
    raw = df['fishery_behavior'].tolist()
    if len(raw) < len(TARGET_SEQ): 
        return None
    # 그룹별 인덱스 매핑
    grp = [raw[0]]; starts=[0]; prev=raw[0]
    for i,b in enumerate(raw[1:], start=1):
        if b != prev:
            grp.append(b)
            starts.append(i)
            prev = b
    loc = find_sequence_groups(grp)
    if not loc:
        return None
    i0,i1 = loc
    start_idx = starts[i0]
    end_idx   = (starts[i1]-1) if i1<len(starts) else len(raw)-1
    return start_idx, end_idx

def seq_times(df, loc):
    s,e = loc
    return df.loc[s,'time_stamp'], df.loc[e,'time_stamp']

# ─── scan_clusters 정의 ──────────────────────────────────────────────
def scan_clusters(df):
    intervals = []
    # 모든 파일의 (t0,t1,fn) 수집
    loc = locate_sequence(df)
    if not loc: 
        return [], []
    t0,t1 = seq_times(df,loc)
    intervals.append((t0,t1))
    # 시작 시간 순 정렬
    intervals.sort(key=lambda x: x[0])
    # 겹치는 구간끼리 묶기
    clusters = []
    cur, cur_end = [], None
    for iv in intervals:
        s,e = iv
        if not cur:
            cur = [iv]; cur_end = e
        elif s <= cur_end:
            cur.append(iv)
            cur_end = max(cur_end, e)
        else:
            clusters.append(cur)
            cur = [iv]; cur_end = e
    if cur:
        clusters.append(cur)
    # 클러스터별 첫/마지막 파일
    first_list = [cluster[0][2] for cluster in clusters]
    last_list  = [cluster[-1][2] for cluster in clusters]
    return first_list, last_list


# ─────────────────────────────────────────────────────
# 6) OpenDrift용 GradualKillDrift 클래스
# ─────────────────────────────────────────────────────
class GradualKillDrift(OceanDrift):
    def __init__(self, kill_order, kill_steps, *args, **kwargs):
        """
        kill_order : [ID0, ID1, ...] – 비활성화 순서의 요소 ID 리스트
        """
        super().__init__(*args, **kwargs)
        self.kill_order = kill_order
        self.kill_steps = kill_steps
        self.killed = 0

    def update(self):
        super().update()
        step = self.steps_calculation

        if self.killed >= len(self.kill_steps):
            return  # 모든 입자 kill 완료 → 종료

        # 현재 step에 대응하는 kill_step이 있는 동안 반복적으로 kill
        while self.killed < len(self.kill_steps) and step >= self.kill_steps[self.killed]:
            id_to_kill = self.kill_order[self.killed]
            mask = (self.elements.ID == id_to_kill)
            self.deactivate_elements(mask, reason='gradual_yang')
            print(f"▶ Step {step}: Deactivated ID {id_to_kill}")
            self.killed += 1

# ─────────────────────────────────────────────────────
# 메인 흐름
# ─────────────────────────────────────────────────────
def run_lost_simulation(
    df,
    nc_folder,
    wind_folder,
    coastline_file,
    plot_output_dir,
    plot_output_dir_first,
    plot_output_dir_last,
    error_log_path,
    service_key_khoa,
    time_step
    ):

    case = {'name': '16_angrev_recompute_wind_0.02', 'options': {'reverse_vector_by_angle_180': True, 'recompute_uv': True}}


    try:
        df = load_df(df)
        loc = locate_sequence(df)
        if loc is None:
            raise RuntimeError("TARGET_SEQ 시퀀스가 포함되지 않았습니다.")
        df = df.loc[loc[0]:loc[1]].reset_index(drop=True)
        df['prev_behavior'] = df['fishery_behavior'].shift(1)
        df0 = df[df['fishery_behavior'] == 0]
        if df0.empty or df[(df['fishery_behavior']==0)&(df['prev_behavior']!=0)].empty:
            raise RuntimeError("투망 구간 또는 시작 시점 데이터가 없습니다.")

        lon_min, lon_max = df0['lon'].min() - 0.5, df0['lon'].max() + 0.5
        lat_min, lat_max = df0['lat'].min() - 0.5, df0['lat'].max() + 0.5
        lon_grid = np.arange(round(lon_min,2), round(lon_max,2)+0.01, 0.01)
        lat_grid = np.arange(round(lat_min,2), round(lat_max,2)+0.01, 0.01)

        df_tumang = df[df['fishery_behavior'] == 0].copy().reset_index(drop=True)
        df_yangmang = df[df['fishery_behavior'] == 1].copy().reset_index(drop=True)
        sim_start = df_tumang['time_stamp'].min()
        sim_end   = df_yangmang['time_stamp'].max()

        start_kill_step = int((df_yangmang['time_stamp'].min() - sim_start).total_seconds() / time_step)
        end_kill_step = int((df_yangmang['time_stamp'].max() - sim_start).total_seconds() / time_step)

        num_particles = len(df_tumang)
        kill_order = list(range(num_particles - 1))
        kill_steps = np.linspace(start_kill_step, end_kill_step, len(kill_order), dtype=int).tolist()

        uv_path = os.path.join(nc_folder, "input_uv.nc")
        time_list = pd.date_range(sim_start, sim_end, freq='h')
        fetch_uv_path = fetch_all_khoa(time_list, lon_min, lon_max, lat_min, lat_max, lon_grid, lat_grid, case['options'], uv_path, service_key_khoa)
        # fetch_uv_path = fetch_khoa_uv(time_list, lon_min, lon_max, lat_min, lat_max, lon_grid, lat_grid, case['options'], uv_path, service_key_khoa)

        wind_path = os.path.join(wind_folder, "input_wind.nc")
        fetch_wind_path = fetch_era5(sim_start, sim_end, lat_min, lat_max, lon_min, lon_max, wind_path)

        o = GradualKillDrift(kill_order=kill_order, kill_steps=kill_steps, loglevel=20)
        o.add_reader([reader_netCDF_CF_generic.Reader(fetch_uv_path),
                        reader_netCDF_CF_generic.Reader(fetch_wind_path)])

        o.set_config('seed:wind_drift_factor', 0.02)
        o.set_config('drift:stokes_drift', True)
        o.set_config('general:seafloor_action', 'none')
        o.set_config('drift:vertical_advection', True)
        o.set_config('drift:vertical_mixing', False)
        o.set_config('general:coastline_action', 'previous')

        for i, row in df_tumang.iterrows():
            o.seed_elements(lon=row['lon'], lat=row['lat'], time=row['time_stamp'],
                            z=0.0, ID=np.array([i], dtype=np.int32), origin_marker=np.array([i], dtype=np.int32))
        o.elements.terminal_velocity[:] = 0.01
        o.run(time_step=time_step, duration=sim_end - sim_start)


        df_sim = None
        df_sim = o.result[['status', 'lat', 'lon', 'origin_marker']].to_dataframe().reset_index()
        df_sim = df_sim.rename(columns={'trajectory': 'seed_id', 'time': 'timestamp'})
        df_sim = df_sim.sort_values(['seed_id', 'timestamp'])
        df_sim['prev_status'] = df_sim.groupby('seed_id')['status'].shift(1)
        last_active_df = df_sim[(df_sim['prev_status'] == 0) & (df_sim['status'] != 0)].index - 1
        df_sim = df_sim[:-1]    # 마지막 입자 제외
        last_active_df = df_sim.loc[last_active_df]
        
        # # 가시거리 가져오기 
        # near_station = find_closest_station(df[0]['lat'], df[0]['lon'])
        # print(near_station)
        # visible_len = get_visibility_from_khoa(near_station, time_step, SERVICE_KEY_KHOA)
        # print(visible_len)

        center_lat = df_sim['lat'][len(df_sim) // 2]
        center_lon = df_sim['lon'][len(df_sim) // 2]

        # 위경도 기준 반경 (단순화: 위도 보정)
        visible_radius_km = 1
        lat_km_per_deg = 111  # 위도 1도 ≈ 111 km
        lon_km_per_deg = 111 * np.cos(np.deg2rad(center_lat))  # 경도는 위도에 따라 줄어듦

        visible_radius_lat = visible_radius_km / lat_km_per_deg
        visible_radius_lon = visible_radius_km / lon_km_per_deg

        # 원 궤적 좌표 생성
        theta = np.linspace(0, 2 * np.pi, 100)
        circle_lon = center_lon + visible_radius_lon * np.cos(theta)
        circle_lat = center_lat + visible_radius_lat * np.sin(theta)


        # plt.figure(figsize=(10, 7))
        # for seed_id, group in df_sim.groupby('seed_id'):
        #     plt.plot(group['lon'], group['lat'], color='gray', alpha=0.4)
        # plt.scatter(last_active_df['lon'], last_active_df['lat'], c='orange', s=10, label='비활성화 직전 위치')
        # plt.plot(last_active_df['lon'], last_active_df['lat'], color='orange', linewidth=10, label='비활성화 위치 경로')
        # plt.scatter(df_tumang['lon'], df_tumang['lat'], s=30, color='blue', marker='^', label='투망(0)')
        # plt.scatter(df_yangmang['lon'], df_yangmang['lat'], s=30, color='red', marker='v', label='양망(1)')
        # plt.title("시뮬레이션 궤적 및 위치 비교")
        # plt.legend()
        # plt.fill(circle_lon, circle_lat, color='green', alpha=0.3, label='가시거리 반경 (1km)')
        # plt.tight_layout()
        # plt.savefig("simulation_result.png", dpi=300)
        # plt.close()

        uv_ds = xr.open_dataset(fetch_uv_path)     
        wind_ds = xr.open_dataset(fetch_wind_path)

        # print("===============해류 데이터==================")
        # print(uv_ds)
        # print("===============바람 데이터==================")
        # print(wind_ds)
        # print("===============투망==================")
        # print(df_tumang.head())
        # print("===============양망==================")
        # print(df_yangmang.head())
        # print("===============시뮬레이션 결과==================")
        # print(df_sim.head())

        return df_sim

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None