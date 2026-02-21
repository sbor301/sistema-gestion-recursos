/* buscador_talento.js */

document.addEventListener('DOMContentLoaded', function () {
    const realSelect = document.getElementById('realSelect');
    const tagsArea = document.getElementById('tagsArea');
    const skillInput = document.getElementById('skillInput');
    const suggestionsList = document.getElementById('suggestionsList');
    const btnClear = document.getElementById('btnClear');

    // Inicializar: mostrar etiquetas si venimos de una búsqueda previa
    renderTags();

    // Evento: Escribir en el input
    skillInput.addEventListener('input', function () {
        const query = this.value.toLowerCase();
        suggestionsList.innerHTML = '';
        
        if (query.length === 0) {
            suggestionsList.style.display = 'none';
            return;
        }

        // Filtrar opciones que coincidan y NO estén ya seleccionadas
        const options = Array.from(realSelect.options);
        const matches = options.filter(opt => 
            opt.text.toLowerCase().includes(query) && !opt.selected
        );

        if (matches.length > 0) {
            suggestionsList.style.display = 'block';
            matches.forEach(opt => {
                const div = document.createElement('div');
                div.className = 'suggestion-item';
                div.textContent = opt.text;
                div.onclick = () => selectSkill(opt.value);
                suggestionsList.appendChild(div);
            });
        } else {
            suggestionsList.style.display = 'none';
        }
    });

    // Evento: Clic fuera para cerrar sugerencias
    document.addEventListener('click', function (e) {
        if (!tagsArea.contains(e.target)) {
            suggestionsList.style.display = 'none';
        }
    });

    // Evento: Enfocar input al hacer clic en el área
    tagsArea.addEventListener('click', () => skillInput.focus());

    // Evento: Botón Limpiar
    if (btnClear) {
        btnClear.addEventListener('click', () => {
            Array.from(realSelect.options).forEach(opt => opt.selected = false);
            renderTags();
            // Recargar la página limpia
            window.location.href = window.location.pathname;
        });
    }

    // --- FUNCIONES AUXILIARES ---

    function selectSkill(value) {
        const option = Array.from(realSelect.options).find(opt => opt.value === value);
        if (option) {
            option.selected = true;
            renderTags();
            skillInput.value = '';
            suggestionsList.style.display = 'none';
            skillInput.focus();
        }
    }

    function removeSkill(value) {
        const option = Array.from(realSelect.options).find(opt => opt.value === value);
        if (option) {
            option.selected = false;
            renderTags();
        }
    }

    function renderTags() {
        // Guardamos referencia al input actual
        const currentInput = skillInput;
        tagsArea.innerHTML = ''; // Limpiamos visualmente

        // Buscamos opciones seleccionadas
        const selectedOptions = Array.from(realSelect.options).filter(opt => opt.selected);

        selectedOptions.forEach(opt => {
            const chip = document.createElement('div');
            chip.className = 'tag-chip';
            chip.innerHTML = `${opt.text} <i class="bi bi-x"></i>`;
            
            // Evento para borrar al hacer clic en la X
            chip.querySelector('i').addEventListener('click', (e) => {
                e.stopPropagation();
                removeSkill(opt.value);
            });
            
            tagsArea.appendChild(chip);
        });

        // Reinsertamos el input al final
        tagsArea.appendChild(currentInput);
    }
});