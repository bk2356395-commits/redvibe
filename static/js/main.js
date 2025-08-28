// Helper: get csrf token from cookie
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
}
const CSRF = getCookie('csrftoken');

// Age modal
document.addEventListener('DOMContentLoaded', () => {
  const shouldShow = document.body.getAttribute('data-show-age') === 'true';
  const modalEl = document.getElementById('ageModal');
  if (shouldShow && modalEl) {
    const modal = new bootstrap.Modal(modalEl, {backdrop: 'static', keyboard: false});
    modal.show();
    document.getElementById('ageAcceptBtn').addEventListener('click', () => {
      fetch('/confirm-age/', {
        method: 'POST',
        headers: {'X-CSRFToken': CSRF, 'Content-Type': 'application/json'},
        body: JSON.stringify({confirmed: true})
      }).then(() => modal.hide());
    });
  }

  // Like buttons
  document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.id;
      fetch(`/like/${id}/`, {method: 'POST', headers: {'X-CSRFToken': CSRF}})
        .then(r => r.json())
        .then(data => {
          if (data.liked) btn.textContent = 'Unlike';
          else btn.textContent = '❤️ Like';
          const countEl = document.querySelector(`.like-count[data-id="${id}"]`);
          if (countEl) countEl.textContent = data.count;
        });
    });
  });

  // Comment forms
  document.querySelectorAll('.comment-form').forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const id = form.dataset.id;
      const fd = new FormData(form);
      fetch(`/comment/${id}/`, {method: 'POST', headers: {'X-CSRFToken': CSRF}, body: fd})
        .then(r => r.json())
        .then(data => {
          if (data.ok) {
            form.reset();
            // Optionally update comment count on page reload; quick toast:
            alert('Comment posted!');
            location.reload();
          } else {
            alert('Error posting comment');
          }
        });
    });
  });

  // Follow buttons
  document.querySelectorAll('.follow-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const uid = btn.dataset.user;
      fetch(`/follow/${uid}/`, {method: 'POST', headers: {'X-CSRFToken': CSRF}})
        .then(r => r.json()).then(data => {
          if (data.ok) btn.textContent = data.following ? 'Unfollow' : 'Follow';
        });
    });
  });

  // Report buttons
  document.querySelectorAll('.report-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      const reason = prompt('Select reason: Nudity / Violence / Spam / Other', 'Spam');
      if (!reason) return;
      const details = prompt('Provide more details (optional)', '');
      const fd = new FormData();
      fd.append('reason', reason);
      fd.append('details', details || '');
      const resp = await fetch(`/report/${id}/`, {method: 'POST', headers: {'X-CSRFToken': CSRF}, body: fd});
      const data = await resp.json();
      if (data.ok) alert(data.message);
      else alert('Report failed');
    });
  });
});
