document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.getElementById('experience-search-form') || document.getElementById('search-form');
    const searchInput = document.getElementById('experience-search-input') || document.getElementById('search-input');
    const SEARCH_DEBOUNCE_DELAY = 300;
    let searchDebounceTimer;
    const loadingElement = document.getElementById('experience-loading-state') || document.getElementById('loading-state');
    const errorElement = document.getElementById('experience-error-state') || document.getElementById('error-state');
    const emptyElement = document.getElementById('experience-empty-state') || document.getElementById('empty-state');
    const gridElement = document.getElementById('experience-grid') || document.getElementById('project-grid');
    const experienceForm = document.getElementById('experience-form');

    const timelineBtn = document.getElementById('experience-view-timeline');
    const gridBtn = document.getElementById('experience-view-grid');

    if (!searchForm || !searchInput || !gridElement) return;

    let currentView = localStorage.getItem('portfolio_experience_view') || 'timeline';

    function setView(view) {
        currentView = view;
        try {
            localStorage.setItem('portfolio_experience_view', view);
        } catch (e) {}

        if (view === 'grid') {
            gridElement.classList.add('is-grid');
            gridElement.classList.remove('is-timeline');
            if (gridBtn) gridBtn.classList.add('is-active');
            if (timelineBtn) timelineBtn.classList.remove('is-active');
        } else {
            gridElement.classList.add('is-timeline');
            gridElement.classList.remove('is-grid');
            if (timelineBtn) timelineBtn.classList.add('is-active');
            if (gridBtn) gridBtn.classList.remove('is-active');
        }
    }

    if (timelineBtn) {
        timelineBtn.addEventListener('click', function () {
            setView('timeline');
        });
    }
    if (gridBtn) {
        gridBtn.addEventListener('click', function () {
            setView('grid');
        });
    }

    // Set initial view mode
    setView(currentView);

    const config = window.APP_CONFIG || {};
    const csrfToken = config.csrfToken || '';
    const isSuperuser = !!config.isSuperuser;
    const isEditor = !!config.isEditor;
    const currentUsername = config.currentUsername || '';

    const categoryMap = {
        'internship': 'Internship',
        'research': 'Research',
        'volunteer': 'Volunteer',
        'part-time': 'Part-Time',
        'full-time': 'Full-Time',
        'freelance': 'Freelance',
    };

    // Mengubah karakter khusus HTML menjadi entity agar ditampilkan sebagai teks (XSS Protection)
    function escapeHtml(value) {
        return String(value ?? '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#39;');
    }

    function t(key, fallback = '') {
        if (window.portfolioI18n && typeof window.portfolioI18n.t === 'function') {
            return window.portfolioI18n.t(key, fallback);
        }
        return fallback;
    }

    function formatPeriod(startedAt, endedAt, isOngoing) {
        const presentLabel = t('period.present', 'Sekarang');
        if (!startedAt) {
            return isOngoing ? t('status.ongoing', 'Sedang berlangsung') : t('status.ended', 'Selesai');
        }
        try {
            const lang = window.portfolioI18n && typeof window.portfolioI18n.getLang === 'function'
                ? window.portfolioI18n.getLang() : 'id';
            const locale = lang === 'en' ? 'en-US' : 'id-ID';
            const startDate = new Date(startedAt);
            const startStr = startDate.toLocaleDateString(locale, { month: 'short', year: 'numeric' });
            if (isOngoing || !endedAt) {
                return `${startStr} — ${presentLabel}`;
            }
            const endDate = new Date(endedAt);
            const endStr = endDate.toLocaleDateString(locale, { month: 'short', year: 'numeric' });
            return `${startStr} — ${endStr}`;
        } catch (e) {
            return isOngoing ? t('status.ongoing', 'Sedang berlangsung') : t('status.ended', 'Selesai');
        }
    }

    function displayPageSection({ showLoading = false, showError = false, showEmpty = false, showGrid = false } = {}) {
        if (loadingElement) loadingElement.classList.toggle('hide', !showLoading);
        if (errorElement) errorElement.classList.toggle('hide', !showError);
        if (emptyElement) emptyElement.classList.toggle('hide', !showEmpty);
        if (gridElement) gridElement.classList.toggle('hide', !showGrid);
    }

    function buildExperienceCardElement(item, index = 0) {
        const itemWrapper = document.createElement('div');
        const isLeft = index % 2 === 0;
        itemWrapper.className = `timeline-item ${isLeft ? 'timeline-item-left' : 'timeline-item-right'}`;

        const id = item.id || item.pk;
        const title = item.title || (item.fields && item.fields.title) || '';
        const description = item.description || (item.fields && item.fields.description) || '';
        const rawCategory = item.category || (item.fields && item.fields.category) || '';
        const categoryText = item.category_display || categoryMap[rawCategory] || rawCategory;
        const isOngoing = item.is_ongoing !== undefined ? item.is_ongoing : !(item.fields && item.fields.ended_at);
        const statusText = isOngoing ? t('status.ongoing', 'Sedang berlangsung') : t('status.ended', 'Selesai');
        const thumbnail = item.thumbnail !== undefined ? item.thumbnail : (item.fields && item.fields.thumbnail);
        const startedAt = item.started_at || (item.fields && item.fields.started_at);
        const endedAt = item.ended_at || (item.fields && item.fields.ended_at);
        const periodText = formatPeriod(startedAt, endedAt, isOngoing);

        const starredUsers = item.starred_by || (item.fields && item.fields.starred_by) || [];
        const starCount = item.star_count !== undefined ? item.star_count : starredUsers.length;
        const isStarred = item.is_starred !== undefined ? item.is_starred : (currentUsername && starredUsers.includes(currentUsername));
        const starTitle = starCount > 0
            ? `${t('star.by', 'Dibintangi oleh')} ${starredUsers.join(', ')}`
            : t('star.be_first', 'Jadilah yang pertama memberi star');

        const editBtn = t('btn.edit', 'Ubah');
        const deleteBtn = t('btn.delete', 'Hapus');
        const cancelBtn = t('btn.cancel', 'Batal');
        const confirmDeleteBtn = t('btn.confirm_delete', 'Ya, Hapus');
        const deleteTitle = t('modal.delete_exp_title', 'Hapus Experience?');
        const confirmPrompt = t('modal.confirm_p1', 'Apakah Anda yakin ingin menghapus');

        const thumbnailHtml = thumbnail
            ? `<img src="${escapeHtml(thumbnail)}" alt="Gambar ${escapeHtml(title)}" class="project-image">`
            : '';

        let actionsHtml = `
            <form method="post" action="/experience/${id}/star/" class="star-form">
                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                <button type="submit"
                        class="button button-star${isStarred ? ' is-starred' : ''}"
                        title="${escapeHtml(starTitle)}">
                    <span aria-hidden="true">★</span>
                    ${isStarred ? 'Unstar' : 'Star'}
                    <span class="star-count">${starCount}</span>
                </button>
            </form>
        `;

        if (isSuperuser || isEditor) {
            actionsHtml += `<a href="/experience/${id}/edit/" class="button button-secondary">${escapeHtml(editBtn)}</a>\n`;
        }

        if (isSuperuser) {
            actionsHtml += `
                <button type="button"
                        class="button button-danger"
                        popovertarget="delete-experience-${id}"
                        aria-label="${escapeHtml(deleteBtn)} ${escapeHtml(title)}"
                        title="${escapeHtml(deleteBtn)} experience">
                    ${escapeHtml(deleteBtn)}
                </button>
                <div id="delete-experience-${id}"
                     class="project-delete-modal"
                     popover="auto"
                     role="dialog"
                     aria-modal="true"
                     aria-labelledby="delete-experience-title-${id}">
                    <button type="button"
                            class="project-delete-modal__backdrop"
                            popovertarget="delete-experience-${id}"
                            popovertargetaction="hide"
                            aria-label="Tutup konfirmasi hapus"></button>
                    <div class="project-delete-modal__content">
                        <button type="button"
                                class="project-delete-modal__close"
                                popovertarget="delete-experience-${id}"
                                popovertargetaction="hide"
                                aria-label="Tutup konfirmasi hapus">×</button>
                        <h2 id="delete-experience-title-${id}">${escapeHtml(deleteTitle)}</h2>
                        <p>
                            ${escapeHtml(confirmPrompt)}
                            <strong>${escapeHtml(title)}</strong>?
                        </p>
                        <div class="project-delete-modal__actions">
                            <button type="button"
                                    class="button button-secondary"
                                    popovertarget="delete-experience-${id}"
                                    popovertargetaction="hide">${escapeHtml(cancelBtn)}</button>
                            <form method="post" action="/experience/${id}/delete/">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                <button type="submit" class="button button-danger">${escapeHtml(confirmDeleteBtn)}</button>
                            </form>
                        </div>
                    </div>
                </div>
            `;
        }

        const markerHtml = `
            <div class="timeline-marker ${isOngoing ? 'is-ongoing' : ''}" aria-hidden="true" title="${escapeHtml(statusText)}">
                <svg class="timeline-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                </svg>
            </div>
        `;

        itemWrapper.innerHTML = `
            ${markerHtml}
            <article class="experience-card timeline-card">
                <div>
                    <div class="timeline-card-header">
                        <span class="experience-category">${escapeHtml(categoryText)}</span>
                        <span class="timeline-period-badge">
                            <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                <circle cx="12" cy="12" r="10"></circle>
                                <polyline points="12 6 12 12 16 14"></polyline>
                            </svg>
                            ${escapeHtml(periodText)}
                        </span>
                    </div>
                    ${thumbnailHtml}
                    <h2>${escapeHtml(title)}</h2>
                    <p class="experience-description">${escapeHtml(description)}</p>
                </div>
                <div class="project-card-actions">
                    <p class="experience-status">${escapeHtml(statusText)}</p>
                    <div class="project-actions">
                        ${actionsHtml}
                    </div>
                </div>
            </article>
        `;

        return itemWrapper;
    }

    let currentController = null;
    let currentData = [];

    function renderExperienceList(data) {
        currentData = data || [];
        gridElement.innerHTML = '';

        if (currentData.length === 0) {
            if (emptyElement && emptyElement.querySelector('p')) {
                const query = searchInput.value.trim();
                emptyElement.querySelector('p').textContent = query
                    ? t('state.empty_search.exp', 'Tidak ada experience dengan nama tersebut.')
                    : t('state.empty.exp', 'Belum ada pengalaman yang ditambahkan.');
            }
            displayPageSection({ showEmpty: true });
        } else {
            const startCap = document.createElement('div');
            startCap.className = 'timeline-cap timeline-start-cap';
            startCap.innerHTML = `<span class="timeline-cap-badge">${escapeHtml(t('timeline.latest', 'Terbaru / Sekarang'))}</span>`;
            gridElement.appendChild(startCap);

            currentData.forEach((item, index) => {
                const card = buildExperienceCardElement(item, index);
                gridElement.appendChild(card);
            });

            const endCap = document.createElement('div');
            endCap.className = 'timeline-cap timeline-end-cap';
            endCap.innerHTML = `<span class="timeline-cap-badge">${escapeHtml(t('timeline.start.exp', 'Awal Pengalaman'))}</span>`;
            gridElement.appendChild(endCap);

            displayPageSection({ showGrid: true });
        }
    }

    window.addEventListener('portfolio:langchange', function () {
        if (currentData && currentData.length > 0) {
            renderExperienceList(currentData);
        }
    });

    async function fetchExperiences(query = '') {
        if (currentController) {
            currentController.abort();
        }
        currentController = new AbortController();

        displayPageSection({ showLoading: true });

        try {
            const url = `/api/experiences/?title=${encodeURIComponent(query)}`;
            const response = await fetch(url, { signal: currentController.signal });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            renderExperienceList(data);
        } catch (error) {
            if (error.name === 'AbortError') return;
            console.error('Error loading experiences:', error);
            displayPageSection({ showError: true });
        }
    }

    // Event Handlers untuk Form Search
    function searchExperiences() {
        fetchExperiences(searchInput.value.trim());
    }

    searchInput.addEventListener('input', function() {
        clearTimeout(searchDebounceTimer);

        searchDebounceTimer = setTimeout(function() {
            searchExperiences();
        }, SEARCH_DEBOUNCE_DELAY);
    });

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        clearTimeout(searchDebounceTimer);
        searchExperiences();
    });

    function closeExperienceModal() {
        const modal = document.getElementById('add-experience-modal');
        if (modal && typeof modal.hidePopover === 'function') {
            modal.hidePopover();
        }
    }
    window.closeExperienceModal = closeExperienceModal;

    // Event Handler untuk Form Tambah Experience AJAX
    if (experienceForm) {
        experienceForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const submitBtn = experienceForm.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = true;

            try {
                const response = await fetch(experienceForm.action, {
                    method: 'POST',
                    body: new FormData(experienceForm),
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                const data = await response.json();

                if (response.ok && data.status === 'success') {
                    experienceForm.reset();
                    closeExperienceModal();
                    if (typeof showToast === 'function') {
                        showToast('Berhasil', data.message || 'Experience baru berhasil ditambahkan!', 'success');
                    }
                    searchExperiences();
                } else {
                    let errorMsg = data.message || 'Gagal menambahkan experience.';
                    if (data.errors && typeof data.errors === 'object') {
                        const errorDetails = Object.values(data.errors)
                            .flat()
                            .map(err => (typeof err === 'object' && err.message) ? err.message : String(err))
                            .join(', ');
                        if (errorDetails) {
                            errorMsg += `: ${errorDetails}`;
                        }
                    }
                    if (typeof showToast === 'function') {
                        showToast('Gagal', errorMsg, 'error');
                    } else {
                        alert(errorMsg);
                    }
                }
            } catch (err) {
                console.error('Error submitting experience form:', err);
                if (typeof showToast === 'function') {
                    showToast('Gagal', 'Terjadi kesalahan sistem saat menyimpan data.', 'error');
                }
            } finally {
                if (submitBtn) submitBtn.disabled = false;
            }
        });
    }

    // Start application
    searchExperiences();
});
