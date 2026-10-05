// Chatbot sederhana: pertanyaan dikirim ke /api/chatbot/ (pencocokan kata kunci di server),
// jawaban ditampilkan dengan textContent agar aman dari XSS.
(function () {
    const fab = document.getElementById('chat-fab');
    const panel = document.getElementById('chat-panel');
    if (!fab || !panel) return;

    const log = document.getElementById('chat-log');
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');
    const suggest = document.getElementById('chat-suggest');
    const closeBtn = document.getElementById('chat-close');
    const endpoint = panel.dataset.endpoint;

    const QUESTIONS = {
        id: ['Siapa kamu?', 'Apa saja skill-nya?', 'Pengalaman apa saja?', 'Riwayat pendidikan?', 'Bagaimana cara menghubungi?'],
        en: ['Who are you?', 'What are the skills?', 'What experience is there?', 'Education history?', 'How can I contact?']
    };
    const TEXT = {
        id: {
            welcome: 'Halo! Saya Abyaz Bot. Silakan pilih pertanyaan di bawah atau ketik sendiri.',
            error: 'Terjadi kesalahan saat menghubungi server. Coba lagi.'
        },
        en: {
            welcome: "Hi! I'm Abyaz Bot. Pick a question below or type your own.",
            error: 'Something went wrong contacting the server. Please try again.'
        }
    };
    const lang = () => (window.portfolioI18n ? window.portfolioI18n.getLang() : 'id');

    // Teks biasa; hanya URL http(s) yang dijadikan tautan, semuanya lewat textContent/href.
    function fillText(el, text) {
        el.textContent = '';
        text.split(/(https?:\/\/[^\s,]*[^\s,.])/).forEach(function (part) {
            if (/^https?:\/\//.test(part)) {
                const a = document.createElement('a');
                a.href = part;
                a.textContent = part;
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
                el.appendChild(a);
            } else if (part) {
                el.appendChild(document.createTextNode(part));
            }
        });
    }

    function addMessage(text, who) {
        const el = document.createElement('div');
        el.className = 'chat-msg ' + who;
        fillText(el, text);
        log.appendChild(el);
        log.scrollTop = log.scrollHeight;
        return el;
    }

    function typingIndicator() {
        const el = document.createElement('div');
        el.className = 'chat-msg bot';
        el.innerHTML = '<span class="chat-typing"><i></i><i></i><i></i></span>';
        log.appendChild(el);
        log.scrollTop = log.scrollHeight;
        return el;
    }

    async function ask(question) {
        question = question.trim();
        if (!question) return;
        addMessage(question, 'user');
        const typing = typingIndicator();
        try {
            const url = `${endpoint}?q=${encodeURIComponent(question)}&lang=${lang()}`;
            const response = await fetch(url, { headers: { Accept: 'application/json' } });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            fillText(typing, data.answer);
            typing.classList.toggle('chat-miss', data.found === false);
        } catch (err) {
            fillText(typing, TEXT[lang()].error);
            typing.classList.add('chat-miss');
        }
        log.scrollTop = log.scrollHeight;
    }

    function renderChips() {
        suggest.textContent = '';
        QUESTIONS[lang()].forEach(function (q) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'chat-chip';
            btn.textContent = q;
            btn.addEventListener('click', function () { ask(q); });
            suggest.appendChild(btn);
        });
    }

    let welcomed = false;
    function open() {
        panel.classList.add('is-open');
        fab.setAttribute('aria-expanded', 'true');
        if (!welcomed) {
            welcomed = true;
            addMessage(TEXT[lang()].welcome, 'bot');
        }
        input.focus();
    }
    function close() {
        panel.classList.remove('is-open');
        fab.setAttribute('aria-expanded', 'false');
    }

    fab.addEventListener('click', function () { panel.classList.contains('is-open') ? close() : open(); });
    closeBtn.addEventListener('click', close);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const value = input.value;
        input.value = '';
        ask(value);
    });

    renderChips();
    window.addEventListener('portfolio:langchange', renderChips);
})();
