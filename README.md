# Portfolio Website - Mata Kuliah Pemrograman Berbasis Platform

Nama : M Naufal Abyaz Bawono  
NPM : 2506656993  
Kelas : PBP B  

Website portofolio statis yang dirancang menggunakan framework Django, struktur HTML5 semantik, dan CSS3.

## Daftar Isi
- [Tentang Proyek](#tentang-proyek)
- [Struktur Direktori](#struktur-direktori)
- [Panduan Setup & Instalasi](#panduan-setup--instalasi)
- [Tugas 1](#tugas-1)
- [Tugas 2](#tugas-2)
- [Tugas 3](#tugas-3)
- [Progress Mingguan](#progress-mingguan)
- [AI Disclosure](#ai-disclosure)
- [Kontak](#kontak)


## Tentang Proyek
Proyek ini adalah website portofolio pribadi statis yang dibuat menggunakan framework Django untuk memenuhi tugas individu Pemrograman Berbasis Platform (PBP) di Fakultas Ilmu Komputer, Universitas Indonesia. Website ini menampilkan profil diri, latar belakang pendidikan, serta daftar keahlian dan minat.

## Struktur Direktori

```text
myportofolio/
├── portofolio/          # Modul utama konfigurasi Django (settings, urls, views)
├── templates/
│   └── index.html       # Landing page utama berbasis HTML5 semantik
├── static/
│   ├── css/
│   │   └── style.css    # File stylesheet CSS3 murni & variabel CSS
│   └── img/
│       └── Abyaz.jpg    # Aset gambar profil
├── manage.py            # Script eksekusi CLI Django
├── requirements.txt     # Daftar dependensi Python
└── README.md            # Dokumentasi proyek & refleksi
```

## Panduan Setup & Instalasi

Pastikan Anda telah memasang Python 3.10+ dan Git pada perangkat Anda.

### 1. Clone Repositori
```bash
git clone https://github.com/Abyaz1/myportofolio.git
cd myportofolio
```

### 2. Aktifkan Virtual Environment
- Windows (PowerShell):
  ```powershell
  .\env\Scripts\activate
  ```
- macOS / Linux:
  ```bash
  source env/bin/activate
  ```

### 3. Install Dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan Development Server Django
```bash
python manage.py runserver
```

Akses server lokal melalui browser pada: `http://127.0.0.1:8000/`

## Tugas 1

### 1. Penggunaan Elemen Semantik HTML5
Ya, saya menggunakan elemen semantik HTML5 pada struktur HTML website ini, antara lain `<header>`, `<nav>`, `<main>`, `<section>`, dan `<footer>`.

Bagaimana elemen tersebut membantu dalam pembuatan static web:
- Aksesibilitas dan SEO: Elemen semantik membantu search engine (SEO) dan pembaca layar (screen reader) memahami hierarki serta arti dari setiap bagian halaman web secara jelas.
- Keterbacaan & Pemeliharaan Kode (Maintainability): Mengelompokkan konten ke dalam elemen semantik seperti `<section class="hero">` dan `<section class="skills-section">` membuat struktur dokumen jauh lebih rapi, terstruktur, dan mudah dibaca dibandingkan hanya menggunakan tumpukan tag `<div>` (div-soup).
- Kemudahan Styling CSS: Penggunaan elemen semantik memperjelas pembagian area layout sehingga penulisan selector di CSS menjadi lebih intuitif dan terorganisasi.


### 2. Tantangan Responsive CSS & Evaluasi Perubahan Layout Desktop ke Mobile
Tantangan Tata Letak:
- Mengatur tata letak grid pada bagian Hero/Profile yang menggunakan grid-template-areas. Pada tampilan desktop, foto profil ditaruh di sebelah kanan teks identitas dan detail profil.
- Memastikan ukuran font judul (h1) dan kartu Skills tidak pecah atau menimbulkan horizontal scrollbar ketika dibuka di perangkat dengan layar kecil.

Evaluasi Perubahan Posisi & Prioritas Ukuran (Desktop ke Mobile):
- Hierarki Visual (Stacking): Saat berpindah ke tampilan mobile (ditangani dengan `@media (max-width: 600px)`), area grid diubah secara vertikal menjadi urutan: identity -> photo -> details. Dengan begitu, nama dan status utama pengguna langsung terlihat pertama kali, diikuti foto profil yang ukurannya dibatasi (max-width: 220px), lalu biodata dan link kontak.
- Responsivitas Ukuran Teks & Grid: Menggunakan fluid typography (clamp(3rem, 7vw, 5rem)) untuk judul serta grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)) pada kartu skills, sehingga konten otomatis menyesuaikan lebar layar secara alami.

### 3. Batasan Static Web & Fungsionalitas Dinamis Iterasi Selanjutnya
Batasan Static Web Murni:
- Pembaruan Konten Manual: Setiap kali ada pembaruan data (misalnya menambah skill, proyek, atau mengubah bio), saya harus mengubah file HTML secara manual.
- Kurangnya Interaksi Dua Arah: Belum ada fitur interaktif bagi pengunjung untuk memilih tema tampilan atau mengirimkan umpan balik secara langsung.
- Tidak Ada Manajemen Data: Data belum tersimpan secara terpusat di database.

Fungsionalitas Dinamis yang Ingin Ditambahkan pada Iterasi Selanjutnya:
1. Fitur Dark Mode (Mode Gelap/Terang): Menambahkan tombol sakelar (toggle) agar pengunjung dapat mengubah tema tampilan antara mode terang dan mode gelap sesuai preferensi.
2. Form Pesan dan Kesan: Menambahkan formulir interaktif tempat pengunjung dapat mengetik dan mengirimkan pesan atau kesan yang nantinya akan disimpan ke database serta ditampilkan secara dinamis.


## Tugas 2

### 1. Alur Request-Response Halaman Portofolio Baru pada Django
Ketika pengguna membuka halaman portofolio baru (misalnya `http://127.0.0.1:8000/experience/` atau `http://127.0.0.1:8000/education/`), alur yang terjadi dari penerimaan permintaan hingga data ditampilkan pada browser adalah sebagai berikut:

- Permintaan Pengguna (HTTP Request): Pengguna mengakses URL portofolio di browser, lalu browser mengirimkan permintaan HTTP ke server Django.
- urls.py Proyek (portofolio/urls.py): Django memeriksa konfigurasi routing utama proyek (`ROOT_URLCONF`). Menggunakan fungsi `include('main.urls')`, Django meneruskan path URL yang cocok ke file `urls.py` pada aplikasi `main`.
- urls.py Aplikasi (main/urls.py): File `urls.py` aplikasi mencocokkan rute URL spesifik (misalnya `path('experience/', show_experience, name='show_experience')`) dan mengarahkan permintaan ke fungsi handler view yang sesuai (`show_experience`).
- View (main/views.py): Fungsi view bertindak sebagai pemroses logika. View menerima objek `request`, memanggil model untuk mengambil data dari database, menyusun data tersebut ke dalam dictionary `context`, dan memanggil fungsi `render()` untuk menggabungkan context dengan file template HTML terkait.
- Model (main/models.py): Model mendefinisikan skema tabel basis data (seperti `Experience` dan `Education`). Saat view memanggil query ORM (misalnya `Experience.objects.all()`), model mengeksekusi query ke database dan mengembalikan kumpulan data objek ke view.
- Template (templates/): Template menerima data dari `context` view dan me-render dokumen HTML dinamis menggunakan Django Template Language (seperti perulangan `{% for exp in experience_list %}` untuk menampilkan data `{{ exp.title }}`, `{{ exp.description }}`, dan atribut lainnya).
- HTTP Response & Render Browser: Django mengirimkan kembali dokumen HTML yang sudah dirender lengkap ke browser dalam bentuk HTTP Response, lalu browser menampilkan halaman portofolio secara visual kepada pengguna.


### 2. Alasan Menyimpan Data Portofolio pada Model
Menyimpan data pada Model dan tidak menuliskannya langsung secara manual (hardcoded) di dalam template HTML memberikan dampak yang baik terhadap pemeliharaan dan pengembangan aplikasi:

- Pemisahan Logika dan Tampilan (Separation of Concerns): Template dikhususkan hanya untuk mengatur tata letak dan tampilan antarmuka (HTML/CSS), sedangkan model bertanggung jawab atas struktur data dan logika penyimpanan. Hal ini membuat struktur kode menjadi jauh lebih rapi dan terorganisasi.
- Kemudahan Pemeliharaan (Maintainability): Jika ada pembaruan isi data (menambah pengalaman baru atau mengubah deskripsi), perubahan cukup dilakukan lewat database atau Django Admin tanpa perlu menyentuh kode HTML. Begitu pula saat ingin mengubah desain kartu, kita cukup mengubah template satu kali dan perubahan tersebut otomatis diterapkan ke seluruh data.
- Menghindari Duplikasi Kode (Prinsip DRY): Template hanya membutuhkan satu blok kode perulangan (`{% for ... %}`) untuk menampilkan semua item. Jika data ditulis manual di template, penambahan data baru akan menyebabkan kode HTML berulang-ulang dan panjang.
- Validasi dan Integritas Data: Model memastikan data yang dimasukkan sesuai dengan tipe data yang ditentukan (seperti batas panjang karakter `CharField`, format link `URLField`, dan tanggal `DateTimeField`), sehingga meminimalkan potensi kesalahan data.
- Fleksibilitas Pengembangan: Data yang tersimpan di basis data dapat dengan mudah difilter, diurutkan, dicari, maupun diekspor ke format lain (seperti JSON/API) untuk kebutuhan pengembangan selanjutnya.


### 3. Perbedaan Fungsi makemigrations dan migrate pada Django
Perbedaan utama kedua perintah:
- makemigrations: Berfungsi untuk mendeteksi perubahan skema pada file `models.py` dan membuat berkas migrasi baru (file Python di dalam folder `migrations/`) sebagai cetak biru (blueprint). Perintah ini belum melakukan perubahan apapun secara langsung pada basis data.
- migrate: Berfungsi untuk membaca berkas migrasi yang belum diterapkan dan mengeksekusi perubahan skema tersebut secara nyata ke dalam basis data (seperti membuat tabel baru, menambah kolom, atau memperbarui constraint).

Contoh Perubahan Model yang Memerlukan Kedua Perintah:
Misalkan pada model `Experience` di `main/models.py`, kita ingin menambahkan atribut baru seperti `company` dan `project_url`:

```python
class Experience(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    # Penambahan field baru:
    company = models.CharField(max_length=255, default='')
    project_url = models.URLField(blank=True, null=True)
```

Karena terjadi perubahan struktur tabel pada model, kita harus menjalankan:
1. `python manage.py makemigrations` untuk membuat berkas migrasi baru yang mencatat penambahan kolom `company` dan `project_url`.
2. `python manage.py migrate` untuk menerapkan perubahan skema tersebut ke basis data nyata (`db.sqlite3`).

## Tugas 3

### 1. Penggunaan ModelForm dan Kewajiban {% csrf_token %}
ModelForm digunakan karena secara otomatis memetakan field model ke elemen form HTML, menyediakan validasi data bawaan lewat `form.is_valid()`, dan mempermudah penyimpanan ke basis data cukup dengan `form.save()`.

Tag `{% csrf_token %}` wajib disertakan untuk mencegah serangan Cross-Site Request Forgery (CSRF). Token acak unik ini memastikan setiap permintaan POST yang masuk benar-benar berasal dari formulir resmi aplikasi kita, bukan dari manipulasi situs luar.

### 2. Alasan JSON Lebih Disukai Dibandingkan XML
JSON memiliki struktur ringkas berbasis pasangan key-value tanpa tag penutup berulang sehingga ukuran payload lebih kecil dan hemat bandwidth. Selain itu, JSON didukung secara native di JavaScript (`JSON.parse()`) tanpa memerlukan proses parsing DOM yang rumit dan lambat seperti pada XML.

### 3. Alur Pengembalian Data JSON dan Perlunya Serialization
Alurnya dimulai ketika klien mengirimkan request GET ke endpoint URL. Rute pada `urls.py` mengarahkan permintaan ke fungsi view, lalu view mengambil data dari database menggunakan ORM Django. Kumpulan data tersebut kemudian diubah menjadi format teks JSON menggunakan `serializers.serialize()`, lalu dibungkus dalam `HttpResponse` dengan header `application/json` untuk dikirim kembali ke klien.

Serialization diperlukan karena objek model Django merupakan objek Python di memori server yang tidak dapat dikirimkan langsung melalui protokol HTTP. Serialisasi menerjemahkan objek tersebut ke format teks universal (JSON) agar dapat dikirim lewat jaringan dan dipahami oleh berbagai platform klien.


## Progress Mingguan

Progres pengembangan proyek portofolio pribadi berdasarkan riwayat commit dan rincian pengerjaan tugas:

### Minggu 1 - Tutorial 1: Setup Proyek Django & Static Web Layout
- Inisialisasi Proyek: Pengaturan awal kerangka kerja Django, penataan direktori aplikasi, serta halaman profil utama (`index.html`).
- Penerapan HTML5 Semantik: Menyusun struktur antarmuka menggunakan tag semantik HTML5 (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, dan `<footer>`).
- Responsive CSS3 Styling: Merancang stylesheet murni `style.css` menggunakan variabel CSS (`:root`), CSS Grid (`grid-template-areas`), Flexbox, serta typography responsif (`clamp()`).
- Dokumentasi Awal: Menuliskan jawaban refleksi tugas 1 dan petunjuk setup awal di `README.md`.

### Minggu 2 - Tutorial 2: Model Data Dinamis & Testing (Education & Experience)
- Implementasi Model ORM: Membuat skema basis data `Education` dan `Experience` pada `main/models.py` serta mengeksekusi migrasi database (`makemigrations` & `migrate`).
- Routing & Dynamic Views: Menyusun fungsi view dan pemetaan URL untuk menampilkan data pendidikan dan pengalaman secara dinamis dari database.
- Konfigurasi Environment & Deployment: Penyesuaian `requirements.txt` ke Django 5.0 dan penambahan `CSRF_TRUSTED_ORIGINS` untuk server PWS.
- Unit Testing & Styling: Menambahkan pengujian otomatis unit test untuk model/views serta menyempurnakan tampilan visual komponen.

### Minggu 3 - Tutorial 3: Form Handling, JSON Serialization & Mading Pesan
- Form Handling & ModelForm: Mengimplementasikan formulir interaktif menggunakan `ModelForm` untuk fitur input dan pembaruan data (`update`) pada `Education` dan `Experience`.
- Fitur Mading Pesan: Menambahkan fitur Mading Pesan/Kesan pengunjung pada profil serta penyesuaian konfigurasi zona waktu (`timezone`).
- Keamanan CSRF & Serialisasi Data: Menerapkan tag `{% csrf_token %}` pada form POST dan menyajikan data JSON menggunakan serialisasi Django ORM.
- Dokumentasi & Refleksi: Menuliskan jawaban refleksi tugas 3 dan memperbarui dokumentasi proyek.


## AI Disclosure

- Tools AI yang Digunakan: Google Gemini / Antigravity
- Link Percakapan / Log AI: [https://share.gemini.google/MdDoL8QyJW4C](https://share.gemini.google/MdDoL8QyJW4C)
- Ringkasan Bantuan AI:

  - Memberikan masukan dalam penyusunan struktur dokumen README agar sesuai dengan panduan dan kriteria penilaian.
  - Membantu menyusun design skill & Interest.
- Refleksi & Penyesuaian Mandiri:
  - Penyesuaian bahasa dan format jawaban reflektif agar ditulis secara alami dengan bahasa yang ramah dan mudah diketik tanpa sintaks khusus (seperti simbol LaTeX).
  - Pengecekan manual terhadap kode model, view, url, dan template agar jawaban sesuai dengan implementasi proyek aktual.

## Kontak
- Nama: M Naufal Abyaz Bawono
- NPM: 2506656993
- GitHub: [github.com/Abyaz1](https://github.com/Abyaz1/)
- LinkedIn: [linkedin.com/in/abyaz](https://linkedin.com/in/abyaz)