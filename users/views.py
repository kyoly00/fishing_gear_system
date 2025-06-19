from django.shortcuts import render, redirect
from .models import Admin

def root_redirect(request):
    return redirect('login')

def login_view(request):
    error_message = None
    if request.method == 'POST':
        try:
            admin_id = int(request.POST.get('admin_id'))
            admin_pw = request.POST.get('admin_pw')

            admin = Admin.objects.get(admin_id=admin_id)
            if admin.admin_pw == admin_pw:
                request.session['admin_id'] = admin.admin_id
                request.session['admin_name'] = admin.admin_name
                return redirect('map_view')
            else:
                error_message = "비밀번호가 틀렸습니다. 다시 시도해주세요."
        except (Admin.DoesNotExist, ValueError):
            error_message = "존재하지 않는 관리자이거나, ID 형식이 잘못되었습니다."

    return render(request, 'users/login.html', {'error_message': error_message})


def signup_view(request):
    error_message = None
    if request.method == 'POST':
        admin_name = request.POST.get('admin_name')
        admin_area = request.POST.get('region')  # HTML에선 region, DB에선 admin_area
        admin_id_raw = request.POST.get('admin_id')
        admin_pw = request.POST.get('admin_pw')
        admin_pw_check = request.POST.get('admin_pw_check')

        # ID가 숫자가 아닐 경우 예외 처리
        try:
            admin_id = int(admin_id_raw)
        except ValueError:
            error_message = "ID는 숫자만 입력 가능합니다."
            return render(request, 'users/signup.html', {'error_message': error_message})

        if admin_pw != admin_pw_check:
            error_message = "비밀번호가 일치하지 않습니다."
        elif Admin.objects.filter(admin_id=admin_id).exists():
            error_message = "이미 존재하는 ID입니다."
        else:
            Admin.objects.create(
                admin_id=admin_id,
                admin_pw=admin_pw,
                admin_name=admin_name,
                admin_area=admin_area
            )
            return redirect('login')

    return render(request, 'users/signup.html', {'error_message': error_message})


  
