from django.shortcuts import render

from main.models import Education, Experience


def show_main(request):
    context = {
        "name": "M Naufal Abyaz Bawono",
        "npm": "2506656993",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada Data Science dan Artificial Intelligence."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "M Naufal Abyaz Bawono",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_education(request):
    context = {
        "name": "M Naufal Abyaz Bawono",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)