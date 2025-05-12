# views.py
from django.shortcuts import render
from django.core.paginator import Paginator
from lists.models import FishingGear, LostingGear, Assignment

def gear_list_view(request):
    # 1) 표시할 월
    months = [9, 10, 11, 12]

    # 2) 월별 통발/자망 수 집계
    trap_counts = []
    gill_counts = []
    for m in months:
        trap_counts.append(
            FishingGear.objects.filter(type="통발", buy_date__month=m).count()
        )
        gill_counts.append(
            FishingGear.objects.filter(type="자망", buy_date__month=m).count()
        )

    # 3) 선택된 월 파라미터
    raw_month = request.GET.get('month', '전체')
    try:
        sel_int = int(raw_month)
        selected_month = sel_int
    except ValueError:
        selected_month = '전체'

    # 4) QS 구성 (필터링)
    if isinstance(selected_month, int):
        qs = FishingGear.objects.filter(buy_date__month=selected_month)\
                                 .select_related('seller','buyer')
        idx = months.index(selected_month)
        sel_trap = trap_counts[idx]
        sel_gill = gill_counts[idx]
    else:
        qs = FishingGear.objects.select_related('seller','buyer').all()
        sel_trap = sum(trap_counts)
        sel_gill = sum(gill_counts)

    # 5) dict 리스트 만들기
    gear_list = []
    for g in qs:
        gear_list.append({
            'buyer_name':     g.buyer.buyer_name,
            'gear_id':        g.gear_id,
            'seller_address': g.seller.address,
            'buy_date':       g.buy_date.strftime("%Y-%m-%d"),
            'type':           g.type,
            'buyer_ph':       g.buyer.buyer_ph,
        })

    # 6) 페이징 (한 페이지당 20개)
    paginator = Paginator(gear_list, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'lists/lists.html', {
        'view_type':           'gear_list',
        'page_obj':            page_obj,
        'month_buttons':       months,
        'selected_month':      selected_month,
        'trap_counts_list':    trap_counts,
        'gillnet_counts_list': gill_counts,
        'sel_trap':            sel_trap,
        'sel_gill':            sel_gill,
    })


def losting_gear_view(request):
    qs = LostingGear.objects.all().order_by('-report_time')

    raw_month = request.GET.get('month')
    if raw_month and raw_month.isdigit():
        sel_month = int(raw_month)
        qs = qs.filter(report_time__month=sel_month)
        selected_month = sel_month
    else:
        selected_month = '전체'

    # 월 버튼용: 보고된 달들
    months_qs = LostingGear.objects.dates('report_time','month',order='DESC')
    month_buttons = [d.month for d in months_qs]

    # dict 리스트 + 페이징
    losting_list = []
    for lg in qs:
        losting_list.append({
            'buyer_id':       lg.lg_buyer_id,
            'cast_latitude':  lg.cast_latitude,
            'cast_longitude': lg.cast_longitude,
            'report_time':    lg.report_time.strftime("%Y년 %m월 %d일 %H시 %M분") if lg.report_time else '',
        })
    paginator = Paginator(losting_list, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    # 전체/월별 수거 통계
    total_reports   = LostingGear.objects.count()
    admin_ids       = Assignment.objects.values_list('as_admin_id', flat=True)
    total_retrieved = LostingGear.objects.filter(
        lg_admin__admin_id__in=admin_ids
    ).count()

    if isinstance(selected_month, int):
        curr_ret     = LostingGear.objects.filter(
            report_time__month=selected_month,
            lg_admin__admin_id__in=admin_ids
        ).count()
        curr_total   = LostingGear.objects.filter(report_time__month=selected_month).count()
        curr_not_ret = curr_total - curr_ret
    else:
        curr_ret     = total_retrieved
        curr_not_ret = total_reports - total_retrieved

    # 월별 수거량 리스트
    retrieved_counts_list = [
        LostingGear.objects.filter(
            report_time__month=m,
            lg_admin__admin_id__in=admin_ids
        ).count()
        for m in month_buttons
    ]

    return render(request, 'lists/lists.html', {
        'view_type':                   'losting_gear',
        'page_obj':                    page_obj,
        'month_buttons':               month_buttons,
        'selected_month':              selected_month,
        'current_month_retrieved':     curr_ret,
        'current_month_not_retrieved': curr_not_ret,
        'retrieved_counts_list':       retrieved_counts_list,
    })
