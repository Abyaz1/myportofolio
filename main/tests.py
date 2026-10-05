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

    def test_experience_page_shows_skeleton(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="experience-grid"')
        self.assertContains(response, 'id="experience-loading-state"')
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()

        self.assertFalse(self.experience.is_ongoing)
        response = self.client.get(reverse("main:get_experience_json"))
        self.assertFalse(response.json()[0]["is_ongoing"])

    # --- Education Tests ---
    def test_education_model(self):
        self.assertEqual(str(self.education), "S1 Ilmu Komputer at Universitas Indonesia")
        self.assertTrue(self.education.is_ongoing)

    def test_education_page_accessible_and_uses_template(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_page_shows_skeleton(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="education-grid"')
        self.assertContains(response, 'id="education-loading-state"')
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_education_page(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:get_education_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_completed_education(self):
        self.education.ended_at = timezone.now()
        self.education.save()

        self.assertFalse(self.education.is_ongoing)
        response = self.client.get(reverse("main:get_education_json"))
        self.assertFalse(response.json()[0]["is_ongoing"])

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
        self.client.login(username="admin", password="adminpassword")
        self.experience.starred_by.add(self.superuser)

        response = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = response.json()
        self.assertEqual(data[0]["starred_by"], ["admin"])
        self.assertEqual(data[0]["star_count"], 1)
        self.assertTrue(data[0]["is_starred"])

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

        # Uji GET & POST edit_mading
        edit_mading_url = reverse("main:edit_mading", kwargs={"mading_id": mading.id})
        get_edit_resp = self.client.get(edit_mading_url)
        self.assertEqual(get_edit_resp.status_code, 200)
        self.assertTemplateUsed(get_edit_resp, "mading_edit_form.html")

        post_edit_resp = self.client.post(edit_mading_url, data={
            "name": "Pengunjung Diedit",
            "message": "Pesan sudah diperbarui!",
        })
        self.assertRedirects(post_edit_resp, reverse("main:show_main") + f"#mading-{mading.id}")
        mading.refresh_from_db()
        self.assertEqual(mading.name, "Pengunjung Diedit")
        self.assertEqual(mading.message, "Pesan sudah diperbarui!")

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
        # 1. Pengunjung anonim (belum login) tidak boleh melihat tombol Tambah
        exp_resp = self.client.get(reverse("main:show_experience"))
        self.assertEqual(exp_resp.status_code, 200)
        self.assertNotContains(exp_resp, "Tambah Experience")
        self.assertNotContains(exp_resp, reverse("main:create_experience"))

        edu_resp = self.client.get(reverse("main:show_education"))
        self.assertEqual(edu_resp.status_code, 200)
        self.assertNotContains(edu_resp, "Tambah Pendidikan")
        self.assertNotContains(edu_resp, reverse("main:create_education"))

        # 2. Superuser harus melihat tombol Tambah
        self.client.login(username="admin", password="adminpassword")

        exp_admin_resp = self.client.get(reverse("main:show_experience"))
        self.assertContains(exp_admin_resp, "Tambah Experience")
        self.assertContains(exp_admin_resp, reverse("main:create_experience"))

        edu_admin_resp = self.client.get(reverse("main:show_education"))
        self.assertContains(edu_admin_resp, "Tambah Pendidikan")
        self.assertContains(edu_admin_resp, reverse("main:create_education"))

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

        # Di AJAX JSON response, star_count = 1 dan is_starred = True
        json_resp = self.client.get(reverse("main:get_experience_json"))
        items = json_resp.json()
        self.assertEqual(items[0]["star_count"], 1)
        self.assertTrue(items[0]["is_starred"])

        # 3. Pengguna login klik lagi untuk unstar
        unstar_resp = self.client.post(
            reverse("main:toggle_star", kwargs={"experience_id": self.experience.id})
        )
        self.assertRedirects(unstar_resp, reverse("main:show_experience"))
        self.assertEqual(self.experience.starred_by.count(), 0)
        self.assertNotIn(regular_user, self.experience.starred_by.all())

        json_resp_after = self.client.get(reverse("main:get_experience_json"))
        items_after = json_resp_after.json()
        self.assertEqual(items_after[0]["star_count"], 0)
        self.assertFalse(items_after[0]["is_starred"])

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

        # --- Peran 2: Pengguna biasa (Regular User) ---
        self.client.login(username="normaluser", password="password123")
        # Dapat membaca & memberi star
        self.assertEqual(self.client.get(reverse("main:show_experience")).status_code, 200)
        self.assertEqual(self.client.post(reverse("main:toggle_star", kwargs={"experience_id": self.experience.id})).status_code, 302)
        # Tidak dapat membuat, mengubah, atau menghapus -> 403 Forbidden
        self.assertEqual(self.client.get(create_exp_url).status_code, 403)
        self.assertEqual(self.client.get(edit_exp_url).status_code, 403)
        self.assertEqual(self.client.post(delete_exp_url).status_code, 403)
        # UI: tidak melihat tombol Tambah
        normal_page = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(normal_page, "Tambah Experience")

        # --- Peran 3: Editor ---
        self.client.login(username="editoruser", password="password123")
        # Dapat membaca & memberi star
        self.assertEqual(self.client.get(reverse("main:show_experience")).status_code, 200)
        # DAPAT mengubah data -> 200 OK
        self.assertEqual(self.client.get(edit_exp_url).status_code, 200)
        # TIDAK DAPAT membuat atau menghapus -> 403 Forbidden
        self.assertEqual(self.client.get(create_exp_url).status_code, 403)
        self.assertEqual(self.client.post(delete_exp_url).status_code, 403)
        # UI: tidak melihat tombol Tambah
        editor_page = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(editor_page, "Tambah Experience")

        # --- Peran 4: Pemilik Portofolio (Superuser) ---
        self.client.login(username="admin", password="adminpassword")
        # DAPAT membuat, mengubah, menghapus
        self.assertEqual(self.client.get(create_exp_url).status_code, 200)
        self.assertEqual(self.client.get(edit_exp_url).status_code, 200)
        # UI: melihat tombol Tambah Experience
        admin_page = self.client.get(reverse("main:show_experience"))
        self.assertContains(admin_page, "Tambah Experience")

    def test_toggle_star_education(self):
        from django.contrib.auth.models import User
        regular_user = User.objects.create_user(username="edutestuser", password="password123")

        # 1. Anonim klik star diarahkan ke login
        anon_star_resp = self.client.post(
            reverse("main:toggle_star_education", kwargs={"education_id": self.education.id})
        )
        self.assertEqual(anon_star_resp.status_code, 302)
        self.assertIn(reverse("main:login"), anon_star_resp.url)
        self.assertEqual(self.education.starred_by.count(), 0)

        # 2. Pengguna login memberi star
        self.client.login(username="edutestuser", password="password123")
        star_resp = self.client.post(
            reverse("main:toggle_star_education", kwargs={"education_id": self.education.id})
        )
        self.assertRedirects(star_resp, reverse("main:show_education"))
        self.assertEqual(self.education.starred_by.count(), 1)
        self.assertIn(regular_user, self.education.starred_by.all())

        json_resp = self.client.get(reverse("main:get_education_json"))
        items = json_resp.json()
        self.assertEqual(items[0]["star_count"], 1)
        self.assertTrue(items[0]["is_starred"])

        # 3. Pengguna login membatalkan star
        unstar_resp = self.client.post(
            reverse("main:toggle_star_education", kwargs={"education_id": self.education.id})
        )
        self.assertRedirects(unstar_resp, reverse("main:show_education"))
        self.assertEqual(self.education.starred_by.count(), 0)
        self.assertNotIn(regular_user, self.education.starred_by.all())

        json_resp_after = self.client.get(reverse("main:get_education_json"))
        items_after = json_resp_after.json()
        self.assertEqual(items_after[0]["star_count"], 0)
        self.assertFalse(items_after[0]["is_starred"])

    # --- Toast Notification Tests ---
    def test_toast_component_rendered(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="toast-component"')
        self.assertContains(response, 'toast.js')

    def test_toast_on_add_and_delete_experience(self):
        self.client.login(username="admin", password="adminpassword")

        # Add experience
        add_resp = self.client.post(reverse("main:create_experience"), data={
            "title": "Data Scientist Intern",
            "description": "Bekerja dengan model AI",
            "category": "internship",
            "thumbnail": "",
        }, follow=True)
        self.assertContains(add_resp, "showToast")
        self.assertContains(add_resp, "Experience baru berhasil ditambahkan!")

        # Delete experience
        created_exp = Experience.objects.get(title="Data Scientist Intern")
        del_resp = self.client.post(
            reverse("main:delete_experience", kwargs={"experience_id": created_exp.id}),
            follow=True
        )
        self.assertContains(del_resp, "showToast")
        self.assertContains(del_resp, "Experience berhasil dihapus!")

    def test_toast_on_add_and_delete_education(self):
        self.client.login(username="admin", password="adminpassword")

        # Add education
        add_resp = self.client.post(reverse("main:create_education"), data={
            "institution": "Fasilkom UI",
            "Activity": "Magister Ilmu Komputer",
        }, follow=True)
        self.assertContains(add_resp, "showToast")
        self.assertContains(add_resp, "Pendidikan baru berhasil ditambahkan!")

        # Delete education
        created_edu = Education.objects.get(institution="Fasilkom UI")
        del_resp = self.client.post(
            reverse("main:delete_education", kwargs={"education_id": created_edu.id}),
            follow=True
        )
        self.assertContains(del_resp, "showToast")
        self.assertContains(del_resp, "Pendidikan berhasil dihapus!")

    def test_toast_on_add_and_delete_mading(self):
        self.client.login(username="admin", password="adminpassword")

        # Add mading
        add_resp = self.client.post(reverse("main:create_mading"), data={
            "name": "Pengunjung",
            "message": "Halo website keren!",
        }, follow=True)
        self.assertContains(add_resp, "showToast")
        self.assertContains(add_resp, "Pesan mading berhasil diposting!")

        # Delete mading
        created_mading = Mading.objects.get(name="Pengunjung")
        del_resp = self.client.post(
            reverse("main:delete_mading", kwargs={"mading_id": created_mading.id}),
            follow=True
        )
        self.assertContains(del_resp, "showToast")
        self.assertContains(del_resp, "Pesan mading berhasil dihapus!")

    def test_ajax_experience_search_elements(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="experience-search-form"')
        self.assertContains(response, 'id="experience-search-input"')
        self.assertContains(response, 'id="experience-loading-state"')
        self.assertContains(response, 'id="experience-error-state"')
        self.assertContains(response, 'id="experience-empty-state"')
        self.assertContains(response, 'id="experience-grid"')
        self.assertContains(response, 'experience.js')

    def test_add_experience_modal_elements(self):
        anon_resp = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(anon_resp, 'id="add-experience-modal"')

        self.client.login(username="admin", password="adminpassword")
        admin_resp = self.client.get(reverse("main:show_experience"))
        self.assertContains(admin_resp, 'popovertarget="add-experience-modal"')
        self.assertContains(admin_resp, 'id="add-experience-modal"')
        self.assertContains(admin_resp, 'id="experience-form"')
        self.assertContains(admin_resp, reverse("main:create_experience"))

    def test_xss_protection(self):
        from main.forms import ExperienceForm

        # 1. Judul hanya berisi tag HTML ditolak
        form_invalid = ExperienceForm(data={
            "title": '<img src="x" onerror="alert(\'XSS!\')">',
            "description": "Deskripsi aman",
            "category": "internship",
            "thumbnail": "",
        })
        self.assertFalse(form_invalid.is_valid())
        self.assertIn("Judul pengalaman tidak boleh hanya berisi tag HTML.", form_invalid.errors["title"])

        # 2. Tag HTML pada judul dan deskripsi dibersihkan oleh server
        form_valid = ExperienceForm(data={
            "title": 'Belajar <b>Django</b> Web',
            "description": 'Pengalaman <i>frontend</i>',
            "category": "part-time",
            "thumbnail": "",
        })
        self.assertTrue(form_valid.is_valid())
        self.assertEqual(form_valid.cleaned_data["title"], "Belajar Django Web")
        self.assertEqual(form_valid.cleaned_data["description"], "Pengalaman frontend")

    def test_ajax_education_search_elements(self):
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="education-search-form"')
        self.assertContains(response, 'id="education-search-input"')
        self.assertContains(response, 'id="education-loading-state"')
        self.assertContains(response, 'id="education-error-state"')
        self.assertContains(response, 'id="education-empty-state"')
        self.assertContains(response, 'id="education-grid"')
        self.assertContains(response, 'education.js')

    def test_add_education_modal_elements(self):
        anon_resp = self.client.get(reverse("main:show_education"))
        self.assertNotContains(anon_resp, 'id="add-education-modal"')

        self.client.login(username="admin", password="adminpassword")
        admin_resp = self.client.get(reverse("main:show_education"))
        self.assertContains(admin_resp, 'popovertarget="add-education-modal"')
        self.assertContains(admin_resp, 'id="add-education-modal"')
        self.assertContains(admin_resp, 'id="education-form"')
        self.assertContains(admin_resp, reverse("main:create_education"))

    def test_get_education_json(self):
        response = self.client.get(reverse("main:get_education_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertContains(response, "Universitas Indonesia")

        filter_resp = self.client.get(reverse("main:get_education_json") + "?title=Indonesia")
        self.assertEqual(filter_resp.status_code, 200)
        self.assertContains(filter_resp, "Universitas Indonesia")

        empty_filter_resp = self.client.get(reverse("main:get_education_json") + "?title=NonExistent")
        self.assertEqual(empty_filter_resp.status_code, 200)
        self.assertEqual(empty_filter_resp.json(), [])

    def test_create_education_ajax(self):
        self.client.login(username="admin", password="adminpassword")

        # Success
        resp = self.client.post(reverse("main:create_education_ajax"), data={
            "institution": "MIT",
            "Activity": "Computer Science",
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(Education.objects.filter(institution="MIT").exists())

        # Invalid form
        bad_resp = self.client.post(reverse("main:create_education_ajax"), data={
            "institution": "",
            "Activity": "",
        })
        self.assertEqual(bad_resp.status_code, 400)
        self.assertEqual(bad_resp.json()["status"], "error")

        # Unauthorized
        self.client.logout()
        unauth_resp = self.client.post(reverse("main:create_education_ajax"), data={
            "institution": "Harvard",
            "Activity": "Math",
        })
        self.assertEqual(unauth_resp.status_code, 403)
        self.assertEqual(unauth_resp.json()["status"], "error")

    def test_create_experience_ajax(self):
        self.client.login(username="admin", password="adminpassword")

        # Success
        resp = self.client.post(reverse("main:create_experience_ajax"), data={
            "title": "Full Stack Dev",
            "description": "Building scalable web apps",
            "category": "full-time",
            "thumbnail": "",
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["status"], "success")
        self.assertTrue(Experience.objects.filter(title="Full Stack Dev").exists())

        # Invalid form
        bad_resp = self.client.post(reverse("main:create_experience_ajax"), data={
            "title": "",
            "description": "",
            "category": "full-time",
        })
        self.assertEqual(bad_resp.status_code, 400)
        self.assertEqual(bad_resp.json()["status"], "error")

        # Unauthorized
        self.client.logout()
        unauth_resp = self.client.post(reverse("main:create_experience_ajax"), data={
            "title": "Hacker",
            "description": "Exploit",
            "category": "full-time",
        })
        self.assertEqual(unauth_resp.status_code, 403)
        self.assertEqual(unauth_resp.json()["status"], "error")

    def test_xss_protection_education(self):
        from main.forms import EducationForm

        # 1. HTML only is rejected
        form_invalid = EducationForm(data={
            "institution": "<script>alert('xss')</script>",
            "Activity": "<b></b>",
        })
        self.assertFalse(form_invalid.is_valid())

        # 2. Strips HTML tags when accompanied with valid text
        form_valid = EducationForm(data={
            "institution": "Universitas <b>Indonesia</b>",
            "Activity": "<i>S1</i> Ilmu Komputer",
        })
        self.assertTrue(form_valid.is_valid())
        self.assertEqual(form_valid.cleaned_data["institution"], "Universitas Indonesia")
        self.assertEqual(form_valid.cleaned_data["Activity"], "S1 Ilmu Komputer")



class AjaxSecurityTest(TestCase):
    """CSRF, otorisasi per peran, dan sanitasi pada endpoint AJAX."""

    def setUp(self):
        from django.contrib.auth.models import Group, User
        from django.test import Client

        self.csrf_client = Client(enforce_csrf_checks=True)
        self.admin = User.objects.create_superuser("admin", "a@example.com", "adminpassword")
        self.regular = User.objects.create_user("biasa", password="userpassword")
        self.editor = User.objects.create_user("editor", password="editorpassword")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.exp_payload = {
            "title": "Riset AI",
            "description": "Meneliti model bahasa.",
            "category": "research",
            "thumbnail": "",
        }
        self.edu_payload = {"institution": "SMAN 1", "Activity": "IPA"}

    def _token(self, client):
        client.get(reverse("main:show_experience"))
        return client.cookies["csrftoken"].value

    def _post(self, client, name, data, token=None):
        extra = {"HTTP_X_CSRFTOKEN": token} if token else {}
        return client.post(reverse(name), data=data, **extra)

    # --- CSRF ---
    def test_ajax_create_rejects_missing_csrf_token(self):
        self.csrf_client.login(username="admin", password="adminpassword")
        for name, data in (
            ("main:create_experience_ajax", self.exp_payload),
            ("main:create_education_ajax", self.edu_payload),
        ):
            self.assertEqual(self._post(self.csrf_client, name, data).status_code, 403)
        self.assertFalse(Experience.objects.exists())
        self.assertFalse(Education.objects.exists())

    def test_ajax_create_accepts_csrf_header(self):
        self.csrf_client.login(username="admin", password="adminpassword")
        token = self._token(self.csrf_client)
        exp = self._post(self.csrf_client, "main:create_experience_ajax", self.exp_payload, token)
        edu = self._post(self.csrf_client, "main:create_education_ajax", self.edu_payload, token)
        self.assertEqual(exp.status_code, 201)
        self.assertEqual(edu.status_code, 201)
        self.assertTrue(Experience.objects.filter(pk=exp.json()["id"]).exists())
        self.assertTrue(Education.objects.filter(pk=edu.json()["id"]).exists())

    def test_ajax_create_accepts_csrfmiddlewaretoken_field(self):
        self.csrf_client.login(username="admin", password="adminpassword")
        token = self._token(self.csrf_client)
        resp = self._post(
            self.csrf_client,
            "main:create_education_ajax",
            {**self.edu_payload, "csrfmiddlewaretoken": token},
        )
        self.assertEqual(resp.status_code, 201)

    # --- Otorisasi per peran ---
    def test_ajax_create_forbidden_for_non_superuser_roles(self):
        from django.test import Client

        for username, password in (("biasa", "userpassword"), ("editor", "editorpassword")):
            client = Client()
            client.login(username=username, password=password)
            for name, data in (
                ("main:create_experience_ajax", self.exp_payload),
                ("main:create_education_ajax", self.edu_payload),
            ):
                resp = self._post(client, name, data)
                self.assertEqual(resp.status_code, 403, f"{username} -> {name}")
                self.assertEqual(resp.json()["status"], "error")
        self.assertFalse(Experience.objects.exists())
        self.assertFalse(Education.objects.exists())

    def test_ajax_create_rejects_non_post_method(self):
        self.client.login(username="admin", password="adminpassword")
        for name in ("main:create_experience_ajax", "main:create_education_ajax"):
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 405)
            self.assertEqual(resp.json()["status"], "error")

    # --- Respons validasi & sanitasi ---
    def test_ajax_validation_error_contains_message_and_field_errors(self):
        self.client.login(username="admin", password="adminpassword")
        resp = self._post(self.client, "main:create_experience_ajax", {**self.exp_payload, "title": ""})
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertEqual(body["status"], "error")
        self.assertTrue(body["message"])
        self.assertIn("title", body["errors"])

    def test_ajax_create_strips_html_tags_before_saving(self):
        self.client.login(username="admin", password="adminpassword")
        resp = self._post(self.client, "main:create_experience_ajax", {
            **self.exp_payload,
            "title": "<b>Asisten</b> Dosen",
            "description": "<img src=x onerror=alert(1)>Mengajar",
        })
        self.assertEqual(resp.status_code, 201)
        saved = Experience.objects.get(pk=resp.json()["id"])
        self.assertEqual(saved.title, "Asisten Dosen")
        self.assertEqual(saved.description, "Mengajar")

        resp = self._post(self.client, "main:create_education_ajax", {
            "institution": "<i>UI</i>", "Activity": "<u>S1</u>",
        })
        saved_edu = Education.objects.get(pk=resp.json()["id"])
        self.assertEqual((saved_edu.institution, saved_edu.Activity), ("UI", "S1"))

    def test_ajax_create_rejects_html_only_input(self):
        self.client.login(username="admin", password="adminpassword")
        resp = self._post(self.client, "main:create_experience_ajax", {**self.exp_payload, "title": "<b></b>"})
        self.assertEqual(resp.status_code, 400)
        resp = self._post(self.client, "main:create_education_ajax", {"institution": "<i></i>", "Activity": "ok"})
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(Experience.objects.exists())
        self.assertFalse(Education.objects.exists())

    def test_mading_form_strips_html_tags(self):
        from main.forms import MadingForm

        form = MadingForm(data={"name": "<b>Budi</b>", "message": "<script>x</script>Halo"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Budi")
        self.assertNotIn("<", form.cleaned_data["message"])
        self.assertFalse(MadingForm(data={"name": "<b></b>", "message": "Halo"}).is_valid())


class ListJsonTest(TestCase):
    """Endpoint JSON untuk halaman daftar (pengunjung, user login, pencarian)."""

    def setUp(self):
        from django.contrib.auth.models import User

        self.user = User.objects.create_user("pengguna", password="userpassword")
        self.other = User.objects.create_user("lain", password="userpassword")
        self.exp = Experience.objects.create(title="Magang Data", description="d", category="internship")
        Experience.objects.create(title="Freelance Web", description="d", category="freelance")
        self.edu = Education.objects.create(institution="Universitas Indonesia", Activity="S1 Ilmu Komputer")
        Education.objects.create(institution="SMAN 8", Activity="IPA")

    def _item(self, url_name, obj):
        return next(i for i in self.client.get(reverse(url_name)).json() if i["id"] == str(obj.id))

    def test_anonymous_gets_star_info_without_own_star(self):
        self.exp.starred_by.add(self.user, self.other)
        self.edu.starred_by.add(self.user)

        exp_item = self._item("main:get_experience_json", self.exp)
        edu_item = self._item("main:get_education_json", self.edu)
        self.assertEqual(exp_item["star_count"], 2)
        self.assertFalse(exp_item["is_starred"])
        self.assertEqual(edu_item["star_count"], 1)
        self.assertFalse(edu_item["is_starred"])

    def test_is_starred_is_per_logged_in_user(self):
        self.exp.starred_by.add(self.user)
        self.edu.starred_by.add(self.user)

        self.client.login(username="pengguna", password="userpassword")
        self.assertTrue(self._item("main:get_experience_json", self.exp)["is_starred"])
        self.assertTrue(self._item("main:get_education_json", self.edu)["is_starred"])

        self.client.login(username="lain", password="userpassword")
        exp_item = self._item("main:get_experience_json", self.exp)
        self.assertFalse(exp_item["is_starred"])
        self.assertEqual(exp_item["star_count"], 1)

    def test_experience_search_is_case_insensitive_and_can_be_empty(self):
        url = reverse("main:get_experience_json")
        self.assertEqual([i["title"] for i in self.client.get(url + "?title=magang").json()], ["Magang Data"])
        self.assertEqual(len(self.client.get(url + "?title=").json()), 2)
        self.assertEqual(len(self.client.get(url + "?title=%20%20").json()), 2)
        self.assertEqual(self.client.get(url + "?title=tidak-ada").json(), [])

    def test_education_search_matches_institution_or_activity(self):
        url = reverse("main:get_education_json")
        self.assertEqual(len(self.client.get(url + "?title=sman").json()), 1)
        self.assertEqual(len(self.client.get(url + "?title=ilmu").json()), 1)
        self.assertEqual(self.client.get(url + "?title=tidak-ada").json(), [])

    def test_json_contains_fields_needed_by_frontend(self):
        exp_item = self.client.get(reverse("main:get_experience_json")).json()[0]
        for key in ("id", "title", "description", "category_display", "thumbnail",
                    "started_at", "is_ongoing", "star_count", "is_starred", "starred_by"):
            self.assertIn(key, exp_item)
        edu_item = self.client.get(reverse("main:get_education_json")).json()[0]
        for key in ("id", "institution", "activity", "started_at", "is_ongoing",
                    "star_count", "is_starred", "starred_by"):
            self.assertIn(key, edu_item)

    def test_list_pages_open_for_anonymous_and_prefill_query(self):
        for name in ("main:show_experience", "main:show_education"):
            resp = self.client.get(reverse(name) + "?title=halo")
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, 'value="halo"')


class MadingAjaxTest(TestCase):
    def setUp(self):
        self.mading = Mading.objects.create(name="Tamu", message="Halo!")

    def test_like_endpoints_return_json_for_ajax(self):
        headers = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        inc = self.client.post(reverse("main:increase_mading", args=[self.mading.id]), **headers)
        self.assertEqual(inc.status_code, 200)
        self.assertEqual(inc.json(), {"status": "success", "likes": 1})
        dec = self.client.post(reverse("main:decrease_mading", args=[self.mading.id]), **headers)
        self.assertEqual(dec.json()["likes"], 0)

    def test_like_endpoint_redirects_without_ajax_header(self):
        resp = self.client.post(reverse("main:increase_mading", args=[self.mading.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("#mading-", resp["Location"])


class ThemeAndLanguageTest(TestCase):
    """Markup dark mode dan pilihan bahasa ID/EN."""

    @staticmethod
    def _read_static(path):
        from django.contrib.staticfiles import finders

        with open(finders.find(path), encoding="utf-8") as handle:
            return handle.read()

    def _known_keys(self):
        import re

        return set(re.findall(r"'([\w.]+)'\s*:", self._read_static("js/site.js")))

    def test_base_has_theme_and_language_controls(self):
        resp = self.client.get(reverse("main:show_main"))
        self.assertContains(resp, 'id="theme-toggle"')
        self.assertContains(resp, 'id="lang-toggle"')
        self.assertContains(resp, "portfolio_theme")
        self.assertContains(resp, "js/site.js")

    def test_theme_script_runs_before_stylesheet(self):
        html = self.client.get(reverse("main:show_main")).content.decode()
        self.assertLess(html.index("portfolio_theme"), html.index("css/style.css"))

    def test_dark_theme_variables_defined(self):
        css = self._read_static("css/style.css")
        self.assertIn(':root[data-theme="dark"]', css)
        for var in ("--surface", "--surface-alt", "--edge", "--danger", "--overlay"):
            self.assertIn(var + ":", css)

    def test_every_i18n_key_used_in_templates_has_english_translation(self):
        import re
        from pathlib import Path

        from django.conf import settings

        used = set()
        for path in Path(settings.BASE_DIR, "templates").rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            used |= set(re.findall(r'data-i18n(?:-placeholder)?="([\w.]+)"', text))
            used |= set(re.findall(r"data-i18n=\"[^\"]*?'([\w.]+)'", text))
        self.assertTrue(used, "tidak ada kunci i18n ditemukan di template")
        self.assertEqual(sorted(used - self._known_keys()), [])

    def test_i18n_keys_used_by_list_scripts_exist(self):
        import re

        known = self._known_keys()
        for script in ("js/experience.js", "js/education.js"):
            used = set(re.findall(r"\bt\('([\w.]+)'", self._read_static(script)))
            self.assertEqual(sorted(used - known), [], script)

    def test_mading_form_placeholders_are_translatable(self):
        resp = self.client.get(reverse("main:show_main"))
        self.assertContains(resp, 'data-i18n-placeholder="mading.name.ph"')
        self.assertContains(resp, 'data-i18n-placeholder="mading.message.ph"')

    def test_search_inputs_are_translatable(self):
        self.assertContains(self.client.get(reverse("main:show_experience")), 'data-i18n-placeholder="search.exp"')
        self.assertContains(self.client.get(reverse("main:show_education")), 'data-i18n-placeholder="search.edu"')
