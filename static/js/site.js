// Tema (dark/light) dan bahasa (ID/EN).
(function () {
    const EN = {
        'nav.profile': 'Profile',
        'nav.experience': 'Experience',
        'nav.education': 'Education',
        'nav.mading': 'Message Board',
        'nav.logout': 'Logout',
        'nav.login': 'Login',
        'nav.register': 'Register',
        'footer.faculty': 'Faculty of Computer Science, Universitas Indonesia.',
        'hero.kicker': 'Computer Science · Universitas Indonesia',
        'bio': 'Computer Science student at Universitas Indonesia interested in Data Science and Artificial Intelligence.',
        'meta.npm': 'Student ID',
        'meta.program': 'Program',
        'meta.lastlogin': 'Last Login Session',
        'meta.nologin': 'No login session / cookie not found',
        'skills.title': 'Skills & Interests',
        'skills.ds': 'Data Science',
        'skills.ds.desc': 'Experience with data analysis, visualization, and statistical modeling.',
        'skills.ai': 'AI / ML',
        'skills.ai.desc': 'Knowledge of machine learning algorithms, deep learning, and neural networks.',
        'skills.web': 'Web Development',
        'skills.web.desc': 'Proficient in building responsive web apps with HTML, CSS, JavaScript, and Django.',
        'mading.title': 'Message Board',
        'mading.kicker': 'Leave a mark, a message, or an impression here',
        'mading.name': 'Your Name',
        'mading.message': 'Message',
        'mading.post': 'Post Message to Board',
        'mading.empty': 'No messages yet. Be the first to post!',
        'experience.kicker': 'My journey so far',
        'education.kicker': 'My education so far',
        'view.timeline': 'Timeline',
        'view.grid': 'Grid',
        'search.btn': 'Search',
        'search.exp': 'Search by experience name',
        'search.edu': 'Search by institution or activity',
        'add.exp': 'Add Experience',
        'add.edu': 'Add Education',
        'state.error': 'Something went wrong while loading data. Please try again.',
        'state.loading.exp': 'Loading experiences...',
        'state.empty.exp': 'No experiences added yet.',
        'state.empty_search.exp': 'No experiences found matching that name.',
        'state.loading.edu': 'Loading education...',
        'state.empty.edu': 'No education added yet.',
        'state.empty_search.edu': 'No education found matching that name.',
        'status.ongoing': 'In progress',
        'status.ended': 'Completed',
        'timeline.latest': 'Latest / Present',
        'timeline.start.exp': 'Beginning of Experience',
        'timeline.start.edu': 'Beginning of Education',
        'period.present': 'Present',
        'btn.edit': 'Edit',
        'btn.delete': 'Delete',
        'btn.cancel': 'Cancel',
        'btn.confirm_delete': 'Yes, Delete',
        'modal.delete_exp_title': 'Delete Experience?',
        'modal.delete_edu_title': 'Delete Education?',
        'modal.confirm_p1': 'Are you sure you want to delete',
        'category.academic': 'Academic',
        'star.be_first': 'Be the first to star',
        'star.by': 'Starred by'
    };

    const root = document.documentElement;
    const store = {
        get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
        set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
    };

    let lang = store.get('portfolio_lang') === 'en' ? 'en' : 'id';

    window.portfolioI18n = {
        t(key, fallback = '') {
            if (lang === 'en' && EN[key]) return EN[key];
            return fallback;
        },
        getLang() {
            return lang;
        }
    };

    function applyLang() {
        root.lang = lang;
        document.querySelectorAll('[data-i18n]').forEach(function (el) {
            const key = el.dataset.i18n;
            if (!key) return;
            if (el.dataset.i18nId === undefined) el.dataset.i18nId = el.textContent.trim();
            el.textContent = lang === 'en' && EN[key] ? EN[key] : el.dataset.i18nId;
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
            if (el.dataset.i18nPhId === undefined) el.dataset.i18nPhId = el.getAttribute('placeholder') || '';
            const key = el.dataset.i18nPlaceholder;
            el.setAttribute('placeholder', lang === 'en' && EN[key] ? EN[key] : el.dataset.i18nPhId);
        });
        const btn = document.getElementById('lang-toggle');
        if (btn) btn.textContent = lang.toUpperCase();

        window.dispatchEvent(new CustomEvent('portfolio:langchange', { detail: { lang } }));
    }

    document.addEventListener('DOMContentLoaded', function () {
        const themeBtn = document.getElementById('theme-toggle');
        if (themeBtn) themeBtn.addEventListener('click', function () {
            const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            root.setAttribute('data-theme', next);
            store.set('portfolio_theme', next);
        });
        const langBtn = document.getElementById('lang-toggle');
        if (langBtn) langBtn.addEventListener('click', function () {
            lang = lang === 'id' ? 'en' : 'id';
            store.set('portfolio_lang', lang);
            applyLang();
        });
        applyLang();
    });
})();
