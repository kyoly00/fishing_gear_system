from django.shortcuts import render
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from collections import defaultdict
from datetime import datetime, timedelta
import calendar

from .models import RetrievalBoat, LostingGear, Assignment

def generate_calendar_data(year, month, holidays):
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, calendar.monthrange(year, month)[1])
    date_list = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    calendar_data = defaultdict(list)
    boats = RetrievalBoat.objects.all()

    for date in date_list:
        if date.weekday() >= 5 or date.date() in holidays:
            continue
        for boat in boats:
            if boat.off_date_start and boat.off_date_end and boat.off_date_start.date() <= date.date() <= boat.off_date_end.date():
                continue
            calendar_data[date.date()].append(boat.retrieval_company)
    return calendar_data

def may_calendar_view(request):
    year, month = 2025, 5
    holidays = {
        datetime(2025, 5, 1).date(),
        datetime(2025, 5, 5).date(),
        datetime(2025, 5, 6).date(),
    }
    calendar_data = generate_calendar_data(year, month, holidays)

    class CustomHTMLCalendar(calendar.HTMLCalendar):
        def __init__(self, calendar_data, holiday_set):
            super().__init__(firstweekday=6)
            self.calendar_data = calendar_data
            self.holiday_set = holiday_set
            self.year = year
            self.month = month

        def formatday(self, day, weekday):
            if day == 0:
                return '<td></td>'
            date = datetime(self.year, self.month, day).date()
            if weekday >= 5 or date in self.holiday_set:
                return f'<td><strong style="color:red;">{day}</strong></td>'
            companies = self.calendar_data.get(date, [])
            companies_str = "<br>".join(set(companies))
            return f'<td><strong>{day}</strong><br><span style="font-size:0.8em">{companies_str}</span></td>'

        def formatmonth(self, theyear, themonth, withyear=True):
            return super().formatmonth(theyear, themonth, withyear)

    html_calendar = CustomHTMLCalendar(calendar_data, holidays).formatmonth(year, month)

    assigned_admin_ids = Assignment.objects.values_list('as_admin_id', flat=True)
    unassigned_reports = LostingGear.objects.exclude(lg_admin_id__in=assigned_admin_ids)

    unassigned_list = [{
        'report_id': report.report_id,
        'buyer_id': report.lg_buyer_id,
        'report_time': report.report_time.strftime('%Y-%m-%d %H:%M'),
        'latitude': report.cast_latitude,
        'longitude': report.cast_longitude
    } for report in unassigned_reports]

    may_dates = [(datetime(year, month, d).date().strftime('%Y-%m-%d')) for d in range(1, 32)]

    return render(request, 'schedule/schedule.html', {
        'calendar': html_calendar,
        'unassigned_list': unassigned_list,
        'may_dates': may_dates,
    })

def available_boats_by_date(request):
    date_str = request.GET.get('date')
    selected_date = parse_date(date_str)
    if not selected_date:
        return HttpResponse('<option value="">잘못된 날짜</option>')

    year, month = 2025, 5
    holidays = {
        datetime(2025, 5, 1).date(),
        datetime(2025, 5, 5).date(),
        datetime(2025, 5, 6).date(),
    }

    calendar_data = generate_calendar_data(year, month, holidays)
    companies = calendar_data.get(selected_date, [])

    if not companies:
        return HttpResponse('<option value="">해당 날짜에 수거선 없음</option>')

    boats = RetrievalBoat.objects.filter(retrieval_company__in=companies)
    option_html = ''.join([f'<option value="{boat.boat_id}">{boat.retrieval_company}</option>' for boat in boats])

    return HttpResponse(option_html)



