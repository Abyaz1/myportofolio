from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Education, Experience, Mading


class MainTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.superuser = User.objects.create_superuser(
            username="admin",
            password="adminpassword",
            email="admin@example.com",
        )
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
        self.client.login(username="admin", password="adminpassword")
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
        import json
        self.experience.starred_by.add(self.superuser)

        response = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data[0]["fields"]["starred_by"], [["admin"]])

        proj_response = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(proj_response.status_code, 200)

        response_filter = self.client.get(reverse("main:get_experience_json") + "?title=Asisten")
        self.assertEqual(response_filter.status_code, 200)
        self.assertContains(response_filter, "Asisten Dosen PBP")

    def test_delete_experience(self):
        self.client.login(username="admin", password="adminpassword")
        post_response = self.client.post(
            reverse("main:delete_experience", kwargs={"experience_id": self.experience.id})
        )
        self.assertRedirects(post_response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(id=self.experience.id).exists())

    def test_delete_education(self):
        self.client.login(username="admin", password="adminpassword")
        post_response = self.client.post(
            reverse("main:delete_education", kwargs={"education_id": self.education.id})
        )
        self.assertRedirects(post_response, reverse("main:show_education"))
        self.assertFalse(Education.objects.filter(id=self.education.id).exists())

    def test_create_experience_view(self):
        self.client.login(username="admin", password="adminpassword")
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

    def test_edit_experience_view(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(
            reverse("main:edit_experience", kwargs={"experience_id": self.experience.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_edit_form.html")

        post_response = self.client.post(
            reverse("main:edit_experience", kwargs={"experience_id": self.experience.id}),
            data={
                "title": "Lead Assistant PBP",
                "description": "Mengkoordinasi asisten dosen.",
                "category": "part-time",
                "thumbnail": "",
            },
        )
        self.assertRedirects(post_response, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Lead Assistant PBP")

    def test_edit_education_view(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(
            reverse("main:edit_education", kwargs={"education_id": self.education.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education_edit_form.html")

        post_response = self.client.post(
            reverse("main:edit_education", kwargs={"education_id": self.education.id}),
            data={
                "institution": "Universitas Indonesia Baru",
                "Activity": "S2 Ilmu Komputer",
            },
        )
        self.assertRedirects(post_response, reverse("main:show_education"))
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Universitas Indonesia Baru")


    def test_mading_crud(self):
        self.client.login(username="admin", password="adminpassword")
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

        # Uji pemanggilan AJAX (Fetch) dengan header XMLHttpRequest
        ajax_inc = self.client.post(
            reverse("main:increase_mading", kwargs={"mading_id": mading.id}),
            headers={"x-requested-with": "XMLHttpRequest"}
        )
        self.assertEqual(ajax_inc.status_code, 200)
        self.assertEqual(ajax_inc.json(), {"status": "success", "likes": 1})

        ajax_dec = self.client.post(
            reverse("main:decrease_mading", kwargs={"mading_id": mading.id}),
            headers={"x-requested-with": "XMLHttpRequest"}
        )
        self.assertEqual(ajax_dec.status_code, 200)
        self.assertEqual(ajax_dec.json(), {"status": "success", "likes": 0})

        create_response = self.client.post(reverse("main:create_mading"), data={
            "name": "Budi",
            "message": "Semangat belajarnya!",
        })
        self.assertTrue(Mading.objects.filter(name="Budi").exists())

        del_response = self.client.post(
            reverse("main:delete_mading", kwargs={"mading_id": mading.id})
        )
        self.assertFalse(Mading.objects.filter(id=mading.id).exists())

    def test_logout_user_post(self):
        from django.contrib.auth.models import User
        user = User.objects.create_user(username="testuser", password="secretpassword")
        self.client.login(username="testuser", password="secretpassword")

        # Pastikan user terautentikasi dan halaman menampilkan tombol/form logout
        main_resp = self.client.get(reverse("main:show_main"))
        self.assertContains(main_resp, 'action="' + reverse("main:logout") + '"')
        self.assertContains(main_resp, 'Logout')

        # Logout via POST
        logout_resp = self.client.post(reverse("main:logout"))
        self.assertRedirects(logout_resp, reverse("main:show_main"))

        # Pastikan user sudah tidak terautentikasi
        after_resp = self.client.get(reverse("main:show_main"))
        self.assertContains(after_resp, reverse("main:login"))
        self.assertNotContains(after_resp, "testuser")

    def test_buttons_hidden_for_anonymous_and_visible_for_superuser(self):
        # 1. Pengunjung anonim (belum login) tidak boleh melihat tombol Tambah & Hapus/Ubah
        exp_resp = self.client.get(reverse("main:show_experience"))
        self.assertEqual(exp_resp.status_code, 200)
        self.assertNotContains(exp_resp, "Tambah Experience")
        self.assertNotContains(exp_resp, reverse("main:create_experience"))
        self.assertNotContains(exp_resp, "delete-experience-")

        edu_resp = self.client.get(reverse("main:show_education"))
        self.assertEqual(edu_resp.status_code, 200)
        self.assertNotContains(edu_resp, "Tambah Pendidikan")
        self.assertNotContains(edu_resp, reverse("main:create_education"))
        self.assertNotContains(edu_resp, "delete-education-")

        # 2. Superuser harus melihat tombol Tambah & Hapus/Ubah
        self.client.login(username="admin", password="adminpassword")

        exp_admin_resp = self.client.get(reverse("main:show_experience"))
        self.assertContains(exp_admin_resp, "Tambah Experience")
        self.assertContains(exp_admin_resp, reverse("main:create_experience"))
        self.assertContains(exp_admin_resp, f"delete-experience-{self.experience.id}")

        edu_admin_resp = self.client.get(reverse("main:show_education"))
        self.assertContains(edu_admin_resp, "Tambah Pendidikan")
        self.assertContains(edu_admin_resp, reverse("main:create_education"))
        self.assertContains(edu_admin_resp, f"delete-education-{self.education.id}")

    def test_toggle_star_experience(self):
        from django.contrib.auth.models import User
        regular_user = User.objects.create_user(username="regularuser", password="password123")

        # 1. Anonim klik star akan di-redirect ke login
        anon_star_resp = self.client.post(
            reverse("main:toggle_star", kwargs={"experience_id": self.experience.id})
        )
        self.assertEqual(anon_star_resp.status_code, 302)
        self.assertIn(reverse("main:login"), anon_star_resp.url)
        self.assertEqual(self.experience.starred_by.count(), 0)

        # 2. Pengguna login memberi star
        self.client.login(username="regularuser", password="password123")
        star_resp = self.client.post(
            reverse("main:toggle_star", kwargs={"experience_id": self.experience.id})
        )
        self.assertRedirects(star_resp, reverse("main:show_experience"))
        self.assertEqual(self.experience.starred_by.count(), 1)
        self.assertIn(regular_user, self.experience.starred_by.all())

        page_resp = self.client.get(reverse("main:show_experience"))
        self.assertContains(page_resp, "is-starred")
        self.assertContains(page_resp, "Unstar")

        # 3. Pengguna login klik lagi untuk unstar
        unstar_resp = self.client.post(
            reverse("main:toggle_star", kwargs={"experience_id": self.experience.id})
        )
        self.assertRedirects(unstar_resp, reverse("main:show_experience"))
        self.assertEqual(self.experience.starred_by.count(), 0)
        self.assertNotIn(regular_user, self.experience.starred_by.all())

    def test_authorization_four_roles(self):
        from django.contrib.auth.models import User, Group
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        editor_user = User.objects.create_user(username="editoruser", password="password123")
        editor_user.groups.add(editor_group)

        regular_user = User.objects.create_user(username="normaluser", password="password123")

        edit_exp_url = reverse("main:edit_experience", kwargs={"experience_id": self.experience.id})
        create_exp_url = reverse("main:create_experience")
        delete_exp_url = reverse("main:delete_experience", kwargs={"experience_id": self.experience.id})

        # --- Peran 1: Pengunjung tanpa login (Guest) ---
        self.client.logout()
        # Dapat membaca
        self.assertEqual(self.client.get(reverse("main:show_experience")).status_code, 200)
        # Akses aksi diarahkan ke login
        self.assertRedirects(self.client.get(create_exp_url), f'/login/?next={create_exp_url}')
        self.assertRedirects(self.client.get(edit_exp_url), f'/login/?next={edit_exp_url}')
        self.assertRedirects(self.client.post(delete_exp_url), f'/login/?next={delete_exp_url}')
        # UI: tidak ada tombol aksi
        guest_page = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(guest_page, "Tambah Experience")
        self.assertNotContains(guest_page, "Ubah")
        self.assertNotContains(guest_page, f"delete-experience-{self.experience.id}")

        # --- Peran 2: Pengguna biasa (Regular User) ---
        self.client.login(username="normaluser", password="password123")
        # Dapat membaca & memberi star
        self.assertEqual(self.client.get(reverse("main:show_experience")).status_code, 200)
        self.assertEqual(self.client.post(reverse("main:toggle_star", kwargs={"experience_id": self.experience.id})).status_code, 302)
        # Tidak dapat membuat, mengubah, atau menghapus -> 403 Forbidden
        self.assertEqual(self.client.get(create_exp_url).status_code, 403)
        self.assertEqual(self.client.get(edit_exp_url).status_code, 403)
        self.assertEqual(self.client.post(delete_exp_url).status_code, 403)
        # UI: melihat star, tetapi tidak melihat tombol Tambah, Ubah, maupun Hapus
        normal_page = self.client.get(reverse("main:show_experience"))
        self.assertContains(normal_page, "button-star")
        self.assertNotContains(normal_page, "Tambah Experience")
        self.assertNotContains(normal_page, "Ubah")
        self.assertNotContains(normal_page, f"delete-experience-{self.experience.id}")

        # --- Peran 3: Editor ---
        self.client.login(username="editoruser", password="password123")
        # Dapat membaca & memberi star
        self.assertEqual(self.client.get(reverse("main:show_experience")).status_code, 200)
        # DAPAT mengubah data -> 200 OK
        self.assertEqual(self.client.get(edit_exp_url).status_code, 200)
        # TIDAK DAPAT membuat atau menghapus -> 403 Forbidden
        self.assertEqual(self.client.get(create_exp_url).status_code, 403)
        self.assertEqual(self.client.post(delete_exp_url).status_code, 403)
        # UI: melihat tombol Ubah & star, TETAPI TIDAK melihat tombol Tambah atau Hapus
        editor_page = self.client.get(reverse("main:show_experience"))
        self.assertContains(editor_page, "button-star")
        self.assertContains(editor_page, "Ubah")
        self.assertNotContains(editor_page, "Tambah Experience")
        self.assertNotContains(editor_page, f"delete-experience-{self.experience.id}")

        # --- Peran 4: Pemilik Portofolio (Superuser) ---
        self.client.login(username="admin", password="adminpassword")
        # DAPAT membuat, mengubah, menghapus
        self.assertEqual(self.client.get(create_exp_url).status_code, 200)
        self.assertEqual(self.client.get(edit_exp_url).status_code, 200)
        # UI: melihat SEMUA tombol (Tambah, Ubah, Hapus, Star)
        admin_page = self.client.get(reverse("main:show_experience"))
        self.assertContains(admin_page, "button-star")
        self.assertContains(admin_page, "Tambah Experience")
        self.assertContains(admin_page, "Ubah")
        self.assertContains(admin_page, f"delete-experience-{self.experience.id}")