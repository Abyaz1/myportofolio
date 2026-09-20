from django.forms import ModelForm, Select, Textarea, TextInput, URLInput
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


