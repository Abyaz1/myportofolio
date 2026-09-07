# Portfolio Website - Mata Kuliah Pemrograman Berbasis Platform

Nama : M Naufal Abyaz Bawono  
NPM : 2506656993  
Kelas : PBP B  

Website portofolio statis yang dirancang menggunakan framework Django, struktur HTML5 semantik, dan CSS3.

## Daftar Isi
- [Tentang Proyek](#tentang-proyek)
- [Fitur Utama](#fitur-utama)
- [Tech Stack](#tech-stack)
- [Struktur Direktori](#struktur-direktori)
- [Panduan Setup & Instalasi](#panduan-setup--instalasi)
- [Keputusan Desain & Arsitektur](#keputusan-desain--arsitektur)
- [Jawaban Pertanyaan Refleksi Tugas](#jawaban-pertanyaan-refleksi-tugas)
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


## AI Disclosure

- Tools AI yang Digunakan: Google Gemini / Antigravity
- Link Percakapan / Log AI: [https://share.gemini.google/MdDoL8QyJW4C](https://share.gemini.google/MdDoL8QyJW4C)
- Ringkasan Bantuan AI:
  - Membantu menyusun jawaban reflektif terkait penggunaan elemen semantik HTML5 dan konsep tata letak CSS responsive.
  - Memberikan masukan dalam penyusunan struktur dokumen README agar sesuai dengan panduan dan kriteria penilaian.
  - Membantu menyusun design skill & Interest.
- Refleksi & Penyesuaian Mandiri:
  - Penyesuaian bahasa dan format jawaban reflektif agar ditulis secara alami dengan bahasa yang ramah dan mudah diketik tanpa sintaks khusus (seperti simbol LaTeX).
  - Pengecekan manual terhadap kode HTML dan CSS agar tetap mematuhi batasan static sesuai kebutuhan.

## Kontak
- Nama: M Naufal Abyaz Bawono
- NPM: 2506656993
- GitHub: [github.com/Abyaz1](https://github.com/Abyaz1/)
- LinkedIn: [linkedin.com/in/abyaz](https://linkedin.com/in/abyaz)