import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class GenericTimetableReader:
    """Универсальный ридер для JSON файлов с расписанием"""

    def __init__(self, json_file_path: str = "timetable.json"):
        """
        Инициализация ридера JSON расписания.

        Args:
            json_file_path: Путь к JSON файлу с расписанием
        """
        self.json_file_path = json_file_path
        self.data = None
        self.last_loaded = None
        self.load_data()

    def load_data(self) -> bool:
        """Загружает данные из JSON файла."""
        try:
            if not os.path.exists(self.json_file_path):
                print(f"Файл {self.json_file_path} не найден")
                return False

            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            self.last_loaded = datetime.now()
            print(f"Данные успешно загружены из {self.json_file_path}")
            return True

        except Exception as e:
            print(f"Ошибка при загрузке JSON файла: {e}")
            return False

    def get_timetable_by_day(self, key: str, date_str: str) -> List[Dict[str, Any]]:
        """
        Получает расписание для ключа (группы/преподавателя/аудитории) на определенный день из JSON.

        Args:
            key: Ключ для поиска (название группы, ФИО преподавателя, название аудитории)
            date_str: Дата в формате DD.MM.YYYY

        Returns:
            Список словарей с занятиями
        """
        date_str = str(date_str)
        if self.data is None:
            if not self.load_data():
                return []

        try:
            # Проверяем, существует ли ключ в данных
            if key not in self.data.get("timetables", {}):
                print(f"Ключ '{key}' не найден в данных")
                return []


            item_data = self.data["timetables"][key]
            schedule = item_data if isinstance(item_data, dict) else item_data.get("schedule", {})


            # Получаем расписание на указанную дату
            print(';')
            try:
                day_schedule = schedule['schedule'][date_str]
            except Exception as e:
                day_schedule = schedule[date_str]


            # Преобразуем формат данных к ожидаемому
            lectures = []

            for lecture in day_schedule:
                lecture_dict = {
                    'time': lecture.get('time', ''),
                    'name': lecture.get('name', ''),
                    'classroom': lecture.get('classroom', ''),
                    'teacher': lecture.get('teacher', ''),
                    'group': lecture.get('group', ''),
                    'number': lecture.get('number', ''),
                    'date': date_str
                }
                lectures.append(lecture_dict)

            print(f"Найдено {len(lectures)} занятий для ключа {key} на {date_str}")
            return lectures

        except Exception as e:
            print(f"Ошибка при получении расписания: {e}")
            return []

    def get_timetable_by_week(self, key: str, date_str: str):
        date_datetime = datetime.strptime(date_str, '%d.%m.%Y')
        current_date = date_datetime
        schedule = list()
        schedule.append(self.get_timetable_by_day(key, date_str))
        for i in range(7):
            schedule.append(self.get_timetable_by_day(key, current_date.strftime("%d.%m.%Y")))
            current_date = date_datetime + timedelta(days=i)

        return schedule


    def get_available_keys(self) -> List[str]:
        """Возвращает список доступных ключей (групп/преподавателей/аудиторий)."""
        if self.data is None:
            if not self.load_data():
                return []

        return list(self.data.get("timetables", {}).keys())

    def get_available_dates(self, key: str = None) -> List[str]:
        """
        Возвращает список доступных дат.

        Args:
            key: Если указано, возвращает даты для конкретного ключа

        Returns:
            Список дат в формате DD.MM.YYYY
        """
        if self.data is None:
            if not self.load_data():
                return []

        if key:
            # Даты для конкретного ключа
            if key in self.data.get("timetables", {}):
                item_data = self.data["timetables"][key]
                schedule = item_data if isinstance(item_data, dict) else item_data.get("schedule", {})
                return sorted(schedule.keys())
            return []
        else:
            # Все даты из метаданных
            return self.data.get("metadata", {}).get("week_dates", [])

    def check_key_exists(self, key: str) -> bool:
        """Проверяет, существует ли ключ в данных."""
        if self.data is None:
            if not self.load_data():
                return False

        return key in self.data.get("timetables", {})

    def check_group_exists(self, group: str) -> bool:
        """Проверяет, существует ли группа в данных."""
        if self.data is None:
            if not self.load_data():
                return False

        return group in self.data.get("timetables", {})

    def get_key_info(self, key: str) -> Dict[str, Any]:
        """Возвращает информацию по ключу."""
        if self.data is None:
            if not self.load_data():
                return {}

        if key in self.data.get("timetables", {}):
            return self.data["timetables"][key]
        return {}


# Создаем глобальные экземпляры для использования во всем приложении
group_timetable_reader = GenericTimetableReader("db/timetable.json")
teacher_timetable_reader = GenericTimetableReader("db/teachers_timetable.json")
classroom_timetable_reader = GenericTimetableReader("db/classrooms_timetable.json")
