let toastTimer;

function showToast(title, message, type = 'normal', duration = 3000) {
  const toastComponent = document.getElementById('toast-component');
  const toastTitle = document.getElementById('toast-title');
  const toastMessage = document.getElementById('toast-message');

  if (!toastComponent) return;

  // Hapus class tipe sebelumnya
  toastComponent.classList.remove('toast-success', 'toast-error', 'toast-normal');

  // Terapkan class baru berdasarkan tipe
  if (type === 'success') {
      toastComponent.classList.add('toast-success');
  } else if (type === 'error') {
      toastComponent.classList.add('toast-error');
  } else {
      toastComponent.classList.add('toast-normal');
  }

  // Perbarui konten teks
  toastTitle.textContent = title;
  toastMessage.textContent = message;

  // Batalkan timer sebelumnya jika toast masih tampil
  clearTimeout(toastTimer);

  // Animasi muncul
  if (typeof toastComponent.showPopover === 'function') {
      if (!toastComponent.matches(':popover-open')) {
          toastComponent.showPopover();
          void toastComponent.offsetHeight; // paksa browser menghitung style agar transisi berjalan
      }
  } else {
      toastComponent.style.display = 'flex';
  }
  toastComponent.classList.remove('toast-hidden');
  toastComponent.classList.add('toast-show');

  // Animasi hilang otomatis
  toastTimer = setTimeout(() => {
      toastComponent.classList.remove('toast-show');
      toastComponent.classList.add('toast-hidden');
      toastTimer = setTimeout(() => {
          if (typeof toastComponent.hidePopover === 'function') {
              try {
                  toastComponent.hidePopover();
              } catch (e) {
                  // ignore if already hidden
              }
          } else {
              toastComponent.style.display = 'none';
          }
      }, 300);
  }, duration);
}
