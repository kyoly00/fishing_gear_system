# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 10:27:06 2023

@author: bgkim
"""

import json
import pandas as pd
import copy
import pickle 
from os.path import join
from os import listdir
import numpy as np
from datetime import datetime, timedelta
from os.path import split
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')

# jsondict_pkl=r'C:\Users\HUFS\Desktop\유실_최종\조업행태모델\jsondict_v0.2.pkl'

# with open(jsondict_pkl, 'rb') as f:
#     features_value_dict = pickle.load(f)
#     geojson_dict = pickle.load(f)

# ================= Nan값 0으로 처리 및 소수 반올림 함수 =================== 
def cal_val(n_value):
    if np.isnan(n_value):
        r_value=0.0
    else:
        r_value=round(n_value,1)
    return r_value

# ======= date_time, sog, cog를 입력받아 모델 입력 변수로 확장하는 함수 =======
def cal_statics(csv_data):
    total_statics=[]
    for trj_i in range(len(csv_data)):
        trj_st=max(0,trj_i-30)
        trj_end=min(trj_i+30,len(csv_data))
        trj2 = csv_data.iloc[trj_st:trj_end]
        
        trj_st2=max(0,trj_i-5)
        trj_end2=min(trj_i+5,len(csv_data))
        trj3 = csv_data.iloc[trj_st2:trj_end2]
        
        trj2['sog_diff']=trj2.sog.diff() #define sog_diff
        trj2['cog_diff']=trj2.cog.diff() #define cog_diff
        
        cog_diff_l_mean = cal_val(trj2[trj2.sog<1].cog_diff.mean())
        cog_diff_m_mean = cal_val(trj2[(trj2.sog>=1) & (trj2.sog<4)].cog_diff.mean())
        cog_diff_h_mean = cal_val(trj2[(trj2.sog>=4) & (trj2.sog<8)].cog_diff.mean())
        
        sog_diff_l_mean = cal_val(trj2[trj2.sog<1].sog_diff.mean())
        sog_diff_m_mean = cal_val(trj2[(trj2.sog>=1) & (trj2.sog<4)].sog_diff.mean())
        sog_diff_h_mean = cal_val(trj2[(trj2.sog>=4) & (trj2.sog<8)].sog_diff.mean())
        
        cog_diff_mean=cal_val(trj2.cog_diff.mean()) #1
        cog_diff_std=cal_val(trj2.cog_diff.std()) #2
        # cog_diff_hist=plt.hist(trj2.cog_diff.to_numpy(),range(-360,360+1,60))[0].tolist() #3 : 12
        cog_diff_hist=np.histogram(trj2.cog_diff.to_numpy(),bins=[i for i in range(-360,360+1,60)])[0].tolist() #3 : 12
        cog_diff_hist_stage=[cog_diff_l_mean,cog_diff_m_mean,cog_diff_h_mean] #4 : 3
        
        sog_diff_mean=cal_val(trj2.sog_diff.mean()) #5
        sog_diff_std=cal_val(trj2.sog_diff.std()) #6
        # sog_mean=cal_val(trj2.sog.mean()) #7
        sog_mean=cal_val(trj3.sog.mean()) #7
        # sog_hist=plt.hist(trj2.sog_diff.abs().to_numpy(),range(0,7+1,1))[0].tolist() #8
        sog_hist=np.histogram(trj2.sog_diff.abs().to_numpy(),bins=[i for i in range(0,7+1,1)])[0].tolist() #8
        # sog_diff_hist=plt.hist(trj2.sog_diff.abs().to_numpy(),range(-8,8+1,2))[0].tolist() #9 : 8
        sog_diff_hist=np.histogram(trj2.sog_diff.abs().to_numpy(),bins=[i for i in range(-8,8+1,2)])[0].tolist() #9 : 8
        sog_diff_mean_stage=[sog_diff_l_mean,sog_diff_m_mean,sog_diff_h_mean] #10 : 3
        
        cnt_statics=[cog_diff_mean,cog_diff_std,cog_diff_hist,cog_diff_hist_stage,
                       sog_diff_mean,sog_diff_std,sog_mean,sog_hist,sog_diff_hist,sog_diff_mean_stage]
        total_statics.append(cnt_statics)
    # plt.close() 
    return total_statics

# cols2=['sea_surface_temperature','sea_surface_salinity','current_speed','wind','tide','bottom_depth','chlorophyll','DIN','DIP','dissolved_oxygen','fishery_density','fishery_type','fishery_behavior']
# static_cols=['mean_ship_course_change','standard_deviation_of_ship_course_change','histogram_of_ship_course_change','mean_ship_course_change_per_velocity_stage',
#              'mean_velocity_change','standard_deviation_of_velocity_change','mean_velocity','histogram_of_velocity','histogram_of_velocity_change',
#              'velocity_change_per_velocity_stage']                



# csv_files=[r'C:\Users\HUFS\Desktop\유실_최종\GPS_DATA\T01_DDJ024EDJ_2022-03-10 000000-000_sogcog.csv']

# print(csv_files[0])
# csv_data = pd.read_csv(csv_files[0], encoding="UTF-8")
# csv_time=csv_data.datetime.apply(pd.to_datetime)

# total_statics=cal_statics(csv_data) #calulate AIS statics
# #total_statics에는 10개의 list 변수가 들어있으며, 이는 static_cols의 각 요소와 매칭됨

# features_value_list = []
# for i in range(len(csv_data)) :
#     for ais_i in range(len(static_cols)):
#         features_value_dict['properties'][static_cols[ais_i]]=total_statics[i][ais_i]
#     temp_dict = copy.deepcopy(features_value_dict)
#     features_value_list.append(temp_dict)
# geojson_dict['features'] = features_value_list

# # json_data = json.dumps(geojson_dict, indent=4, ensure_ascii=False) #indent 4 옵션으로 줄바꿈 옵션 지정

# # with open('test_result.json', 'w', encoding="UTF-8") as f:
# #     f.write(json_data)



# #---------------------------------------------------
# # CSV로 저장하기 위한 리스트 초기화
# csv_rows = []

# # 원래 AIS 데이터프레임에 통계 열 추가
# for i, col in enumerate(static_cols):
#     csv_data[col] = [row[i] for row in total_statics]

# # 새로운 CSV로 저장
# csv_data.to_csv('test_result_joined.csv', index=False, encoding='utf-8-sig')

# print("변환 완료: test_result_joined.csv")


# # # DataFrame으로 변환
# # df_result = pd.DataFrame(csv_rows)

# # # CSV로 저장
# # df_result.to_csv('test_result.csv', index=False, encoding='utf-8-sig')

# # print("CSV 저장 완료: test_result.csv")

        
