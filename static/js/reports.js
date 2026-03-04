/* Reports JS */
let revChart, occChart;

async function loadSummary() {
  try {
    const d = await api('/reports/api/summary');
    document.getElementById('rpt-monthly').textContent  = fmtMoney(d.monthly_revenue);
    document.getElementById('rpt-annual').textContent   = fmtMoney(d.annual_revenue);
    document.getElementById('rpt-bookings').textContent = d.monthly_bookings;
    document.getElementById('rpt-avgstay').textContent  = d.avg_stay_nights + ' nights';
  } catch (e) { showToast('Error loading summary', 'error'); }
}

async function loadRevenue(period = 'daily', btn = null) {
  if (btn) {
    document.querySelectorAll('.btn-group .btn-outline').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }
  try {
    const data = await api(`/reports/api/revenue?period=${period}`);
    const ctx  = document.getElementById('revChart').getContext('2d');
    if (revChart) revChart.destroy();
    revChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map(d => d.label),
        datasets: [{
          label: 'Revenue',
          data: data.map(d => d.revenue),
          backgroundColor: 'rgba(212,168,83,0.7)',
          borderColor: '#D4A853',
          borderWidth: 1, borderRadius: 4,
        }]
      },
      options: chartOpts()
    });
  } catch (e) { showToast('Error loading revenue chart', 'error'); }
}

async function loadOccupancy() {
  try {
    const data = await api('/reports/api/occupancy');
    const ctx  = document.getElementById('occChart').getContext('2d');
    if (occChart) occChart.destroy();
    occChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map(d => d.date),
        datasets: [{
          label: 'Occupancy %',
          data: data.map(d => d.rate),
          borderColor: '#2D82B7',
          backgroundColor: 'rgba(45,130,183,0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointRadius: 2,
        }]
      },
      options: chartOpts()
    });
  } catch (e) { showToast('Error loading occupancy chart', 'error'); }
}

function chartOpts() {
  return {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { ticks: { color: '#8FA3B8', font: { size: 10 }, maxRotation: 45 }, grid: { color: 'rgba(255,255,255,0.04)' } },
      y: { ticks: { color: '#8FA3B8', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,0.04)' } }
    }
  };
}

loadSummary();
loadRevenue('daily');
loadOccupancy();
