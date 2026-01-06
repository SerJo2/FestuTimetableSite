document.addEventListener('DOMContentLoaded', function() {
    // ==================== ВКЛАДКИ ====================
    const tabButtons = document.querySelectorAll('.tab-btn');
    const groupTab = document.getElementById('group-tab');
    const teacherTab = document.getElementById('teacher-tab');
    let currentMode = 'group'; // 'group' или 'teacher'

    // Обработчики переключения вкладок
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');

            // Обновляем активные вкладки
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            // Скрываем все панели
            groupTab.classList.remove('active-tab');
            teacherTab.classList.remove('active-tab');

            // Показываем выбранную панель
            if (tabId === 'group-tab') {
                groupTab.classList.add('active-tab');
                currentMode = 'group';
            } else if (tabId === 'teacher-tab') {
                teacherTab.classList.add('active-tab');
                currentMode = 'teacher';
                // При первом открытии вкладки преподавателя загружаем кафедры
                if (!departmentsLoaded) {
                    loadDepartments();
                }
            }

            // Сбрасываем расписание
            scheduleContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">
                        <i class="fas fa-calendar-plus"></i>
                    </div>
                    <h3>Расписание не загружено</h3>
                    <p>Выберите параметры и нажмите "Показать расписание"</p>
                </div>
            `;
            hideError();
        });
    });

    // ==================== ДАННЫЕ ====================
    let departmentsLoaded = false;
    const departments = {
        "126": "Автоматизированные, телекоммуникационные и электротехнические системы",
        "88": "Автоматика, телемеханика и связь",
        "72": "АмИЖТ-филиал ДВГУПС в г. Свободном",
        "70": "БАмИЖТ-филиал ДВГУПС в г. Тынде",
        "76": "Военные сообщения",
        "114": "Военный учебный центр",
        "63": "Восстановление железных дорог",
        "34": "Высшая математика",
        "81": "Вычислительная техника и компьютерная графика",
        "9": "Гидравлика и водоснабжение",
        "46": "Гражданское, предпринимательское и транспортное право",
        "102": "Железнодорожный путь",
        "103": "Изыскания и проектирование железных и автомобильных дорог",
        "91": "Иностранные языки и межкультурная коммуникация",
        "121": "Институт воздушных сообщений и мультитранспортных технологий",
        "25": "Информационные технологии и системы",
        "104": "Международные коммуникации, сервис и туризм",
        "30": "Менеджмент",
        "96": "Мосты, тоннели и подземные сооружения",
        "83": "Нефтегазовое дело, химия и экология",
        "100": "Общая, юридическая и инженерная психология",
        "118": "Перезачёт",
        "68": "ПримИЖТ-филиал ДВГУПС в г. Уссурийске",
        "71": "СахИЖТ-филиал ДВГУПС в г. Ю.-Сахалинске",
        "120": "Сетевая кафедра",
        "99": "Системы электроснабжения",
        "6": "Строительные конструкции, здания и сооружения",
        "95": "Строительство",
        "105": "Таможенное право и служебная деятельность",
        "43": "Теория и история государства и права",
        "80": "Техносферная безопасность",
        "113": "Транспорт железных дорог",
        "84": "Транспортно-технологические комплексы",
        "50": "Уголовно-правовые дисциплины",
        "123": "Управление процессами перевозок",
        "75": "Учебный военный центр",
        "49": "Факультет Воздушных Сообщений",
        "82": "Физика и теоретическая механика",
        "59": "Физическое воспитание и спорт",
        "92": "Философия, социология и право",
        "89": "Финансы и бухгалтерский учёт",
        "108": "ФСПО БАмИЖТ-филиал ДВГУПС в г. Тынде",
        "111": "ФСПО ПримИЖТ-филиал ДВГУПС",
        "115": "ФСПО СМУ АмИЖТ-филиал ДВГУПС в г. Свободном",
        "110": "ФСПОАмИЖТ-филиал ДВГУПС в г. Свободном",
        "109": "Хабаровский техникум железнодорожного транспорта",
        "112": "Экономика и коммерция",
        "27": "Электротехника, электроника и электромеханика",
        "73": "ЮЯИЖТ-филиал ДВГУПС в г. Нерюнгри"
    };

    // ==================== DOM ЭЛЕМЕНТЫ ====================
    // Группы
    const instituteSelect = document.getElementById('institute-select');
    const groupSelect = document.getElementById('group-select');
    const groupDateInput = document.getElementById('group-date-input');
    const groupShowButton = document.getElementById('group-show-btn');
    const groupResetButton = document.getElementById('group-reset-btn');
    const groupExportButton = document.getElementById('group-export-btn');
    const groupTodayButton = document.getElementById('group-today-btn');
    const groupTomorrowButton = document.getElementById('group-tomorrow-btn');
    const groupCount = document.getElementById('group-count');

    // Преподаватели
    const departmentSelect = document.getElementById('department-select');
    const teacherSelect = document.getElementById('teacher-select');
    const teacherDateInput = document.getElementById('teacher-date-input');
    const teacherShowButton = document.getElementById('teacher-show-btn');
    const teacherResetButton = document.getElementById('teacher-reset-btn');
    const teacherExportButton = document.getElementById('teacher-export-btn');
    const teacherTodayButton = document.getElementById('teacher-today-btn');
    const teacherTomorrowButton = document.getElementById('teacher-tomorrow-btn');
    const teacherCount = document.getElementById('teacher-count');

    // Общие элементы
    const scheduleContainer = document.getElementById('schedule-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const errorTitle = document.getElementById('error-title');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const statusUpdate = document.getElementById('status-update');

    // ==================== ФУНКЦИИ ====================

    // Установка даты по умолчанию
    function setDefaultDate() {
        const today = new Date().toISOString().split('T')[0];
        groupDateInput.value = today;
        teacherDateInput.value = today;
    }

    // Проверка статуса сервера
    async function checkServerStatus() {
        try {
            const response = await fetch('/api/health');
            if (response.ok) {
                statusDot.classList.remove('offline');
                statusDot.classList.add('online');
                statusText.textContent = 'Система онлайн';
                statusUpdate.textContent = new Date().toLocaleTimeString('ru-RU');
            } else {
                throw new Error('Ошибка сервера');
            }
        } catch (error) {
            statusDot.classList.remove('online');
            statusDot.classList.add('offline');
            statusText.textContent = 'Система офлайн';
            statusUpdate.textContent = 'Нет связи с сервером';
        }
    }

    // Загрузка кафедр
    function loadDepartments() {
        departmentSelect.innerHTML = '<option value="">-- Выберите кафедру --</option>';

        Object.entries(departments).forEach(([id, name]) => {
            const option = document.createElement('option');
            option.value = id;
            option.textContent = name;
            departmentSelect.appendChild(option);
        });

        departmentsLoaded = true;
    }

    // Загрузка преподавателей для кафедры
    async function loadTeachers(departmentId) {
        teacherSelect.innerHTML = '<option value="">Загрузка преподавателей...</option>';
        teacherSelect.disabled = true;
        teacherShowButton.disabled = true;
        teacherExportButton.disabled = true;

        try {
            const response = await fetch(`/api/teachers/${departmentId}`);
            const data = await response.json();

            if (data.success) {
                teacherSelect.innerHTML = '<option value="">-- Выберите преподавателя --</option>';

                data.teachers.forEach(teacher => {
                    const option = document.createElement('option');
                    option.value = teacher.id;
                    option.textContent = teacher.name;
                    teacherSelect.appendChild(option);
                });

                teacherSelect.disabled = false;
                teacherCount.innerHTML = `<i class="fas fa-info-circle"></i> Преподавателей: ${data.teachers.length}`;
            } else {
                teacherSelect.innerHTML = '<option value="">Ошибка загрузки</option>';
                showError('Ошибка загрузки', data.error || 'Неизвестная ошибка');
            }
        } catch (error) {
            teacherSelect.innerHTML = '<option value="">Ошибка соединения</option>';
            showError('Ошибка сети', 'Не удалось загрузить список преподавателей');
        }
    }

    // ==================== ОБРАБОТЧИКИ СОБЫТИЙ ДЛЯ ГРУПП ====================

    // Загрузка групп для выбранного института
    instituteSelect.addEventListener('change', async function() {
        const instituteId = this.value;

        if (!instituteId) {
            groupSelect.innerHTML = '<option value="">-- Сначала выберите институт --</option>';
            groupSelect.disabled = true;
            groupShowButton.disabled = true;
            groupExportButton.disabled = true;
            groupCount.innerHTML = '<i class="fas fa-info-circle"></i> Групп: 0';
            return;
        }

        groupSelect.innerHTML = '<option value="">Загрузка групп...</option>';
        groupSelect.disabled = true;

        try {
            const response = await fetch(`/api/groups/${instituteId}`);
            const data = await response.json();

            if (data.success) {
                groupSelect.innerHTML = '<option value="">-- Выберите группу --</option>';

                data.groups.forEach(group => {
                    const option = document.createElement('option');
                    option.value = group;
                    option.textContent = group;
                    groupSelect.appendChild(option);
                });

                groupSelect.disabled = false;
                groupCount.innerHTML = `<i class="fas fa-info-circle"></i> Групп: ${data.groups.length}`;
            } else {
                groupSelect.innerHTML = '<option value="">Ошибка загрузки групп</option>';
                showError('Ошибка загрузки', data.error || 'Неизвестная ошибка');
            }
        } catch (error) {
            groupSelect.innerHTML = '<option value="">Ошибка соединения</option>';
            showError('Ошибка сети', 'Не удалось загрузить список групп');
        }
    });

    // Обновление состояния кнопок для групп
    groupSelect.addEventListener('change', updateGroupButtons);
    groupDateInput.addEventListener('change', updateGroupButtons);

    function updateGroupButtons() {
        const isValid = instituteSelect.value && groupSelect.value && groupDateInput.value;
        groupShowButton.disabled = !isValid;
        groupExportButton.disabled = !isValid;
    }

    // Кнопки сегодня/завтра для групп
    groupTodayButton.addEventListener('click', function() {
        const today = new Date().toISOString().split('T')[0];
        groupDateInput.value = today;
        triggerGroupDateChange();
    });

    groupTomorrowButton.addEventListener('click', function() {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        groupDateInput.value = tomorrow.toISOString().split('T')[0];
        triggerGroupDateChange();
    });

    function triggerGroupDateChange() {
        const event = new Event('change');
        groupDateInput.dispatchEvent(event);
    }

    // Кнопка "Показать расписание" для групп
    groupShowButton.addEventListener('click', function() {
        if (currentMode === 'group') {
            loadSchedule('group');
        }
    });

    // Кнопка "Сбросить" для групп
    groupResetButton.addEventListener('click', function() {
        instituteSelect.value = '';
        groupSelect.innerHTML = '<option value="">-- Сначала выберите институт --</option>';
        groupSelect.disabled = true;
        groupDateInput.value = '';
        groupShowButton.disabled = true;
        groupExportButton.disabled = true;
        groupCount.innerHTML = '<i class="fas fa-info-circle"></i> Групп: 0';
        showEmptyState();
        hideError();
    });

    // Кнопка "Экспорт" для групп
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

        const scheduleText = generateExportText();
        downloadFile(filename, scheduleText);
    });

    // ==================== ОБРАБОТЧИКИ СОБЫТИЙ ДЛЯ ПРЕПОДАВАТЕЛЕЙ ====================

    // Загрузка преподавателей при выборе кафедры
    departmentSelect.addEventListener('change', function() {
        const departmentId = this.value;

        if (!departmentId) {
            teacherSelect.innerHTML = '<option value="">-- Сначала выберите кафедру --</option>';
            teacherSelect.disabled = true;
            teacherShowButton.disabled = true;
            teacherExportButton.disabled = true;
            teacherCount.innerHTML = '<i class="fas fa-info-circle"></i> Преподавателей: 0';
            return;
        }

        loadTeachers(departmentId);
    });

    // Обновление состояния кнопок для преподавателей
    teacherSelect.addEventListener('change', updateTeacherButtons);
    teacherDateInput.addEventListener('change', updateTeacherButtons);

    function updateTeacherButtons() {
        const isValid = departmentSelect.value && teacherSelect.value && teacherDateInput.value;
        teacherShowButton.disabled = !isValid;
        teacherExportButton.disabled = !isValid;
    }

    // Кнопки сегодня/завтра для преподавателей
    teacherTodayButton.addEventListener('click', function() {
        const today = new Date().toISOString().split('T')[0];
        teacherDateInput.value = today;
        triggerTeacherDateChange();
    });

    teacherTomorrowButton.addEventListener('click', function() {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        teacherDateInput.value = tomorrow.toISOString().split('T')[0];
        triggerTeacherDateChange();
    });

    function triggerTeacherDateChange() {
        const event = new Event('change');
        teacherDateInput.dispatchEvent(event);
    }

    // Кнопка "Показать расписание" для преподавателей
    teacherShowButton.addEventListener('click', function() {
        if (currentMode === 'teacher') {
            loadSchedule('teacher');
        }
    });

    // Кнопка "Сбросить" для преподавателей
    teacherResetButton.addEventListener('click', function() {
        departmentSelect.value = '';
        teacherSelect.innerHTML = '<option value="">-- Сначала выберите кафедру --</option>';
        teacherSelect.disabled = true;
        teacherDateInput.value = '';
        teacherShowButton.disabled = true;
        teacherExportButton.disabled = true;
        teacherCount.innerHTML = '<i class="fas fa-info-circle"></i> Преподавателей: 0';
        showEmptyState();
        hideError();
    });

    // Кнопка "Экспорт" для преподавателей
    teacherExportButton.addEventListener('click', function() {
        const teacherId = teacherSelect.value;
        const teacherName = teacherSelect.options[teacherSelect.selectedIndex].text;
        const date = teacherDateInput.value;

        if (!teacherId || !date) {
            showError('Ошибка экспорта', 'Выберите преподавателя и дату');
            return;
        }

        const dateObj = new Date(date);
        const formattedDate = dateObj.toLocaleDateString('ru-RU');
        const filename = `Расписание_${teacherName}_${formattedDate}.txt`;

        const scheduleText = generateExportText();
        downloadFile(filename, scheduleText);
    });

    // ==================== ОБЩИЕ ФУНКЦИИ ====================

    // Загрузка расписания
    async function loadSchedule(mode) {
        let url, body;

        if (mode === 'group') {
            const group = groupSelect.value;
            const date = groupDateInput.value;

            if (!group || !date) {
                showError('Ошибка', 'Выберите группу и дату');
                return;
            }

            url = '/api/schedule';
            body = { group, date };
        } else if (mode === 'teacher') {
            const teacherId = teacherSelect.value;
            const date = teacherDateInput.value;

            if (!teacherId || !date) {
                showError('Ошибка', 'Выберите преподавателя и дату');
                return;
            }

            url = '/api/schedule/teacher';
            body = { teacher_id: teacherId, date };
        } else {
            return;
        }

        // Показываем индикатор загрузки
        loadingIndicator.style.display = 'block';
        scheduleContainer.style.display = 'none';
        hideError();

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
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

    // Генерация текста для экспорта
    function generateExportText() {
        const scheduleElement = scheduleContainer.querySelector('.schedule-result');
        if (!scheduleElement) return '';

        let text = '';

        if (currentMode === 'group') {
            const group = scheduleElement.querySelector('.group-badge')?.textContent || 'Неизвестная группа';
            const date = scheduleElement.querySelector('h2')?.textContent.replace('Расписание на ', '') || 'Неизвестная дата';

            text = `Расписание ДВГУПС\n`;
            text += `Группа: ${group}\n`;
            text += `Дата: ${date}\n`;
        } else if (currentMode === 'teacher') {
            const teacher = scheduleElement.querySelector('.teacher-badge')?.textContent ||
                          teacherSelect.options[teacherSelect.selectedIndex].text;
            const date = scheduleElement.querySelector('h2')?.textContent.replace('Расписание на ', '') || 'Неизвестная дата';

            text = `Расписание ДВГУПС\n`;
            text += `Преподаватель: ${teacher}\n`;
            text += `Дата: ${date}\n`;
        }

        text += `\n========================================\n\n`;

        const rows = scheduleElement.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const number = row.querySelector('.number-cell')?.textContent || '';
            const time = row.querySelector('.time-cell')?.textContent || '';
            const subject = row.querySelector('.subject-cell')?.textContent || '';
            const room = row.querySelector('.room-cell')?.textContent || '';
            const teacher = row.querySelector('.teacher-cell')?.textContent || '';
            const group = row.querySelector('.group-cell')?.textContent || '';

            text += `${number}. ${time}\n`;
            text += `   Дисциплина: ${subject}\n`;

            if (room) text += `   Аудитория: ${room}\n`;
            if (teacher && currentMode === 'group') text += `   Преподаватель: ${teacher}\n`;
            if (group && currentMode === 'teacher') text += `   Группа: ${group}\n`;

            text += `\n`;
        });

        return text;
    }

    // Функция для скачивания файла
    function downloadFile(filename, text) {
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    // Показать состояние "пусто"
    function showEmptyState() {
        scheduleContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-calendar-times"></i>
                </div>
                <h3>Расписание не загружено</h3>
                <p>Попробуйте выбрать другие параметры или проверьте соединение</p>
            </div>
        `;
    }

    // Показать ошибку
    function showError(title, message) {
        errorTitle.textContent = title;
        errorText.textContent = message;
        errorMessage.style.display = 'flex';
    }

    // Скрыть ошибку
    function hideError() {
        errorMessage.style.display = 'none';
    }

    // ==================== ИНИЦИАЛИЗАЦИЯ ====================
    setDefaultDate();
    checkServerStatus();

    // Проверять статус каждые 30 секунд
    setInterval(checkServerStatus, 30000);

    // Разрешаем Enter на форме
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            if (currentMode === 'group' && !groupShowButton.disabled) {
                loadSchedule('group');
            } else if (currentMode === 'teacher' && !teacherShowButton.disabled) {
                loadSchedule('teacher');
            }
        }
    });
});