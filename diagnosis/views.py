from django.shortcuts import render
from .models import SkinDiseaseModel
from django.core.files.storage import default_storage
import os
from django.conf import settings
import requests
def diagnosis_form(request):
    return render(request, 'diagnosis.html')


def diagnosis_result(request):
    if request.method == 'POST' and request.FILES.get('image'):
        model = SkinDiseaseModel()
        img_file = request.FILES['image']
        temp_path = default_storage.save(f"temp/{img_file.name}", img_file)
        full_path = os.path.join(default_storage.location, temp_path)

        # Dự đoán
        result = model.predict(full_path)
        os.remove(full_path)

        # Gọi Gemini API
        gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
        headers = {
            "Content-Type": "application/json",
        }
        prompt_text = (
            f"Kết quả chẩn đoán là: {result}. "
            "Hãy đưa ra khuyến cáo y tế phù hợp cho bệnh nhân, "
            "nhưng không được đề xuất thuốc, hoặc bất kỳ phương pháp điều trị nào mà bệnh nhân có thể tự thực hiện tại nhà. "
            "Chỉ nên đưa ra lời khuyên chung hoặc đề xuất đến cơ sở y tế."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt_text}
                    ]
                }
            ]
        }

        try:
            response = requests.post(gemini_api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Lấy phần text khuyến cáo từ Gemini
            recommendation = data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            recommendation = f"Lỗi khi gọi Gemini: {str(e)}"

        return render(request, 'diagnosis_result.html', {
            'result': result,
            'recommendation': recommendation
        })

    return render(request, 'diagnosis.html')
