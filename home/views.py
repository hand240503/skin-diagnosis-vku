from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings
from accounts.models import UserProfile
from chuyen_khoa.models import ChuyenKhoa

def index(request):
    return render(request, 'index.html')

GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', None)
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)

        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": user_message}
                    ]
                }
            ]
        }

        try:
            response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Lấy nội dung trả về (chuỗi)
            reply = data.get('candidates', [{}])[0].get('content', 'Không có phản hồi từ AI.')
            return JsonResponse({'reply': reply})
        except Exception as e:
            return JsonResponse({'reply': f"Lỗi khi gọi API Gemini: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

def team(request):
    chuyen_khoa_list = ChuyenKhoa.objects.all()
    chuyen_khoa_id = request.GET.get('specialist')

    doctors = UserProfile.objects.filter(type=1)
    if chuyen_khoa_id:
        doctors = doctors.filter(chuyen_khoa_id=chuyen_khoa_id)

    return render(request, 'team.html', {
        'chuyen_khoa_list': chuyen_khoa_list,
        'doctors': doctors,
        'selected_chuyen_khoa': chuyen_khoa_id
    })

