/* static/js/dashboard.js */

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. LEER DATOS DESDE DJANGO (Usando JSON Scripts seguros)
    const labelsProyectos = JSON.parse(document.getElementById('data-labels-proyectos').textContent);
    const dataProyectos = JSON.parse(document.getElementById('data-values-proyectos').textContent);
    
    const labelsRecursos = JSON.parse(document.getElementById('data-labels-recursos').textContent);
    const dataRecursos = JSON.parse(document.getElementById('data-values-recursos').textContent);

    // 2. CONFIGURACIÓN GRÁFICA DE DONA
    const ctxProyectos = document.getElementById('chartProyectos').getContext('2d');
    new Chart(ctxProyectos, {
        type: 'doughnut',
        data: {
            labels: labelsProyectos,
            datasets: [{
                data: dataProyectos,
                backgroundColor: ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#6610f2', '#0dcaf0'],
                borderWidth: 2,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, padding: 20 } },
                title: { display: dataProyectos.length === 0, text: 'Sin datos registrados', position: 'top' }
            },
            cutout: '75%'
        }
    });

    // 3. CONFIGURACIÓN GRÁFICA DE BARRAS
    const ctxRecursos = document.getElementById('chartRecursos').getContext('2d');
    new Chart(ctxRecursos, {
        type: 'bar',
        data: {
            labels: labelsRecursos,
            datasets: [{
                label: 'Tareas Pendientes',
                data: dataRecursos,
                backgroundColor: '#0d6efd',
                borderRadius: 4,
                barPercentage: 0.6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { 
                    beginAtZero: true, 
                    ticks: { stepSize: 1 }, 
                    grid: { borderDash: [5, 5] } 
                },
                x: { grid: { display: false } }
            },
            plugins: { legend: { display: false } }
        }
    });
});