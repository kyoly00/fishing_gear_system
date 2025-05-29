# 1. cal_ais_values   # neo 6m으로 받은 lat, lon, cog, sog 데이터를 모델 입력 형태로 변경
# 2. model_def        # 조업 행태 모델을 위한 데이터셋 생성 및 모델 정의 파일
# 3. create_behavior_input    # 변경한 데이터를 이용해 모델에 맞도록 추가 변수 및 값 조정해 json파일로 생성 + 모델 실행해 조업 행태가 labeling된 json파일로 재생성 
# 4. env_api          # 시뮬레이션 모델을 위한 api데이터 가져오는 파일일
# 5. lost_simulation_model    # labeling된 json파일을 이용해 유실 어구 시뮬레이션 실행


from create_behavior_input import create_input_json, run_behavior_model
from lost_simulation_model import run_lost_simulation

import os

if __name__ == '__main__':
    # === 1단계: 경로 설정 ===
    jsondict_pkl = r'./jsondict_v0.2.pkl'  # 조업행태 모델용 템플릿
    gps_folder = r'./GPS_DATA'             # NEO-6M 기반 lat, lon, sog, cog 포함 CSV 위치
    filename_hint = 'ais'             # 'test_ais_2025-05-21.csv' 같은 이름이면 'test_ais'만 넣으면 됨
    model_ckpt_path = r'./new_29_acuur_0_8100'  # 학습된 TCN 모델 체크포인트
    BASE_DIR         = r"C:\Users\Kyohyun\Desktop\abandoned_fishing_gear\opendrift-master\examples\opendrfit_middle"
    GEOJSON_DIR      = os.path.join(BASE_DIR, "AI_HUB_data")
    NC_FOLDER        = os.path.join(BASE_DIR, "khoa_data")
    WIND_FOLDER      = os.path.join(BASE_DIR, "wind_data")
    COASTLINE_FILE   = os.path.join(BASE_DIR, "2024년 전국해안선.shp")
    PLOT_OUTPUT_DIR  = os.path.join(BASE_DIR, "visualization")
    # PLOT_OUTPUT_DIR_FIRST  = os.path.join(BASE_DIR, "first_visualization")
    # PLOT_OUTPUT_DIR_LAST  = os.path.join(BASE_DIR, "last_visualization")
    PLOT_OUTPUT_DIR_FIRST  = BASE_DIR
    PLOT_OUTPUT_DIR_LAST  = BASE_DIR    
    ERROR_LOG_PATH   = os.path.join(GEOJSON_DIR, "error_log.csv")
    SERVICE_KEY_KHOA = 'ANM8LV6zTsRNiGg6FCUMpw=='  # KHOA API 키
    time_step = 1200


    # === 2단계: 모델 입력용 CSV 생성 ===
    output_csv_path = f'./label_dataset_csv/{filename_hint}_input.csv'
    input_df = create_input_json(jsondict_pkl, gps_folder, filename_hint)

    # === 3단계: 조업행태 예측 및 GeoJSON 저장 ===
    label_df = run_behavior_model(
        input_df=input_df,
        output_prefix=filename_hint,
        model_ckpt_path=model_ckpt_path
    )


    # === 4단계: 유실 어구 시뮬레이션 실행 ===
    result_df = run_lost_simulation(
        df=label_df,
        nc_folder=NC_FOLDER,
        wind_folder=WIND_FOLDER,
        coastline_file=COASTLINE_FILE,
        plot_output_dir=PLOT_OUTPUT_DIR,
        plot_output_dir_first=PLOT_OUTPUT_DIR_FIRST,
        plot_output_dir_last=PLOT_OUTPUT_DIR_LAST,
        error_log_path=ERROR_LOG_PATH,
        service_key_khoa=SERVICE_KEY_KHOA,
        time_step=time_step
    )
