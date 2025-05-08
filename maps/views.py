from django.shortcuts import render
from .models import LostingGear, FishingActivity, Buyer, Assignment

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

    context = {
        'lost_reports': lost_reports,
        'view_type': view_type,
    }
    return render(request, 'maps/maps.html', context)













