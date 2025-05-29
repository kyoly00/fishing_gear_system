# views.py (전체 수정 버전)
from django.shortcuts import render
from .models import LostingGear, FishingActivity, Buyer, Assignment
from rds.models import SystemData

def map_view(request):
    view_type = request.GET.get('view', 'assigned')  # 기본값: 수거 완료 어구
    lost_reports = []

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
            'latitude': float(report.cast_latitude),
            'longitude': float(report.cast_longitude),
        })

    # ✅ SystemData 기반 가상 신고 추가 (buyer_id 동일, press=0 중간값만 대표로 표시)
    if view_type == 'unassigned':
        system_data = SystemData.objects.using('gpsdb').filter(buyer_id='alsdfhu204hdufs').order_by('time_stamp')

        press_0_data = [row for row in system_data if row.press == 0]
        press_4_time = next((row.time_stamp for row in reversed(system_data) if row.press == 4), None)

        if press_0_data:
            middle_idx = len(press_0_data) // 2
            middle = press_0_data[middle_idx]

            lost_reports.append({
                'report_id': '20',  # 신고 번호를 명시적으로 20으로 설정
                'buyer_name': middle.buyer_id,
                'report_time': press_4_time.strftime('%Y-%m-%d %H:%M') if press_4_time else '알 수 없음',
                'latitude': middle.lat,
                'longitude': middle.lon,
            })

    context = {
        'lost_reports': lost_reports,
        'view_type': view_type,
    }
    return render(request, 'maps/maps.html', context)

















