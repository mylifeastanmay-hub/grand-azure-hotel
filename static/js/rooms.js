/* Rooms JS */
async function loadRooms() {
  const status = document.getElementById('filterStatus').value;
  const type   = document.getElementById('filterType').value;
  let url = '/rooms/api?';
  if (status) url += `status=${status}&`;
  if (type)   url += `room_type=${encodeURIComponent(type)}`;

  try {
    const rooms = await api(url);
    const grid  = document.getElementById('roomsGrid');
    if (!rooms.length) {
      grid.innerHTML = '<div class="table-empty">No rooms found</div>';
      return;
    }
    grid.innerHTML = rooms.map(r => `
      <div class="room-card">
        <div class="room-card-top">
          <div>
            <div class="room-number">${r.room_number}</div>
            <div class="room-type">${r.room_type} · Floor ${r.floor}</div>
          </div>
          ${badge(r.status)}
        </div>
        <div class="room-card-body">
          <div class="room-price">${fmtMoney(r.price_per_night)} <span>/ night</span></div>
          <div class="room-info">👤 Max ${r.max_occupancy} | ${r.amenities || 'Standard amenities'}</div>
          <div class="room-info" style="margin-top:6px;color:var(--text-secondary);font-size:11px">${r.description || ''}</div>
        </div>
        <div class="room-card-footer">
          <button class="btn btn-sm btn-outline" onclick="openEditRoom(${r.room_id})">Edit</button>
          <button class="btn btn-sm btn-danger"  onclick="deleteRoom(${r.room_id})">Delete</button>
        </div>
      </div>`).join('');
  } catch (e) { showToast('Error loading rooms: ' + e.message, 'error'); }
}

function roomForm(r = {}) {
  const types = ['Standard','Deluxe','Suite','Presidential'];
  const statuses = ['available','occupied','maintenance','reserved'];
  return `
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Room Number *</label>
        <input id="r-num" class="form-input" value="${r.room_number || ''}" placeholder="e.g. 101"/>
      </div>
      <div class="form-group">
        <label class="form-label">Floor *</label>
        <input id="r-floor" type="number" class="form-input" value="${r.floor || 1}" min="1"/>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Room Type *</label>
        <select id="r-type" class="form-select">
          ${types.map(t => `<option value="${t}" ${r.room_type===t?'selected':''}>${t}</option>`).join('')}
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Status</label>
        <select id="r-status" class="form-select">
          ${statuses.map(s => `<option value="${s}" ${r.status===s?'selected':''}>${s}</option>`).join('')}
        </select>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Price / Night *</label>
        <input id="r-price" type="number" class="form-input" value="${r.price_per_night || ''}" step="0.01" placeholder="99.00"/>
      </div>
      <div class="form-group">
        <label class="form-label">Max Occupancy</label>
        <input id="r-occ" type="number" class="form-input" value="${r.max_occupancy || 2}" min="1"/>
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Amenities</label>
      <input id="r-amen" class="form-input" value="${r.amenities || ''}" placeholder="WiFi, TV, AC, Mini-bar"/>
    </div>
    <div class="form-group">
      <label class="form-label">Description</label>
      <textarea id="r-desc" class="form-textarea">${r.description || ''}</textarea>
    </div>`;
}

function getRoomData() {
  return {
    room_number: document.getElementById('r-num').value,
    floor: parseInt(document.getElementById('r-floor').value),
    room_type: document.getElementById('r-type').value,
    status: document.getElementById('r-status').value,
    price_per_night: parseFloat(document.getElementById('r-price').value),
    max_occupancy: parseInt(document.getElementById('r-occ').value),
    amenities: document.getElementById('r-amen').value,
    description: document.getElementById('r-desc').value,
  };
}

function openAddRoom() {
  openModal('Add New Room', roomForm(),
    `<button class="btn btn-outline" onclick="closeModal()">Cancel</button>
     <button class="btn btn-primary" onclick="saveRoom()">Save Room</button>`);
}

let editRoomId = null;
async function openEditRoom(id) {
  editRoomId = id;
  const rooms = await api('/rooms/api');
  const r = rooms.find(x => x.room_id === id);
  openModal('Edit Room', roomForm(r),
    `<button class="btn btn-outline" onclick="closeModal()">Cancel</button>
     <button class="btn btn-primary" onclick="saveRoom(${id})">Update Room</button>`);
}

async function saveRoom(id = null) {
  try {
    const data = getRoomData();
    if (id) {
      await api(`/rooms/api/${id}`, 'PUT', data);
      showToast('Room updated');
    } else {
      await api('/rooms/api', 'POST', data);
      showToast('Room added');
    }
    closeModal();
    loadRooms();
  } catch (e) { showToast(e.message, 'error'); }
}

async function deleteRoom(id) {
  confirmAction('Delete this room? This cannot be undone.', async () => {
    try {
      await api(`/rooms/api/${id}`, 'DELETE');
      showToast('Room deleted');
      loadRooms();
    } catch (e) { showToast(e.message, 'error'); }
  });
}

loadRooms();
