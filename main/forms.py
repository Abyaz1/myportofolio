from django.core.exceptions import ValidationError
from django.forms import ModelForm, Select, Textarea, TextInput, URLInput
from django.utils.html import strip_tags
from main.models import Education, Experience, Mading


class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = [
            "institution",
            "Activity",
        ]

        labels = {
            "institution": "Nama Institusi",
            "Activity": "Aktivitas / Program",
        }

        widgets = {
            "institution": TextInput(
                attrs={
                    "placeholder": "Universitas Indonesia",
                    "maxlength": 255,
                }
            ),
            "Activity": TextInput(
                attrs={
                    "placeholder": "S1 Ilmu Komputer",
                    "maxlength": 255,
                }
            ),
        }

    def clean_institution(self):
        institution = strip_tags(self.cleaned_data.get("institution", "")).strip()
        if not institution:
            raise ValidationError("Nama institusi tidak boleh hanya berisi tag HTML.")
        return institution

    def clean_Activity(self):
        activity = strip_tags(self.cleaned_data.get("Activity", "")).strip()
        if not activity:
            raise ValidationError("Aktivitas tidak boleh hanya berisi tag HTML.")
        return activity


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
        ]

        labels = {
            "title": "Judul Pengalaman",
            "description": "Deskripsi",
            "category": "Kategori",
            "thumbnail": "URL Gambar/Thumbnail",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Asisten Dosen PBP",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan pengalamanmu",
                    "rows": 3,
                }
            ),
            "category": Select(),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://example.com/image.jpg",
                }
            ),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data.get("title", "")).strip()
        if not title:
            raise ValidationError("Judul pengalaman tidak boleh hanya berisi tag HTML.")
        return title

    def clean_description(self):
        return strip_tags(self.cleaned_data.get("description", "")).strip()


class MadingForm(ModelForm):
    class Meta:
        model = Mading
        fields = [
            "name",
            "message",
        ]

        labels = {
            "name": "Nama Pengirim",
            "message": "Pesan Mading",
        }

        widgets = {
            "name": TextInput(
                attrs={
                    "placeholder": "Masukkan nama Anda",
                    "maxlength": 100,
                }
            ),
            "message": Textarea(
                attrs={
                    "placeholder": "Tuliskan pesan mading di sini...",
                    "rows": 3,
                }
            ),
        }

    def clean_name(self):
        name = strip_tags(self.cleaned_data.get("name", "")).strip()
        if not name:
            raise ValidationError("Nama tidak boleh hanya berisi tag HTML.")
        return name

    def clean_message(self):
        message = strip_tags(self.cleaned_data.get("message", "")).strip()
        if not message:
            raise ValidationError("Pesan tidak boleh hanya berisi tag HTML.")
        return message



