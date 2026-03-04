/* Services JS */
function switchTab(tab, btn) {
  document.getElementById('tab-services').style.display = tab === 'services' ? '' : 'none';
  document.getElementById('tab-orders').style.display   = tab === 'orders'   ? '' : 'none';
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  if (tab === 'orders') loadOrders();
}

async function loadServices() {
  try {
    const services = await api('/services/api');
    const grid = document.getElementById('servicesGrid');
    if (!services.length) { grid.innerHTML = '<div class="table-empty">No services available</div>'; return; }
    const cats = { food:'🍽', spa:'💆', transport:'🚗', laundry:'👕', other:'✨' };
    grid.innerHTML = services.map(s => `
      <div class="service-card">
        <div class="service-category">${cats[s.category] || '✦'} ${s.category || 'Service'}</div>
        <div class="service-name">${s.service_name}</div>
        <div class="service-desc">${s.description || ''}</div>
        <div class="service-price">${fmtMoney(s.price)}</div>
        <div style="display:flex;gap:6px;margin-top:14px">
          <button class="btn btn-sm btn-outline" onclick="openEditService(${s.service_id},'${s.service_name}',${s.price},'${s.category}','${s.description || ''}')">Edit</button>
          <button class="btn btn-sm btn-danger" onclick="deleteService(${s.service_id})">Remove</button>
        </div>
      </div>`).join('');
  } catch (e) { showToast('Error: ' + e.message, 'error'); }
}

async function loadOrders() {
  try {
    const orders = await api('/services/api/orders');
    const tbody  = document.getElementById('ordersBody');
    if (!orders.length) { tbody.innerHTML = '<tr><td colspan="8" class="table-empty">No orders</td></tr>'; return; }
    tbody.innerHTML = orders.map(o => `
      <tr>
        <td>#${o.guest_service_id}</td>
        <td>${o.guest_name}</td>
        <td>${o.service_name}</td>
        <td>${o.quantity}</td>
        <td>${fmtMoney(o.total_price)}</td>
        <td>${badge(o.status)}</td>
        <td>${fmtDate(o.date)}</td>
        <td>
          ${o.status === 'pending' ? `
            <button class="btn btn-sm btn-success" onclick="updateOrderStatus(${o.guest_service_id},'delivered')">Mark Delivered</button>
            <button class="btn btn-sm btn-danger"  onclick="updateOrderStatus(${o.guest_service_id},'cancelled')">Cancel</button>` : ''}
        </td>
      </tr>`).join('');
  } catch (e) { showToast('Error: ' + e.message, 'error'); }
}

async function updateOrderStatus(id, status) {
  try {
    await api(`/services/api/orders/${id}/status`, 'PUT', { status });
    showToast('Order updated');
    loadOrders();
  } catch (e) { showToast(e.message, 'error'); }
}

function serviceForm(s = {}) {
  return `
    <div class="form-group">
      <label class="form-label">Service Name *</label>
      <input id="s-name" class="form-input" value="${s.service_name || ''}" placeholder="Service name"/>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Price *</label>
        <input id="s-price" type="number" class="form-input" value="${s.price || ''}" step="0.01" placeholder="0.00"/>
      </div>
      <div class="form-group">
        <label class="form-label">Category</label>
        <select id="s-cat" class="form-select">
          ${['food','spa','transport','laundry','other'].map(c =>
            `<option value="${c}" ${s.category===c?'selected':''}>${c}</option>`
          ).join('')}
        </select>
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Description</label>
      <textarea id="s-desc" class="form-textarea">${s.description || ''}</textarea>
    </div>`;
}

function openAddService() {
  openModal('Add Service', serviceForm(),
    `<button class="btn btn-outline" onclick="closeModal()">Cancel</button>
     <button class="btn btn-primary" onclick="saveService()">Add Service</button>`);
}

function openEditService(id, name, price, category, description) {
  openModal('Edit Service', serviceForm({ service_id: id, service_name: name, price, category, description }),
    `<button class="btn btn-outline" onclick="closeModal()">Cancel</button>
     <button class="btn btn-primary" onclick="saveService(${id})">Update</button>`);
}

async function saveService(id = null) {
  try {
    const data = {
      service_name: document.getElementById('s-name').value,
      price: parseFloat(document.getElementById('s-price').value),
      category: document.getElementById('s-cat').value,
      description: document.getElementById('s-desc').value,
    };
    if (id) await api(`/services/api/${id}`, 'PUT', data);
    else     await api('/services/api', 'POST', data);
    showToast(id ? 'Service updated' : 'Service added');
    closeModal(); loadServices();
  } catch (e) { showToast(e.message, 'error'); }
}

async function deleteService(id) {
  confirmAction('Deactivate this service?', async () => {
    try { await api(`/services/api/${id}`, 'DELETE'); showToast('Service removed'); loadServices(); }
    catch (e) { showToast(e.message, 'error'); }
  });
}

async function openNewOrder() {
  const [guests, services] = await Promise.all([api('/guests/api'), api('/services/api')]);
  openModal('New Service Order', `
    <div class="form-group">
      <label class="form-label">Guest *</label>
      <select id="o-guest" class="form-select">
        <option value="">— Select guest —</option>
        ${guests.map(g => `<option value="${g.guest_id}">${g.name}</option>`).join('')}
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">Service *</label>
      <select id="o-service" class="form-select">
        <option value="">— Select service —</option>
        ${services.map(s => `<option value="${s.service_id}">${s.service_name} (${fmtMoney(s.price)})</option>`).join('')}
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">Quantity</label>
      <input id="o-qty" type="number" class="form-input" value="1" min="1"/>
    </div>
    <div class="form-group">
      <label class="form-label">Notes</label>
      <textarea id="o-notes" class="form-textarea" placeholder="Special instructions…"></textarea>
    </div>`,
    `<button class="btn btn-outline" onclick="closeModal()">Cancel</button>
     <button class="btn btn-primary" onclick="saveOrder()">Place Order</button>`);
}

async function saveOrder() {
  try {
    const data = {
      guest_id: parseInt(document.getElementById('o-guest').value),
      service_id: parseInt(document.getElementById('o-service').value),
      quantity: parseInt(document.getElementById('o-qty').value),
      notes: document.getElementById('o-notes').value,
    };
    await api('/services/api/orders', 'POST', data);
    showToast('Order placed!');
    closeModal();
    loadOrders();
  } catch (e) { showToast(e.message, 'error'); }
}

loadServices();
