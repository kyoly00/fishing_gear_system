import pandas as pd

# 절대 경로에 맞게 수정
df1 = pd.read_csv(r"C:\Users\ime\Desktop\doomido_gpx.csv", encoding='utf-8')
df2 = pd.read_csv(r"C:\Users\ime\Desktop\T01_DDJ054AEJ_2018-01-31 000000-000.csv", encoding='utf-8')

# 컬럼명 직접 비교
print("doomido_gpx.csv:", df1.columns.tolist())
print("T01_DDJ.csv     :", df2.columns.tolist())

# 각 컬럼명 repr로 비교
print("\nREPR 비교:")
for a, b in zip(df1.columns, df2.columns):
    print(f"{repr(a):<20} | {repr(b)}")


