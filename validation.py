import xarray as xr

# 파일 경로
ocean = xr.open_dataset(r"C:\Users\ime\Desktop\simtest-20250528T111044Z-1-001\simtest_final\HYCOM_for_opendrift.nc2")
wind = xr.open_dataset(r"C:\Users\ime\Desktop\simtest-20250528T111044Z-1-001\simtest_final\wind_converted_clean2_fixed.nc")
depth = xr.open_dataset(r"C:\Users\ime\Desktop\simtest-20250528T111044Z-1-001\simtest_final\rename_output.nc")

print("ocean lat:", ocean['lat'].values)
print("wind lat:", wind['lat'].values)
print("depth lat:", depth['lat'].values)

print("ocean lon:", ocean['lon'].values)
print("wind lon:", wind['lon'].values)
print("depth lon:", depth['lon'].values)





