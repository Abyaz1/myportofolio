document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.getElementById('education-search-form');
    const searchInput = document.getElementById('education-search-input');
    const SEARCH_DEBOUNCE_DELAY = 300;
    let searchDebounceTimer;
    const loadingElement = document.getElementById('education-loading-state');
    const errorElement = document.getElementById('education-error-state');
    const emptyElement = document.getElementById('education-empty-state');
    const gridElement = document.getElementById('education-grid');
    const educationForm = document.getElementById('education-form');

    if (!searchForm || !searchInput || !gridElement) return;

    const config = window.APP_CONFIG || {};
    const csrfToken = config.csrfToken || '';
    const isSuperuser = !!config.isSuperuser;
    const isEditor = !!config.isEditor;
    const currentUsername = config.currentUsername || '';

    // Mengubah karakter khusus HTML menjadi entity agar aman dari XSS
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

    function buildEducationCardElement(item) {
        const article = document.createElement('article');
        article.className = 'education-card';

        const isOngoing = !item.fields.ended_at;
        const statusText = isOngoing ? 'Sedang berlangsung' : 'Selesai';

        const starredUsers = (item.fields.starred_by || []).map(u => Array.isArray(u) ? u[0] : u);
        const starCount = starredUsers.length;
        const isStarred = currentUsername && starredUsers.includes(currentUsername);
        const starTitle = starCount > 0
            ? `Dibintangi oleh ${starredUsers.join(', ')}`
            : 'Jadilah yang pertama memberi star';

        let actionsHtml = `
            <form method="post" action="/education/${item.pk}/star/" class="star-form">
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
            actionsHtml += `<a href="/education/${item.pk}/edit/" class="button button-secondary">Ubah</a>\n`;
        }

        if (isSuperuser) {
            actionsHtml += `
                <button type="button"
                        class="button button-danger"
                        popovertarget="delete-education-${item.pk}"
                        aria-label="Hapus ${escapeHtml(item.fields.institution)}"
                        title="Hapus pendidikan">
                    Hapus
                </button>
                <div id="delete-education-${item.pk}"
                     class="project-delete-modal"
                     popover="auto"
                     role="dialog"
                     aria-modal="true"
                     aria-labelledby="delete-education-title-${item.pk}">
                    <button type="button"
                            class="project-delete-modal__backdrop"
                            popovertarget="delete-education-${item.pk}"
                            popovertargetaction="hide"
                            aria-label="Tutup konfirmasi hapus"></button>
                    <div class="project-delete-modal__content">
                        <button type="button"
                                class="project-delete-modal__close"
                                popovertarget="delete-education-${item.pk}"
                                popovertargetaction="hide"
                                aria-label="Tutup konfirmasi hapus">×</button>
                        <h2 id="delete-education-title-${item.pk}">Hapus Pendidikan?</h2>
                        <p>
                            Apakah Anda yakin ingin menghapus
                            <strong>${escapeHtml(item.fields.institution)} - ${escapeHtml(item.fields.Activity)}</strong>?
                        </p>
                        <div class="project-delete-modal__actions">
                            <button type="button"
                                    class="button button-secondary"
                                    popovertarget="delete-education-${item.pk}"
                                    popovertargetaction="hide">Batal</button>
                            <form method="post" action="/education/${item.pk}/delete/">
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
                <span class="education-category">Akademik</span>
                <h2>${escapeHtml(item.fields.institution)}</h2>
                <p class="education-description">${escapeHtml(item.fields.Activity)}</p>
            </div>
            <div class="project-card-actions">
                <p class="education-status">${escapeHtml(statusText)}</p>
                <div class="project-actions">
                    ${actionsHtml}
                </div>
            </div>
        `;

        return article;
    }

    let currentController = null;

    async function fetchEducations(query = '') {
        if (currentController) {
            currentController.abort();
        }
        currentController = new AbortController();

        displayPageSection({ showLoading: true });

        try {
            const url = `/api/educations/?title=${encodeURIComponent(query)}`;
            const response = await fetch(url, { signal: currentController.signal });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            gridElement.innerHTML = '';

            if (data.length === 0) {
                if (emptyElement && emptyElement.querySelector('p')) {
                    emptyElement.querySelector('p').textContent = query
                        ? 'Tidak ada pendidikan dengan nama tersebut.'
                        : 'Belum ada pendidikan yang ditambahkan.';
                }
                displayPageSection({ showEmpty: true });
            } else {
                data.forEach(item => {
                    const card = buildEducationCardElement(item);
                    gridElement.appendChild(card);
                });
                displayPageSection({ showGrid: true });
            }
        } catch (error) {
            if (error.name === 'AbortError') return;
            console.error('Error loading educations:', error);
            displayPageSection({ showError: true });
        }
    }

    // Event Handlers untuk Form Search
    function searchEducations() {
        fetchEducations(searchInput.value.trim());
    }

    searchInput.addEventListener('input', function () {
        clearTimeout(searchDebounceTimer);

        searchDebounceTimer = setTimeout(function () {
            searchEducations();
        }, SEARCH_DEBOUNCE_DELAY);
    });

    searchForm.addEventListener('submit', function (event) {
        event.preventDefault();
        clearTimeout(searchDebounceTimer);
        searchEducations();
    });

    function closeEducationModal() {
        const modal = document.getElementById('add-education-modal');
        if (modal && typeof modal.hidePopover === 'function') {
            modal.hidePopover();
        }
    }
    window.closeEducationModal = closeEducationModal;

    // Event Handler untuk Form Tambah Pendidikan AJAX
    if (educationForm) {
        educationForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const submitBtn = educationForm.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = true;

            try {
                const response = await fetch(educationForm.action, {
                    method: 'POST',
                    body: new FormData(educationForm),
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                const data = await response.json();

                if (response.ok && data.status === 'success') {
                    educationForm.reset();
                    closeEducationModal();
                    if (typeof showToast === 'function') {
                        showToast('Berhasil', data.message || 'Pendidikan baru berhasil ditambahkan!', 'success');
                    }
                    searchEducations();
                } else {
                    const errorMsg = data.message || 'Gagal menambahkan pendidikan.';
                    if (typeof showToast === 'function') {
                        showToast('Gagal', errorMsg, 'error');
                    } else {
                        alert(errorMsg);
                    }
                }
            } catch (err) {
                console.error('Error submitting education form:', err);
                if (typeof showToast === 'function') {
                    showToast('Gagal', 'Terjadi kesalahan sistem saat menyimpan data.', 'error');
                }
            } finally {
                if (submitBtn) submitBtn.disabled = false;
            }
        });
    }

    // Start application
    searchEducations();
});
