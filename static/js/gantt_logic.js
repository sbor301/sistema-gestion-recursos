/* static/js/gantt_logic.js */

let gantt_inst = null; // Variable global para controlar la instancia

// 1. Obtener Token CSRF (Seguridad Django)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 2. Función Principal de Inicialización
function iniciarGantt(tareas, urlApiActualizar) {
    if (!tareas || tareas.length === 0) return;

    gantt_inst = new Gantt(".gantt-target", tareas, {
        header_height: 50,
        column_width: 30,
        step: 24,
        view_modes: ['Quarter Day', 'Half Day', 'Day', 'Week', 'Month'],
        bar_height: 25,
        bar_corner_radius: 4,
        arrow_curve: 5,
        padding: 18,
        view_mode: 'Day',
        date_format: 'YYYY-MM-DD',
        language: 'es',

        // HTML del Popup al pasar el mouse
        custom_popup_html: function(task) {
            return `
            <div class="popover fade show bs-popover-bottom custom-gantt-popover" role="tooltip" style="position: relative;">
                <div class="popover-arrow"></div>
                <h3 class="popover-header text-center bg-light text-dark fw-bold border-bottom-0">${task.name}</h3>
                <div class="popover-body pt-2">
                    <div class="mb-2">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="badge bg-primary">${task.progress}%</span>
                            <span class="text-muted small">${task.responsable}</span>
                        </div>
                        <div class="text-primary small fw-bold text-truncate">${task.proyecto}</div>
                    </div>
                    
                    <div class="text-muted small mb-3 border-top pt-2">
                        <i class="bi bi-calendar-event me-1"></i> ${task.start} <br>
                        <i class="bi bi-arrow-right-short ms-1"></i> ${task.end}
                    </div>
                    
                    <div class="d-grid">
                        <a href="/buscar/?tarea_id=${task.id}" class="btn btn-sm btn-outline-primary">
                            <i class="bi bi-search me-1"></i> Gestionar
                        </a>
                    </div>
                </div>
            </div>
            `;
        },

        // Evento: Al arrastrar una barra (Actualizar fecha)
        on_date_change: function(task, start, end) {
            console.log("📅 Actualizando fecha:", task.name);
            
            const datos = {
                id: task.id,
                start: start.toISOString().split('T')[0],
                end: end.toISOString().split('T')[0]
            };

            fetch(urlApiActualizar, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(datos)
            })
            .then(response => {
                if(response.ok) {
                    // Opcional: Mostrar toast de éxito
                    console.log("✅ Guardado en BD");
                } else {
                    alert("⚠️ Error al guardar la nueva fecha en el servidor.");
                }
            })
            .catch(error => console.error("Error crítico:", error));
        }
    });
}

// 3. Control de Vistas (Día, Semana, Mes)
function cambiarVista(modo, btn) {
    if(gantt_inst) {
        gantt_inst.change_view_mode(modo);
        
        // Actualizar estado visual de los botones
        document.querySelectorAll('.btn-group-vista .btn').forEach(b => b.classList.remove('active'));
        if(btn) btn.classList.add('active');
    }
}