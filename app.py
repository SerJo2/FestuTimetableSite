from flask import Flask, render_template, request, jsonify
from flask_caching import Cache
from datetime import datetime
from festutimetable import TimetableService
from festutimetable.FestuApi import DateNotFoundError, GroupNotFoundError
import requests
import sys
import os

application = Flask(__name__)
cache = Cache(application, config={'CACHE_TYPE': 'simple'})

from institute_groups import INSTITUTES, INSTITUTE_GROUPS

timetable_service = TimetableService()

# Кафедры для преподавателей
DEPARTMENTS = {
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
}

# Сессия для запросов к API ДВГУПС
session = requests.Session()
session.cookies.update({
    '_ym_uid': '1724630000439844202',
    '_ym_d': '1756719934',
    'c463f467348ffb9feac9c0a5f4225ac9': 't8oellqo7249ojj2k88tp2i2jl',
    '_ym_isad': '1'
})


@cache.cached(timeout=300)
@application.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', institutes=INSTITUTES)


@application.route('/api/groups/<institute_id>')
def get_groups(institute_id):
    """Получить список групп для выбранного института"""
    try:
        institute_id = int(institute_id)
        if institute_id in INSTITUTE_GROUPS:
            return jsonify({
                'success': True,
                'groups': INSTITUTE_GROUPS[institute_id]
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Институт с ID {institute_id} не найден'
            }), 404
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Неверный ID института'
        }), 400


@application.route('/api/departments')
def get_departments():
    """Получить список кафедр"""
    try:
        departments_list = [{'id': k, 'name': v} for k, v in DEPARTMENTS.items()]
        return jsonify({
            'success': True,
            'departments': departments_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при получении кафедр: {str(e)}'
        }), 500


@application.route('/api/teachers/<department_id>')
def get_teachers(department_id):
    """Получить список преподавателей для выбранной кафедры"""
    try:
        if department_id not in DEPARTMENTS:
            return jsonify({
                'success': False,
                'error': f'Кафедра с ID {department_id} не найдена'
            }), 404

        # Запрос к API ДВГУПС для получения преподавателей
        headers = {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://dvgups.ru',
            'Referer': 'https://dvgups.ru/index.php?Itemid=1246&option=com_timetable&view=newtimetable',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        params = {
            'Itemid': '1246',
            'option': 'com_timetable',
            'view': 'newtimetable',
        }

        data = {
            'KafID': department_id,
        }

        response = session.post('https://dvgups.ru/index.php',
                                params=params,
                                headers=headers,
                                data=data,
                                timeout=10)

        if response.status_code == 200:
            # Парсинг HTML для получения списка преподавателей
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            print(response.text)
            teachers = []
            select_element = soup

            if select_element:
                options = select_element.find_all('option')
                for option in options[1:]:  # Пропускаем первый пустой option
                    teacher_id = option.get('value')
                    teacher_name = option.get_text(strip=True)
                    if teacher_id and teacher_name and teacher_id != '0':
                        teachers.append({
                            'id': teacher_id,
                            'name': teacher_name
                        })

            return jsonify({
                'success': True,
                'teachers': teachers
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Ошибка API: {response.status_code}'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при получении преподавателей: {str(e)}'
        }), 500


@application.route('/api/schedule', methods=['POST'])
def get_schedule():
    """Получить расписание для выбранной группы и даты"""
    try:
        data = request.get_json()
        group = data.get('group', '').strip()
        date_str = data.get('date', '')

        # Валидация
        if not group:
            return jsonify({
                'success': False,
                'error': 'Выберите группу'
            }), 400

        if not date_str:
            return jsonify({
                'success': False,
                'error': 'Выберите дату'
            }), 400

        # Преобразуем дату из формата YYYY-MM-DD в DD.MM.YYYY
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d.%m.%Y')
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Неверный формат даты'
            }), 400

        # Получаем расписание
        try:
            day_timetable = timetable_service.get_timetable_by_day(group, formatted_date)

            # Преобразуем в удобный формат
            schedule_data = []
            for lecture in day_timetable.lectures:
                schedule_data.append({
                    'number': lecture.number,
                    'name': lecture.name,
                    'classroom': lecture.classroom,
                    'teacher': lecture.teacher,
                    'group': lecture.group
                })

            return jsonify({
                'success': True,
                'date': formatted_date,
                'group': group,
                'schedule': schedule_data,
                'html': generate_group_schedule_html(schedule_data, group, formatted_date)
            })

        except GroupNotFoundError:
            return jsonify({
                'success': False,
                'error': f'Группа "{group}" не найдена в системе'
            }), 404
        except DateNotFoundError:
            return jsonify({
                'success': False,
                'error': f'Расписание на {formatted_date} не найдено'
            }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Ошибка при получении расписания: {str(e)}'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500


@application.route('/api/schedule/teacher', methods=['POST'])
def get_teacher_schedule():
    """Получить расписание для выбранного преподователя"""
    try:
        data = request.get_json()
        teacher_id = data.get('teacher_id', '').strip()
        date_str = data.get('date', '')

        # Валидация
        if not teacher_id:
            return jsonify({
                'success': False,
                'error': 'Выберите группу'
            }), 400

        if not date_str:
            return jsonify({
                'success': False,
                'error': 'Выберите дату'
            }), 400

        # Преобразуем дату из формата YYYY-MM-DD в DD.MM.YYYY
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d.%m.%Y')
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Неверный формат даты'
            }), 400

        # Получаем расписание
        try:
            day_timetable = timetable_service.get_timetable_by_day_by_teacher(teacher_id, formatted_date)

            # Преобразуем в удобный формат
            schedule_data = []
            for lecture in day_timetable.lectures:
                schedule_data.append({
                    'number': lecture.number,
                    'name': lecture.name,
                    'classroom': lecture.classroom,
                    'teacher': lecture.teacher,
                    'group': lecture.group
                })

            return jsonify({
                'success': True,
                'date': formatted_date,
                'teacher_id': teacher_id,
                'schedule': schedule_data,
                'html': generate_group_schedule_html(schedule_data, lecture.group, formatted_date)
            })

        except GroupNotFoundError:
            return jsonify({
                'success': False,
                'error': f'Учитель "{teacher_id}" не найдена в системе'
            }), 404
        except DateNotFoundError:
            return jsonify({
                'success': False,
                'error': f'Расписание на {formatted_date} не найдено'
            }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Ошибка при получении расписания: {str(e)}'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500


def generate_group_schedule_html(schedule_data, group, date):
    """Генерация HTML таблицы расписания для группы"""
    if not schedule_data:
        return '''
        <div class="no-schedule">
            <div class="no-schedule-icon">
                <i class="fas fa-calendar-times"></i>
            </div>
            <h3>Занятий нет</h3>
            <p>На выбранную дату у группы нет занятий</p>
        </div>
        '''

    day_number = datetime.strptime(date, '%d.%m.%Y').isocalendar()[1]
    week_type = "четная" if day_number % 2 == 0 else "нечетная"

    html = f'''
    <div class="schedule-result">
        <div class="schedule-header">
            <h2><i class="fas fa-calendar-alt"></i> Расписание на {date}</h2>
            <div class="schedule-meta">
                <span class="group-badge">
                    <i class="fas fa-users"></i> {group}
                </span>
                <span class="week-badge">
                    <i class="fas fa-calendar-week"></i> {week_type} неделя
                </span>
            </div>
        </div>

        <div class="schedule-table-container">
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th><i class="fas fa-hashtag"></i> №</th>
                        <th><i class="fas fa-book"></i> Дисциплина</th>
                        <th><i class="fas fa-door-open"></i> Аудитория</th>
                        <th><i class="fa-solid fa-chalkboard-user"></i> Преподаватель</th>
                        <th><i class="fas fa-users"></i> Группы</th>
                    </tr>
                </thead>
                <tbody>
    '''

    for i, lesson in enumerate(schedule_data):
        row_class = 'even' if i % 2 == 0 else 'odd'

        html += f'''
                    <tr class="{row_class}">
                        <td class="number-cell">{lesson['number']}</td>
                        <td class="subject-cell">{lesson['name']}</td>
                        <td class="room-cell">
                            <span class="room-badge">
                                <i class="fas fa-building"></i> {lesson['classroom']}
                            </span>
                        </td>
                        <td class="teacher-cell">{lesson['teacher']}</td>
                        <td>{lesson['group']}</td>
                    </tr>
        '''

    html += f'''
                </tbody>
            </table>

            <div class="schedule-summary">
                <div class="summary-item">
                    <i class="fas fa-list-ol"></i>
                    <span>Всего пар: <strong>{len(schedule_data)}</strong></span>
                </div>
                <div class="summary-item">
                    <i class="fas fa-university"></i>
                    <span>Аудитории: <strong>{len(set(l['classroom'] for l in schedule_data if l['classroom']))}</strong></span>
                </div>
                <div class="summary-item">
                    <i class="fas fa-user-tie"></i>
                    <span>Преподаватели: <strong>{len(set(l['teacher'] for l in schedule_data if l['teacher']))}</strong></span>
                </div>
            </div>
        </div>

        <div class="schedule-footer">
            <p class="update-info">
                <i class="fas fa-sync-alt"></i> Данные обновлены: {datetime.now().strftime('%d.%m.%Y %H:%M')}
            </p>
            <p class="source-info">
                <i class="fas fa-database"></i> Источник: официальное расписание ДВГУПС
            </p>
        </div>
    </div>
    '''

    return html


def generate_teacher_schedule_html(schedule_data, teacher_name, date):
    """Генерация HTML таблицы расписания для преподавателя"""
    if not schedule_data:
        return '''
        <div class="no-schedule">
            <div class="no-schedule-icon">
                <i class="fas fa-calendar-times"></i>
            </div>
            <h3>Занятий нет</h3>
            <p>На выбранную дату у преподавателя нет занятий</p>
        </div>
        '''

    day_number = datetime.strptime(date, '%d.%m.%Y').isocalendar()[1]
    week_type = "четная" if day_number % 2 == 0 else "нечетная"

    html = f'''
    <div class="schedule-result">
        <div class="schedule-header">
            <h2><i class="fas fa-calendar-alt"></i> Расписание на {date}</h2>
            <div class="schedule-meta">
                <span class="teacher-badge">
                    <i class="fas fa-user-tie"></i> {teacher_name}
                </span>
                <span class="week-badge">
                    <i class="fas fa-calendar-week"></i> {week_type} неделя
                </span>
            </div>
        </div>

        <div class="schedule-table-container">
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th><i class="fas fa-hashtag"></i> №</th>
                        <th><i class="fas fa-clock"></i> Время</th>
                        <th><i class="fas fa-book"></i> Дисциплина</th>
                        <th><i class="fas fa-users"></i> Группы</th>
                        <th><i class="fas fa-door-open"></i> Аудитория</th>
                    </tr>
                </thead>
                <tbody>
    '''

    for i, lesson in enumerate(schedule_data):
        row_class = 'even' if i % 2 == 0 else 'odd'

        html += f'''
                    <tr class="{row_class}">
                        <td class="number-cell">{lesson['number']}</td>
                        <td class="time-cell">{lesson['time']}</td>
                        <td class="subject-cell">{lesson['subject']}</td>
                        <td class="group-cell">{lesson['groups']}</td>
                        <td class="room-cell">
                            <span class="room-badge">
                                <i class="fas fa-building"></i> {lesson['classroom']}
                            </span>
                        </td>
                    </tr>
        '''

    html += f'''
                </tbody>
            </table>

            <div class="schedule-summary">
                <div class="summary-item">
                    <i class="fas fa-list-ol"></i>
                    <span>Всего пар: <strong>{len(schedule_data)}</strong></span>
                </div>
                <div class="summary-item">
                    <i class="fas fa-users"></i>
                    <span>Групп: <strong>{len(set(l['groups'] for l in schedule_data if l['groups']))}</strong></span>
                </div>
                <div class="summary-item">
                    <i class="fas fa-university"></i>
                    <span>Аудитории: <strong>{len(set(l['classroom'] for l in schedule_data if l['classroom']))}</strong></span>
                </div>
            </div>
        </div>

        <div class="schedule-footer">
            <p class="update-info">
                <i class="fas fa-sync-alt"></i> Данные обновлены: {datetime.now().strftime('%d.%m.%Y %H:%M')}
            </p>
            <p class="source-info">
                <i class="fas fa-database"></i> Источник: официальное расписание ДВГУПС
            </p>
        </div>
    </div>
    '''

    return html


@application.route('/api/health')
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({
        'status': 'ok',
        'service': 'FESTU Schedule API',
        'timestamp': datetime.now().isoformat()
    })


@application.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@application.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    application.run(debug=True, port=5000)