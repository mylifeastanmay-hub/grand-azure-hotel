/* Dashboard JS */
let revChart, roomChart;

async function loadDashboard() {
  try {
    const d = await api('/api/dashboard/stats');

    document.getElementById('stat-occupancy').textContent  = d.occupancy_rate + '%';
    document.getElementById('stat-rooms').textContent      = `${d.occupied_rooms} / ${d.total_rooms} rooms`;
    document.getElementById('stat-revenue').textContent    = fmtMoney(d.monthly_revenue);
    document.getElementById('stat-today-rev').textContent  = `Today: ${fmtMoney(d.today_revenue)}`;
    document.getElementById('stat-reservations').textContent = d.active_reservations;
    document.getElementById('stat-checkins').textContent   = `Check-ins today: ${d.checkins_today}`;
    document.getElementById('stat-guests').textContent     = d.total_guests;
    document.getElementById('stat-checkouts').textContent  = `Check-outs today: ${d.checkouts_today}`;

    // Revenue Chart
    const rCtx = document.getElementById('revenueChart').getContext('2d');
    if (revChart) revChart.destroy();
    revChart = new Chart(rCtx, {
      type: 'bar',
      data: {
        labels: d.revenue_chart.map(r => r.date),
        datasets: [{
          label: 'Revenue',
          data: d.revenue_chart.map(r => r.revenue),
          backgroundColor: 'rgba(212,168,83,0.7)',
          borderColor: '#D4A853',
          borderWidth: 1,
          borderRadius: 4,
        }]
      },
      options: chartOptions('Revenue ($)')
    });

    // Room Types Chart
    const tCtx = document.getElementById('roomTypesChart').getContext('2d');
    if (roomChart) roomChart.destroy();
    roomChart = new Chart(tCtx, {
      type: 'doughnut',
      data: {
        labels: d.room_types.map(r => r.type),
        datasets: [{
          data: d.room_types.map(r => r.count),
          backgroundColor: ['rgba(45,130,183,0.8)','rgba(212,168,83,0.8)','rgba(45,184,127,0.8)','rgba(139,92,246,0.8)'],
          borderWidth: 0,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#8FA3B8', font: { size: 12 } } }
        }
      }
    });

    // Recent reservations
    const tbody = document.getElementById('recentBody');
    if (!d.recent_reservations.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="table-empty">No reservations yet</td></tr>';
    } else {
      tbody.innerHTML = d.recent_reservations.map(r => `
        <tr>
          <td>#${r.reservation_id}</td>
          <td>${r.guest_name}</td>
          <td>${r.room_number} <small style="color:var(--text-muted)">${r.room_type}</small></td>
          <td>${fmtDate(r.check_in_date)}</td>
          <td>${fmtDate(r.check_out_date)}</td>
          <td>${fmtMoney(r.total_price)}</td>
          <td>${badge(r.status)}</td>
        </tr>`).join('');
    }
  } catch (e) {
    showToast('Failed to load dashboard: ' + e.message, 'error');
  }
}

function chartOptions(yLabel) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { ticks: { color: '#8FA3B8', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
      y: { ticks: { color: '#8FA3B8', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,0.04)' } }
    }
  };
}

loadDashboard();
