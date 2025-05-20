from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from accounts.models import UserProfile
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(username=username)
            if not user_obj.is_active:
                messages.error(request, 'Tài khoản của bạn chưa được kích hoạt.')
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
            return redirect('login')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)

            if user.is_superuser:
                return redirect('accounts')

            try:
                profile = UserProfile.objects.get(user=user)
                if profile.type == 2:
                    return redirect('index')
                elif profile.type == 1:
                    return redirect('accounts')
                else:
                    return redirect('index')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Không tìm thấy hồ sơ người dùng.')
                return redirect('login')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')

    return render(request, 'login.html')



def logout_view(request):
    logout(request)
    return redirect('index')
