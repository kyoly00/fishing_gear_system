import os
import json
import pickle
import copy
import pandas as pd
import numpy as np
from datetime import datetime
import ast
from cal_ais_values import cal_statics
import torch
from torch.utils.data import DataLoader
from model_def import CustomModel, CustomDataset


# ========================= behavior 모델의 입력 geojson 파일 생성 =================================

def load_csv_from_name(directory, filename):
    for file in os.listdir(directory):
        if filename in file and file.endswith('.csv'):
            full_path = os.path.join(directory, file)
            print(f"✅ 파일 로드: {full_path}")
            df = pd.read_csv(full_path, encoding="UTF-8")
            return full_path, df
    raise FileNotFoundError(f"❌ '{filename}'를 포함한 .csv 파일을 '{directory}'에서 찾을 수 없습니다.")


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

def create_input_json(jsondict_pkl, gps_folder, filename_hint):
    # 생성해야 하는 변수 목록
    static_cols = [
        'mean_ship_course_change','standard_deviation_of_ship_course_change','histogram_of_ship_course_change',
        'mean_ship_course_change_per_velocity_stage','mean_velocity_change','standard_deviation_of_velocity_change',
        'mean_velocity','histogram_of_velocity','histogram_of_velocity_change','velocity_change_per_velocity_stage'
    ]

    with open(jsondict_pkl, 'rb') as f:
        features_value_dict = pickle.load(f)
        geojson_dict = pickle.load(f)

    csv_path, csv_data = load_csv_from_name(gps_folder, filename_hint)
    total_statics = cal_statics(csv_data)

    for i, col in enumerate(static_cols):
        csv_data[col] = [row[i] for row in total_statics]

    df = csv_data.rename(columns={'datetime': 'time_stamp', 'lat': 'latitude', 'lon': 'longitude'})

    df = expand_list_column(df, 'histogram_of_ship_course_change', 'histogram_of_ship_course_change', 12)
    df = expand_list_column(df, 'mean_ship_course_change_per_velocity_stage', 'mean_ship_course_change_per_velocity_stage', 3)
    df = expand_list_column(df, 'histogram_of_velocity', 'histogram_of_velocity', 7)
    df = expand_list_column(df, 'histogram_of_velocity_change', 'histogram_of_velocity_change', 8)
    df = expand_list_column(df, 'velocity_change_per_velocity_stage', 'velocity_change_per_velocity_stage', 3)

    required_cols = CustomDataset.required_columns()

    # 누락된 컬럼을 0으로 채우기
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0

    df = df[required_cols]
    df['fishery_behavior'] = 3

    return df


# =========================== behavior 모델 실행부 =======================================

def run_behavior_model(input_df, output_prefix, model_ckpt_path):
    df = input_df

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = CustomModel().to(device)
    ckpt = torch.load(model_ckpt_path, map_location=device)
    model.load_state_dict(ckpt.get('model_state_dict', ckpt))
    model.eval()

    dataset = CustomDataset(df)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False)

    all_preds = []
    for xb, _, _, _ in dataloader:
        xb = xb.to(device).permute(0, 2, 1)
        with torch.no_grad():
            logits = model(xb)
            preds = logits.argmax(dim=2).cpu().numpy()
            all_preds.extend(preds)

    flat_preds = np.array(all_preds).flatten()
    valid_len = flat_preds.shape[0]
    df = df.iloc[:valid_len].copy() 
    df['fishery_behavior'] = flat_preds[:len(df)]

    return df