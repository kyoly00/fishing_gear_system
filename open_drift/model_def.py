import os, ast, gc
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as func
from torch import nn
from torch.utils.data import DataLoader, Dataset
import datetime as dt
from torch.nn.utils import weight_norm

# ─────────────────────────────────────────────────────────────────────────────
class TemporalBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride, dilation, padding, dropout=0.2):
        super().__init__()
        self.conv1 = weight_norm(nn.Conv1d(in_channels, out_channels, kernel_size,
                                           stride=stride, padding=padding, dilation=dilation))
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(dropout)

        self.conv2 = weight_norm(nn.Conv1d(out_channels, out_channels, kernel_size,
                                           stride=stride, padding=padding, dilation=dilation))
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(dropout)

        self.downsample = nn.Conv1d(in_channels, out_channels, 1) if in_channels != out_channels else None
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.conv1(x)
        out = self.relu1(out)
        out = self.dropout1(out)
        out = self.conv2(out)
        out = self.relu2(out)
        out = self.dropout2(out)
        res = x if self.downsample is None else self.downsample(x)
        return self.relu(out + res)

class CustomModel(nn.Module):  # TCN 모델
    def __init__(self, input_size=68, num_channels=[64,64,64], kernel_size=7, dropout=0.2):
        super().__init__()
        layers = []
        num_levels = len(num_channels)
        for i in range(num_levels):
            dilation_size = 2 ** i
            in_channels = input_size if i == 0 else num_channels[i - 1]
            out_channels = num_channels[i]
            # Padding을 SAME처럼 맞춤
            padding = ((kernel_size - 1) * dilation_size) // 2
            layers += [TemporalBlock(in_channels, out_channels, kernel_size, stride=1,
                                     dilation=dilation_size, padding=padding, dropout=dropout)]
        self.tcn = nn.Sequential(*layers)
        self.classifier = nn.Linear(num_channels[-1], 4)
        self.softmax = nn.Softmax(dim=2)

    def forward(self, x):  # x: (B, C, T)
        y = self.tcn(x)  # (B, C_out, T)
        y = y.permute(0, 2, 1)  # (B, T, C_out)
        y = self.classifier(y)  # (B, T, 4)
        # y = self.softmax(y)
        return y
#   ──────────────────────────────────────────────────────
# # 2) 모델 로드
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# model = CustomModel().to(device)
# ckpt = torch.load(r"C:\Users\HUFS\Desktop\유실_최종\조업행태모델\new_29_acuur_0_8100", map_location=device)
# sd   = ckpt.get('model_state_dict', ckpt)
# model.load_state_dict(sd)
# model.eval()

# ─────────────────────────────────────────────────────────────────────────────
class CustomDataset(Dataset):
    def __init__(self, data):
        np.random.seed(42)

        if isinstance(data, str):
            # 디렉토리 경로에서 모든 CSV 읽기
            files = os.listdir(data)
            dfs = []
            for file in files:
                if file.endswith('.csv'):
                    full_path = os.path.join(data, file)
                    print(f"파일명: {full_path}")
                    df_temp = pd.read_csv(full_path, sep=',', dtype={
                    'latitude':np.float16,'longitude':np.float16,'px':np.float16,'py':np.float16,
                    'mean_ship_course_change':np.float16,'standard_deviation_of_ship_course_change':np.float16,
                    'histogram_of_ship_course_change1':np.int8,'histogram_of_ship_course_change2':np.int8,
                    'histogram_of_ship_course_change3':np.int8,'histogram_of_ship_course_change4':np.int8,
                    'histogram_of_ship_course_change5':np.int8,'histogram_of_ship_course_change6':np.int8,
                    'histogram_of_ship_course_change7':np.int8,'histogram_of_ship_course_change8':np.int8,
                    'histogram_of_ship_course_change9':np.int8,'histogram_of_ship_course_change10':np.int8,
                    'histogram_of_ship_course_change11':np.int8,'histogram_of_ship_course_change12':np.int8,
                    'mean_ship_course_change_per_velocity_stage1':np.float16,'mean_ship_course_change_per_velocity_stage2':np.float16,
                    'mean_ship_course_change_per_velocity_stage3':np.float16,'mean_velocity_change':np.float16,
                    'standard_deviation_of_velocity_change':np.float16,'mean_velocity':np.float16,
                    'histogram_of_velocity1':np.int8,'histogram_of_velocity2':np.int8,'histogram_of_velocity3':np.int8,
                    'histogram_of_velocity4':np.int8,'histogram_of_velocity5':np.int8,'histogram_of_velocity6':np.int8,
                    'histogram_of_velocity7':np.int8,'histogram_of_velocity_change1':np.int8,'histogram_of_velocity_change2':np.int8,
                    'histogram_of_velocity_change3':np.int8,'histogram_of_velocity_change4':np.int8,'histogram_of_velocity_change5':np.int8,
                    'histogram_of_velocity_change6':np.int8,'histogram_of_velocity_change7':np.int8,'histogram_of_velocity_change8':np.int8,
                    'velocity_change_per_velocity_stage1':np.float16,'velocity_change_per_velocity_stage2':np.float16,
                    'velocity_change_per_velocity_stage3':np.float16,'fishery_type':np.int8,'fishery_behavior':np.int8,'filename':np.int32
                })
                dfs.append(df_temp)

            df = pd.concat(dfs, ignore_index=True)
            del dfs

        elif isinstance(data, pd.DataFrame):
            # DataFrame 직접 입력
            df = data.copy()
            # 여기서도 dtype 적용 필요 시 수동 변환
            df = df.astype({
                    'latitude':np.float16,'longitude':np.float16,'px':np.float16,'py':np.float16,
                    'mean_ship_course_change':np.float16,'standard_deviation_of_ship_course_change':np.float16,
                    'histogram_of_ship_course_change1':np.int8,'histogram_of_ship_course_change2':np.int8,
                    'histogram_of_ship_course_change3':np.int8,'histogram_of_ship_course_change4':np.int8,
                    'histogram_of_ship_course_change5':np.int8,'histogram_of_ship_course_change6':np.int8,
                    'histogram_of_ship_course_change7':np.int8,'histogram_of_ship_course_change8':np.int8,
                    'histogram_of_ship_course_change9':np.int8,'histogram_of_ship_course_change10':np.int8,
                    'histogram_of_ship_course_change11':np.int8,'histogram_of_ship_course_change12':np.int8,
                    'mean_ship_course_change_per_velocity_stage1':np.float16,'mean_ship_course_change_per_velocity_stage2':np.float16,
                    'mean_ship_course_change_per_velocity_stage3':np.float16,'mean_velocity_change':np.float16,
                    'standard_deviation_of_velocity_change':np.float16,'mean_velocity':np.float16,
                    'histogram_of_velocity1':np.int8,'histogram_of_velocity2':np.int8,'histogram_of_velocity3':np.int8,
                    'histogram_of_velocity4':np.int8,'histogram_of_velocity5':np.int8,'histogram_of_velocity6':np.int8,
                    'histogram_of_velocity7':np.int8,'histogram_of_velocity_change1':np.int8,'histogram_of_velocity_change2':np.int8,
                    'histogram_of_velocity_change3':np.int8,'histogram_of_velocity_change4':np.int8,'histogram_of_velocity_change5':np.int8,
                    'histogram_of_velocity_change6':np.int8,'histogram_of_velocity_change7':np.int8,'histogram_of_velocity_change8':np.int8,
                    'velocity_change_per_velocity_stage1':np.float16,'velocity_change_per_velocity_stage2':np.float16,
                    'velocity_change_per_velocity_stage3':np.float16,'fishery_type':np.int8,'fishery_behavior':np.int8,'filename':np.int32
                })
        else:
            raise ValueError("입력은 디렉토리 경로나 DataFrame이어야 합니다.")



        gc.collect()

        additional_cols = ['time_stamp', 'sea_surface_temperature', 'sea_surface_salinity',
                           'current_speed1', 'current_speed2', 'wind1', 'wind2', 'tide1', 'tide2',
                           'bottom_depth', 'chlorophyll', 'DIN', 'DIP', 'dissolved_oxygen',
                           'fishery_density1', 'fishery_density2', 'fishery_density3', 'fishery_density4',
                           'fishery_density5', 'fishery_density6', 'fishery_density7', 'month', 'hour', 'px', 'py',]
        for col in additional_cols:
            df[col] = 0

        x_cols = ["time_stamp", "latitude", "longitude", "sea_surface_temperature",
                  "sea_surface_salinity",
                  "current_speed1", "current_speed2", "wind1", "wind2", "tide1", "tide2", "bottom_depth",
                  "chlorophyll", "DIN", "DIP", "dissolved_oxygen", "fishery_density1", "fishery_density2",
                  "fishery_density3", "fishery_density4", "fishery_density5", "fishery_density6", "fishery_density7",
                  "fishery_type", "month", "hour", "mean_ship_course_change", "standard_deviation_of_ship_course_change",
                  "histogram_of_ship_course_change1", "histogram_of_ship_course_change2", "histogram_of_ship_course_change3",
                  "histogram_of_ship_course_change4", "histogram_of_ship_course_change5", "histogram_of_ship_course_change6",
                  "histogram_of_ship_course_change7", "histogram_of_ship_course_change8", "histogram_of_ship_course_change9",
                  "histogram_of_ship_course_change10", "histogram_of_ship_course_change11", "histogram_of_ship_course_change12",
                  "mean_ship_course_change_per_velocity_stage1", "mean_ship_course_change_per_velocity_stage2",
                  "mean_ship_course_change_per_velocity_stage3", "mean_velocity_change", "standard_deviation_of_velocity_change",
                  "mean_velocity", "histogram_of_velocity1", "histogram_of_velocity2", "histogram_of_velocity3",
                  "histogram_of_velocity4", "histogram_of_velocity5", "histogram_of_velocity6", "histogram_of_velocity7",
                  "histogram_of_velocity_change1", "histogram_of_velocity_change2", "histogram_of_velocity_change3",
                  "histogram_of_velocity_change4", "histogram_of_velocity_change5", "histogram_of_velocity_change6",
                  "histogram_of_velocity_change7", "histogram_of_velocity_change8", "velocity_change_per_velocity_stage1",
                  "velocity_change_per_velocity_stage2", "velocity_change_per_velocity_stage3", "observed_fishing_type",
                  "observed_fishing_info", "px", "py"]

        df[x_cols] = df[x_cols].astype(np.float32)

        x = df[x_cols].to_numpy(dtype=np.float32)
        y = df[["fishery_behavior"]].to_numpy(dtype=np.int64)
        yt = df[["fishery_type"]].to_numpy(dtype=np.int64)
        name = df[["filename"]].to_numpy(dtype=np.int32)
        del df
        gc.collect()

        self.train_x = torch.tensor(np.array(self.make_sequence(x, 1440)), dtype=torch.float32)
        self.train_y = torch.tensor(np.array(self.make_sequence(y, 1440)), dtype=torch.long)
        self.train_yt = torch.tensor(np.array(self.make_sequence(yt, 1440)), dtype=torch.long)
        self.train_filename = torch.tensor(np.array(self.make_sequence(name, 1440)), dtype=torch.int32)

        seed = np.random.permutation(len(self.train_x))
        self.train_x = self.train_x[seed]
        self.train_y = self.train_y[seed]
        self.train_yt = self.train_yt[seed]
        self.train_filename = self.train_filename[seed]
        print("전처리 완료")

    def __getitem__(self, index):
        return (self.train_x[index], self.train_y[index], self.train_yt[index], self.train_filename[index])

    def __len__(self):
        return len(self.train_x)

    def make_sequence(self, data, size):
        return [data[i:i+size] for i in range(0, len(data)-size+1, size)]

    def required_columns():
        return [
            "time_stamp", "latitude", "longitude", "sea_surface_temperature",
            "sea_surface_salinity",
            "current_speed1", "current_speed2", "wind1", "wind2", "tide1", "tide2", "bottom_depth",
            "chlorophyll", "DIN", "DIP", "dissolved_oxygen", "fishery_density1", "fishery_density2",
            "fishery_density3", "fishery_density4", "fishery_density5", "fishery_density6", "fishery_density7",
            "fishery_type", "month", "hour", "mean_ship_course_change", "standard_deviation_of_ship_course_change",
            "histogram_of_ship_course_change1", "histogram_of_ship_course_change2", "histogram_of_ship_course_change3",
            "histogram_of_ship_course_change4", "histogram_of_ship_course_change5", "histogram_of_ship_course_change6",
            "histogram_of_ship_course_change7", "histogram_of_ship_course_change8", "histogram_of_ship_course_change9",
            "histogram_of_ship_course_change10", "histogram_of_ship_course_change11", "histogram_of_ship_course_change12",
            "mean_ship_course_change_per_velocity_stage1", "mean_ship_course_change_per_velocity_stage2",
            "mean_ship_course_change_per_velocity_stage3", "mean_velocity_change", "standard_deviation_of_velocity_change",
            "mean_velocity", "histogram_of_velocity1", "histogram_of_velocity2", "histogram_of_velocity3",
            "histogram_of_velocity4", "histogram_of_velocity5", "histogram_of_velocity6", "histogram_of_velocity7",
            "histogram_of_velocity_change1", "histogram_of_velocity_change2", "histogram_of_velocity_change3",
            "histogram_of_velocity_change4", "histogram_of_velocity_change5", "histogram_of_velocity_change6",
            "histogram_of_velocity_change7", "histogram_of_velocity_change8", "velocity_change_per_velocity_stage1",
            "velocity_change_per_velocity_stage2", "velocity_change_per_velocity_stage3", "observed_fishing_type",
            "observed_fishing_info", "px", "py", "filename"]

# # ─────────────────────────────────────────────────────────────────────────────
# # 4) 최종 추론 루프
# if __name__ == "__main__":
#     x = dt.datetime.now()
#     print("데이터 로딩 from csv {:d}/{:d} {:d}:{:d}:{:d}".format(x.month, x.day, x.hour+9, x.minute, x.second))
#     dataset = CustomDataset(r'C:\Users\ime_203\Downloads\fishing_behavior\test\\')
    
#     dataloader = DataLoader(dataset, batch_size=32, shuffle=False)

#     total, correct = 0, 0
#     with torch.no_grad():
#         for xb, yb, _, _ in dataloader:  # ✅ 4개 받아서 필요한 2개만 사용

#             xb = xb.to(device)
#             yb = yb.to(device).squeeze(-1)  # (B, 1440)으로 만듬

#             xb = xb.permute(0, 2, 1)

#             logits = model(xb)              # (B, 1440, 4)
#             preds = logits.argmax(dim=2)    # (B, 1440)
#             total += preds.numel()
#             correct += (preds == yb).sum().item()

#     print(f"=> Test Accuracy: {correct/total:.4f}")