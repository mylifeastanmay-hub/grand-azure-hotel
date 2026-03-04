/* Reservations JS */
let resData = [];

async function loadReservations() {
  const status = document.getElementById('filterStatus').value;
  const url = `/reservations/api${status ? `?status=${status}` : ''}`;
  try {
    resData = await api(url);
    renderReservations(resData);
  } catch (e) { showToast('Error: ' + e.message, 'error'); }
}

function renderReservations(list) {
  const tbody = document.getElementById('reservationsBody');
  if (!list.length) {
    tbody.innerHTML = '<tr><td colspan="8" class="table-empty">No reservations found</td></tr>';
    return;
  }
  tbody.innerHTML = list.map(r => `
    <tr>
      <td>#${r.reservation_id}</td>
      <td><strong>${r.guest_name}</strong></td>
      <td>${r.room_number} <small style="color:var(--text-muted)">${r.room_type}</small></td>
      <td>${fmtDate(r.check_in_date)}</td>
      <td>${fmtDate(r.check_out_date)}</td>
      <td>${fmtMoney(r.total_price)}</td>
      <td>${badge(r.status)}</td>
      <td>
        <div style="display:flex;gap:4px;flex-wrap:wrap">
          ${r.status === 'confirmed'  ? `<button class="btn btn-sm btn-blue"    onclick="doCheckin(${r.reservation_id})">Check In</button>` : ''}
          ${r.status === 'checked_in' ? `<button class="btn btn-sm btn-success" onclick="doCheckout(${r.reservation_id})">Check Out</button>` : ''}
          ${['confirmed','checked_in'].includes(r.status) ? `<button class="btn btn-sm btn-danger" onclick="doCancel(${r.reservation_id})">Cancel</button>` : ''}
          <a href="/invoices/view/${r.reservation_id}" target="_blank" class="btn btn-sm btn-outline">Invoice</a>
        </div>
      </td>
    </tr>`).join('');
}

async function doCheckin(id) {
  try {
    await api(`/reservations/api/${id}/checkin`, 'POST');
    showToast('Guest checked in!');
    loadReservations();
  } catch (e) { showToast(e.message, 'error'); }
}

async function doCheckout(id) {
  confirmAction('Check out this guest?', async () => {
    try {
      await api(`/reservations/api/${id}/checkout`, 'POST');
      showToast('Guest checked out');
      loadReservations();
    } catch (e) { showToast(e.message, 'error'); }
  });
}

async function doCancel(id) {
  confirmAction('Cancel this reservation?', async () => {
    try {
      await api(`/reservations/api/${id}/cancel`, 'POST');
      showToast('Reservation cancelled');
      loadReservations();
    } catch (e) { showToast(e.message, 'error'); }
  });
}

// ── New Reservation form ─────────────────────────────────────
async function openNewReservation() {
  let guests = [], rooms = [];
  try {
    [guests, rooms] = await Promise.all([
      api('/guests/api'),
      api('/rooms/api?status=available')
    ]);
  } catch (e) { showToast('Could not load form data', 'error'); return; }

  const today = new Date().toISOString().split('T')[0];
  const tmr   = new Date(Date.now() + 86400000).toISOString().split('T')[0];

  openModal('New Reservation', `
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Guest *</label>
        <select id="res-guest" class="form-select">
          <option value="">— Select guest —</option>
          ${guests.map(g => `<option value="${g.guest_id}">${g.name} (${g.email})</option>`).join('')}
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Room *</label>
        <select id="res-room" class="form-select">
          <option value="">— Select room —</option>
          ${rooms.map(r => `<option value="${r.room_id}">${r.room_number} — ${r.room_type} (${fmtMoney(r.price_per_night)}/night)</option>`).join('')}
        </select>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Check-in Date *</label>
        <input id="res-ci" type="date" class="form-input" value="${today}" min="${today}"/>
      </div>
      <div class="form-group">
        <label class="form-label">Check-out Date *</label>
        <input id="res-co" type="date" class="form-input" value="${tmr}" min="${tmr}"/>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Adults</label>
        <input id="res-adults" type="number" class="form-input" value="1" min="1"/>
      </div>
      <div class="form-group">
        <label class="form-label">Children</label>
        <input id="res-children" type="number" class="form-input" value="0" min="0"/>
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Special Requests</label>
      <textarea id="res-special" class="form-textarea" placeholder="Any special requests…"></textarea>
    </div>`,
    `<button class="btn btn-outline" onclick="closeModal()">Cancel</button>
     <button class="btn btn-primary" onclick="saveReservation()">Create Reservation</button>`
  );
}

async function saveReservation() {
  try {
    const data = {
      guest_id: parseInt(document.getElementById('res-guest').value),
      room_id:  parseInt(document.getElementById('res-room').value),
      check_in_date:  document.getElementById('res-ci').value,
      check_out_date: document.getElementById('res-co').value,
      adults:   parseInt(document.getElementById('res-adults').value),
      children: parseInt(document.getElementById('res-children').value),
      special_requests: document.getElementById('res-special').value,
    };
    if (!data.guest_id || !data.room_id) throw new Error('Please select guest and room');
    await api('/reservations/api', 'POST', data);
    showToast('Reservation created!');
    closeModal();
    loadReservations();
  } catch (e) { showToast(e.message, 'error'); }
}

loadReservations();
