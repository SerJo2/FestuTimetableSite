import traceback
from pprint import pprint

from flask import Flask, render_template, request, jsonify, render_template_string
from flask_caching import Cache
from datetime import datetime, timedelta
from festutimetable import TimetableService
from festutimetable.FestuApi import DateNotFoundError, GroupNotFoundError
import requests
import sys
import os
from flask import send_from_directory
from json_timetable_reader import group_timetable_reader, teacher_timetable_reader, classroom_timetable_reader

application = Flask(__name__)
cache = Cache(application, config={'CACHE_TYPE': 'simple'})

from institute_groups import INSTITUTES, INSTITUTE_GROUPS


timetable_service = TimetableService()
# аудитории и их id
AUDITORIUMS = {
    "а. 10": "а. 10",
    "а. 15": "а. 15",
    "а. 17": "а. 17",
    "а. 18": "а. 18",
    "а. 19": "а. 19",
    "а. 21": "а. 21",
    "а. 25": "а. 25",
    "а. 26": "а. 26",
    "а. 27": "а. 27",
    "а. 29": "а. 29",
    "а. 31": "а. 31",
    "а. 33": "а. 33",
    "а. 5": "а. 5",
    "а. 7": "а. 7",
    "а.  101": "а.  101",
    "а.  101/1": "а.  101/1",
    "а.  104/1": "а.  104/1",
    "а.  104/2": "а.  104/2",
    "а.  116": "а.  116",
    "а.  201": "а.  201",
    "а.  201/1": "а.  201/1",
    "а.  208": "а.  208",
    "а.  211": "а.  211",
    "а.  222": "а.  222",
    "а.  225": "а.  225",
    "а.  247": "а.  247",
    "а.  252": "а.  252",
    "а.  318": "а.  318",
    "а.  320": "а.  320",
    "а.  326": "а.  326",
    "а.  328": "а.  328",
    "а.  332": "а.  332",
    "а.  335": "а.  335",
    "а.  356": "а.  356",
    "а.  362": "а.  362",
    "а.  364": "а.  364",
    "а.  408": "а.  408",
    "а.  424": "а.  424",
    "а.  426": "а.  426",
    "а.  428": "а.  428",
    "а.  433": "а.  433",
    "а.  443": "а.  443",
    "а.  450": "а.  450",
    "а.  452": "а.  452",
    "а. 1201": "а. 1201",
    "а. 1203": "а. 1203",
    "а. 1403": "а. 1403",
    "а. 1601": "а. 1601",
    "а. 1703": "а. 1703",
    "а. 1807": "а. 1807",
    "а. 2200": "а. 2200",
    "а. 2202": "а. 2202",
    "а. 2302": "а. 2302",
    "а. 2402": "а. 2402",
    "а. 2800": "а. 2800",
    "а. 2804": "а. 2804",
    "а. 3108": "а. 3108",
    "а. 3118": "а. 3118",
    "а. 3122": "а. 3122",
    "а. 3211": "а. 3211",
    "а. 3217": "а. 3217",
    "а. 3223": "а. 3223",
    "а. 3228": "а. 3228",
    "а. 3229": "а. 3229",
    "а. 3230": "а. 3230",
    "а. 3243": "а. 3243",
    "а. 3245": "а. 3245",
    "а. 3246": "а. 3246",
    "а. 3248": "а. 3248",
    "а. 3301": "а. 3301",
    "а. 3328": "а. 3328",
    "а. 3329": "а. 3329",
    "а. 3330": "а. 3330",
    "а. 3337": "а. 3337",
    "а. 3339": "а. 3339",
    "а. 3346": "а. 3346",
    "а. 3415": "а. 3415",
    "а. 3417": "а. 3417",
    "а. 3421": "а. 3421",
    "а. 3431": "а. 3431",
    "а. 3435": "а. 3435",
    "а. 3528": "а. 3528",
    "а. 3532": "а. 3532",
    "а. 3534": "а. 3534",
    "а. 3536": "а. 3536",
    "а. 3537": "а. 3537",
    "а. 3541а": "а. 3541а",
    "а.    1": "а.    1",
    "а.    8": "а.    8",
    "а.   12": "а.   12",
    "а.   70": "а.   70",
    "дистанционно": "дистанционно"
}

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


@application.route('/api/teachers')
def get_teachers():
    """Получить список преподавателей для выбранной кафедры"""
    teachers = [
        {'id': 'Агалакова Марина Борисовна', 'name': 'Агалакова Марина Борисовна'},
        {'id': 'Агаширинова Валентина Юрьевна', 'name': 'Агаширинова Валентина Юрьевна'},
        {'id': 'Акимов Олег Владимирович', 'name': 'Акимов Олег Владимирович'},
        {'id': 'Алексеева Лариса Владимировна', 'name': 'Алексеева Лариса Владимировна'},
        {'id': 'Анисимов Виктор Александрович', 'name': 'Анисимов Виктор Александрович'},
        {'id': 'Антонов Дмитрий Олегович', 'name': 'Антонов Дмитрий Олегович'},
        {'id': 'Баленко Виктория Витальевна', 'name': 'Баленко Виктория Витальевна'},
        {'id': 'Барановская Иоланта Геннадьевна', 'name': 'Барановская Иоланта Геннадьевна'},
        {'id': 'Белоус Татьяна Викторовна', 'name': 'Белоус Татьяна Викторовна'},
        {'id': 'Богомолова Оксана Юрьевна', 'name': 'Богомолова Оксана Юрьевна'},
        {'id': 'Бондарев Константин Дмитриевич', 'name': 'Бондарев Константин Дмитриевич'},
        {'id': 'Бородулин Денис Александрович', 'name': 'Бородулин Денис Александрович'},
        {'id': 'Брагер Дмитрий Константинович', 'name': 'Брагер Дмитрий Константинович'},
        {'id': 'Буняева Екатерина Викторовна', 'name': 'Буняева Екатерина Викторовна'},
        {'id': 'Велиева Елена Александровна', 'name': 'Велиева Елена Александровна'},
        {'id': 'Вялкова Оксана Сергеевна', 'name': 'Вялкова Оксана Сергеевна'},
        {'id': 'Ганевич Олег Константинович', 'name': 'Ганевич Олег Константинович'},
        {'id': 'Ганевич Светлана Геннадьевна', 'name': 'Ганевич Светлана Геннадьевна'},
        {'id': 'Галкина Наталья Юрьевна', 'name': 'Галкина Наталья Юрьевна'},
        {'id': 'Гильмутдинов Станислав Алексеевич', 'name': 'Гильмутдинов Станислав Алексеевич'},
        {'id': 'Гопкало Вадим Николаевич', 'name': 'Гопкало Вадим Николаевич'},
        {'id': 'Григорович Наталья Николаевна', 'name': 'Григорович Наталья Николаевна'},
        {'id': 'Гулевская Альфия Фаиловна', 'name': 'Гулевская Альфия Фаиловна'},
        {'id': 'Дидур Екатерина Александровна', 'name': 'Дидур Екатерина Александровна'},
        {'id': 'Егоров Петр Егорович', 'name': 'Егоров Петр Егорович'},
        {'id': 'Ефимова Анна Андреевна', 'name': 'Ефимова Анна Андреевна'},
        {'id': 'Ефимова Ольга Сергеевна', 'name': 'Ефимова Ольга Сергеевна'},
        {'id': 'Жалдак Алла Александровна', 'name': 'Жалдак Алла Александровна'},
        {'id': 'Зангиров Владимир Гайфулович', 'name': 'Зангиров Владимир Гайфулович'},
        {'id': 'Зиссер Ирина Сергеевна', 'name': 'Зиссер Ирина Сергеевна'},
        {'id': 'Исакова Дарья Сергеевна', 'name': 'Исакова Дарья Сергеевна'},
        {'id': 'Калинина Галина Николаевна', 'name': 'Калинина Галина Николаевна'},
        {'id': 'Калинцев Олег Викторович', 'name': 'Калинцев Олег Викторович'},
        {'id': 'Карачанская Елена Викторовна', 'name': 'Карачанская Елена Викторовна'},
        {'id': 'Кернаджук Игорь Васильевич', 'name': 'Кернаджук Игорь Васильевич'},
        {'id': 'Ковалев Владимир Александрович', 'name': 'Ковалев Владимир Александрович'},
        {'id': 'Ковальчук Михаил Александрович', 'name': 'Ковальчук Михаил Александрович'},
        {'id': 'Ковтун Богдан Анатольевич', 'name': 'Ковтун Богдан Анатольевич'},
        {'id': 'Колесникова Марина Геннадьевна', 'name': 'Колесникова Марина Геннадьевна'},
        {'id': 'Кононец Анастасия Николаевна', 'name': 'Кононец Анастасия Николаевна'},
        {'id': 'Коровина Светлана Викторовна', 'name': 'Коровина Светлана Викторовна'},
        {'id': 'Кривошеев Игорь Александрович', 'name': 'Кривошеев Игорь Александрович'},
        {'id': 'Кудрявцев Игорь Геннадьевич', 'name': 'Кудрявцев Игорь Геннадьевич'},
        {'id': 'Куликова Генриетта Владимировна', 'name': 'Куликова Генриетта Владимировна'},
        {'id': 'Кулян-Козионова Мария Эдуардовна', 'name': 'Кулян-Козионова Мария Эдуардовна'},
        {'id': 'Куприянов Дмитрий Петрович', 'name': 'Куприянов Дмитрий Петрович'},
        {'id': 'Лазарева Светлана Пимоновна', 'name': 'Лазарева Светлана Пимоновна'},
        {'id': 'Листопадова Евгения Вячеславовна', 'name': 'Листопадова Евгения Вячеславовна'},
        {'id': 'Любицкая Ольга Андреевна', 'name': 'Любицкая Ольга Андреевна'},
        {'id': 'Людвиг Лидия Петровна', 'name': 'Людвиг Лидия Петровна'},
        {'id': 'Мазурова Валентина Васильевна', 'name': 'Мазурова Валентина Васильевна'},
        {'id': 'Макаров Иван Александрович', 'name': 'Макаров Иван Александрович'},
        {'id': 'Макеев Валерий Александрович', 'name': 'Макеев Валерий Александрович'},
        {'id': 'Малиновская Светлана Анатольевна', 'name': 'Малиновская Светлана Анатольевна'},
        {'id': 'Малова Юлия Германовна', 'name': 'Малова Юлия Германовна'},
        {'id': 'Марек Павел Болиславович', 'name': 'Марек Павел Болиславович'},
        {'id': 'Мартынюк Марина Петровна', 'name': 'Мартынюк Марина Петровна'},
        {'id': 'Микулин Андрей Иванович', 'name': 'Микулин Андрей Иванович'},
        {'id': 'Моисеев Владимир Васильевич', 'name': 'Моисеев Владимир Васильевич'},
        {'id': 'Муравьева Любовь Геннадьевна', 'name': 'Муравьева Любовь Геннадьевна'},
        {'id': 'Муровский Сергей Петрович', 'name': 'Муровский Сергей Петрович'},
        {'id': 'Некрасова Олеся Игоревна', 'name': 'Некрасова Олеся Игоревна'},
        {'id': 'Нестерова Маргарита Владимировна', 'name': 'Нестерова Маргарита Владимировна'},
        {'id': 'Неустроев Александр Николаевич', 'name': 'Неустроев Александр Николаевич'},
        {'id': 'Нечепуренко Юрий Николаевич', 'name': 'Нечепуренко Юрий Николаевич'},
        {'id': 'Оганесян Овсеп Амирханович', 'name': 'Оганесян Овсеп Амирханович'},
        {'id': 'Оккель Светлана Алексеевна', 'name': 'Оккель Светлана Алексеевна'},
        {'id': 'Панов Александр Геннадьевич', 'name': 'Панов Александр Геннадьевич'},
        {'id': 'Пешкова Ксения Евгеньевна', 'name': 'Пешкова Ксения Евгеньевна'},
        {'id': 'Петерс Анастасия Александровна', 'name': 'Петерс Анастасия Александровна'},
        {'id': 'Петров Юрий Викторович', 'name': 'Петров Юрий Викторович'},
        {'id': 'Пицюк Инесса Леонидовна', 'name': 'Пицюк Инесса Леонидовна'},
        {'id': 'Повх Ирина Владимировна', 'name': 'Повх Ирина Владимировна'},
        {'id': 'Подкорытова Владислава Александровна', 'name': 'Подкорытова Владислава Александровна'},
        {'id': 'Пономарчук Юлия Викторовна', 'name': 'Пономарчук Юлия Викторовна'},
        {'id': 'Потехина Наталья Иосифовна', 'name': 'Потехина Наталья Иосифовна'},
        {'id': 'Приходько Алена Викторовна', 'name': 'Приходько Алена Викторовна'},
        {'id': 'Пухова Анастасия Игоревна', 'name': 'Пухова Анастасия Игоревна'},
        {'id': 'Пячин Сергей Анатольевич', 'name': 'Пячин Сергей Анатольевич'},
        {'id': 'Разумовская Марина Ивановна', 'name': 'Разумовская Марина Ивановна'},
        {'id': 'Ромель Светлана Александровна', 'name': 'Ромель Светлана Александровна'},
        {'id': 'Руднева Зарета Сергеевна', 'name': 'Руднева Зарета Сергеевна'},
        {'id': 'Рыбкина Олеся Викторовна', 'name': 'Рыбкина Олеся Викторовна'},
        {'id': 'Садыкова Ульяна Фаниховна', 'name': 'Садыкова Ульяна Фаниховна'},
        {'id': 'Сайфутдинов Ринат Хасанович', 'name': 'Сайфутдинов Ринат Хасанович'},
        {'id': 'Самодина Анна Валерьевна', 'name': 'Самодина Анна Валерьевна'},
        {'id': 'Серебрянникова Мария Викторовна', 'name': 'Серебрянникова Мария Викторовна'},
        {'id': 'Синаторов Андрей Леонидович', 'name': 'Синаторов Андрей Леонидович'},
        {'id': 'Скорик Виталий Геннадьевич', 'name': 'Скорик Виталий Геннадьевич'},
        {'id': 'Соколов Геннадий Павлович', 'name': 'Соколов Геннадий Павлович'},
        {'id': 'Соколова Дарья Дмитриевна', 'name': 'Соколова Дарья Дмитриевна'},
        {'id': 'Татауров Андрей Алексеевич', 'name': 'Татауров Андрей Алексеевич'},
        {'id': 'Тесленко Ирина Михайловна', 'name': 'Тесленко Ирина Михайловна'},
        {'id': 'Тряпкин Дмитрий Александрович', 'name': 'Тряпкин Дмитрий Александрович'},
        {'id': 'Тумали Людмила Евгеньевна', 'name': 'Тумали Людмила Евгеньевна'},
        {'id': 'Туркулец Иван Алексеевич', 'name': 'Туркулец Иван Алексеевич'},
        {'id': 'Фалеева Елена Валерьевна', 'name': 'Фалеева Елена Валерьевна'},
        {'id': 'Фетисова Елена Александровна', 'name': 'Фетисова Елена Александровна'},
        {'id': 'Финогенова Яна Георгиевна', 'name': 'Финогенова Яна Георгиевна'},
        {'id': 'Холзинёва Анна Геннадьевна', 'name': 'Холзинёва Анна Геннадьевна'},
        {'id': 'Цало Илья Маркович', 'name': 'Цало Илья Маркович'},
        {'id': 'Царионова Юлия Вячеславовна', 'name': 'Царионова Юлия Вячеславовна'},
        {'id': 'Цвигунов Дмитрий Геннадьевич', 'name': 'Цвигунов Дмитрий Геннадьевич'},
        {'id': 'Чопова Наталья Валерьевна', 'name': 'Чопова Наталья Валерьевна'},
        {'id': 'Шабалин Виктор Александрович', 'name': 'Шабалин Виктор Александрович'},
        {'id': 'Шишкова Елена Николаевна', 'name': 'Шишкова Елена Николаевна'},
        {'id': 'Шкаран Анастасия Антоновна', 'name': 'Шкаран Анастасия Антоновна'},
        {'id': 'Шувалова Светлана Николаевна', 'name': 'Шувалова Светлана Николаевна'},
        {'id': 'Шухарев Сергей Анатольевич', 'name': 'Шухарев Сергей Анатольевич'},
        {'id': 'Юдаев Павел Андреевич', 'name': 'Юдаев Павел Андреевич'}
    ]
    return jsonify({
        'success': True,
        'teachers': teachers
    })

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

        # Получаем расписание ИЗ JSON
        weekly = group_timetable_reader.get_timetable_by_week(group, formatted_date)

        # Если группа не найдена, предлагаем похожие группы
        if not weekly and not group_timetable_reader.check_group_exists(group):
            available_groups = group_timetable_reader.get_available_groups()
            similar_groups = [g for g in available_groups if group.upper() in g.upper()]

            error_msg = f'Группа "{group}" не найдена'
            if similar_groups:
                error_msg += f'. Возможно, вы искали: {", ".join(similar_groups[:5])}'

            return jsonify({
                'success': False,
                'error': error_msg
            }), 404

        # Преобразуем в удобный формат
        schedule_data = []
        for day in weekly:
            day_data =[]
            for lecture in day:
                day_data.append({
                    'number': lecture.get('time', ''),  # или lecture.get('number', '') если нужен номер пары
                    'name': lecture.get('name', ''),
                    'classroom': lecture.get('classroom', ''),
                    'teacher': lecture.get('teacher', ''),
                    'group': lecture.get('group', group)
                })
            schedule_data.append(day_data)

        return jsonify({
            'success': True,
            'date': formatted_date,
            'group': group,
            'schedule': schedule_data,
            'html': genarate_weekly_schedule_html(schedule_data, group, formatted_date)
        })

    except Exception as e:
        print(f"Ошибка в обработке запроса: {e} \n {traceback.format_exc()} \n {type(e).__name__}")
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
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
                'error': 'Выберите преподавателя'
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

        # Пытаемся найти ФИО преподавателя по ID
        teacher_name = teacher_id

        # Если teacher_id является числовым ID, пробуем найти его в словаре
        # Иначе считаем, что teacher_id уже является ФИО преподавателя
        if teacher_id.isdigit():
            # Если не нашли в словаре, пытаемся получить из списка преподавателей
            if teacher_name == teacher_id:
                # Запрашиваем список всех преподавателей из JSON
                all_teachers = teacher_timetable_reader.get_available_keys()
                # Ищем преподавателя с похожим ID в названии (это хак, лучше иметь отдельное соответствие)
                for teacher in all_teachers:
                    if teacher_id in teacher:
                        teacher_name = teacher
                        break

        # Получаем расписание ИЗ JSON для преподавателя
        schedule_data = []
        weekly = teacher_timetable_reader.get_timetable_by_week(teacher_name, formatted_date)

        # Если преподаватель не найден, предлагаем похожих преподавателей
        if not weekly and not teacher_timetable_reader.check_key_exists(teacher_name):
            available_teachers = teacher_timetable_reader.get_available_keys()
            similar_teachers = [t for t in available_teachers if teacher_name.upper() in t.upper()]

            error_msg = f'Преподаватель "{teacher_name}" не найден'
            if similar_teachers:
                error_msg += f'. Возможно, вы искали: {", ".join(similar_teachers[:5])}'

            return jsonify({
                'success': False,
                'error': error_msg
            }), 404

        # Преобразуем в удобный формат
        for day in weekly:
            day_data = []
            print(day)
            for lecture in day:
                day_data.append({
                    'number': lecture.get('time', ''),  # Используем время как номер пары
                    'name': lecture.get('name', ''),
                    'classroom': lecture.get('classroom', ''),
                    'teacher': lecture.get('teacher', ''),
                    'group': lecture.get('group', '')
                })
            schedule_data.append(day_data)

        # Генерируем HTML используя вашу функцию
        html = genarate_weekly_schedule_html(schedule_data, f"Преподаватель: {teacher_name}", formatted_date)

        return jsonify({
            'success': True,
            'date': formatted_date,
            'teacher': teacher_name,
            'schedule': schedule_data,
            'html': html
        })

    except Exception as e:
        print(f"Ошибка в обработке запроса преподавателя: {e} \n {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }), 500

@application.route('/api/auditoriums')
def get_auditoriums():
    """Получить список аудиторий"""
    try:
        auditoriums_list = [{'id': k, 'name': v} for k, v in AUDITORIUMS.items()]
        return jsonify({
            'success': True,
            'auditoriums': auditoriums_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при получении аудиторий: {str(e)}'
        }), 500


@application.route('/api/schedule/auditorium', methods=['POST'])
def get_auditorium_schedule():
    """Получить расписание для выбранной аудитории"""
    try:
        data = request.get_json()
        auditorium_id = data.get('auditorium_id', '').strip()
        date_str = data.get('date', '')

        # Валидация
        if not auditorium_id:
            return jsonify({
                'success': False,
                'error': 'Выберите аудиторию'
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

        # Получаем название аудитории по ID
        # Пытаемся найти в нашем словаре соответствий
        auditorium_name = auditorium_id

        # Если не нашли, проверяем AUDITORIUMS
        if not auditorium_name and auditorium_id in AUDITORIUMS:
            full_name = AUDITORIUMS[auditorium_id]
            # Извлекаем краткое название (до первой открывающей скобки)
            if '(' in full_name:
                auditorium_name = full_name.split('(')[0].strip()
            else:
                auditorium_name = full_name

        # Если все еще не нашли, используем ID как есть
        if not auditorium_name:
            auditorium_name = auditorium_id

        # Получаем расписание ИЗ JSON для аудитории
        schedule_data = []
        weekly = classroom_timetable_reader.get_timetable_by_week(auditorium_name, formatted_date)

        # Если аудитория не найдена, предлагаем похожие аудитории
        if not weekly and not classroom_timetable_reader.check_key_exists(auditorium_name):
            # Пробуем найти аудитории с похожим названием
            available_classrooms = classroom_timetable_reader.get_available_keys()
            similar_classrooms = [c for c in available_classrooms if auditorium_name in c]

            error_msg = f'Аудитория "{auditorium_name}" не найдена'
            if similar_classrooms:
                error_msg += f'. Возможно, вы искали: {", ".join(similar_classrooms[:5])}'

            return jsonify({
                'success': False,
                'error': error_msg
            }), 404

        # Преобразуем в удобный формат
        for day in weekly:
            day_data = []
            for lecture in day:
                day_data.append({
                    'number': lecture.get('time', ''),  # Используем время как номер пары
                    'name': lecture.get('name', ''),
                    'classroom': lecture.get('classroom', ''),
                    'teacher': lecture.get('teacher', ''),
                    'group': lecture.get('group', '')
                })
            schedule_data.append(day_data)

        # Генерируем HTML используя вашу функцию
        html = genarate_weekly_schedule_html(schedule_data, f"Аудитория: {auditorium_name}", formatted_date)

        return jsonify({
            'success': True,
            'date': formatted_date,
            'auditorium_id': auditorium_id,
            'auditorium_name': auditorium_name,
            'schedule': schedule_data,
            'html': html
        })

    except Exception as e:
        print(f"Ошибка в обработке запроса аудитории: {e} \n {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }), 500


def genarate_weekly_schedule_html(schedule_data, group, date):
    final_html = ""
    date_datetime = datetime.strptime(date, '%d.%m.%Y')
    current_date = date_datetime
    for i in range(7):
        current_date = date_datetime + timedelta(days=i)
        final_html += generate_group_schedule_html(schedule_data[i], group, current_date.strftime("%d.%m.%Y"))

    return final_html


def generate_group_schedule_html(schedule_data, group, date):
    """Генерация HTML таблицы расписания для группы"""
    if not schedule_data:
        return f'''
        <div class="no-schedule">
            <div class="no-schedule-icon">
                <i class="fas fa-calendar-times"></i>
            </div>
            <h3>Занятий нет</h3>
            <p>На {date} у группы нет занятий</p>
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