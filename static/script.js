document.addEventListener('DOMContentLoaded', function() {
    // DOM элементы
    const instituteSelect = document.getElementById('institute-select');
    const groupSelect = document.getElementById('group-select');
    const dateInput = document.getElementById('date-input');
    const showButton = document.getElementById('show-schedule-btn');
    const resetButton = document.getElementById('reset-btn');
    const exportButton = document.getElementById('export-btn');
    const todayButton = document.getElementById('today-btn');
    const tomorrowButton = document.getElementById('tomorrow-btn');
    const scheduleContainer = document.getElementById('schedule-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const errorTitle = document.getElementById('error-title');
    const groupCount = document.getElementById('group-count');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const statusUpdate = document.getElementById('status-update');

    // Установка даты по умолчанию
    function setDefaultDate() {
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);

        dateInput.value = today.toISOString().split('T')[0];
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

    // Загрузка групп для выбранного института
    instituteSelect.addEventListener('change', async function() {
        const instituteId = this.value;

        if (!instituteId) {
            groupSelect.innerHTML = '<option value="">-- Сначала выберите институт --</option>';
            groupSelect.disabled = true;
            showButton.disabled = true;
            groupCount.innerHTML = '<i class="fas fa-info-circle"></i> Групп: 0';
            return;
        }

        // Показываем загрузку
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

    // Обновление состояния кнопки "Показать"
    groupSelect.addEventListener('change', function() {
        const isValid = instituteSelect.value && groupSelect.value && dateInput.value;
        showButton.disabled = !isValid;
        exportButton.disabled = !isValid;
    });

    dateInput.addEventListener('change', function() {
        const isValid = instituteSelect.value && groupSelect.value && dateInput.value;
        showButton.disabled = !isValid;
        exportButton.disabled = !isValid;
    });

    // Кнопка "Сегодня"
    todayButton.addEventListener('click', function() {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
        triggerDateChange();
    });

    // Кнопка "Завтра"
    tomorrowButton.addEventListener('click', function() {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.value = tomorrow.toISOString().split('T')[0];
        triggerDateChange();
    });

    // Функция для триггера события change у dateInput
    function triggerDateChange() {
        const event = new Event('change');
        dateInput.dispatchEvent(event);
    }

    // Кнопка "Показать расписание"
    showButton.addEventListener('click', loadSchedule);

    // Кнопка "Сбросить"
    resetButton.addEventListener('click', function() {
        instituteSelect.value = '';
        groupSelect.innerHTML = '<option value="">-- Сначала выберите институт --</option>';
        groupSelect.disabled = true;
        setDefaultDate();
        showButton.disabled = true;
        exportButton.disabled = true;
        groupCount.innerHTML = '<i class="fas fa-info-circle"></i> Групп: 0';
        scheduleContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-calendar-plus"></i>
                </div>
                <h3>Расписание не загружено</h3>
                <p>Выберите институт, группу и дату, затем нажмите "Показать расписание"</p>
                <div class="empty-tips">
                    <div class="tip">
                        <i class="fas fa-lightbulb"></i>
                        <span>Институт → Группа → Дата → Показать</span>
                    </div>
                    <div class="tip">
                        <i class="fas fa-clock"></i>
                        <span>Данные берутся из официальной системы ДВГУПС</span>
                    </div>
                </div>
            </div>
        `;
        hideError();
    });

    // Кнопка "Экспорт"
    exportButton.addEventListener('click', function() {
        const group = groupSelect.value;
        const date = dateInput.value;

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

    // Загрузка расписания
    async function loadSchedule() {
        const group = groupSelect.value;
        const date = dateInput.value;

        // Валидация
        if (!group) {
            showError('Ошибка', 'Выберите группу');
            return;
        }

        if (!date) {
            showError('Ошибка', 'Выберите дату');
            return;
        }

        // Показываем индикатор загрузки
        loadingIndicator.style.display = 'block';
        scheduleContainer.style.display = 'none';
        hideError();

        try {
            const response = await fetch('/api/schedule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    group: group,
                    date: date
                })
            });

            const data = await response.json();

            // Скрываем индикатор загрузки
            loadingIndicator.style.display = 'none';
            scheduleContainer.style.display = 'block';

            if (data.success) {
                // Отображаем расписание
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

        const group = scheduleElement.querySelector('.group-badge').textContent;
        const date = scheduleElement.querySelector('h2').textContent.replace('Расписание на ', '');

        let text = `Расписание ДВГУПС\n`;
        text += `Группа: ${group}\n`;
        text += `Дата: ${date}\n`;
        text += `\n`;
        text += `========================================\n\n`;

        const rows = scheduleElement.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const time = row.querySelector('.time-cell').textContent;
            const number = row.querySelector('.number-cell').textContent;
            const subject = row.querySelector('.subject-cell').textContent;
            const room = row.querySelector('.room-cell').textContent;
            const teacher = row.querySelector('.teacher-cell').textContent;

            text += `${number}. ${time}\n`;
            text += `   Дисциплина: ${subject}\n`;
            text += `   Аудитория: ${room}\n`;
            text += `   Преподаватель: ${teacher}\n`;
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

    // Инициализация
    setDefaultDate();
    checkServerStatus();

    // Проверять статус каждые 30 секунд
    setInterval(checkServerStatus, 30000);

    // Разрешаем Enter на форме
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !showButton.disabled) {
            loadSchedule();
        }
    });
});