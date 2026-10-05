"""Chatbot sederhana berbasis kata kunci.

Alur: pertanyaan dinormalisasi -> dicocokkan ke kata kunci per topik -> data
ditarik dari database (Experience, Education, Mading) atau dari template jawaban
tetap -> jika tidak ada yang cocok, balas "informasi tidak tersedia".
Jawaban tidak pernah memuat teks mentah dari pertanyaan pengguna.
"""
import re

from main.models import Education, Experience, Mading

MAX_QUERY_LENGTH = 200

PROFILE = {
    "name": "M Naufal Abyaz Bawono",
    "npm": "2506656993",
    "program": "S1 Ilmu Komputer, Fakultas Ilmu Komputer, Universitas Indonesia",
    "email": "abyazbawono@gmail.com",
    "github": "https://github.com/Abyaz1/",
    "linkedin": "https://linkedin.com/in/abyaz",
}

# Kata kunci per topik. Kata >= 5 huruf juga dicocokkan sebagai awalan (mis. "pengalamannya").
KEYWORDS = {
    "thanks": {"terima kasih", "makasih", "thanks", "thank"},
    "help": {"bantuan", "help", "menu", "topik"},
    "who": {"siapa", "nama", "who", "name", "kenalkan", "perkenalan", "tentang", "about", "profil", "profile", "bio"},
    "npm": {"npm", "nim", "student id"},
    "program": {"jurusan", "prodi", "program studi", "major", "fakultas", "faculty"},
    "skills": {"skill", "skills", "keahlian", "kemampuan", "teknologi", "tech", "stack", "python", "django",
               "pytorch", "pandas", "javascript", "ai", "ml", "data science", "minat", "interest"},
    "experience": {"pengalaman", "experience", "magang", "internship", "kerja", "bekerja", "work", "riset",
                   "research", "volunteer", "freelance", "karir", "career"},
    "education": {"pendidikan", "education", "sekolah", "school", "kuliah", "kampus", "universitas",
                  "university", "studi", "belajar", "lulus"},
    "contact": {"kontak", "contact", "email", "surel", "hubungi", "github", "linkedin", "sosmed", "social", "reach"},
    "mading": {"mading", "pesan", "kesan", "message", "guestbook", "board"},
    "greet": {"halo", "hai", "hi", "hello", "hey", "pagi", "siang", "sore", "malam", "assalamualaikum"},
}

# Urutan prioritas saat skor sama (yang lebih awal menang).
PRIORITY = ["thanks", "help", "npm", "program", "contact", "mading", "skills", "experience",
            "education", "who", "greet"]

STOPWORDS = {
    "apa", "yang", "di", "ke", "dari", "dan", "ini", "itu", "saja", "ada", "apakah", "bagaimana", "tentang",
    "the", "is", "are", "what", "about", "of", "and", "a", "an", "you", "your", "kamu", "anda", "dia", "nya",
    "tolong", "ceritakan", "jelaskan", "tell", "me", "please", "sebutkan", "lihat", "show", "punya", "have",
    "does", "do", "his", "her", "mu", "saya", "aku", "bisa", "can", "boleh", "dong", "ya", "nih",
}

SUGGESTIONS = {
    "id": ["Siapa kamu?", "Apa saja skill-nya?", "Pengalaman apa saja?", "Riwayat pendidikan?", "Bagaimana cara menghubungi?"],
    "en": ["Who are you?", "What are the skills?", "What experience is there?", "Education history?", "How can I contact?"],
}

TEXT = {
    "unavailable": {
        "id": "Informasi tidak tersedia. Coba tanyakan tentang profil, skill, pengalaman, pendidikan, kontak, atau mading.",
        "en": "Information is not available. Try asking about the profile, skills, experience, education, contact, or message board.",
    },
    "greet": {
        "id": "Halo! Saya bot asisten portofolio ini. Tanyakan tentang profil, skill, pengalaman, pendidikan, kontak, atau mading.",
        "en": "Hi! I'm this portfolio's assistant bot. Ask about the profile, skills, experience, education, contact, or message board.",
    },
    "thanks": {"id": "Sama-sama!", "en": "You're welcome!"},
    "help": {
        "id": "Topik yang bisa ditanyakan: profil, NPM, program studi, skill, pengalaman, pendidikan, kontak, dan mading.",
        "en": "Topics you can ask about: profile, student ID, study program, skills, experience, education, contact, and message board.",
    },
    "who": {
        "id": "{name} adalah mahasiswa {program} yang tertarik pada Data Science dan Artificial Intelligence.",
        "en": "{name} is a student of {program}, interested in Data Science and Artificial Intelligence.",
    },
    "npm": {"id": "NPM: {npm}.", "en": "Student ID (NPM): {npm}."},
    "program": {"id": "Program studi: {program}.", "en": "Study program: {program}."},
    "skills": {
        "id": "Tiga bidang utama: Data Science (Python, Pandas, Matplotlib), AI/ML (Scikit-Learn, Google ADK, PyTorch), dan Web Development (Django, HTML/CSS, JavaScript).",
        "en": "Three main areas: Data Science (Python, Pandas, Matplotlib), AI/ML (Scikit-Learn, Google ADK, PyTorch), and Web Development (Django, HTML/CSS, JavaScript).",
    },
    "contact": {
        "id": "Kontak: email {email}, GitHub {github}, LinkedIn {linkedin}.",
        "en": "Contact: email {email}, GitHub {github}, LinkedIn {linkedin}.",
    },
    "experience_list": {"id": "Pengalaman ({count}):", "en": "Experience ({count}):"},
    "education_list": {"id": "Pendidikan ({count}):", "en": "Education ({count}):"},
    "mading": {
        "id": "Ada {count} pesan di mading. Pesan terbaru dari {author}: \"{snippet}\"",
        "en": "There are {count} messages on the board. Latest from {author}: \"{snippet}\"",
    },
    "mading_empty": {"id": "Belum ada pesan di mading.", "en": "There are no messages on the board yet."},
    "ongoing": {"id": "sedang berlangsung", "en": "ongoing"},
    "completed": {"id": "selesai", "en": "completed"},
    "no_description": {"id": "Tidak ada deskripsi.", "en": "No description."},
}


def _t(key, lang, **kwargs):
    return TEXT[key][lang].format(**kwargs)


def normalize(text):
    text = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    return re.sub(r"\s+", " ", text).strip()


def _keyword_hit(keyword, text, tokens):
    if " " in keyword:
        return keyword in text
    if keyword in tokens:
        return True
    return len(keyword) >= 5 and any(token.startswith(keyword) for token in tokens)


def detect_intent(text):
    """Kembalikan topik dengan skor tertinggi, atau None."""
    tokens = set(text.split())
    scores = {
        intent: sum(_keyword_hit(kw, text, tokens) for kw in kws)
        for intent, kws in KEYWORDS.items()
    }
    best = max(scores.values(), default=0)
    if best == 0:
        return None
    for intent in PRIORITY:
        if scores[intent] == best:
            return intent
    return None


def _content_tokens(text):
    """Token pencarian: bukan stopword dan bukan kata kunci topik."""
    all_keywords = {kw for kws in KEYWORDS.values() for kw in kws}
    return [t for t in text.split() if len(t) >= 3 and t not in STOPWORDS and t not in all_keywords]


def _year(dt):
    return dt.year if dt else None


def _overlap(tokens, title):
    """Jumlah token pencarian yang menjadi awalan salah satu kata pada judul."""
    words = normalize(title).split()
    return sum(any(word.startswith(token) for word in words) for token in tokens)


def _find_entity(tokens, intent):
    """Cari experience/education yang judul/institusinya memuat token pencarian."""
    if not tokens:
        return None
    best, best_score = None, 0
    if intent in (None, "experience"):
        for exp in Experience.objects.all():
            score = _overlap(tokens, exp.title)
            if score > best_score:
                best, best_score = ("experience", exp), score
    if intent in (None, "education"):
        for edu in Education.objects.all():
            score = _overlap(tokens, f"{edu.institution} {edu.Activity}")
            if score > best_score:
                best, best_score = ("education", edu), score
    return best


def _entity_answer(kind, obj, lang):
    status = _t("ongoing" if obj.is_ongoing else "completed", lang)
    if kind == "experience":
        desc = (obj.description or "").strip() or _t("no_description", lang)
        return f"{obj.title} ({obj.get_category_display()}, {_year(obj.started_at)}, {status}). {desc[:300]}"
    return f"{obj.Activity} - {obj.institution} ({_year(obj.started_at)}, {status})."


def _list_answer(intent, lang):
    if intent == "experience":
        items = list(Experience.objects.all().order_by("-started_at")[:5])
        total = Experience.objects.count()
        header_key = "experience_list"
        lines = [f"- {e.title} ({e.get_category_display()}, {_year(e.started_at)})" for e in items]
    else:
        items = list(Education.objects.all().order_by("-started_at")[:5])
        total = Education.objects.count()
        header_key = "education_list"
        lines = [f"- {e.Activity} - {e.institution} ({_year(e.started_at)})" for e in items]
    if not items:
        return None
    return "\n".join([_t(header_key, lang, count=total)] + lines)


def _mading_answer(lang):
    latest = Mading.objects.order_by("-created_at").first()
    if latest is None:
        return _t("mading_empty", lang)
    snippet = latest.message.strip().replace("\n", " ")
    if len(snippet) > 80:
        snippet = snippet[:77] + "..."
    return _t("mading", lang, count=Mading.objects.count(), author=latest.name, snippet=snippet)


def get_answer(question, lang="id"):
    """Kembalikan dict {answer, found, suggestions}. Tidak pernah memantulkan teks pertanyaan."""
    lang = "en" if lang == "en" else "id"
    text = normalize((question or "")[:MAX_QUERY_LENGTH])
    intent = detect_intent(text) if text else None
    if intent == "who":
        # "siapa presiden amerika" bukan tentang pemilik portofolio; hanya nama pemilik yang boleh tersisa.
        owner_words = set(normalize(PROFILE["name"]).split())
        if any(token not in owner_words for token in _content_tokens(text)):
            intent = None
    answer = None

    if intent in (None, "experience", "education"):
        entity = _find_entity(_content_tokens(text), intent)
        if entity:
            answer = _entity_answer(entity[0], entity[1], lang)

    if answer is None and intent in ("experience", "education"):
        answer = _list_answer(intent, lang)
    elif answer is None and intent == "mading":
        answer = _mading_answer(lang)
    elif answer is None and intent in TEXT:
        answer = _t(intent, lang, **PROFILE)

    found = answer is not None
    return {
        "answer": answer if found else _t("unavailable", lang),
        "found": found,
        "suggestions": [] if found else SUGGESTIONS[lang],
    }
