/* Staff JS */
async function loadStaff() {
  try {
    const staff = await api('/staff/api');
    const tbody = document.getElementById('staffBody');
    if (!staff.length) { tbody.innerHTML = '<tr><td colspan="8" class="table-empty">No staff found</td></tr>'; return; }
    tbody.innerHTML = staff.map(s => `
      <tr>
        <td>#${s.staff_id}</td>
        <td><strong>${s.name}</strong></td>
        <td>${s.position}</td>
        <td><span class="badge badge-confirmed">${s.shift}</span></td>
        <td>${s.contact}</td>
        <td><span class="badge badge-${s.role === 'admin' ? 'occupied' : s.role === 'manager' ? 'reserved' : 'available'}">${s.role}</span></td>
        <td>${badge(s.status)}</td>
        <td>
          <div style="display:flex;gap:6px">
            <button class="btn btn-sm btn-outline" onclick="openEditStaff(${s.staff_id})">Edit</button>
            <button class="btn btn-sm btn-danger"  onclick="deactivateStaff(${s.staff_id})">Deactivate</button>
          </div>
        </td>
      </tr>`).join('');
  } catch (e) { showToast('Error: ' + e.message, 'error'); }
}

function staffForm(s = {}) {
  return `
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Full Name *</label>
        <input id="st-name" class="form-input" value="${s.name || ''}" placeholder="Full name"/>
      </div>
      <div class="form-group">
        <label class="form-label">Position *</label>
        <input id="st-pos" class="form-input" value="${s.position || ''}" placeholder="e.g. Receptionist"/>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Contact *</label>
        <input id="st-contact" class="form-input" value="${s.contact || ''}" placeholder="Phone number"/>
      </div>
      <div class="form-group">
        <label class="form-label">Email</label>
        <input id="st-email" type="email" class="form-input" value="${s.email || ''}" placeholder="Email address"/>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Salary *</label>
        <input id="st-salary" type="number" class="form-input" value="${s.salary || ''}" step="0.01" placeholder="Monthly salary"/>
      </div>
      <div class="form-group">
        <label class="form-label">Shift</label>
        <select id="st-shift" class="form-select">
          ${['morning','afternoon','night'].map(sh =>
            `<option value="${sh}" ${s.shift===sh?'selected':''}>${sh}</option>`
          ).join('')}
        </select>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Username</label>
        <input id="st-user" class="form-input" value="${s.username || ''}" placeholder="Login username"/>
      </div>
      <div class="form-group">
        <label class="form-label">Role</label>
        <select id="st-role" class="form-select">
          ${['staff','manager','admin'].map(r =>
            `<option value="${r}" ${s.role===r?'selected':''}>${r}</option>`
          ).join('')}
        </select>
      </div>
    </div>
    ${!s.staff_id ? `
    <div class="form-group">
      <label class="form-label">Password</label>
      <input id="st-pw" type="password" class="form-input" placeholder="Set initial password"/>
    </div>` : ''}`;
}

function getStaffData(isNew = false) {
  const d = {
    name: document.getElementById('st-name').value,
    position: document.getElementById('st-pos').value,
    contact: document.getElementById('st-contact').value,
    email: document.getElementById('st-email').value,
    salary: parseFloat(document.getElementById('st-salary').value),
    shift: document.getElementById('st-shift').value,
    username: document.getElementById('st-user').value,
    role: document.getElementById('st-role').value,
  };
  if (isNew && document.getElementById('st-pw')) {
    d.password = document.getElementById('st-pw').value;
  }
  return d;
}

function openAddStaff() {
  openModal('Add Staff Member', staffForm(),
    `<button class="btn btn-outline" onclick="closeModal()">Cancel</button>
     <button class="btn btn-primary" onclick="saveStaff()">Add Staff</button>`);
}

let editStaffId = null;
async function openEditStaff(id) {
  editStaffId = id;
  const staff = await api('/staff/api');
  const s = staff.find(x => x.staff_id === id);
  openModal('Edit Staff', staffForm(s),
    `<button class="btn btn-outline" onclick="closeModal()">Cancel</button>
     <button class="btn btn-primary" onclick="saveStaff(${id})">Update</button>`);
}

async function saveStaff(id = null) {
  try {
    const data = getStaffData(!id);
    if (id) await api(`/staff/api/${id}`, 'PUT', data);
    else     await api('/staff/api', 'POST', data);
    showToast(id ? 'Staff updated' : 'Staff added');
    closeModal(); loadStaff();
  } catch (e) { showToast(e.message, 'error'); }
}

async function deactivateStaff(id) {
  confirmAction('Deactivate this staff member?', async () => {
    try { await api(`/staff/api/${id}`, 'DELETE'); showToast('Staff deactivated'); loadStaff(); }
    catch (e) { showToast(e.message, 'error'); }
  });
}

loadStaff();
