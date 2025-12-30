from flask import Flask, render_template, request, jsonify
from datetime import datetime
from festutimetable import TimetableService
from festutimetable.FestuApi import DateNotFoundError, GroupNotFoundError
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'festu_timetable_lib'))

app = Flask(__name__)

from institute_groups import INSTITUTES, INSTITUTE_GROUPS

timetable_service = TimetableService()


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', institutes=INSTITUTES)


@app.route('/api/groups/<institute_id>')
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


@app.route('/api/schedule', methods=['POST'])
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
                    'time': lecture.time,
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
                'html': generate_schedule_html(schedule_data, group, formatted_date)
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


def generate_schedule_html(schedule_data, group, date):
    """Генерация HTML таблицы расписания"""

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
                        <th><i class="fas fa-clock"></i> Время</th>
                        <th><i class="fas fa-hashtag"></i> №</th>
                        <th><i class="fas fa-book"></i> Дисциплина</th>
                        <th><i class="fas fa-door-open"></i> Аудитория</th>
                        <th><i class="fas fa-chalkboard-teacher"></i> Преподаватель</th>
                    </tr>
                </thead>
                <tbody>
    '''

    for i, lesson in enumerate(schedule_data):
        # Чередуем цвета строк для лучшей читаемости
        row_class = 'even' if i % 2 == 0 else 'odd'

        html += f'''
                    <tr class="{row_class}">
                        <td class="time-cell">{lesson['time']}</td>
                        <td class="number-cell">{lesson['number']}</td>
                        <td class="subject-cell">{lesson['name']}</td>
                        <td class="room-cell">
                            <span class="room-badge">
                                <i class="fas fa-building"></i> {lesson['classroom']}
                            </span>
                        </td>
                        <td class="teacher-cell">{lesson['teacher']}</td>
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


@app.route('/api/health')
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({
        'status': 'ok',
        'service': 'FESTU Schedule API',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)