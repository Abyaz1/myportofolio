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

    setView(currentView);

    const config = window.APP_CONFIG || {};
    const csrfToken = config.csrfToken || '';
    const isSuperuser = !!config.isSuperuser;
    const isAuthenticated = !!(config.isAuthenticated ?? isSuperuser);
    const isEditor = !!config.isEditor;
    const currentUsername = config.currentUsername || '';

    const listUrl = (config.endpoints && config.endpoints.list) || '/api/v1/experiences/';
    const detailPattern = (config.endpoints && config.endpoints.detail) || '/api/v1/experiences/00000000-0000-0000-0000-000000000000/';
    const starPattern = (config.endpoints && config.endpoints.star) || '/api/v1/experiences/00000000-0000-0000-0000-000000000000/star/';

    const categoryMap = {
        'internship': 'Internship',
        'research': 'Research',
        'volunteer': 'Volunteer',
        'part-time': 'Part-Time',
        'full-time': 'Full-Time',
        'freelance': 'Freelance',
    };

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

    function getCookie(name) {
        const prefix = `${name}=`;
        const cookie = document.cookie.split(';').map(v => v.trim()).find(v => v.startsWith(prefix));
        return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
    }

    function endpointWithId(pattern, id) {
        return pattern.replace('00000000-0000-0000-0000-000000000000', id);
    }

    function apiErrorMessage(data, status) {
        const messages = Object.values(data).flat().filter(v => typeof v === 'string');
        return messages.join(' ') || `Request failed (HTTP ${status}).`;
    }

    async function writeExperience(url, method, payload) {
        const response = await fetch(url, {
            method,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') || csrfToken,
            },
            body: payload === undefined ? undefined : JSON.stringify(payload),
        });
        if (response.status === 204) return null;
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(apiErrorMessage(data, response.status));
        return data;
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
        const names = item.starred_by_names || (Array.isArray(starredUsers) ? starredUsers.join(', ') : '');
        const starTitle = starCount > 0 && names
            ? `${t('star.by', 'Dibintangi oleh')} ${names}`
            : (starCount > 0 ? `${t('star.by', 'Dibintangi oleh')} (${starCount})` : t('star.be_first', 'Jadilah yang pertama memberi star'));

        const editBtn = t('btn.edit', 'Ubah');
        const deleteBtn = t('btn.delete', 'Hapus');
        const cancelBtn = t('btn.cancel', 'Batal');
        const confirmDeleteBtn = t('btn.confirm_delete', 'Ya, Hapus');
        const deleteTitle = t('modal.delete_exp_title', 'Hapus Experience?');
        const confirmPrompt = t('modal.confirm_p1', 'Apakah Anda yakin ingin menghapus');

        const thumbnailHtml = thumbnail
            ? `<img src="${escapeHtml(thumbnail)}" alt="Gambar ${escapeHtml(title)}" class="project-image">`
            : '';

        let actionsHtml = '';
        if (isAuthenticated) {
            actionsHtml += `
                <button type="button"
                        class="button button-star${isStarred ? ' is-starred' : ''}"
                        data-action="star"
                        data-id="${escapeHtml(id)}"
                        title="${escapeHtml(starTitle)}">
                    <span aria-hidden="true">★</span>
                    ${isStarred ? 'Unstar' : 'Star'}
                    <span class="star-count">${starCount}</span>
                </button>
            `;
        } else {
            actionsHtml += `
                <a href="/login/"
                   class="button button-star"
                   title="${escapeHtml(starTitle)}">
                    <span aria-hidden="true">★</span>
                    Star
                    <span class="star-count">${starCount}</span>
                </a>
            `;
        }

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
                            <button type="button"
                                    class="button button-danger"
                                    data-action="delete"
                                    data-id="${escapeHtml(id)}">${escapeHtml(confirmDeleteBtn)}</button>
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
            const url = new URL(listUrl, window.location.origin);
            if (query) url.searchParams.set('title', query);
            const response = await fetch(url, {
                headers: { 'Accept': 'application/json' },
                signal: currentController.signal,
            });

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

    function searchExperiences() {
        fetchExperiences(searchInput.value.trim());
    }

    searchInput.addEventListener('input', function () {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(function () {
            searchExperiences();
        }, SEARCH_DEBOUNCE_DELAY);
    });

    searchForm.addEventListener('submit', function (event) {
        event.preventDefault();
        clearTimeout(searchDebounceTimer);
        searchExperiences();
    });

    gridElement.addEventListener('click', async function (event) {
        const button = event.target.closest('button[data-action]');
        if (!button || button.disabled) return;
        const action = button.dataset.action;
        const id = button.dataset.id;
        if (!id) return;

        button.disabled = true;
        try {
            if (action === 'star') {
                await writeExperience(endpointWithId(starPattern, id), 'POST');
                if (typeof showToast === 'function') {
                    showToast('Success', 'Star updated.', 'success');
                }
                await fetchExperiences(searchInput.value.trim());
            } else if (action === 'delete') {
                const modal = document.getElementById(`delete-experience-${id}`);
                if (modal && typeof modal.hidePopover === 'function') {
                    modal.hidePopover();
                }
                await writeExperience(endpointWithId(detailPattern, id), 'DELETE');
                if (typeof showToast === 'function') {
                    showToast('Success', 'Experience deleted.', 'success');
                }
                await fetchExperiences(searchInput.value.trim());
            }
        } catch (error) {
            if (typeof showToast === 'function') {
                showToast('Request failed', error.message, 'error');
            }
        } finally {
            button.disabled = false;
        }
    });

    function closeExperienceModal() {
        const modal = document.getElementById('add-experience-modal');
        if (modal && typeof modal.hidePopover === 'function') {
            modal.hidePopover();
        }
    }
    window.closeExperienceModal = closeExperienceModal;
    window.writeExperience = writeExperience;
    window.fetchExperiences = fetchExperiences;

    if (experienceForm) {
        experienceForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const submitBtn = experienceForm.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = true;

            try {
                const fields = new FormData(experienceForm);
                const payload = Object.fromEntries([
                    'title', 'description', 'category', 'thumbnail',
                ].map(name => [name, fields.get(name) || '']));

                await writeExperience(listUrl, 'POST', payload);
                experienceForm.reset();
                closeExperienceModal();
                if (typeof showToast === 'function') {
                    showToast('Success', 'Experience created.', 'success');
                }
                await fetchExperiences(searchInput.value.trim());
            } catch (err) {
                if (typeof showToast === 'function') {
                    showToast('Could not create experience', err.message, 'error');
                }
            } finally {
                if (submitBtn) submitBtn.disabled = false;
            }
        });
    }

    searchExperiences();
});
