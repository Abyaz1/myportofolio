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

    if (!searchForm || !searchInput || !gridElement) return;

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

    function displayPageSection({ showLoading = false, showError = false, showEmpty = false, showGrid = false } = {}) {
        if (loadingElement) loadingElement.classList.toggle('hide', !showLoading);
        if (errorElement) errorElement.classList.toggle('hide', !showError);
        if (emptyElement) emptyElement.classList.toggle('hide', !showEmpty);
        if (gridElement) gridElement.classList.toggle('hide', !showGrid);
    }

    function buildExperienceCardElement(item) {
        const article = document.createElement('article');
        article.className = 'experience-card';

        const categoryText = categoryMap[item.fields.category] || item.fields.category;
        const isOngoing = !item.fields.ended_at;
        const statusText = isOngoing ? 'Sedang berlangsung' : 'Selesai';

        const starredUsers = (item.fields.starred_by || []).map(u => Array.isArray(u) ? u[0] : u);
        const starCount = starredUsers.length;
        const isStarred = currentUsername && starredUsers.includes(currentUsername);
        const starTitle = starCount > 0
            ? `Dibintangi oleh ${starredUsers.join(', ')}`
            : 'Jadilah yang pertama memberi star';

        const thumbnailHtml = item.fields.thumbnail
            ? `<img src="${escapeHtml(item.fields.thumbnail)}" alt="Gambar ${escapeHtml(item.fields.title)}" class="project-image">`
            : '';

        let actionsHtml = `
            <form method="post" action="/experience/${item.pk}/star/" class="star-form">
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
            actionsHtml += `<a href="/experience/${item.pk}/edit/" class="button button-secondary">Ubah</a>\n`;
        }

        if (isSuperuser) {
            actionsHtml += `
                <button type="button"
                        class="button button-danger"
                        popovertarget="delete-experience-${item.pk}"
                        aria-label="Hapus ${escapeHtml(item.fields.title)}"
                        title="Hapus experience">
                    Hapus
                </button>
                <div id="delete-experience-${item.pk}"
                     class="project-delete-modal"
                     popover="auto"
                     role="dialog"
                     aria-modal="true"
                     aria-labelledby="delete-experience-title-${item.pk}">
                    <button type="button"
                            class="project-delete-modal__backdrop"
                            popovertarget="delete-experience-${item.pk}"
                            popovertargetaction="hide"
                            aria-label="Tutup konfirmasi hapus"></button>
                    <div class="project-delete-modal__content">
                        <button type="button"
                                class="project-delete-modal__close"
                                popovertarget="delete-experience-${item.pk}"
                                popovertargetaction="hide"
                                aria-label="Tutup konfirmasi hapus">×</button>
                        <h2 id="delete-experience-title-${item.pk}">Hapus Experience?</h2>
                        <p>
                            Apakah Anda yakin ingin menghapus
                            <strong>${escapeHtml(item.fields.title)}</strong>?
                        </p>
                        <div class="project-delete-modal__actions">
                            <button type="button"
                                    class="button button-secondary"
                                    popovertarget="delete-experience-${item.pk}"
                                    popovertargetaction="hide">Batal</button>
                            <form method="post" action="/experience/${item.pk}/delete/">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                <button type="submit" class="button button-danger">Ya, Hapus</button>
                            </form>
                        </div>
                    </div>
                </div>
            `;
        }

        article.innerHTML = `
            <div>
                ${thumbnailHtml}
                <span class="experience-category">${escapeHtml(categoryText)}</span>
                <h2>${escapeHtml(item.fields.title)}</h2>
                <p class="experience-description">${escapeHtml(item.fields.description)}</p>
            </div>
            <div class="project-card-actions">
                <p class="experience-status">${escapeHtml(statusText)}</p>
                <div class="project-actions">
                    ${actionsHtml}
                </div>
            </div>
        `;

        return article;
    }

    let currentController = null;

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

            gridElement.innerHTML = '';

            if (data.length === 0) {
                if (emptyElement && emptyElement.querySelector('p')) {
                    emptyElement.querySelector('p').textContent = query
                        ? 'Tidak ada experience dengan nama tersebut.'
                        : 'Belum ada pengalaman yang ditambahkan.';
                }
                displayPageSection({ showEmpty: true });
            } else {
                data.forEach(item => {
                    const card = buildExperienceCardElement(item);
                    gridElement.appendChild(card);
                });
                displayPageSection({ showGrid: true });
            }
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
                    const errorMsg = data.message || 'Gagal menambahkan experience.';
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
