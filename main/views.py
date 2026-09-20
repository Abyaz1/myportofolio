from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from main.forms import EducationForm, ExperienceForm, MadingForm
from main.models import Education, Experience, Mading


def show_main(request):
    mading_list = Mading.objects.all().order_by("-created_at")
    mading_form = MadingForm()
    context = {
        "name": "M Naufal Abyaz Bawono",
        "npm": "2506656993",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada Data Science dan Artificial Intelligence."
        ),
        "mading_list": mading_list,
        "mading_form": mading_form,
    }
    return render(request, "index.html", context)



def show_experience(request):
    json_response = get_experience_json(request)

    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    experiences = [experience.object for experience in experiences]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "M Naufal Abyaz Bawono",
        "experience_list": experiences,
        "title_query": title_query,
    }
    return render(request, "experience.html", context)


def show_education(request):
    context = {
        "name": "M Naufal Abyaz Bawono",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)


def create_education(request):
    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pendidikan baru berhasil ditambahkan!")
        return redirect("main:show_education")

    context = {
        "name": "M Naufal Abyaz Bawono",
        "form": form,
    }
    return render(request, "education_form.html", context)


def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Pendidikan berhasil dihapus!")
        return redirect("main:show_education")

    return redirect("main:show_education")


def create_experience(request):
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "M Naufal Abyaz Bawono",
        "form": form,
    }
    return render(request, "experience_form.html", context)


def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    experiences_json = serializers.serialize("json", experiences)
    return HttpResponse(experiences_json, content_type="application/json")


def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")


def create_mading(request):
    form = MadingForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pesan mading berhasil diposting!")

    return redirect(reverse("main:show_main") + "#mading")


def increase_mading(request, mading_id):
    mading = get_object_or_404(Mading, pk=mading_id)

    if request.method == "POST":
        mading.likes += 1
        mading.save()

    return redirect(reverse("main:show_main") + f"#mading-{mading.id}")


def decrease_mading(request, mading_id):
    mading = get_object_or_404(Mading, pk=mading_id)

    if request.method == "POST":
        if mading.likes > 0:
            mading.likes -= 1
            mading.save()

    return redirect(reverse("main:show_main") + f"#mading-{mading.id}")


def delete_mading(request, mading_id):
    mading = get_object_or_404(Mading, pk=mading_id)

    if request.method == "POST":
        mading.delete()
        messages.success(request, "Pesan mading berhasil dihapus!")

    return redirect(reverse("main:show_main") + "#mading")


