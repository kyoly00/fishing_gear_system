import sys
sys.path.append(r'C:\Users\ime\Desktop\유실_최종\조업행태모델')

from cal_ais_values import cal_val, cal_statics
# from load_test_model_1dcnn import CustomModel, CustomDataset  # TCN 기반 모델/데이터셋
from model_def import CustomModel, CustomDataset  # TCN 기반 모델/데이터셋




import json
import pandas as pd
import copy
import pickle
import os
from os.path import join
from os import listdir
import numpy as np
from datetime import datetime, timedelta
from os.path import split
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')



#-------------------------------
# 데이터셋 준비
#-------------------------------

# 1. 파일명 일부로 자동 로드 함수
def load_csv_from_partial_name(directory, partial_filename):
    """
    지정한 폴더 안에서 partial_filename을 포함하는 첫 번째 CSV 파일을 찾아 불러옵니다.
    """
    for file in os.listdir(directory):
        if partial_filename in file and file.endswith('.csv'):
            full_path = os.path.join(directory, file)
            print(f"✅ 파일 로드: {full_path}")
            df = pd.read_csv(full_path, encoding="UTF-8")
            return full_path, df
    raise FileNotFoundError(f"❌ '{partial_filename}'를 포함한 .csv 파일을 '{directory}'에서 찾을 수 없습니다.")

# ──────────────────────────────────────────────
# 2. 사용자 설정
jsondict_pkl = r'C:\Users\ime\Desktop\유실_최종\조업행태모델\jsondict_v0.2.pkl'
gps_folder = r'C:\Users\ime\Desktop\유실_최종\GPS_DATA'





#======================================================
filename_hint = '33_5__128_5__2022-03-10'  # 파일명 일부
#======================================================



cols2 = ['sea_surface_temperature','sea_surface_salinity','current_speed','wind','tide','bottom_depth','chlorophyll','DIN','DIP','dissolved_oxygen','fishery_density','fishery_type','fishery_behavior']
static_cols = ['mean_ship_course_change','standard_deviation_of_ship_course_change','histogram_of_ship_course_change','mean_ship_course_change_per_velocity_stage',
               'mean_velocity_change','standard_deviation_of_velocity_change','mean_velocity','histogram_of_velocity','histogram_of_velocity_change',
               'velocity_change_per_velocity_stage']


# ──────────────────────────────────────────────
# 3. JSON dict 로드
with open(jsondict_pkl, 'rb') as f:
    features_value_dict = pickle.load(f)
    geojson_dict = pickle.load(f)

# ──────────────────────────────────────────────
# 4. CSV 자동 로드 및 처리
csv_path, csv_data = load_csv_from_partial_name(gps_folder, filename_hint)
csv_time = pd.to_datetime(csv_data['datetime'])



# 5. 통계 계산 및 geojson feature 채우기
total_statics = cal_statics(csv_data)  # → static_cols 기준 10개 리스트


features_value_list = []

for i in range(len(csv_data)) :
    for ais_i in range(len(static_cols)):
        features_value_dict['properties'][static_cols[ais_i]]=total_statics[i][ais_i]
    temp_dict = copy.deepcopy(features_value_dict)
    features_value_list.append(temp_dict)
geojson_dict['features'] = features_value_list



# 원래 AIS 데이터프레임에 통계 열 추가
for i, col in enumerate(static_cols):
    csv_data[col] = [row[i] for row in total_statics]




#----------------------------------------------

import ast

# ─────────────────────────────────────
# 2. 컬럼명 변경
df2 = csv_data.rename(columns={
    'datetime': 'time_stamp',
    'lat': 'latitude',
    'lon': 'longitude'
})

# ─────────────────────────────────────
# 3. 리스트형 컬럼 분해 함수
def expand_list_column(df, column_name, new_column_prefix, target_length):
    def parse_list(val):
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            try:
                return ast.literal_eval(val)
            except:
                return [0] * target_length
        return [0] * target_length

    parsed_lists = df[column_name].apply(parse_list)
    for i in range(target_length):
        df[f'{new_column_prefix}{i+1}'] = parsed_lists.apply(lambda x: x[i] if i < len(x) else 0)

    df = df.drop(columns=[column_name])
    return df

# ─────────────────────────────────────
# 4. 리스트형 컬럼들 확장
df2 = expand_list_column(df2, 'histogram_of_ship_course_change', 'histogram_of_ship_course_change', 12)
df2 = expand_list_column(df2, 'mean_ship_course_change_per_velocity_stage', 'mean_ship_course_change_per_velocity_stage', 3)
df2 = expand_list_column(df2, 'histogram_of_velocity', 'histogram_of_velocity', 7)
df2 = expand_list_column(df2, 'histogram_of_velocity_change', 'histogram_of_velocity_change', 8)
df2 = expand_list_column(df2, 'velocity_change_per_velocity_stage', 'velocity_change_per_velocity_stage', 3)

# ─────────────────────────────────────
# 5. x_cols 정의
x_cols = [
    'time_stamp', 'latitude', 'longitude', 'sea_surface_temperature', 'sea_surface_salinity',
    'current_speed1', 'current_speed2', 'wind1', 'wind2', 'tide1', 'tide2', 'bottom_depth',
    'chlorophyll', 'DIN', 'DIP', 'dissolved_oxygen',
    'fishery_density1', 'fishery_density2', 'fishery_density3', 'fishery_density4',
    'fishery_density5', 'fishery_density6', 'fishery_density7',
    'fishery_type', 'fishery_behavior', 'month', 'hour',
    'mean_ship_course_change', 'standard_deviation_of_ship_course_change',
    'histogram_of_ship_course_change1', 'histogram_of_ship_course_change2',
    'histogram_of_ship_course_change3', 'histogram_of_ship_course_change4',
    'histogram_of_ship_course_change5', 'histogram_of_ship_course_change6',
    'histogram_of_ship_course_change7', 'histogram_of_ship_course_change8',
    'histogram_of_ship_course_change9', 'histogram_of_ship_course_change10',
    'histogram_of_ship_course_change11', 'histogram_of_ship_course_change12',
    'mean_ship_course_change_per_velocity_stage1', 'mean_ship_course_change_per_velocity_stage2',
    'mean_ship_course_change_per_velocity_stage3',
    'mean_velocity_change', 'standard_deviation_of_velocity_change', 'mean_velocity',
    'histogram_of_velocity1', 'histogram_of_velocity2', 'histogram_of_velocity3',
    'histogram_of_velocity4', 'histogram_of_velocity5', 'histogram_of_velocity6',
    'histogram_of_velocity7',
    'histogram_of_velocity_change1', 'histogram_of_velocity_change2',
    'histogram_of_velocity_change3', 'histogram_of_velocity_change4',
    'histogram_of_velocity_change5', 'histogram_of_velocity_change6',
    'histogram_of_velocity_change7', 'histogram_of_velocity_change8',
    'velocity_change_per_velocity_stage1', 'velocity_change_per_velocity_stage2',
    'velocity_change_per_velocity_stage3',
    'observed_fishing_type', 'observed_fishing_info', 'px', 'py', 'filename'
]

# ─────────────────────────────────────
# 6. 누락된 컬럼을 0으로 채우기
for col in x_cols:
    if col not in df2.columns:
        df2[col] = 0

# ─────────────────────────────────────
# 7. 최종 컬럼 순서 정렬
df2 = df2[x_cols]

# # ─────────────────────────────────────
# # 8. 결과 저장 (선택사항)
# df2.to_csv('원본데이터_구조맞추기.csv', index=False)



#---------------------------------------------------------------------
# 학습 모델

import torch
from torch.utils.data import DataLoader
import datetime as dt

# ───────────────────────────────────────────────────────
# 1. 모델 로드
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = CustomModel().to(device)
ckpt = torch.load(r'C:\Users\ime\Desktop\유실_최종\조업행태모델\new_29_acuur_0_8100', map_location=device)
sd   = ckpt.get('model_state_dict', ckpt)
model.load_state_dict(sd)
model.eval()


# ───────────────────────────────────────────────────────
# 2. 전처리 + 예측
dataset = CustomDataset(df2)
dataloader = DataLoader(dataset, batch_size=32, shuffle=False)

all_preds = []
for xb, _, _, _ in dataloader:  # 4개 받아서 첫 번째만 사용
    xb = xb.to(device)
    xb = xb.permute(0, 2, 1)  # (B, 68, 1440)
    with torch.no_grad():
        logits = model(xb)        # (B, 1440, 4)
        preds = logits.argmax(dim=2).cpu().numpy()  # (B, 1440)
        all_preds.extend(preds)

# for xb, _ in dataloader:
#     xb = xb.to(device)
#     xb = xb.permute(0, 2, 1)  # (B, 68, 1440)
#     with torch.no_grad():
#         logits = model(xb)        # (B, 1440, 4)
#         preds = logits.argmax(dim=2).cpu().numpy()  # (B, 1440)
#         all_preds.extend(preds)


# ───────────────────────────────────────────────────────
# 3. 예측 결과를 원본 CSV에 병합
flat_preds = np.array(all_preds).flatten()


df2['fishery_behavior'] = flat_preds[:len(df2)]

# ───────────────────────────────────────────────────────
# 4. 결과 저장 (파일명 기반으로 경로 지정)
output_dir = r'C:\Users\ime\Desktop\유실_최종\label_dataset_csv'
os.makedirs(output_dir, exist_ok=True)

output_filename = f'{filename_hint}_label_data.csv'
output_path = os.path.join(output_dir, output_filename)

df2.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"✅ 예측 및 저장 완료: {output_path}")




#========================================================================
#========================================================================

import json

# CSV 파일 경로
csv_path = os.path.join(output_dir, output_filename)
df = pd.read_csv(csv_path)

# 리스트로 병합할 필드 정의
list_fields = {
    "current_speed": [f"current_speed{i}" for i in range(1, 3)],
    "wind": [f"wind{i}" for i in range(1, 3)],
    "tide": [f"tide{i}" for i in range(1, 3)],
    "fishery_density": [f"fishery_density{i}" for i in range(1, 8)],
    "histogram_of_ship_course_change": [f"histogram_of_ship_course_change{i}" for i in range(1, 13)],
    "mean_ship_course_change_per_velocity_stage": [f"mean_ship_course_change_per_velocity_stage{i}" for i in range(1, 4)],
    "histogram_of_velocity": [f"histogram_of_velocity{i}" for i in range(1, 8)],
    "histogram_of_velocity_change": [f"histogram_of_velocity_change{i}" for i in range(1, 9)],
    "velocity_change_per_velocity_stage": [f"velocity_change_per_velocity_stage{i}" for i in range(1, 4)]
}

# features 생성
features = []
for _, row in df.iterrows():
    properties = {}

    # 일반 필드 복사
    for col in df.columns:
        if any(col in subcols for subcols in list_fields.values()):
            continue
        properties[col] = row[col] if not pd.isna(row[col]) else None

    # 리스트 필드 병합
    for field_name, subcols in list_fields.items():
        values = [row[c] if not pd.isna(row[c]) else 0 for c in subcols]
        properties[field_name] = values

    # geometry 생성
    feature = {
        "type": "Feature",
        "properties": properties,
        "geometry": {
            "type": "Point",
            "coordinates": [round(row["longitude"], 4), round(row["latitude"], 4)]
        },
    }
    features.append(feature)

# 전체 GeoJSON 구조
geojson_output = {
    "type": "FeatureCollection",
    "name": f'{filename_hint}_label_data.geojson',
    "crs": {
        "filename": f'{filename_hint}_label_data.geojson',
        "start_time": str(df["time_stamp"].min()),
        "end_time": str(df["time_stamp"].max()),
        "weather": None,
        "AIS_porcessing_method": "Statistics",
        "phyiscial_information_processing_method": "Original",
        "biological_information_processing_method": "Original",
        "multiple_fishery_type": None,
        "nationality": None
    },
    "features": features
}


# 4. 결과 저장 (파일명 기반으로 경로 지정)
output_dir = r'C:\Users\ime\Desktop\유실_최종\label_dataset_geojson'
os.makedirs(output_dir, exist_ok=True)

output_filename = f'{filename_hint}_label_data.geojson'
output_path = os.path.join(output_dir, output_filename)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(geojson_output, f, ensure_ascii=False, indent=2)

print(f"✅ 저장 완료: {output_path}")



#=================================================================================
#=================================================================================
#=================================================================================
#=================================================================================



import os
#–– PROJ 환경 변수 설정 (pyproj ≥3용 PROJ_DATA 포함)
os.environ['PROJ_LIB']  = r'C:\Users\HUFS\anaconda3\envs\opendrift_env\Library\share\proj'
os.environ['PROJ_DATA'] = r'C:\Users\HUFS\anaconda3\envs\opendrift_env\Library\share\proj'

import json
import glob
import time
from datetime import datetime, timedelta


import csv
from dateutil import parser
import numpy as np
import pandas as pd
import xarray as xr
import cdsapi
import requests
import geopandas as gpd
from shapely.geometry import Point, LineString

import matplotlib.pyplot as plt
from scipy.interpolate import griddata

from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_netCDF_CF_generic
from collections import OrderedDict

import matplotlib.pyplot as plt
import matplotlib as mpl

plt.rcParams['font.family'] = 'Malgun Gothic'
mpl.rcParams['axes.unicode_minus'] = False



# 폴더 경로 및 파일명 완성
folder_path = r'.\label_dataset_geojson'
geojson_filename = f'{filename_hint}_label_data.geojson'
geojson_file = os.path.join(folder_path, geojson_filename)

# 에러 로그 경로
error_log_path = os.path.join(r'.\error_log', "error_log.csv")

# 에러 로그 파일이 없으면 생성
if not os.path.exists(error_log_path):
    with open(error_log_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["파일명", "오류종류", "오류메시지"])

# 단일 파일 처리
try:
    geojson_filename = os.path.basename(geojson_file)
    visibility = None            # 가시거리(m)
    distance_km = None           # 중간 투망 ↔ 양망 거리(km)
    prediction_result = "판단 불가"  # 예측 성공 여부

    with open(geojson_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 여기서 데이터 처리 로직 추가
    print(f"✅ 파일 로드 성공: {geojson_file}")



    ###############################################################################
    # PART 1: GeoJSON → DataFrame (투망 궤적 추출)
    ###############################################################################
    rows = []
    for feat in data.get("features", []):
        p = feat["properties"]
        beh = p.get("fishery_behavior")
        rows.append({
            "time_stamp": p["time_stamp"],
            "lon":         p["longitude"],
            "lat":         p["latitude"],
            "fishery_behavior": beh
        })

    df = pd.DataFrame(rows)
    df['time_stamp'] = pd.to_datetime(df['time_stamp'])
    df = df.sort_values('time_stamp').reset_index(drop=True)

    # 투망 시작 지점만 필터링 (1->3 또는 0->3 변화 시점)
    df['prev_behavior'] = df['fishery_behavior'].shift(1)
    drop_points = df[
        (df['fishery_behavior'] == 3) &
        (df['prev_behavior'] != 3)
    ].copy()

    df3 = df[df['fishery_behavior'] == 3].copy()
    if df3.empty or drop_points.empty:
        raise RuntimeError("투망 구간 또는 시작 시점 데이터가 없습니다.")

    lat_min = df3['lat'].min()
    lat_max = df3['lat'].max()
    lon_min = df3['lon'].min()
    lon_max = df3['lon'].max()
    start_time = df3['time_stamp'].min()
    end_limit  = df3['time_stamp'].max()

    first_time = pd.to_datetime(df3['time_stamp'].min())
    last_time  = pd.to_datetime(df3['time_stamp'].max())

    simulation_duration = last_time - start_time

    # 연, 월, 일 문자열로 추출
    year  = f"{first_time.strftime('%Y')}"
    month = f"{first_time.strftime('%m')}"
    day   = f"{first_time.strftime('%d')}"

    lat_min = df3['lat'].min() - 0.3
    lat_max = df3['lat'].max() + 0.3
    lon_min = df3['lon'].min() - 0.3
    lon_max = df3['lon'].max() + 0.3





    #=======================================================
    # 📌 1. GeoJSON → DataFrame
    #======================================================
    geojson_file
    with open(geojson_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = []
    for feature in data['features']:
        p = feature['properties']
        records.append({
            'time_stamp': p['time_stamp'],
            'lat': p['latitude'],
            'lon': p['longitude'],
            'fishery_behavior': p['fishery_behavior']
        })

    df = pd.DataFrame(records)
    df['time_stamp'] = pd.to_datetime(df['time_stamp'])

    # 📌 2. 시간 리스트 (1시간 간격)
    start_time = df['time_stamp'].min().replace(minute=0, second=0)
    end_time = df['time_stamp'].max()
    time_list = []
    current_time = start_time
    while current_time <= end_time:
        time_list.append(current_time)
        current_time += timedelta(hours=1)


    lat_grid = np.arange(round(lat_min, 2), round(lat_max, 2) + 0.01, 0.01)
    lon_grid = np.arange(round(lon_min, 2), round(lon_max, 2) + 0.01, 0.01)



    # ====== NetCDF 파일 경로 미리 설정 ======
    input_basename = os.path.splitext(os.path.basename(geojson_file))[0]
    nc_folder = r".\KHOA_nc_data"
    os.makedirs(nc_folder, exist_ok=True)


        # ====== API 호출 및 보간 수행 ======
    service_key = 'ANM8LV6zTsRNiGg6FCUMpw=='
    base_url = "http://www.khoa.go.kr/api/oceangrid/tidalCurrentAreaGeoJson/search.do"
    all_data = []


    output_path = os.path.join(nc_folder, f"{input_basename}_uv.nc")

    # ====== 파일 존재 시 생략 ======
    if os.path.exists(output_path):
        print(f"🔄 이미 NetCDF 존재, 다운로드 생략: {output_path}")
    else:

    # 📌 5. API 호출 및 데이터 저장
        for t in time_list:
            params = {
                "DataType": "tidalCurrentAreaGeoJson",
                "ServiceKey": service_key,
                "Date": t.strftime("%Y%m%d"),
                "Hour": t.strftime("%H"),
                "Minute": "00",
                "MinX": lon_min,
                "MaxX": lon_max,
                "MinY": lat_min,
                "MaxY": lat_max,
                "Scale": 2000000
            }

            print(f"[요청] {params['Date']} {params['Hour']}시")
            try:
                response = requests.get(base_url, params=params)
                if response.status_code == 200 and response.text.startswith('{'):
                    geojson_data = response.json()
                    for feature in geojson_data.get("features", []):
                        p = feature["properties"]
                        lat = p.get("lat")
                        lon = p.get("lon")
                        spd = p.get("current_speed")
                        direction = p.get("current_direct")
                        if None in (lat, lon, spd, direction):
                            continue
                        spd_m = spd / 100
                        rad = np.radians(direction)
                        u = spd_m * np.sin(rad)
                        v = spd_m * np.cos(rad)
                        all_data.append({
                            "time": t,
                            "lat": lat,
                            "lon": lon,
                            "u": u,
                            "v": v
                        })
                else:
                    print(f"❌ API 실패: status={response.status_code}")
            except Exception as e:
                print(f"[예외] {e}")

        # 📌 6. 정방격자 보간 및 NetCDF 생성
        df_all = pd.DataFrame(all_data)
        times = sorted(df_all["time"].unique())
        u_interp = []
        v_interp = []

        lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)

        for t in times:
            sub = df_all[df_all["time"] == t]
            points = np.array(sub[["lon", "lat"]])
            u_vals = sub["u"].values
            v_vals = sub["v"].values

            u_grid = griddata(points, u_vals, (lon_mesh, lat_mesh), method='linear')
            v_grid = griddata(points, v_vals, (lon_mesh, lat_mesh), method='linear')

            u_interp.append(u_grid)
            v_interp.append(v_grid)

        # 7. OpenDrift 인식 가능하도록 변수명 + 메타데이터 설정
        ds = xr.Dataset(
            {
                "eastward_sea_water_velocity": (["time", "lat", "lon"], np.array(u_interp)),
                "northward_sea_water_velocity": (["time", "lat", "lon"], np.array(v_interp)),
            },
            coords={
                "time": times,
                "lat": lat_grid,
                "lon": lon_grid,
            },
            attrs={
                "title": "정방격자 보간된 KHOA 해류 예측 데이터",
                "source": "tidalCurrentAreaGeoJson API"
            }
        )

        # 변수에 CF-convention 메타데이터 추가
        ds["eastward_sea_water_velocity"].attrs["standard_name"] = "eastward_sea_water_velocity"
        ds["eastward_sea_water_velocity"].attrs["units"] = "m s-1"
        ds["northward_sea_water_velocity"].attrs["standard_name"] = "northward_sea_water_velocity"
        ds["northward_sea_water_velocity"].attrs["units"] = "m s-1"

        os.makedirs(nc_folder, exist_ok=True)

        output_path = os.path.join(nc_folder, f"{input_basename}_uv.nc")
        ds.to_netcdf(output_path)
        print(f"✅ NetCDF 저장 완료: {output_path}")





    #=======================================================
    # PART 3: ERA5 CDS API 데이터 다운로드ㅡ
    #=======================================================

    # 날짜 범위 자동 생성 (예: ['09','10','11'] 등)
    num_days = (last_time.date() - first_time.date()).days + 1
    days = [(first_time + timedelta(days=i)).strftime("%d") for i in range(num_days)]

    # 시간 리스트 (00:00 ~ 23:00)
    times = [f"{h:02d}:00" for h in range(24)]


    area   = [lat_max, lon_min, lat_min, lon_max]

    era5_request = {
        "product_type": ["reanalysis"],
        "variable": [
            "10m_u_component_of_wind",
            "10m_v_component_of_wind"
        ],
        "year":  [year],
        "month": [month],
        "day":   days,
        "time":  times,
        "area":  area,
        "format": "netcdf"
    }


    # ====== 저장 경로 및 파일명 =====
    print("ERA5 요청:", era5_request)
    client = cdsapi.Client()
    wind_folder = r".\wind_data"
    os.makedirs(wind_folder, exist_ok=True)
    wind_path = os.path.join(wind_folder, f"{input_basename}_wind.nc")

    # ====== 파일 존재 시 다운로드 생략 ======
    if os.path.exists(wind_path):
        print(f"🔄 이미 wind 파일 존재, 다운로드 생략: {wind_path}")
    else:
        print("🌬️ ERA5 wind 요청:", era5_request)
        client = cdsapi.Client()
        client.retrieve(
            'reanalysis-era5-single-levels',
            era5_request,
            wind_path
        )
        print(f"✅ ERA5 다운로드 완료: {wind_path}")

    ###############################################################################
    # 가시거리 데이터 가져오기
    ###############################################################################

    from geopy.distance import geodesic

    # 관측소 목록 (위도, 경도)
    observation_stations = {
        "SF_0001": {"name": "부산항", "latitude": 35.091, "longitude": 129.099},
        "SF_0002": {"name": "부산항(신항)", "latitude": 35.023, "longitude": 128.808},
        "SF_0009": {"name": "해운대", "latitude": 35.15909, "longitude": 129.16026},
        "SF_0010": {"name": "울산항", "latitude": 35.501, "longitude": 129.387},
        "SF_0008": {"name": "여수항", "latitude": 34.754, "longitude": 127.752},
    }

    # API 키
    service_key = 'ANM8LV6zTsRNiGg6FCUMpw=='  # 발급받은 인증키

    # JSON 파일 로드
    json_file = geojson_file

    # fishery_behavior가 1인 데이터 추출 (첫 번째만)
    first_fishery_behavior = None
    for feature in data['features']:
        if feature['properties']['fishery_behavior'] == 1:
            first_fishery_behavior = feature
            break  # 첫 번째 데이터만 처리

    # 가장 가까운 관측소 찾기
    def find_closest_station(lat, lon):
        closest_station = None
        min_distance = float('inf')

        # 각 관측소와의 거리 계산
        for obs_code, station in observation_stations.items():
            station_location = (station["latitude"], station["longitude"])
            current_location = (lat, lon)
            distance = geodesic(station_location, current_location).kilometers
            
            if distance < min_distance:
                min_distance = distance
                closest_station = obs_code
        
        return closest_station
    

    # 가장 가까운 관측소에서 가시거리 정보 가져오기
    def get_visibility_from_station(obs_code, timestamp):
        # 날짜만 추출해서 YYYYMMDD 형식으로 변환
        date_only = timestamp.split(" ")[0].replace("-", "")  # 날짜만 추출 (YYYYMMDD)

        # API 요청 URL 생성
        url = f"http://www.khoa.go.kr/api/oceangrid/seafogReal/search.do" \
            f"?DataType=seafogReal" \
            f"&ServiceKey={service_key}" \
            f"&ObsCode={obs_code}" \
            f"&Date={date_only}" \
            f"&ResultType=json"
        
        # API 요청
        response = requests.get(url)

        # 응답 데이터 확인
        if response.status_code == 200:
            data = response.json()
            
            # 응답 데이터 출력
            if 'result' in data and 'data' in data['result']:
                closest_time_diff = float('inf')  # 가장 가까운 시간 차이
                closest_visibility = None

                for observation in data['result']['data']:
                    obs_time = observation['obs_time']
                    print(f"응답시간: {obs_time}")  # 응답 시간 출력

                    # 시간 차이 계산 (두 시간의 차이를 분 단위로 계산)
                    try:
                        timestamp_dt = parser.parse(timestamp.strip())
                        obs_time_dt = parser.parse(obs_time.strip())
                    except Exception as e:
                        print(f"시간 파싱 오류: {e}")
                        continue

                    time_diff = abs((timestamp_dt - obs_time_dt).total_seconds())  # 시간 차이 (초 단위)

                    # 가장 가까운 시간 찾기
                    if time_diff < closest_time_diff:
                        closest_time_diff = time_diff
                        if 'vis' in observation:
                            closest_visibility = observation['vis']
                
                if closest_visibility:
                    return closest_visibility  # 가장 가까운 가시거리 반환
        return None

    # 초기 변수
    visibility = None
    latitude = None
    longitude = None
    timestamp = None
    closest_station = None

    # fishery_behavior = 1인 데이터가 있다면 정보 저장
    if first_fishery_behavior:
        timestamp = first_fishery_behavior['properties']['time_stamp']
        latitude = first_fishery_behavior['properties']['latitude']
        longitude = first_fishery_behavior['properties']['longitude']
        closest_station = find_closest_station(latitude, longitude)
    else:
        print("fishery_behavior가 1인 데이터가 없습니다.")

    # CSV 경로 지정
    output_csv_path = r".\가시거리csv\visibility_log.csv"

    # 1. CSV에서 확인
    if os.path.exists(output_csv_path):
        with open(output_csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["filename"] == geojson_filename:
                    visibility = row["visibility_m"]
                    print(f"🔄 기존 CSV에서 가시거리 불러옴: {visibility}")
                    break

    # 2. 없으면 API 호출
    if visibility is None  and timestamp and closest_station:
        visibility = get_visibility_from_station(closest_station, timestamp)

        if visibility:
            print(f"시간: {timestamp} / 위치: ({latitude}, {longitude})")
            print(f"가장 가까운 관측소: {observation_stations[closest_station]['name']} ({closest_station})")
            print(f"가시거리: {visibility} 미터")
        else:
            print(f"가시거리 정보를 불러올 수 없습니다.")

    # 3. CSV에 저장
    if not os.path.exists(output_csv_path):
        with open(output_csv_path, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "visibility_m"])

    # 4. 중복 저장 방지 후 추가
    already_exists = False
    with open(output_csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["filename"] == geojson_filename:
                already_exists = True
                break

    if not already_exists:
        with open(output_csv_path, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([geojson_filename, visibility if visibility else "N/A"])



    ###############################################################################
    # (4) ERA5 wind파일 경로
    ###############################################################################
    merged_file = os.path.join(nc_folder, f"{input_basename}_uv.nc")


    wind_file = os.path.join(wind_folder, f"{input_basename}_wind.nc")


    # bottom_depth = r"C:\Users\HUFS\Desktop\opendrfit_middle-20250501T132247Z-1-001\bottom_depth.nc"
    # print("Bottom depth file:", bottom_depth)





    ###############################################################################
    # PART 3: 해안선 읽기
    ###############################################################################
    # 해안선 읽기
    coastline_file = r"C:\Users\HUFS\Desktop\2024년 전국해안선.shp"
    coast = gpd.read_file(coastline_file)
    if coast.crs is None or coast.crs.to_string() != 'EPSG:4326':
        coast = coast.to_crs(epsg=4326)
    coast_proj = coast.to_crs(epsg=3857)
    coastal_zone = coast_proj.buffer(15000).unary_union
    coastal_zone_wgs84 = gpd.GeoSeries(coastal_zone, crs=3857).to_crs(epsg=4326).unary_union




    ###############################################################################
    # OpenDrift 모델 설정 - ConnectedNetDrift로 변경
    ###############################################################################
    class ConnectedNetDrift(OceanDrift):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.ideal_distance_m = 270  # 자망 이상 거리 (m)
            self.k = 0.05  # 조정 강도 계수 (0~1 사이, 높일수록 자망 형태 강함)
            self.step = 2  # 몇 개 간격으로 연결할지 (3개 간격 연결)
            self.adjustment_loops = 2  # update 내 반복 조정 횟수

        def update(self):
            super().update()
            lon = self.elements.lon.copy()
            lat = self.elements.lat.copy()
            n = len(lon)

            for _ in range(self.adjustment_loops):
                for i in range(self.step, n):
                    prev_coord = (lat[i - self.step], lon[i - self.step])
                    curr_coord = (lat[i], lon[i])
                    dist = geodesic(prev_coord, curr_coord).meters
                    delta = dist - self.ideal_distance_m

                    if abs(delta) > 0.1:
                        dlat = lat[i] - lat[i - self.step]
                        dlon = lon[i] - lon[i - self.step]
                        scale = delta / dist * self.k

                        lat[i]              -= dlat * scale
                        lon[i]              -= dlon * scale
                        lat[i - self.step]  += dlat * scale
                        lon[i - self.step]  += dlon * scale

            self.elements.lon[:] = lon
            self.elements.lat[:] = lat


    o = ConnectedNetDrift(loglevel=20)
    reader_ocean = reader_netCDF_CF_generic.Reader(merged_file)
    reader_met   = reader_netCDF_CF_generic.Reader(wind_file)
    # reader_bathy = reader_netCDF_CF_generic.Reader(bottom_depth)
    o.add_reader([reader_ocean, reader_met])

    o.set_config('seed:wind_drift_factor', 0.02)
    o.set_config('drift:stokes_drift', True)
    o.set_config('general:seafloor_action', 'none')
    o.set_config('drift:vertical_advection', False)
    o.set_config('drift:vertical_mixing', False)
    o.set_config('general:coastline_action', 'previous')

    ###############################################################################
    # 입자 시딩 (자망을 순차적으로 시딩)
    df_tumang = df[df['fishery_behavior'] == 0].copy()
    df_yangmang = df[df['fishery_behavior'] == 1].copy()
    df_tumang['time_stamp'] = pd.to_datetime(df_tumang['time_stamp'])
    df_tumang = df_tumang.sort_values('time_stamp').reset_index(drop=True)
    df_yangmang = df_yangmang.sort_values('time_stamp').reset_index(drop=True)

    for i, row in df_tumang.iterrows():
        o.seed_elements(
            lon=row['lon'],
            lat=row['lat'],
            time=row['time_stamp'],
            z=0.0,
            origin_marker=np.array([i], dtype=np.int32)
        )
        print(f"[SEED] time={row['time_stamp']}, 위치=({row['lon']}, {row['lat']})")

    ###############################################################################
    # 시뮬레이션 실행
    start_time_sim = df_tumang['time_stamp'].min()
    end_time_sim   = df[df['fishery_behavior'] == 1]['time_stamp'].max()
    # end_time_sim   = df_yangmang['time_stamp'].min()
    simulation_duration = end_time_sim - start_time_sim

    o.run(
        time_step=600,
        time_step_output=1800,
        duration=simulation_duration
    )


    ###############################################################################
    # 중간 입자 최종 위치 추출
    num_particles = len(df_tumang)
    mid_index = num_particles // 2  # 자망 중간 시딩 입자

    lon_traj, _ = o.get_property('lon')
    lat_traj, _ = o.get_property('lat')

    mid_lon = lon_traj[-1, mid_index].item()  # float 값 추출
    mid_lat = lat_traj[-1, mid_index].item()

    print(f"[중간 입자 최종 위치] lon: {mid_lon:.5f}, lat: {mid_lat:.5f}")

    ###############################################################################
    # 양망 구간 중간 위치 추출
    num_yangmang = len(df_yangmang)
    if num_yangmang == 0:
        raise RuntimeError("양망 데이터가 존재하지 않습니다.")

    mid_index_yangmang = num_yangmang // 2
    mid_row_yangmang = df_yangmang.iloc[mid_index_yangmang]

    mid_lon_yang = mid_row_yangmang['lon']
    mid_lat_yang = mid_row_yangmang['lat']
    mid_time_yang = mid_row_yangmang['time_stamp']

    print(f"[양망 중간 위치] time={mid_time_yang}, lon={mid_lon_yang:.5f}, lat={mid_lat_yang:.5f}")

    ###############################################################################
    # 투망 시딩 중간 위치 추출
    mid_row_tumang = df_tumang.iloc[mid_index]
    mid_lon_tumang = mid_row_tumang['lon']
    mid_lat_tumang = mid_row_tumang['lat']
    print(f"[투망 중간 시딩 위치] lon={mid_lon_tumang:.5f}, lat={mid_lat_tumang:.5f}")


    #####################################################################
    # 거리 계산
    from geopy.distance import geodesic

    point_mid_drift = (mid_lat, mid_lon)  # 예측된 자망 중간 입자의 최종 위치
    point_mid_yang = (mid_lat_yang, mid_lon_yang)  # 실제 양망 중간 위치
    point_mid_tumang = (mid_lat_tumang, mid_lon_tumang)  # 실제 투망 중간 시딩 위치

    distance_km = geodesic(point_mid_drift, point_mid_yang).kilometers
    distance_tumang_yang_km = geodesic(point_mid_tumang, point_mid_yang).kilometers

    print(f"[중간 입자 ↔ 양망 중간 지점 거리] 약 {distance_km:.3f} km")
    print(f"[투망 시딩 중간 ↔ 양망 중간 거리] 약 {distance_tumang_yang_km:.3f} km")

    ###############################################################################
    # 가시거리 단위 변환 및 결과 판단
    try:
        # 문자열일 경우 숫자로 변환 시도
        visibility_km = float(visibility) / 1000 if visibility not in (None, "N/A", "불러오기 실패") else None
    except (ValueError, TypeError):
        visibility_km = None
    prediction_result = "판단 불가"
    if visibility_km is not None:
        prediction_result = "성공" if distance_km < visibility_km else "실패"

    ###############################################################################
    # CSV 저장

    result_csv_path = r".\예측csv\prediction_result.csv"

    # 헤더 작성
    if not os.path.exists(result_csv_path):
        with open(result_csv_path, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                "filename", 
                "예측거리_km", 
                "가시거리_km", 
                "예측결과", 
                "투망중간↔양망중간_km"
            ])

    # 파일명 추출
    geojson_filename = os.path.basename(geojson_file)

    # 문자열 변환 (None 대응)
    distance_str = f"{distance_km:.3f}" if distance_km is not None else "N/A"
    visibility_str = f"{visibility_km:.3f}" if visibility_km is not None else "N/A"
    tumang_yang_str = f"{distance_tumang_yang_km:.3f}" if distance_tumang_yang_km is not None else "N/A"
    result_str = prediction_result if prediction_result is not None else "판단 불가"


    # 결과 쓰기
    with open(result_csv_path, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([
            geojson_filename, 
            distance_str, 
            visibility_str, 
            result_str, 
            tumang_yang_str
        ])

    ###############################################################################
    # 결과 시각화


    # 궤적 추출 (OpenDrift 1.13.1 기준)
    lon_traj, _ = o.get_property('lon')
    lat_traj, _ = o.get_property('lat')

    plt.figure(figsize=(10, 7))

    # 궤적 라인
    for i in range(lon_traj.shape[1]):
        plt.plot(lon_traj[:, i], lat_traj[:, i], linewidth=0.5, alpha=0.3, color='gray')

    # 최종 위치 (마지막 시간단계)
    lon_final = lon_traj[-1, :]
    lat_final = lat_traj[-1, :]
    plt.scatter(lon_final, lat_final, s=10, color='black', alpha=0.6, label='시뮬레이션 최종 위치')

    # 실제 투망 및 양망
    plt.scatter(df_tumang['lon'], df_tumang['lat'], s=30, color='blue', marker='^', label='투망 위치 (0)')
    plt.scatter(df_yangmang['lon'], df_yangmang['lat'], s=30, color='red', marker='v', label='양망 위치 (1)')
    plt.scatter(mid_lon, mid_lat, color='green', s=50, marker='*', label='중간 입자 최종 위치')
    plt.scatter(mid_lon_yang, mid_lat_yang, color='orange', s=60, marker='X', label='양망 중간 지점')
    plt.scatter(mid_lon_tumang, mid_lat_tumang, color='cyan', s=60, marker='P', label='투망 중간 지점')



    # 축 범위 자동 설정 (전체 좌표 포함)
    all_lon = np.concatenate([lon_final, df_tumang['lon'].values, df_yangmang['lon'].values])
    all_lat = np.concatenate([lat_final, df_tumang['lat'].values, df_yangmang['lat'].values])
    plt.xlim(all_lon.min() - 0.01, all_lon.max() + 0.01)
    plt.ylim(all_lat.min() - 0.01, all_lat.max() + 0.01)


    # 예측된 중간 입자 좌표 텍스트 표시
    plt.text(
        mid_lon + 0.005, mid_lat, 
        f"({mid_lon:.3f}, {mid_lat:.3f})", 
        fontsize=8, 
        ha='left',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='gray', alpha=0.7)
    )


    plt.text(
        all_lon.max() - 0.005, all_lat.max() - 0.005,
        f"중간 거리: {distance_km:.2f} km",
        fontsize=10,
        ha='right',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.7)
    )


    # 예측 정보 박스 (오른쪽 하단)
    info_text = f"가시거리: {visibility_str} km\n예측결과: {result_str}"
    plt.text(
        all_lon.min() + 0.005, all_lat.min() + 0.005,
        info_text,
        fontsize=10,
        ha='left',
        va='bottom',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='black', alpha=0.6)
    )

    # 투망↔양망 거리 박스 (왼쪽 상단)
    tumang_yang_text = f"투망↔양망 거리: {distance_tumang_yang_km:.2f} km"
    plt.text(
        all_lon.min() + 0.005, all_lat.max() - 0.005,
        tumang_yang_text,
        fontsize=10,
        ha='left',
        va='top',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='black', alpha=0.6)
    )

    plt.title("시뮬레이션 궤적 및 최종 위치 vs 실제 투망/양망 위치")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    # plt.show()

    # === 시각화 결과 자동 저장 ===
    plot_output_dir = r".\시각화결과"
    os.makedirs(plot_output_dir, exist_ok=True)
    plot_filename = f"{input_basename}.png"
    plot_path = os.path.join(plot_output_dir, plot_filename)
    plt.savefig(plot_path, dpi=300)
    plt.close()


        # === 예측된 중간 위치 저장 ===
    latlon_output_dir = r".\prediction_lat_lon"
    os.makedirs(latlon_output_dir, exist_ok=True)
    latlon_csv_path = os.path.join(latlon_output_dir, "predicted_positions.csv")

    # CSV 없으면 헤더 작성
    if not os.path.exists(latlon_csv_path):
        with open(latlon_csv_path, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "lat", "lon"])

    # 중복 저장 방지 (같은 파일명 중복 저장 안 함)
    already_exists = False
    with open(latlon_csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["filename"] == geojson_filename:
                already_exists = True
                break

    if not already_exists:
        with open(latlon_csv_path, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([geojson_filename, mid_lat, mid_lon])




    print("✅ 완료")

except Exception as e:
    print(f"❌ 오류 발생: {geojson_file} - {e}")
    with open(error_log_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([os.path.basename(geojson_file), type(e).__name__, str(e)])