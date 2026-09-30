import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from main.forms import EducationForm, ExperienceForm, MadingForm
from main.models import Education, Experience, Mading


def check_is_editor(user):
    return user.is_authenticated and (
        user.groups.filter(name="Editor").exists()
        or user.has_perm("main.change_experience")
        or user.has_perm("main.change_education")
    )


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
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
        "last_login": last_login,
        "is_editor": check_is_editor(request.user),
    }
    return render(request, "index.html", context)


def show_experience(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()
    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    context = {
        "name": "M Naufal Abyaz Bawono",
        "experience_list": experiences,
        "title_query": title_query,
        "form": ExperienceForm(),
        "is_editor": check_is_editor(request.user),
    }
    return render(request, "experience.html", context)


def show_education(request):
    title_query = request.GET.get("title", "").strip()
    educations = Education.objects.all()
    if title_query:
        educations = educations.filter(
            Q(institution__icontains=title_query) | Q(Activity__icontains=title_query)
        )

    context = {
        "name": "M Naufal Abyaz Bawono",
        "education_list": educations,
        "title_query": title_query,
        "form": EducationForm(),
        "is_editor": check_is_editor(request.user),
    }
    return render(request, "education.html", context)

@login_required(login_url="/login/")
def create_education(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    if request.method == "POST" and (request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")):
        return create_education_ajax(request)
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

@login_required(login_url="/login/")
def delete_education(request, education_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Pendidikan berhasil dihapus!")

    return redirect("main:show_education")

@login_required(login_url="/login/")
def edit_education(request, education_id):
    if not (request.user.is_superuser or check_is_editor(request.user)):
        raise PermissionDenied
    education = get_object_or_404(Education, pk=education_id)
    form = EducationForm(request.POST or None, instance=education)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pendidikan berhasil diperbarui!")
        return redirect("main:show_education")

    context = {
        "name": "M Naufal Abyaz Bawono",
        "form": form,
        "education": education,
    }
    return render(request, "education_edit_form.html", context)

@login_required(login_url="/login/")
def create_experience_ajax(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save()
            return JsonResponse({
                "status": "success",
                "message": "Experience baru berhasil ditambahkan!",
                "id": str(experience.id),
            }, status=201)
        else:
            first_error = next(iter(form.errors.values()))[0] if form.errors else "Gagal menambahkan experience."
            return JsonResponse({
                "status": "error",
                "message": first_error,
                "errors": form.errors.get_json_data(),
            }, status=400)
    return JsonResponse({"status": "error", "message": "Metode tidak diizinkan."}, status=405)

@login_required(login_url="/login/")
def create_education_ajax(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    if request.method == "POST":
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save()
            return JsonResponse({
                "status": "success",
                "message": "Pendidikan baru berhasil ditambahkan!",
                "id": str(education.id),
            }, status=201)
        else:
            first_error = next(iter(form.errors.values()))[0] if form.errors else "Gagal menambahkan pendidikan."
            return JsonResponse({
                "status": "error",
                "message": first_error,
                "errors": form.errors.get_json_data(),
            }, status=400)
    return JsonResponse({"status": "error", "message": "Metode tidak diizinkan."}, status=405)

@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    if request.method == "POST" and (request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")):
        return create_experience_ajax(request)
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

@login_required(login_url="/login/")
def edit_experience(request, experience_id):
    if not (request.user.is_superuser or check_is_editor(request.user)):
        raise PermissionDenied
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": "M Naufal Abyaz Bawono",
        "form": form,
        "experience": experience,
    }
    return render(request, "experience_edit_form.html", context)


def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    experiences_json = serializers.serialize(
        "json",
        experiences,
        use_natural_foreign_keys=True,
    )
    return HttpResponse(experiences_json, content_type="application/json")


def get_education_json(request):
    title_query = request.GET.get("title", "").strip()
    educations = Education.objects.all()

    if title_query:
        educations = educations.filter(
            Q(institution__icontains=title_query) | Q(Activity__icontains=title_query)
        )

    educations_json = serializers.serialize(
        "json",
        educations,
        use_natural_foreign_keys=True,
    )
    return HttpResponse(educations_json, content_type="application/json")


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")

    return redirect("main:show_experience")


@login_required(login_url="/login/")
def toggle_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        if request.user in experience.starred_by.all():
            experience.starred_by.remove(request.user)
        else:
            experience.starred_by.add(request.user)

    return redirect("main:show_experience")


@login_required(login_url="/login/")
def toggle_star_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        if request.user in education.starred_by.all():
            education.starred_by.remove(request.user)
        else:
            education.starred_by.add(request.user)

    return redirect("main:show_education")


@login_required(login_url="/login/")
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
        if request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", ""):
            return JsonResponse({"status": "success", "likes": mading.likes})

    return redirect(reverse("main:show_main") + f"#mading-{mading.id}")


def decrease_mading(request, mading_id):
    mading = get_object_or_404(Mading, pk=mading_id)

    if request.method == "POST":
        if mading.likes > 0:
            mading.likes -= 1
            mading.save()
        if request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", ""):
            return JsonResponse({"status": "success", "likes": mading.likes})

    return redirect(reverse("main:show_main") + f"#mading-{mading.id}")

@login_required(login_url="/login/")
def edit_mading(request, mading_id):
    if not (request.user.is_superuser or check_is_editor(request.user)):
        raise PermissionDenied
    mading = get_object_or_404(Mading, pk=mading_id)
    form = MadingForm(request.POST or None, instance=mading)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pesan mading berhasil diperbarui!")
        return redirect(reverse("main:show_main") + f"#mading-{mading.id}")

    context = {
        "name": "M Naufal Abyaz Bawono",
        "form": form,
        "mading": mading,
    }
    return render(request, "mading_edit_form.html", context)


@login_required(login_url="/login/")
def delete_mading(request, mading_id):
    mading = get_object_or_404(Mading, pk=mading_id)

    if request.method == "POST":
        mading.delete()
        messages.success(request, "Pesan mading berhasil dihapus!")

    return redirect(reverse("main:show_main") + "#mading")

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Abyaz",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Abyaz",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    if request.method == "POST":
        logout(request)
        response = redirect("main:show_main")
        response.delete_cookie('last_login')
        return response
    return redirect("main:show_main")

