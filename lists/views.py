from django.shortcuts import render
from lists.models import FishingGear, LostingGear, Assignment

def gear_list_view(request):
	months = [9, 10, 11, 12]
	month_percentages = {}
	month_counts = {}

	total_gears = FishingGear.objects.count()
	trap_count = FishingGear.objects.filter(type="통발").count()
	gillnet_count = FishingGear.objects.filter(type="자망").count()
	if total_gears > 0:
		total_trap_percentage = trap_count / total_gears * 100
		total_gillnet_percentage = gillnet_count / total_gears * 100
	else:
		total_trap_percentage = total_gillnet_percentage = 0

	for m in months:
		t = FishingGear.objects.filter(buy_date__month=m).count()
		c1 = FishingGear.objects.filter(type="통발", buy_date__month=m).count()
		c2 = FishingGear.objects.filter(type="자망", buy_date__month=m).count()
		if t > 0:
			month_percentages[m] = {
				'trap_percentage': c1 / t * 100,
				'gillnet_percentage': c2 / t * 100,
			}
		else:
			month_percentages[m] = {'trap_percentage': 0, 'gillnet_percentage': 0}
		month_counts[m] = {
			'trap_count': c1,
			'gillnet_count': c2,
		}

	selected_month = request.GET.get('month', '전체')
	if selected_month != '전체':
		try:
			sel_int = int(selected_month)
			selected_month = sel_int
			qs = FishingGear.objects.filter(buy_date__month=sel_int).select_related('seller', 'buyer')
		except ValueError:
			selected_month = '전체'
			qs = FishingGear.objects.select_related('seller', 'buyer').all()
	else:
		qs = FishingGear.objects.select_related('seller', 'buyer').all()

	gear_list = []
	for g in qs:
		gear_list.append({
			'buyer_name': g.buyer.buyer_name,
			'gear_id': g.gear_id,
			'seller_address': g.seller.address,
			'type': g.type,
			'buyer_ph': g.buyer.buyer_ph,
		})

	if isinstance(selected_month, int):
		month_data = month_percentages.get(selected_month, {'trap_percentage': 0, 'gillnet_percentage': 0})
	else:
		month_data = {
			'trap_percentage': total_trap_percentage,
			'gillnet_percentage': total_gillnet_percentage,
		}

	return render(request, 'lists/lists.html', {
		'view_type': 'gear_list',
		'gear_list': gear_list,
		'month_buttons': months,
		'selected_month': selected_month,
		'month_percentages': month_percentages,
		'month_data': month_data,
		'total_trap_percentage': total_trap_percentage,
		'total_gillnet_percentage': total_gillnet_percentage,
		'month_counts': month_counts,
	})


def losting_gear_view(request):
	qs = LostingGear.objects.all().order_by('-report_time')

	month = request.GET.get('month')
	if month and month.isdigit():
		sel_month = int(month)
		selected_month = sel_month
		qs = qs.filter(report_time__month=sel_month)
	else:
		selected_month = '전체'

	months_qs = LostingGear.objects.dates('report_time', 'month', order='DESC')
	month_buttons = [d.month for d in months_qs]

	monthly_report_count = {
		m: LostingGear.objects.filter(report_time__month=m).count()
		for m in month_buttons
	}

	admin_ids = Assignment.objects.values_list('as_admin_id', flat=True)
	monthly_retrieved_count = {
		m: LostingGear.objects.filter(
			report_time__month=m,
			lg_admin__admin_id__in=admin_ids
		).count()
		for m in month_buttons
	}
	monthly_retrieval_ratio = {
		m: (monthly_retrieved_count[m] / monthly_report_count[m] * 100)
		if monthly_report_count[m] > 0 else 0
		for m in month_buttons
	}

	total_report_count = LostingGear.objects.count()
	total_retrieved_count = LostingGear.objects.filter(
		lg_admin__admin_id__in=admin_ids
	).count()
	total_retrieval_ratio = (total_retrieved_count / total_report_count * 100) if total_report_count > 0 else 0

	current_month_count = monthly_report_count.get(selected_month, 0) if isinstance(selected_month, int) else None
	current_month_retrieved = monthly_retrieved_count.get(selected_month, 0) if isinstance(selected_month, int) else None
	current_month_ratio = monthly_retrieval_ratio.get(selected_month, 0) if isinstance(selected_month, int) else None

	losting_gear_list = []
	for lg in qs:
		losting_gear_list.append({
			'buyer_id': lg.lg_buyer_id,
			'cast_latitude': lg.cast_latitude,
			'cast_longitude': lg.cast_longitude,
			'report_time': lg.report_time.strftime("%Y년 %m월 %d일 %H시 %M분") if lg.report_time else '',
		})

	return render(request, 'lists/lists.html', {
		'view_type': 'losting_gear',
		'losting_gear_list': losting_gear_list,
		'month_buttons': month_buttons,
		'selected_month': selected_month,
		'monthly_report_count': monthly_report_count,
		'monthly_retrieved_count': monthly_retrieved_count,
		'monthly_retrieval_ratio': monthly_retrieval_ratio,
		'current_month_count': current_month_count,
		'current_month_retrieved': current_month_retrieved,
		'current_month_ratio': current_month_ratio,
		'total_report_count': total_report_count,
		'retrieved_count': total_retrieved_count,
		'total_retrieval_ratio': total_retrieval_ratio,
	})

