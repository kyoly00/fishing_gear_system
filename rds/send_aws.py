import requests

# ["T02_DDJ054AEJ_2020-11-09 132400-015.csv", "T02_DDJ054AEJ_2018-01-31 000000-000.csv", 'T02_DDJ054AEJ_2018-04-08 161600-000.csv'] 

# 파일 경로
file_path = r"C:\Users\ime\Desktop\T02_DDJ054AEJ_2018-04-08 161600-000.csv"

# API URL
url = "https://b1a7l3nkxg.execute-api.ap-southeast-2.amazonaws.com/report/join"

# 파일 업로드 요청
with open(file_path, 'rb') as f:
    files = {'file': (f.name, f, 'text/csv')}
    response = requests.post(url, files=files)

print(f"Status: {response.status_code}")
print("Response:", response.text)
