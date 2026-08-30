document.addEventListener('DOMContentLoaded', function() {
    // ==================== ВКЛАДКИ ====================
    const tabButtons = document.querySelectorAll('.tab-btn');
    const groupTab = document.getElementById('group-tab');
    const teacherTab = document.getElementById('teacher-tab');
    const auditoriumTab = document.getElementById('auditorium-tab');
    let currentMode = 'group';

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            groupTab.classList.remove('active-tab');
            teacherTab.classList.remove('active-tab');
            auditoriumTab.classList.remove('active-tab');

            if (tabId === 'group-tab') {
                groupTab.classList.add('active-tab');
                currentMode = 'group';
            } else if (tabId === 'teacher-tab') {
                teacherTab.classList.add('active-tab');
                currentMode = 'teacher';
                if (!window.teachersLoaded) {
                    loadAllTeachers();
                }
            } else if (tabId === 'auditorium-tab') {
                auditoriumTab.classList.add('active-tab');
                currentMode = 'auditorium';
                if (!window.auditoriumsLoaded) {
                    loadAuditoriums();
                }
            }

            scheduleContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"><i class="fas fa-calendar-plus"></i></div>
                    <h3>Расписание не загружено</h3>
                    <p>Выберите параметры и нажмите "Показать расписание"</p>
                </div>
            `;
            hideError();
        });
    });

    // ==================== DOM ЭЛЕМЕНТЫ ====================
    // ГРУППЫ
    const groupSelect = document.getElementById('group-select');
    const groupDateInput = document.getElementById('group-date-input');
    const groupShowButton = document.getElementById('group-show-btn');
    const groupResetButton = document.getElementById('group-reset-btn');
    const groupExportButton = document.getElementById('group-export-btn');
    const groupTodayButton = document.getElementById('group-today-btn');
    const groupTomorrowButton = document.getElementById('group-tomorrow-btn');
    const groupCount = document.getElementById('group-count');

    // ПРЕПОДАВАТЕЛИ
    const teacherSelect = document.getElementById('teacher-select');
    const teacherDateInput = document.getElementById('teacher-date-input');
    const teacherShowButton = document.getElementById('teacher-show-btn');
    const teacherResetButton = document.getElementById('teacher-reset-btn');
    const teacherExportButton = document.getElementById('teacher-export-btn');
    const teacherTodayButton = document.getElementById('teacher-today-btn');
    const teacherTomorrowButton = document.getElementById('teacher-tomorrow-btn');
    const teacherCount = document.getElementById('teacher-count');

    // АУДИТОРИИ
    const auditoriumSelect = document.getElementById('auditorium-select');
    const auditoriumDateInput = document.getElementById('auditorium-date-input');
    const auditoriumShowButton = document.getElementById('auditorium-show-btn');
    const auditoriumResetButton = document.getElementById('auditorium-reset-btn');
    const auditoriumExportButton = document.getElementById('auditorium-export-btn');
    const auditoriumTodayButton = document.getElementById('auditorium-today-btn');
    const auditoriumTomorrowButton = document.getElementById('auditorium-tomorrow-btn');
    const auditoriumCount = document.getElementById('auditorium-count');

    // ОБЩИЕ
    const scheduleContainer = document.getElementById('schedule-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const errorTitle = document.getElementById('error-title');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const statusUpdate = document.getElementById('status-update');

    // ==================== ИНИЦИАЛИЗАЦИЯ ====================
    setDefaultDate();
    checkServerStatus();
    setInterval(checkServerStatus, 30000);

    loadAllGroups();

    // ==================== ФУНКЦИИ ====================

    function setDefaultDate() {
        const today = new Date().toISOString().split('T')[0];
        groupDateInput.value = today;
        teacherDateInput.value = today;
        auditoriumDateInput.value = today;
        updateGroupButtons();
        updateTeacherButtons();
        updateAuditoriumButtons();
        groupDateInput.dispatchEvent(new Event('change'));
        teacherDateInput.dispatchEvent(new Event('change'));
        auditoriumDateInput.dispatchEvent(new Event('change'));
    }

    async function checkServerStatus() {
        try {
            const response = await fetch('/api/health');
            if (response.ok) {
                statusDot.classList.remove('offline');
                statusDot.classList.add('online');
                statusText.textContent = 'Система онлайн';
                statusUpdate.textContent = new Date().toLocaleTimeString('ru-RU');
            } else throw new Error('Ошибка сервера');
        } catch (error) {
            statusDot.classList.remove('online');
            statusDot.classList.add('offline');
            statusText.textContent = 'Система офлайн';
            statusUpdate.textContent = 'Нет связи с сервером';
        }
    }

    // Загрузка всех групп (NEW_GROUPS)
    async function loadAllGroups() {
        groupSelect.innerHTML = '<option value="">Загрузка групп...</option>';
        groupSelect.disabled = true;

        try {
            const response = await fetch('/api/all_groups');
            const data = await response.json();
            if (data.success) {
                groupSelect.innerHTML = '<option value="">-- Выберите группу --</option>';
                data.groups.forEach(g => {
                    const opt = document.createElement('option');
                    opt.value = g.id;
                    opt.textContent = g.text;
                    groupSelect.appendChild(opt);
                });
                groupSelect.disabled = false;
                groupCount.innerHTML = `<i class="fas fa-info-circle"></i> Групп: ${data.groups.length}`;

                // Инициализация Select2
                $(groupSelect).select2({
                    placeholder: 'Выберите группу',
                    allowClear: true
                });
                // При выборе через Select2 обновляем кнопки
                $(groupSelect).on('select2:select select2:clear', function(e) {
                    updateGroupButtons();
                });
                updateGroupButtons();
            } else {
                showError('Ошибка загрузки групп', data.error || 'Неизвестная ошибка');
            }
        } catch (error) {
            showError('Ошибка сети', 'Не удалось загрузить список групп');
        }
    }

    // Загрузка всех преподавателей
    async function loadAllTeachers() {
        teacherSelect.innerHTML = '<option value="">Загрузка преподавателей...</option>';
        teacherSelect.disabled = true;
        teacherShowButton.disabled = true;
        teacherExportButton.disabled = true;

        try {
            const response = await fetch('/api/teachers');
            const data = await response.json();
            if (data.success) {
                teacherSelect.innerHTML = '<option value="">-- Выберите преподавателя --</option>';
                data.teachers.forEach(t => {
                    const opt = document.createElement('option');
                    opt.value = t.id;
                    opt.textContent = t.name;
                    teacherSelect.appendChild(opt);
                });
                teacherSelect.disabled = false;
                teacherCount.innerHTML = `<i class="fas fa-info-circle"></i> Преподавателей: ${data.teachers.length}`;
                window.teachersLoaded = true;
                // Инициализация Select2 для преподавателей
                $(teacherSelect).select2({
                    placeholder: 'Выберите преподавателя',
                    allowClear: true
                });
                $(teacherSelect).on('select2:select select2:clear', function(e) {
                    updateTeacherButtons();
                });
                updateTeacherButtons();
            } else {
                showError('Ошибка загрузки', data.error || 'Неизвестная ошибка');
            }
        } catch (error) {
            showError('Ошибка сети', 'Не удалось загрузить список преподавателей');
        }
    }

    // Загрузка аудиторий
    async function loadAuditoriums() {
        auditoriumSelect.innerHTML = '<option value="">Загрузка аудиторий...</option>';
        auditoriumSelect.disabled = true;
        auditoriumShowButton.disabled = true;
        auditoriumExportButton.disabled = true;

        try {
            const response = await fetch('/api/auditoriums');
            const data = await response.json();
            if (data.success) {
                auditoriumSelect.innerHTML = '<option value="">-- Выберите аудиторию --</option>';
                data.auditoriums.forEach(a => {
                    const opt = document.createElement('option');
                    opt.value = a.id;
                    opt.textContent = a.name;
                    auditoriumSelect.appendChild(opt);
                });
                auditoriumSelect.disabled = false;
                auditoriumCount.innerHTML = `<i class="fas fa-info-circle"></i> Аудиторий: ${data.auditoriums.length}`;
                window.auditoriumsLoaded = true;
                // Инициализация Select2 для аудиторий
                $(auditoriumSelect).select2({
                    placeholder: 'Выберите аудиторию',
                    allowClear: true
                });
                $(auditoriumSelect).on('select2:select select2:clear', function(e) {
                    updateAuditoriumButtons();
                });
                updateAuditoriumButtons();
            } else {
                showError('Ошибка загрузки', data.error || 'Неизвестная ошибка');
            }
        } catch (error) {
            showError('Ошибка сети', 'Не удалось загрузить список аудиторий');
        }
    }

    // ==================== ГРУППЫ ====================
    function updateGroupButtons() {
        const isValid = groupSelect.value && groupDateInput.value;
        groupShowButton.disabled = !isValid;
        groupExportButton.disabled = !isValid;
    }

    groupSelect.addEventListener('change', updateGroupButtons);
    groupDateInput.addEventListener('change', updateGroupButtons);

    groupTodayButton.addEventListener('click', function() {
        groupDateInput.value = new Date().toISOString().split('T')[0];
        groupDateInput.dispatchEvent(new Event('change'));
    });
    groupTomorrowButton.addEventListener('click', function() {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        groupDateInput.value = tomorrow.toISOString().split('T')[0];
        groupDateInput.dispatchEvent(new Event('change'));
    });

    groupShowButton.addEventListener('click', function() {
        if (currentMode === 'group') loadSchedule('group');
    });

    groupResetButton.addEventListener('click', function() {
        $(groupSelect).val(null).trigger('change');
        groupDateInput.value = '';
        updateGroupButtons();
        showEmptyState();
        hideError();
    });

    groupExportButton.addEventListener('click', function() {
        const group = groupSelect.value;
        const date = groupDateInput.value;
        if (!group || !date) {
            showError('Ошибка экспорта', 'Выберите группу и дату');
            return;
        }
        const dateObj = new Date(date);
        const formattedDate = dateObj.toLocaleDateString('ru-RU');
        const filename = `Расписание_${group}_${formattedDate}.txt`;
        const text = generateExportText('group');
        downloadFile(filename, text);
    });

    // ==================== ПРЕПОДАВАТЕЛИ ====================
    function updateTeacherButtons() {
        const isValid = teacherSelect.value && teacherDateInput.value;
        teacherShowButton.disabled = !isValid;
        teacherExportButton.disabled = !isValid;
    }

    teacherSelect.addEventListener('change', updateTeacherButtons);
    teacherDateInput.addEventListener('change', updateTeacherButtons);

    teacherTodayButton.addEventListener('click', function() {
        teacherDateInput.value = new Date().toISOString().split('T')[0];
        teacherDateInput.dispatchEvent(new Event('change'));
    });
    teacherTomorrowButton.addEventListener('click', function() {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        teacherDateInput.value = tomorrow.toISOString().split('T')[0];
        teacherDateInput.dispatchEvent(new Event('change'));
    });

    teacherShowButton.addEventListener('click', function() {
        if (currentMode === 'teacher') loadSchedule('teacher');
    });

    teacherResetButton.addEventListener('click', function() {
        $(teacherSelect).val(null).trigger('change');
        teacherDateInput.value = '';
        updateTeacherButtons();
        showEmptyState();
        hideError();
    });

    teacherExportButton.addEventListener('click', function() {
        const teacher = teacherSelect.value;
        const name = teacherSelect.options[teacherSelect.selectedIndex]?.text || teacher;
        const date = teacherDateInput.value;
        if (!teacher || !date) {
            showError('Ошибка экспорта', 'Выберите преподавателя и дату');
            return;
        }
        const dateObj = new Date(date);
        const formattedDate = dateObj.toLocaleDateString('ru-RU');
        const filename = `Расписание_${name}_${formattedDate}.txt`;
        const text = generateExportText('teacher');
        downloadFile(filename, text);
    });

    // ==================== АУДИТОРИИ ====================
    function updateAuditoriumButtons() {
        const isValid = auditoriumSelect.value && auditoriumDateInput.value;
        auditoriumShowButton.disabled = !isValid;
        auditoriumExportButton.disabled = !isValid;
    }

    auditoriumSelect.addEventListener('change', updateAuditoriumButtons);
    auditoriumDateInput.addEventListener('change', updateAuditoriumButtons);

    auditoriumTodayButton.addEventListener('click', function() {
        auditoriumDateInput.value = new Date().toISOString().split('T')[0];
        auditoriumDateInput.dispatchEvent(new Event('change'));
    });
    auditoriumTomorrowButton.addEventListener('click', function() {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        auditoriumDateInput.value = tomorrow.toISOString().split('T')[0];
        auditoriumDateInput.dispatchEvent(new Event('change'));
    });

    auditoriumShowButton.addEventListener('click', function() {
        if (currentMode === 'auditorium') loadSchedule('auditorium');
    });

    auditoriumResetButton.addEventListener('click', function() {
        $(auditoriumSelect).val(null).trigger('change');
        auditoriumDateInput.value = '';
        updateAuditoriumButtons();
        showEmptyState();
        hideError();
    });

    auditoriumExportButton.addEventListener('click', function() {
        const aud = auditoriumSelect.value;
        const name = auditoriumSelect.options[auditoriumSelect.selectedIndex]?.text || aud;
        const date = auditoriumDateInput.value;
        if (!aud || !date) {
            showError('Ошибка экспорта', 'Выберите аудиторию и дату');
            return;
        }
        const dateObj = new Date(date);
        const formattedDate = dateObj.toLocaleDateString('ru-RU');
        const filename = `Расписание_${name}_${formattedDate}.txt`;
        const text = generateExportText('auditorium');
        downloadFile(filename, text);
    });

    // ==================== ЗАГРУЗКА РАСПИСАНИЯ ====================
    async function loadSchedule(mode) {
        let url, body;
        if (mode === 'group') {
            const group = groupSelect.value;
            const date = groupDateInput.value;
            if (!group || !date) { showError('Ошибка', 'Выберите группу и дату'); return; }
            url = '/api/schedule';
            body = { group, date };
        } else if (mode === 'teacher') {
            const teacherId = teacherSelect.value;
            const date = teacherDateInput.value;
            if (!teacherId || !date) { showError('Ошибка', 'Выберите преподавателя и дату'); return; }
            url = '/api/schedule/teacher';
            body = { teacher_id: teacherId, date };
        } else if (mode === 'auditorium') {
            const auditoriumId = auditoriumSelect.value;
            const date = auditoriumDateInput.value;
            if (!auditoriumId || !date) { showError('Ошибка', 'Выберите аудиторию и дату'); return; }
            url = '/api/schedule/auditorium';
            body = { auditorium_id: auditoriumId, date };
        } else return;

        loadingIndicator.style.display = 'block';
        scheduleContainer.style.display = 'none';
        hideError();

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await response.json();
            loadingIndicator.style.display = 'none';
            scheduleContainer.style.display = 'block';
            if (data.success) {
                scheduleContainer.innerHTML = data.html;
            } else {
                showError('Ошибка загрузки', data.error || 'Неизвестная ошибка');
                showEmptyState();
            }
        } catch (error) {
            loadingIndicator.style.display = 'none';
            scheduleContainer.style.display = 'block';
            showError('Ошибка сети', 'Не удалось загрузить расписание');
            showEmptyState();
        }
    }

    // ==================== ЭКСПОРТ ====================
    function generateExportText(mode) {
        const scheduleElement = scheduleContainer.querySelector('.schedule-result');
        if (!scheduleElement) return '';

        let text = 'Расписание ДВГУПС\n';
        const date = scheduleElement.querySelector('h2')?.textContent.replace('Расписание на ', '') || 'Неизвестная дата';

        if (mode === 'group') {
            const group = scheduleElement.querySelector('.group-badge')?.textContent?.trim() || groupSelect.value || 'Неизвестная группа';
            text += `Группа: ${group}\nДата: ${date}\n\n`;
        } else if (mode === 'teacher') {
            const teacher = scheduleElement.querySelector('.teacher-badge')?.textContent?.trim() || teacherSelect.options[teacherSelect.selectedIndex]?.text || 'Неизвестный преподаватель';
            text += `Преподаватель: ${teacher}\nДата: ${date}\n\n`;
        } else if (mode === 'auditorium') {
            const aud = scheduleElement.querySelector('.auditorium-badge')?.textContent?.trim() || auditoriumSelect.options[auditoriumSelect.selectedIndex]?.text || 'Неизвестная аудитория';
            text += `Аудитория: ${aud}\nДата: ${date}\n\n`;
        }

        text += '========================================\n\n';
        const rows = scheduleElement.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const number = row.querySelector('.number-cell')?.textContent || '';
            const subject = row.querySelector('.subject-cell')?.textContent || '';
            const room = row.querySelector('.room-cell')?.textContent?.trim() || '';
            const teacher = row.querySelector('.teacher-cell')?.textContent || '';
            const group = row.querySelector('.group-cell')?.textContent || '';

            text += `${number}. ${subject}\n`;
            if (room && mode !== 'auditorium') text += `   Аудитория: ${room}\n`;
            if (teacher && mode !== 'teacher') text += `   Преподаватель: ${teacher}\n`;
            if (group && mode !== 'group') text += `   Группа: ${group}\n`;
            text += '\n';
        });
        return text;
    }

    function downloadFile(filename, text) {
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    // ==================== ВСПОМОГАТЕЛЬНЫЕ ====================
    function showEmptyState() {
        scheduleContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon"><i class="fas fa-calendar-times"></i></div>
                <h3>Расписание не загружено</h3>
                <p>Попробуйте выбрать другие параметры или проверьте соединение</p>
            </div>
        `;
    }

    function showError(title, message) {
        errorTitle.textContent = title;
        errorText.textContent = message;
        errorMessage.style.display = 'flex';
    }

    function hideError() {
        errorMessage.style.display = 'none';
    }

    // Enter для быстрого поиска
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            if (currentMode === 'group' && !groupShowButton.disabled) loadSchedule('group');
            else if (currentMode === 'teacher' && !teacherShowButton.disabled) loadSchedule('teacher');
            else if (currentMode === 'auditorium' && !auditoriumShowButton.disabled) loadSchedule('auditorium');
        }
    });
});