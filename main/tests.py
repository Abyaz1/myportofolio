from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Education, Experience, Mading


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            Activity="S1 Ilmu Komputer",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_education")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    # --- Experience Tests ---
    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page_accessible_and_uses_template(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")

    def test_experience_page_shows_data(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    # --- Education Tests ---
    def test_education_model(self):
        self.assertEqual(str(self.education), "S1 Ilmu Komputer at Universitas Indonesia")
        self.assertTrue(self.education.is_ongoing)

    def test_education_page_accessible_and_uses_template(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_page_shows_data(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.education.institution)
        self.assertContains(response, self.education.Activity)
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_education_page(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, "Belum ada pendidikan yang ditambahkan.")

    def test_completed_education(self):
        self.education.ended_at = timezone.now()
        self.education.save()
        response = self.client.get(reverse("main:show_education"))

        self.assertFalse(self.education.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_education_form_valid(self):
        from main.forms import EducationForm
        form = EducationForm(data={
            "institution": "Universitas Indonesia",
            "Activity": "S1 Ilmu Komputer",
        })
        self.assertTrue(form.is_valid())

    def test_create_education_view(self):
        response = self.client.get(reverse("main:create_education"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education_form.html")

        post_response = self.client.post(reverse("main:create_education"), data={
            "institution": "SMA Negeri 1",
            "Activity": "IPA",
        })
        self.assertRedirects(post_response, reverse("main:show_education"))
        self.assertTrue(Education.objects.filter(institution="SMA Negeri 1").exists())

    def test_get_experience_json(self):
        response = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        response_filter = self.client.get(reverse("main:get_experience_json") + "?title=Asisten")
        self.assertEqual(response_filter.status_code, 200)
        self.assertContains(response_filter, "Asisten Dosen PBP")

    def test_delete_experience(self):
        post_response = self.client.post(
            reverse("main:delete_experience", kwargs={"experience_id": self.experience.id})
        )
        self.assertRedirects(post_response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(id=self.experience.id).exists())

    def test_delete_education(self):
        post_response = self.client.post(
            reverse("main:delete_education", kwargs={"education_id": self.education.id})
        )
        self.assertRedirects(post_response, reverse("main:show_education"))
        self.assertFalse(Education.objects.filter(id=self.education.id).exists())

    def test_create_experience_view(self):
        response = self.client.get(reverse("main:create_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")

        post_response = self.client.post(reverse("main:create_experience"), data={
            "title": "Software Engineer Intern",
            "description": "Magang di perusahaan IT",
            "category": "internship",
            "thumbnail": "",
        })
        self.assertRedirects(post_response, reverse("main:show_experience"))
        self.assertTrue(Experience.objects.filter(title="Software Engineer Intern").exists())

    def test_mading_crud(self):
        mading = Mading.objects.create(
            name="Pengunjung",
            message="Keren banget portofolionya!",
        )
        self.assertEqual(str(mading), "Pengunjung: Keren banget portofolionya!")
        self.assertEqual(mading.likes, 0)

        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, "Mading Pesan")
        self.assertContains(response, "Keren banget portofolionya!")

        inc_response = self.client.post(
            reverse("main:increase_mading", kwargs={"mading_id": mading.id})
        )
        mading.refresh_from_db()
        self.assertEqual(mading.likes, 1)

        dec_response = self.client.post(
            reverse("main:decrease_mading", kwargs={"mading_id": mading.id})
        )
        mading.refresh_from_db()
        self.assertEqual(mading.likes, 0)

        self.client.post(
            reverse("main:decrease_mading", kwargs={"mading_id": mading.id})
        )
        mading.refresh_from_db()
        self.assertEqual(mading.likes, 0)

        create_response = self.client.post(reverse("main:create_mading"), data={
            "name": "Budi",
            "message": "Semangat belajarnya!",
        })
        self.assertTrue(Mading.objects.filter(name="Budi").exists())

        del_response = self.client.post(
            reverse("main:delete_mading", kwargs={"mading_id": mading.id})
        )
        self.assertFalse(Mading.objects.filter(id=mading.id).exists())