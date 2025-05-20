from django.shortcuts import render, redirect
from .models import User 
from .models import UserProfile

def accounts(request):
    users = User.objects.all()
    return render(request, 'accounts.html', {'users': users})

def add_doctor(request):
    if request.method == "POST":
        ten = request.POST.get('ten')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        UserProfile.objects.create(
            ten=ten,
            email=email,
            phone=phone,
            type=1,            
            is_activated=True 
        )

        return redirect('accounts')

    return render(request, 'add_doctor.html')

