import os
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# S3 Presigned URLs (로컬 테스트용)
OCEAN_URL = "https://simulation-data-nsm123.s3.ap-southeast-2.amazonaws.com/sm123/REAL_FINAL/new_dataset/new_sediment_data_final_uv.nc"
WIND_URL = "https://simulation-data-nsm123.s3.ap-southeast-2.amazonaws.com/sm123/REAL_FINAL/new_dataset/new_wind.nc"
BATHY_URL = "https://simulation-data-nsm123.s3.ap-southeast-2.amazonaws.com/sm123/REAL_FINAL/new_dataset/new_BADA2024.nc"

def download_from_s3(url, filename):
    local_path = os.path.join("tmp", filename)
    os.makedirs("tmp", exist_ok=True)
    if not os.path.exists(local_path):
        print(f"📥 다운로드 중: {filename}")
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            f.write(response.content)
    else:
        print(f"✅ 이미 있음: {filename}")
    return local_path

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
            lats = [float(x) for x in data.getlist('lats[]')]
            lons = [float(x) for x in data.getlist('lons[]')]
            coords = list(zip(lons, lats))

            start = datetime.strptime(data['start_date'], "%Y-%m-%d")
            end = datetime.strptime(data['end_date'], "%Y-%m-%d")
            if end <= start:
                end = start + timedelta(hours=1)

            # 다운로드 후 경로 설정
            ocean_file = download_from_s3(OCEAN_URL, "new_sediment_data_final_uv.nc")
            wind_file = download_from_s3(WIND_URL, "new_wind.nc")
            bathy_file = download_from_s3(BATHY_URL, "new_BADA2024.nc")

            from opendrift.models.sedimentdrift import SedimentDrift
            from opendrift.readers import reader_netCDF_CF_generic

            reader_ocean = reader_netCDF_CF_generic.Reader(ocean_file)
            reader_wind = reader_netCDF_CF_generic.Reader(wind_file)
            reader_bathy = reader_netCDF_CF_generic.Reader(bathy_file)

            model = SedimentDrift(loglevel=20)
            model.add_reader([reader_ocean, reader_wind, reader_bathy])
            model.set_config('vertical_mixing:diffusivitymodel', 'windspeed_Large1994')
            model.set_config('seed:wind_drift_factor', 0.02)
            model.set_config('drift:stokes_drift', True)
            model.set_config('drift:vertical_advection', True)
            model.set_config('drift:vertical_mixing', False)
            model.set_config('general:coastline_action', 'previous')
            model.set_config('general:seafloor_action', 'deactivate')
            model.set_config('drift:horizontal_diffusivity', 100)
            model.set_config('drift:current_uncertainty', 0.2)
            model.set_config('drift:wind_uncertainty', 2)

            mean_v, std_v = 0.5, 0.05
            terminal_velocity = np.random.normal(loc=-mean_v, scale=std_v, size=len(lons))
            model.seed_elements(
                lon=lons,
                lat=lats,
                time=start,
                terminal_velocity=terminal_velocity
            )

            model.run(
                time_step=1800,
                time_step_output=10800,
                duration=end - start
            )

            results = pd.DataFrame({
                'lon': model.elements.lon,
                'lat': model.elements.lat,
                'z': model.elements.z,
                'status': model.elements.status
            })

            output = []
            for i in range(len(lons)):
                output.append({
                    'lon': float(results['lon'].iloc[i]),
                    'lat': float(results['lat'].iloc[i]),
                })
            return JsonResponse(output, safe=False)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
