/* ============================================================
   GRAND AZURE — MAIN.JS  (utilities, modal, toast, nav)
   ============================================================ */

// ── Live Date ────────────────────────────────────────────────
function updateDate() {
  const el = document.getElementById('live-date');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleDateString('en-US', {
    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
  });
}
updateDate();
setInterval(updateDate, 60000);

// ── Sidebar Toggle ───────────────────────────────────────────
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// ── Modal ────────────────────────────────────────────────────
function openModal(title, bodyHTML, footerHTML = '') {
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalBody').innerHTML   = bodyHTML;
  document.getElementById('modalFooter').innerHTML = footerHTML;
  document.getElementById('mainModal').classList.add('modal-open');
  document.getElementById('modalOverlay').classList.add('modal-open');
}

function closeModal() {
  document.getElementById('mainModal').classList.remove('modal-open');
  document.getElementById('modalOverlay').classList.remove('modal-open');
}

// ── Toast ────────────────────────────────────────────────────
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// ── API helper ───────────────────────────────────────────────
async function api(url, method = 'GET', body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' }
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Status badge ─────────────────────────────────────────────
function badge(status) {
  return `<span class="badge badge-${status}">${status.replace(/_/g, ' ')}</span>`;
}

// ── Format currency ──────────────────────────────────────────
function fmtMoney(val) {
  return '$' + Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// ── Format date ──────────────────────────────────────────────
function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// ── Confirm dialog (quick inline) ───────────────────────────
function confirmAction(msg, onYes) {
  openModal('Confirm Action',
    `<p style="color:var(--text-secondary)">${msg}</p>`,
    `<button class="btn btn-outline" onclick="closeModal()">Cancel</button>
     <button class="btn btn-danger" onclick="(${onYes.toString()})(); closeModal()">Confirm</button>`
  );
}
