from django.shortcuts import render
from django.http import JsonResponse
from rds.models import SystemData
from datetime import datetime
import io
import base64

def map_view(request):
    view_type = request.GET.get('view', 'assigned')
    lost_reports = []

    if view_type == 'unassigned':
        # SystemData 2명만!
        report_name_map = {2: "서민석", 3: "금교현"}
        for rid in [2, 3]:
            rows = SystemData.objects.using('gpsdb').filter(report2_id=rid).order_by('-time_stamp')
            if rows.exists():
                row = rows.first()
                lost_reports.append({
                    'report_id': f'{row.report2_id}',
                    'buyer_name': report_name_map[row.report2_id],
                    'report_time': row.time_stamp.strftime('%Y-%m-%d %H:%M'),
                    'report_time_raw': row.time_stamp.strftime('%Y-%m-%d'),
                    'latitude': row.lat,
                    'longitude': row.lon,
                })
    else:
        from .models import LostingGear, FishingActivity, Buyer, Assignment
        assigned_ids = set(Assignment.objects.values_list('as_admin_id', flat=True))
        for report in LostingGear.objects.all():
            if (view_type == 'assigned' and report.lg_admin_id not in assigned_ids) or \
               (view_type == 'unassigned' and report.lg_admin_id in assigned_ids):
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
                'report_time_raw': report.report_time.strftime('%Y-%m-%d'),
                'latitude': float(report.cast_latitude),
                'longitude': float(report.cast_longitude),
            })
    context = {
        'lost_reports': lost_reports,
        'view_type': view_type,
    }
    return render(request, 'maps/maps.html', context)

# --- AJAX 엔드포인트: 시뮬레이션 실행 ---
from django.views.decorators.csrf import csrf_exempt
import json
from .legend import run_lost_simulation  # legend.py와 같은 디렉토리여야 함

@csrf_exempt
def simulate_drift(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        report2_id = int(data.get('report2_id'))
        sim_date = data.get('sim_date', '')

        # sim_date가 값이 있으면 datetime 객체로 변환
        if sim_date:
            try:
                sim_date_dt = datetime.strptime(sim_date, "%Y-%m-%d")
            except Exception as e:
                return JsonResponse({'error': f"날짜 형식 오류: {sim_date} (YYYY-MM-DD 필요)", 'success': False})
        else:
            sim_date_dt = ''  # 그대로 빈 문자열 넘김

        SERVICE_KEY_KHOA = 'ANM8LV6zTsRNiGg6FCUMpw=='  # KHOA API 키
        TIME_STEP = 600

        try:
            # 시뮬레이션 실행 및 base64 이미지 반환
            lat, lon, img_base64 = run_lost_simulation(
                report2_id, SERVICE_KEY_KHOA, TIME_STEP, retrieve_date=sim_date_dt,  # 추가: 이미지를 base64로 반환하도록 legend.py run_lost_simulation 수정
            )
            return JsonResponse({
                'sim_latitude': float(lat),
                'sim_longitude': float(lon),
                'report2_id': int(report2_id),
                'sim_img_base64': img_base64,
                'success': True
            })
        except Exception as e:
            return JsonResponse({'error': str(e), 'success': False})
    return JsonResponse({'error': 'Invalid request'}, status=400)


















