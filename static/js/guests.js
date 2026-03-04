/* Guests JS */
let guestsData = [];

async function loadGuests(q = '') {
  try {
    const url = q ? `/guests/api?q=${encodeURIComponent(q)}` : '/guests/api';
    guestsData = await api(url);
    renderGuests(guestsData);
  } catch (e) { showToast('Error loading guests: ' + e.message, 'error'); }
}

function renderGuests(list) {
  const tbody = document.getElementById('guestsBody');
  if (!list.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="table-empty">No guests found</td></tr>';
    return;
  }
  tbody.innerHTML = list.map(g => `
    <tr>
      <td>#${g.guest_id}</td>
      <td><strong>${g.name}</strong></td>
      <td>${g.email}</td>
      <td>${g.phone}</td>
      <td>${g.id_proof_type ? `<span class="badge badge-confirmed">${g.id_proof_type}</span>` : '—'}</td>
      <td>
        <div style="display:flex;gap:6px">
          <button class="btn btn-sm btn-outline" onclick="openEditGuest(${g.guest_id})">Edit</button>
          <button class="btn btn-sm btn-danger"  onclick="deleteGuest(${g.guest_id})">Delete</button>
        </div>
      </td>
    </tr>`).join('');
}

function searchGuests(q) { loadGuests(q); }

function guestForm(g = {}) {
  return `
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Full Name *</label>
        <input id="g-name" class="form-input" value="${g.name || ''}" placeholder="Full name" required/>
      </div>
      <div class="form-group">
        <label class="form-label">Email *</label>
        <input id="g-email" type="email" class="form-input" value="${g.email || ''}" placeholder="Email"/>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Phone *</label>
        <input id="g-phone" class="form-input" value="${g.phone || ''}" placeholder="Phone number"/>
      </div>
      <div class="form-group">
        <label class="form-label">ID Proof Type</label>
        <select id="g-idtype" class="form-select">
          <option value="">— Select —</option>
          ${['passport','driver_license','national_id'].map(v =>
            `<option value="${v}" ${g.id_proof_type === v ? 'selected' : ''}>${v.replace(/_/g,' ')}</option>`
          ).join('')}
        </select>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">ID Proof Number</label>
        <input id="g-idnum" class="form-input" value="${g.id_proof_number || ''}" placeholder="ID number"/>
      </div>
      <div class="form-group">
        <label class="form-label">Address</label>
        <input id="g-addr" class="form-input" value="${g.address || ''}" placeholder="Full address"/>
      </div>
    </div>`;
}

function getGuestData() {
  return {
    name: document.getElementById('g-name').value,
    email: document.getElementById('g-email').value,
    phone: document.getElementById('g-phone').value,
    id_proof_type: document.getElementById('g-idtype').value,
    id_proof_number: document.getElementById('g-idnum').value,
    address: document.getElementById('g-addr').value,
  };
}

function openAddGuest() {
  openModal('Add New Guest', guestForm(),
    `<button class="btn btn-outline" onclick="closeModal()">Cancel</button>
     <button class="btn btn-primary" onclick="saveGuest()">Save Guest</button>`
  );
}

async function openEditGuest(id) {
  const g = guestsData.find(x => x.guest_id === id);
  openModal('Edit Guest', guestForm(g),
    `<button class="btn btn-outline" onclick="closeModal()">Cancel</button>
     <button class="btn btn-primary" onclick="saveGuest(${id})">Update Guest</button>`
  );
}

async function saveGuest(id = null) {
  try {
    const data = getGuestData();
    if (id) {
      await api(`/guests/api/${id}`, 'PUT', data);
      showToast('Guest updated');
    } else {
      await api('/guests/api', 'POST', data);
      showToast('Guest added');
    }
    closeModal();
    loadGuests();
  } catch (e) { showToast(e.message, 'error'); }
}

async function deleteGuest(id) {
  confirmAction('Are you sure you want to delete this guest?', async () => {
    try {
      await api(`/guests/api/${id}`, 'DELETE');
      showToast('Guest deleted');
      loadGuests();
    } catch (e) { showToast(e.message, 'error'); }
  });
}

loadGuests();
