import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from opendrift.models.sedimentdrift import SedimentDrift
from opendrift.readers.reader_netCDF_CF_generic import Reader as GenericReader
import geopandas as gpd

def sediment_map_view(request):
    from maps.models import LostingGear, Assignment, Buyer, FishingActivity

    assigned_ids = set(Assignment.objects.values_list('as_admin_id', flat=True))
    lost_reports = []

    for report in LostingGear.objects.all():
        if report.lg_admin_id in assigned_ids:
            continue
        try:
            activity = FishingActivity.objects.get(fa_buyer_id=report.lg_buyer_id)
            buyer = Buyer.objects.get(buyer_id=activity.fa_buyer_id)
        except (FishingActivity.DoesNotExist, Buyer.DoesNotExist):
            continue

        lost_reports.append({
            'report_id': report.report_id,
            'buyer_name': buyer.buyer_name,
            'report_time': report.report_time.strftime('%Y-%m-%d %H:%M'),
            'latitude': float(report.cast_latitude),
            'longitude': float(report.cast_longitude),
        })

    return render(request, 'sediment/sediment.html', {
        'lost_reports': lost_reports
    })


@csrf_exempt
def run_simulation(request):
    if request.method == 'POST':
        try:
            data = request.POST
            coords = [
                (float(lon), float(lat))
                for lon, lat in zip(data.getlist('lons[]'), data.getlist('lats[]'))
            ]
            start = datetime.strptime(data['start_date'], "%Y-%m-%d")
            end = datetime.strptime(data['end_date'], "%Y-%m-%d")

            if end <= start:
                end = start + timedelta(hours=1)

            print("=== 시뮬레이션 디버그 시작 ===")
            print("start:", start)
            print("end:", end)
            print("duration (초):", (end - start).total_seconds())
            print("coords:", coords)
            print("=== 시뮬레이션 디버그 종료 ===")

            # NetCDF 파일 경로 (절대경로)
            base_path = r"C:\Users\ime\Desktop\simtest-20250528T111044Z-1-001\simtest_final"

            ocean_file = os.path.join(base_path, "HYCOM_for_opendrift.nc2")
            wind_file = os.path.join(base_path, "wind_converted_clean2_fixed.nc")
            depth_file = os.path.join(base_path, "rename_output.nc")

            # 리더 생성 (순서: depth → wind → ocean)
            depth_reader = GenericReader(depth_file)
            wind_reader = GenericReader(wind_file)
            ocean_reader = GenericReader(ocean_file)

            # 모델 초기화 및 리더 추가
            model = SedimentDrift(loglevel=20)
            model.add_reader([depth_reader, wind_reader, ocean_reader])

            # 설정
            model.set_config('drift:horizontal_diffusivity', 50)
            model.set_config('general:seafloor_action', 'deactivate')

            # 입자 시딩
            lons, lats = zip(*coords)
            model.seed_elements(
                lon=lons,
                lat=lats,
                time=start,
                terminal_velocity=np.full(len(coords), 10)
            )

            # 시뮬레이션 실행
            model.run(time_step=1800, time_step_output=10800, duration=end - start)

            # 결과 반환
            results = pd.DataFrame({
                'lon': model.elements.lon,
                'lat': model.elements.lat
            })

            return JsonResponse(results.to_dict(orient='records'), safe=False)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)












