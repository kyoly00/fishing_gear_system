import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import xarray as xr
import cdsapi
import requests
from scipy.interpolate import griddata
from geopy.distance import geodesic

# ─────────────────────────────────────────────
# 1. 유속 보정 함수
# ─────────────────────────────────────────────
def apply_adjustments(spd, direction, adjust_dict):
    rad = np.radians(direction)

    # 기본 벡터 계산
    u = spd * np.sin(rad)
    v = spd * np.cos(rad)

    # 4. TO → FROM 회전
    if adjust_dict.get('reverse_vector_by_angle_180', False):
        rad = rad + np.pi
        u = spd * np.sin(rad)
        v = spd * np.cos(rad)

    # 6. 좌표계 반시계 전환
    if adjust_dict.get('counterclockwise', False):
        rad = np.radians(360 - direction)
        u = spd * np.sin(rad)
        v = spd * np.cos(rad)

    # 7. 임의 각도 회전 (예: 20도)
    theta = adjust_dict.get('rotate_deg', 0)
    if theta != 0:
        theta_rad = np.radians(theta)
        u_new = u * np.cos(theta_rad) - v * np.sin(theta_rad)
        v_new = u * np.sin(theta_rad) + v * np.cos(theta_rad)
        u, v = u_new, v_new

    # 8. 스케일 조정
    scale = adjust_dict.get('scale_factor', 1.0)
    u *= scale
    v *= scale

    # 1~3. 좌/우/상/하/완전 반전
    if adjust_dict.get('invert_x', False):
        u *= -1
    if adjust_dict.get('invert_y', False):
        v *= -1
    if adjust_dict.get('invert_all', False):
        u *= -1
        v *= -1

    return u, v


# ─────────────────────────────────────────────
# 2. 가장 가까운 관측소 선택 함수
# ─────────────────────────────────────────────
def get_sorted_stations(station_df, lat, lon):
    station_df = station_df.copy()
    station_df['distance'] = station_df.apply(
        lambda row: geodesic((row['lat'], row['lon']), (lat, lon)).km, axis=1
    )
    return station_df.sort_values('distance')

# ─────────────────────────────────────────────
# 3. KHOA 해류 API 호출 및 NetCDF 저장
# ─────────────────────────────────────────────
def fetch_khoa_uv(time_list, lon_min, lon_max, lat_min, lat_max, lon_grid, lat_grid,
                adjust_dict, output_path, service_key):
    
    if os.path.exists(output_path):
        print(f"🔄 기존 NetCDF 발견, 방향 복정 및 패치 중: {output_path}")
        ds = xr.open_dataset(output_path)

        if 'eastward_sea_water_velocity' in ds and 'northward_sea_water_velocity' in ds:
            ds = ds.rename({
                'eastward_sea_water_velocity': 'x_sea_water_velocity',
                'northward_sea_water_velocity': 'y_sea_water_velocity'
            })
            ds['x_sea_water_velocity'].attrs['standard_name'] = 'x_sea_water_velocity'
            ds['y_sea_water_velocity'].attrs['standard_name'] = 'y_sea_water_velocity'

            ds = ds.interpolate_na(dim='time', method='linear')  # 9. 시간 보간 적용

            return ds
        else:
            raise RuntimeError("필수 변수(eastward/northward)가 존재하지 않음")

    all_data = []
    base_url = "http://www.khoa.go.kr/api/oceangrid/tidalCurrentAreaGeoJson/search.do"
    for t in time_list:
        params = {
            "DataType": "tidalCurrentAreaGeoJson",
            "ServiceKey": service_key,
            "Date": t.strftime("%Y%m%d"),
            "Hour": t.strftime("%H"),
            "Minute": "00",
            "MinX": lon_min, "MaxX": lon_max,
            "MinY": lat_min, "MaxY": lat_max,
            "Scale": 1000000
        }
        resp = requests.get(base_url, params=params)
        if resp.status_code != 200 or not resp.text.startswith('{'):
            print(f"❌ API 실패({resp.status_code}) at {t}")
            continue

        for feat in resp.json().get('features', []):
            p = feat['properties']
            lat, lon = p.get('lat'), p.get('lon')
            spd_raw, direction = p.get('current_speed'), p.get('current_direct')
            if None in (lat, lon, spd_raw, direction):
                continue
            spd = spd_raw / 100.0
            u, v = apply_adjustments(spd, direction, adjust_dict)
            all_data.append({
                'time': t,
                'lat': lat,
                'lon': lon,
                'u': u,
                'v': v
            })

    df_all = pd.DataFrame(all_data)
    times = sorted(df_all['time'].unique())
    lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)
    u_interp, v_interp = [], []
    for t in times:
        sub = df_all[df_all['time'] == t]
        pts = sub[['lon', 'lat']].values
        u_grid = griddata(pts, sub['u'], (lon_mesh, lat_mesh), method='linear')
        v_grid = griddata(pts, sub['v'], (lon_mesh, lat_mesh), method='linear')
        u_interp.append(u_grid)
        v_interp.append(v_grid)

    ds = xr.Dataset(
        {
            'x_sea_water_velocity': (['time', 'lat', 'lon'], np.array(u_interp)),
            'y_sea_water_velocity': (['time', 'lat', 'lon'], np.array(v_interp))
        },
        coords={
            'time': times,
            'lat': lat_grid,
            'lon': lon_grid
        },
        attrs={
            'title': "KHOA 해류 예측 데이터 (ub/vb 복정 적용)",
            'source': "tidalCurrentAreaGeoJson API"
        }
    )
    ds['x_sea_water_velocity'].attrs.update(standard_name="x_sea_water_velocity", units="m s-1")
    ds['y_sea_water_velocity'].attrs.update(standard_name="y_sea_water_velocity", units="m s-1")

    return ds

def fetch_temperature(time_list, lat, lon, service_key):
    # 조위관측소 데이터
    tide_data = [
        ["DT_0063", "가덕도", 35.024, 128.81],
        ["DT_0031", "거문도", 34.028, 127.308],
        ["DT_0029", "거제도", 34.801, 128.699],
        ["DT_0026", "고흥발포", 34.481, 127.342],
        ["DT_0018", "군산", 35.975, 126.563],
        ["DT_0017", "대산", 37.007, 126.352],
        ["DT_0062", "마산", 35.197, 128.576],
        ["DT_0023", "모슬포", 33.214, 126.251],
        ["DT_0007", "목포", 34.779, 126.375],
        ["DT_0006", "묵호", 37.55, 129.116],
        ["DT_0025", "보령", 36.406, 126.486],
        ["DT_0005", "부산", 35.096, 129.035],
        ["DT_0061", "삼천포", 34.924, 128.069],
        ["DT_0094", "서거차도", 34.251, 125.915],
        ["DT_0010", "서귀포", 33.24, 126.561],
        ["DT_0022", "성산포", 33.474, 126.927],
        ["DT_0012", "속초", 38.207, 128.594],
        ["IE_0061", "신안가거초", 33.941, 124.592],
        ["DT_0008", "안산", 37.192, 126.647],
        ["DT_0067", "안흥", 36.674, 126.129],
        ["DT_0037", "어청도", 36.117, 125.984],
        ["DT_0016", "여수", 34.747, 127.765],
        ["IE_0062", "옹진소청초", 37.423, 124.738],
        ["DT_0027", "완도", 34.315, 126.759],
        ["DT_0013", "울릉도", 37.491, 130.913],
        ["DT_0020", "울산", 35.501, 129.387],
        ["IE_0060", "이어도", 32.122, 125.182],
        ["DT_0001", "인천", 37.451, 126.592],
        ["DT_0004", "제주", 33.527, 126.543],
        ["DT_0028", "진도", 34.377, 126.308],
        ["DT_0021", "추자도", 33.961, 126.3],
        ["DT_0014", "통영", 34.827, 128.434],
        ["DT_0002", "평택", 36.966, 126.822],
        ["DT_0091", "포항", 36.051, 129.376],
        ["DT_0011", "후포", 36.677, 129.453],
        ["DT_0035", "흑산도", 34.684, 125.435],
    ]

    df_tide = pd.DataFrame(tide_data, columns=["obs_code", "name", "lat", "lon"])


    # 해상관측부이 데이터
    buoy_data = [
        ["TW_0088", "감천항", 35.052, 129.003],
        ["TW_0077", "경인항", 37.523, 126.592],
        ["TW_0089", "경포대해수욕장", 37.808, 128.931],
        ["TW_0095", "고래불해수욕장", 36.58, 129.454],
        ["TW_0074", "광양항", 34.859, 127.792],
        ["TW_0072", "군산항", 35.984, 126.508],
        ["TW_0091", "낙산해수욕장", 38.122, 128.65],
        ["KG_0025", "남해동부", 34.222, 128.419],
        ["TW_0069", "대천해수욕장", 36.274, 126.457],
        ["TW_0085", "마산항", 35.103, 128.631],
        ["TW_0094", "망상해수욕장", 37.616, 129.103],
        ["TW_0086", "부산항신항", 35.043, 128.761],
        ["TW_0079", "상왕등도", 35.652, 126.194],
        ["TW_0081", "생일도", 34.258, 126.96],
        ["TW_0093", "속초해수욕장", 38.198, 128.631],
        ["TW_0083", "여수항", 34.794, 127.808],
        ["TW_0078", "완도항", 34.325, 126.763],
        ["TW_0080", "우이도", 34.543, 125.802],
        ["KG_0101", "울릉도북동", 38.007, 131.552],
        ["KG_0102", "울릉도북서", 37.742, 130.601],
        ["TW_0076", "인천항", 37.389, 126.533],
        ["KG_0021", "제주남부", 32.09, 126.965],
        ["KG_0028", "제주해협", 33.7, 126.59],
        ["TW_0075", "중문해수욕장", 33.234, 126.409],
        ["TW_0082", "태안항", 37.006, 126.27],
        ["TW_0084", "통영항", 34.773, 128.46],
        ["TW_0070", "평택당진항", 37.136, 126.54],
        ["HB_0002", "한수원_고리", 35.318, 129.314],
        ["HB_0001", "한수원_기장", 35.182, 129.235],
        ["HB_0009", "한수원_나곡", 37.119, 129.395],
        ["HB_0008", "한수원_덕천", 37.1, 129.404],
        ["HB_0007", "한수원_온양", 37.019, 129.425],
        ["HB_0003", "한수원_진하", 35.384, 129.368],
    ]

    df_buoy = pd.DataFrame(buoy_data, columns=["obs_code", "name", "lat", "lon"])

    total_stations = pd.concat([df_tide, df_buoy], ignore_index=True)
    sorted_stations = get_sorted_stations(total_stations, lat, lon)

    temp_records = []
    for _, row in sorted_stations.iterrows():
        obs_code = row['obs_code']
        data_type = "tideObsTemp" if obs_code.startswith("DT") or obs_code.startswith("IE") else "tidalBuTemp"
        url_with_key = f"http://www.khoa.go.kr/api/oceangrid/{data_type}/search.do?ServiceKey={service_key}"

        temp_records.clear()
        for date_str in sorted(set(t.strftime('%Y%m%d') for t in time_list)):
            params = {
                "ObsCode": obs_code,
                "Date": date_str,
                "ResultType": "json"
            }
            r = requests.get(url_with_key, params=params)
            if not r.ok:
                continue
            result_json = r.json()
            if result_json.get("result", {}).get("error") == "No search data":
                continue

            for rec in result_json.get("result", {}).get("data", []):
                try:
                    temp_records.append({
                        "time": pd.to_datetime(rec["record_time"]),
                        "sea_water_temperature": float(rec["water_temp"])
                    })
                except:
                    continue

        if temp_records:
            print(f"✅ 수온 데이터 사용 관측소: {row['name']} ({obs_code})")
            break  # ✔️ 한 관측소에서 데이터 수집되면 종료

    if not temp_records:
        print("⚠️ 수온 데이터 없음 (모든 관측소 시도 실패)")

    return pd.DataFrame(temp_records)



def fetch_salinity(time_list, lat, lon, service_key):
    stations = [
    ["DT_0063", "가덕도", 35.024, 128.81],
    ["DT_0031", "거문도", 34.028, 127.308],
    ["DT_0029", "거제도", 34.801, 128.699],
    ["DT_0026", "고흥발포", 34.481, 127.342],
    ["DT_0018", "군산", 35.975, 126.563],
    ["DT_0062", "마산", 35.197, 128.576],
    ["DT_0023", "모슬포", 33.214, 126.251],
    ["DT_0007", "목포", 34.779, 126.375],
    ["DT_0006", "묵호", 37.55, 129.116],
    ["DT_0025", "보령", 36.406, 126.486],
    ["DT_0005", "부산", 35.096, 129.035],
    ["DT_0061", "삼천포", 34.924, 128.069],
    ["DT_0094", "서거차도", 34.251, 125.915],
    ["DT_0010", "서귀포", 33.24, 126.561],
    ["DT_0022", "성산포", 33.474, 126.927],
    ["DT_0012", "속초", 38.207, 128.594],
    ["IE_0061", "신안가거초", 33.941, 124.592],
    ["DT_0008", "안산", 37.192, 126.647],
    ["DT_0067", "안흥", 36.674, 126.129],
    ["DT_0037", "어청도", 36.117, 125.984],
    ["DT_0016", "여수", 34.747, 127.765],
    ["IE_0062", "옹진소청초", 37.423, 124.738],
    ["DT_0027", "완도", 34.315, 126.759],
    ["DT_0013", "울릉도", 37.491, 130.913],
    ["DT_0020", "울산", 35.501, 129.387],
    ["IE_0060", "이어도", 32.122, 125.182],
    ["DT_0001", "인천", 37.451, 126.592],
    ["DT_0004", "제주", 33.527, 126.543],
    ["DT_0028", "진도", 34.377, 126.308],
    ["DT_0021", "추자도", 33.961, 126.3],
    ["DT_0014", "통영", 34.827, 128.434],
    ["DT_0091", "포항", 36.051, 129.376],
    ["DT_0011", "후포", 36.677, 129.453],
    ["DT_0035", "흑산도", 34.684, 125.435]
    ]
    station_df = pd.DataFrame(stations, columns=['obs_code', 'name', 'lat', 'lon'])
    sorted_stations = get_sorted_stations(station_df, lat, lon)

    url = "http://www.khoa.go.kr/api/oceangrid/tideObsSalt/search.do"
    url_with_key = f"{url}?ServiceKey={service_key}"
    sal_records = []

    for _, row in sorted_stations.iterrows():
        obs_code = row['obs_code']
        sal_records.clear()

        for date_str in sorted(set(t.strftime('%Y%m%d') for t in time_list)):
            params = {
                "ObsCode": obs_code,
                "Date": date_str,
                "ResultType": "json"
            }
            r = requests.get(url_with_key, params=params)
            if not r.ok:
                continue

            result_json = r.json()
            if result_json.get("result", {}).get("error") == "No search data":
                continue

            for d in result_json.get("result", {}).get("data", []):
                try:
                    sal_records.append({
                        "time": pd.to_datetime(d['record_time']),
                        "sea_water_salinity": float(d['salinity'])
                    })
                except:
                    continue

        if sal_records:
            print(f"✅ 염분 데이터 사용 관측소: {row['name']} ({obs_code})")
            break

    if not sal_records:
        print("⚠️ 염분 데이터 없음 (모든 관측소 시도 실패)")

    return pd.DataFrame(sal_records)


def fetch_all_khoa(time_list, lon_min, lon_max, lat_min, lat_max,
                   lon_grid, lat_grid, adjust_dict, output_path, service_key):

    # 1. 해류 데이터 (기존 방식 유지)
    ds = fetch_khoa_uv(time_list, lon_min, lon_max, lat_min, lat_max,
                       lon_grid, lat_grid, adjust_dict, output_path, service_key)

    # 2. 기준 시간 및 공간 정보
    ds_time = pd.to_datetime(ds['time'].values)
    lat_vals = ds['lat'].values
    lon_vals = ds['lon'].values

    # 3. 중심 좌표 및 날짜 리스트 생성
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2
    day_time_list = pd.to_datetime(sorted(set(t.normalize() for t in time_list)))

    # 4. 수온/염분 요청 (분 단위 데이터 → 하루 단위 요청)
    temp_df = fetch_temperature(day_time_list, center_lat, center_lon, service_key)
    sal_df  = fetch_salinity(day_time_list, center_lat, center_lon, service_key)

    # 5. 시간 기준 최근접 보간 (공간 동일값으로 확장)
    def expand_to_grid(df, var_name):
        ts = df.set_index('time')[var_name]
        ts_interp = ts.reindex(ds_time, method='nearest', tolerance=pd.Timedelta('6H'))
        ts_interp = ts_interp.ffill().bfill()

        # (time, lat, lon) → 전체 공간에 동일한 값
        var_3d = np.broadcast_to(ts_interp.values[:, np.newaxis, np.newaxis],
                                 (len(ds_time), len(lat_vals), len(lon_vals)))
        return var_3d

    temp_grid = expand_to_grid(temp_df, 'sea_water_temperature')
    sal_grid  = expand_to_grid(sal_df, 'sea_water_salinity')

    # 6. dataset에 삽입
    ds['sea_water_temperature'] = (('time', 'lat', 'lon'), temp_grid)
    ds['sea_water_salinity'] = (('time', 'lat', 'lon'), sal_grid)

    ds['sea_water_temperature'].attrs.update(standard_name="sea_water_temperature", units="degree_Celsius")
    ds['sea_water_salinity'].attrs.update(standard_name="sea_water_salinity", units="psu")

    # 7. 저장
    patched_path = output_path.replace('.nc', '_patched.nc')
    os.makedirs(os.path.dirname(patched_path), exist_ok=True)
    ds.to_netcdf(patched_path)
    print(f"✅ 새 NetCDF 저장 완료: {patched_path}")
    return patched_path



# ─────────────────────────────────────────────────────
# 4) ERA5 풍속 다운로드
# ─────────────────────────────────────────────────────

def fetch_era5(first_time, last_time, lat_min, lat_max,
            lon_min, lon_max, output_path):
    patched_path = output_path.replace('.nc', '_patched.nc')

    # wind 파일이 없으면 다운로드
    if not os.path.exists(output_path):
        year  = first_time.strftime('%Y')
        month = first_time.strftime('%m')
        num_days = (last_time.date() - first_time.date()).days + 1
        days = [(first_time + timedelta(days=i)).strftime('%d') for i in range(num_days)]
        times = [f"{h:02d}:00" for h in range(24)]
        area = [lat_max, lon_min, lat_min, lon_max]

        era5_request = {
            'product_type': ['reanalysis'],
            'variable': ['10m_u_component_of_wind','10m_v_component_of_wind'],
            'year':  [year], 'month': [month], 'day': days,
            'time': times, 'area': area, 'format': 'netcdf'
        }
        print('🌬️ ERA5 wind 요청:', era5_request)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cds = cdsapi.Client()
        cds.retrieve('reanalysis-era5-single-levels', era5_request, output_path)
        print(f"✅ ERA5 다운로드 완료: {output_path}")
    else:
        print(f"🔄 기존 wind 파일 사용: {output_path}")

    # ✅ 원본 wind 파일을 열어서 rename + 속성 추가 + 저장
    ds = xr.open_dataset(output_path)

    rename_dict = {}
    if 'u10' in ds:
        rename_dict['u10'] = 'x_wind'
    if 'v10' in ds:
        rename_dict['v10'] = 'y_wind'
    ds = ds.rename(rename_dict)

    if 'x_wind' in ds:
        ds['x_wind'].attrs['standard_name'] = 'x_wind'
    if 'y_wind' in ds:
        ds['y_wind'].attrs['standard_name'] = 'y_wind'

    ds.to_netcdf(patched_path)
    print(f"✅ wind 패치 저장 완료: {patched_path}")
    return patched_path


# ─────────────────────────────────────────────────────
# 5) 가시거리 조회
# ─────────────────────────────────────────────────────

def get_visibility_from_khoa(lat, lon, timestamp_str, service_key):
    stations = [
        ['SF_0001', '부산항',    35.091,  129.099],
        ['SF_0002', '부산항(신항)',35.023,  128.808],
        ['SF_0009', '해운대',    35.15909,129.16026],
        ['SF_0010', '울산항',    35.501,  129.387],
        ['SF_0008', '여수항',    34.754,  127.752],
    ]
    stations = pd.DataFrame(stations, columns=['obs_code', 'name', 'lat', 'lon'])
    station_code = find_closest_station(stations, lat, lon)  # 예시 좌표 (부산항)
    date_only = timestamp_str.split()[0].replace('-', '')
    url = (
        f"http://www.khoa.go.kr/api/oceangrid/seafogReal/search.do"
        f"?DataType=seafogReal&ServiceKey={service_key}"
        f"&ObsCode={station_code}&Date={date_only}&ResultType=json"
    )
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json().get('result', {}).get('data', [])
    base = pd.to_datetime(timestamp_str)
    closest_vis, min_diff = None, float('inf')
    for obs in data:
        try:
            obs_time = pd.to_datetime(obs['obs_time'])
            diff = abs((base - obs_time).total_seconds())
            if diff < min_diff and 'vis' in obs:
                closest_vis, min_diff = obs['vis'], diff
        except:
            continue
    return closest_vis

