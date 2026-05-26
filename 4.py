
"# JSON export method added"
import csv
import os
from datetime import datetime
from typing import Optional, Iterator, Generator, List, Any


class DomainEntity:
    """
    Базовый класс предметной области.
    Все записи свойств проходят через __setattr__.
    """

    # ПУНКТ 4: Единая точка записи свойств для всех дочерних классов
    def __setattr__(self, key: str, value: Any) -> None:
        """
        Единая точка записи свойств для всех дочерних классов.
        Базовый класс не выполняет валидацию, оставляя её дочерним классам.
        """
        object.__setattr__(self, key, value)

# ПУНКТ 3 Наследование DomainEntity → BaseRecord
class BaseRecord(DomainEntity):
    """Базовый класс для записи с общей функциональностью."""

    # ПУНКТ 2: Перегрузка __repr__
    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        attrs = []
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            if isinstance(value, str):
                attrs.append(f"{key}='{value}'")
            else:
                attrs.append(f"{key}={value}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    def to_dict(self) -> dict:
        """Преобразование в словарь."""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }


class CallRecord(BaseRecord):
    """Одна запись истории обзвона."""

    def __init__(
            self,
            number: int,
            phone: str,
            answered: bool,
            client_full_name: str,
            next_call_date: str,
            next_step_description: str,
    ) -> None:
        """
        Инициализация записи обзвона.
        """
        self._validate_and_set('number', number)
        self._validate_and_set('phone', phone)
        self._validate_and_set('answered', answered)
        self._validate_and_set('client_full_name', client_full_name)
        self._validate_and_set('next_call_date', next_call_date)
        self._validate_and_set('next_step_description', next_step_description)

    # ПУНКТ 4: Вспомогательный метод для записи через __setattr__
    def _validate_and_set(self, key: str, value: Any) -> None:
        """
        Вспомогательный метод для валидации и установки значения.
        Использует __setattr__ для единой точки записи.
        """
        self.__setattr__(key, value)

    # ПУНКТ 4: Перегрузка __setattr__ с валидацией значений
    def __setattr__(self, key: str, value: Any) -> None:
        """
        Перегрузка __setattr__ с валидацией значений.
        """
        if key == "number":
            if isinstance(value, str):
                value = value.strip()
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise ValueError("Номер записи должен быть числом")
            if value <= 0:
                raise ValueError("Номер записи должен быть положительным")

        elif key == "phone":
            value = self._normalize_phone(value)

        elif key == "answered":
            value = self._parse_answered(value)

        elif key == "client_full_name":
            value = str(value).strip()
            if not value:
                raise ValueError("ФИО клиента не может быть пустым")
            # Дополнительная проверка: ФИО должно содержать минимум 2 слова
            if len(value.split()) < 2:
                raise ValueError("ФИО должно содержать имя и фамилию")

        elif key == "next_call_date":
            value = self._validate_date(value)

        elif key == "next_step_description":
            value = str(value).strip()
            if not value:
                raise ValueError("Описание следующего шага не может быть пустым")

        super().__setattr__(key, value)

    # ПУНКТ 2: Перегрузка __str__
    def __str__(self) -> str:
        """
        Пользовательское строковое представление записи.
        """
        answered_text = "да" if self.answered else "нет"
        return (
            f"№: {self.number}\n"
            f"Телефон: {self.phone}\n"
            f"Взял трубку: {answered_text}\n"
            f"ФИО: {self.client_full_name}\n"
            f"Дата следующего созвона: {self.next_call_date}\n"
            f"Следующий шаг: {self.next_step_description}"
        )

    # ПУНКТ 6: Статический метод
    @staticmethod
    def _normalize_phone(phone_value: Any) -> str:
        """
        Статический метод: нормализация номера телефона.
        """
        raw = str(phone_value).strip()
        # Оставляем только цифры и знак +
        cleaned = "".join(ch for ch in raw if ch.isdigit() or ch == "+")
        if not cleaned:
            raise ValueError("Телефон не может быть пустым")
        return cleaned

    # ПУНКТ 6: Статический метод
    @staticmethod
    def _parse_answered(value: Any) -> bool:
        """
        Статический метод: парсинг поля 'взял трубку'.
        """
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in ("да", "yes", "y", "true", "1"):
            return True
        if text in ("нет", "no", "n", "false", "0"):
            return False
        raise ValueError("Поле 'взял трубку' должно быть 'да' или 'нет'")

    # ПУНКТ 6: Статический метод
    @staticmethod
    def _validate_date(date_value: Any) -> str:
        """
        Статический метод: валидация даты.
        """
        date_text = str(date_value).strip()
        try:
            datetime.strptime(date_text, "%d.%m.%Y")
        except ValueError:
            raise ValueError(f"Дата должна быть в формате дд.мм.гггг, получено: {date_text}")
        return date_text

    # ПУНКТ 6: Статический метод
    @staticmethod
    def csv_fields() -> List[str]:
        """
        Статический метод: возвращает заголовки CSV.
        """
        return [
            "№",
            "Телефон",
            "Взял трубку",
            "ФИО клиента",
            "Дата следующего созвона",
            "Описание следующего шага",
        ]

    def to_dict(self) -> dict:
        """
        Преобразование записи в словарь для CSV.
        """
        return {
            "№": self.number,
            "Телефон": self.phone,
            "Взял трубку": "да" if self.answered else "нет",
            "ФИО клиента": self.client_full_name,
            "Дата следующего созвона": self.next_call_date,
            "Описание следующего шага": self.next_step_description,
        }

    @classmethod
    def from_dict(cls, row: dict) -> 'CallRecord':
        """
        Классовый метод: создание записи из словаря.
        """
        return cls(
            number=row.get("№", 0),
            phone=row.get("Телефон", ""),
            answered=row.get("Взял трубку", "нет"),
            client_full_name=row.get("ФИО клиента", ""),
            next_call_date=row.get("Дата следующего созвона", "01.01.2000"),
            next_step_description=row.get("Описание следующего шага", ""),
        )


class BaseHistory(DomainEntity):
    """Базовый класс для коллекций записей."""

    def __init__(self) -> None:
        """Инициализация базовой коллекции."""
        self._items: List[Any] = []
        self._iter_index = 0

    # ПУНКТ 2: Перегрузка __len__
    def __len__(self) -> int:
        """Возвращает количество элементов в коллекции."""
        return len(self._items)

    # ПУНКТ 5: Доступ к элементам по индексу
    def __getitem__(self, index: int) -> Any:
        """
        Доступ к элементам по индексу.
        Поддерживает отрицательные индексы.
        """
        return self._items[index]

    # ПУНКТ 1: Реализация итератора (метод __iter__)
    def __iter__(self) -> Iterator:
        """Возвращает итератор для коллекции."""
        self._iter_index = 0
        return self

    # ПУНКТ 1: Реализация итератора (метод __next__)
    def __next__(self) -> Any:
        """Следующий элемент в итерации."""
        if self._iter_index >= len(self._items):
            raise StopIteration
        item = self._items[self._iter_index]
        self._iter_index += 1
        return item

    def add_item(self, item: Any) -> None:
        """
        Добавление элемента в коллекцию.
        Должен быть переопределен в дочерних классах.
        """
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")


class CallHistory(BaseHistory):
    """Коллекция записей обзвона."""

    def __init__(self) -> None:
        """Инициализация коллекции записей."""
        super().__init__()

    # ПУНКТ 2: Перегрузка __repr__
    def __repr__(self) -> str:
        """
        Перегрузка __repr__ для отладки.
        """
        return f"CallHistory(records_count={len(self._items)})"

    def add_item(self, item: Any) -> None:
        """
        Добавление записи в коллекцию с проверкой типа.
        """
        if not isinstance(item, CallRecord):
            raise TypeError("Можно добавлять только объекты CallRecord")
        self._items.append(item)

    # Сохраняем старый метод для обратной совместимости
    def add_record(self, record: CallRecord) -> None:
        """Добавление записи (метод-обертка для add_item)."""
        self.add_item(record)

    # ПУНКТ 7: Генератор - клиенты, которые не ответили
    def iter_not_answered(self) -> Generator[CallRecord, None, None]:
        """
        Генератор: возвращает записи клиентов, которые не ответили.
        """
        for record in self._items:
            if not record.answered:
                yield record

    # ПУНКТ 7: Генератор - записи по дате созвона
    def iter_by_date(self, date_text: str) -> Generator[CallRecord, None, None]:
        """
        Генератор: возвращает записи по указанной дате созвона.
        """
        for record in self._items:
            if record.next_call_date == date_text:
                yield record

    # ПУНКТ 7: Дополнительный генератор (расширение функциональности)
    def iter_by_phone(self, phone_pattern: str) -> Generator[CallRecord, None, None]:
        """
        Генератор: возвращает записи по номеру телефона (частичное совпадение).
        """
        pattern = phone_pattern.strip().lower()
        for record in self._items:
            if pattern in record.phone.lower():
                yield record

    def sorted_by_name(self) -> List[CallRecord]:
        """
        Сортировка записей по ФИО.
        """
        return sorted(self._items, key=lambda rec: rec.client_full_name.lower())

    def sorted_by_number(self) -> List[CallRecord]:
        """
        Сортировка записей по номеру.
        """
        return sorted(self._items, key=lambda rec: rec.number)

    def sorted_by_date(self) -> List[CallRecord]:
        """
        Сортировка записей по дате следующего созвона.
        """
        return sorted(self._items, key=lambda rec: rec.next_call_date)

    # ПУНКТ 6: Статический метод
    @staticmethod
    def count_files_in_directory(path: str) -> int:
        """
        Статический метод: подсчет количества файлов в директории.
        """
        if not os.path.exists(path):
            return 0
        count = 0
        for item in os.listdir(path):
            if os.path.isfile(os.path.join(path, item)):
                count += 1
        return count

    # ПУНКТ 6: Статический метод
    @staticmethod
    def create_empty_csv_if_missing(filename: str) -> None:
        """
        Статический метод: создание пустого CSV файла с заголовками.
        """
        if os.path.exists(filename):
            return
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CallRecord.csv_fields())
            writer.writeheader()

    @classmethod
    def from_csv(cls, filename: str) -> 'CallHistory':
        """
        Классовый метод: загрузка коллекции из CSV файла.
        """
        history = cls()
        if not os.path.exists(filename):
            return history

        with open(filename, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    record = CallRecord.from_dict(row)
                    history.add_record(record)
                except (ValueError, TypeError) as e:
                    # Логируем ошибку, но продолжаем загрузку
                    print(f"Пропущена некорректная запись: {row}, ошибка: {e}")
                    continue

        return history

    def save_to_csv(self, filename: str) -> None:
        """
        Сохранение коллекции в CSV файл.
        """
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CallRecord.csv_fields())
            writer.writeheader()
            for record in self._items:
                writer.writerow(record.to_dict())

    def get_statistics(self) -> dict:
        """
        Получение статистики по обзвонам.
        """
        if not self._items:
            return {
                'total': 0,
                'answered': 0,
                'not_answered': 0,
                'answered_percentage': 0
            }

        answered_count = sum(1 for record in self._items if record.answered)
        return {
            'total': len(self._items),
            'answered': answered_count,
            'not_answered': len(self._items) - answered_count,
            'answered_percentage': (answered_count / len(self._items)) * 100
        }


def print_records(records: any, title: Optional[str] = None) -> None:
    """
    Вспомогательная функция для вывода записей.
    """
    if title:
        print(f"\n{title}")
        print("-" * len(title))

    if isinstance(records, Generator):
        records = list(records)

    if not records:
        print("Нет данных для отображения.")
        return

    for idx, rec in enumerate(records, start=1):
        print(f"\n--- Запись {idx} ---")
        print(rec)


def main() -> None:
    """Основная функция программы."""
    print("=== История обзвона клиентов ===")
    filename = "call_history.csv"

    # ПУНКТ 6: Демонстрация статического метода
    folder = input("Введите путь к папке для подсчета файлов: ").strip()
    if folder:
        files_count = CallHistory.count_files_in_directory(folder)
        print(f"Файлов в папке '{folder}': {files_count}")

    # Загрузка данных
    CallHistory.create_empty_csv_if_missing(filename)
    history = CallHistory.from_csv(filename)
    print(f"Загружено записей: {len(history)}")

    # ПУНКТ 1: Демонстрация итератора коллекции
    print_records(history, "Все записи (итератор коллекции)")

    # Демонстрация сортировок
    print_records(history.sorted_by_name(), "Сортировка по ФИО")
    print_records(history.sorted_by_number(), "Сортировка по номеру записи")
    print_records(history.sorted_by_date(), "Сортировка по дате созвона")

    # ПУНКТ 7: Демонстрация генераторов
    print_records(history.iter_not_answered(), "Клиенты, которые не взяли трубку")
    print_records(history.iter_by_date("01.01.2025"), "Записи на дату 01.01.2025")

    # ПУНКТ 5: Демонстрация доступа по индексу (__getitem__)
    if len(history) > 0:
        print("\n" + "=" * 50)
        print("Демонстрация доступа по индексу (__getitem__):")
        print(f"Первая запись: {history[0]}")
        print(f"Последняя запись: {history[-1]}")

    # Добавление новой записи
    print("\n" + "=" * 50)
    print("Введите новую запись:")

    try:
        number_input = input("№: ").strip()
        phone_input = input("Телефон: ").strip()
        answered_input = input("Взял трубку (да/нет): ").strip()
        name_input = input("ФИО клиента: ").strip()
        date_input = input("Дата следующего созвона (дд.мм.гггг): ").strip()
        step_input = input("Описание следующего шага: ").strip()

        new_record = CallRecord(
            number=number_input,
            phone=phone_input,
            answered=answered_input,
            client_full_name=name_input,
            next_call_date=date_input,
            next_step_description=step_input,
        )

        history.add_record(new_record)
        history.save_to_csv(filename)
        print("\n✓ Запись добавлена и сохранена в файл.")

        # Показываем статистику после добавления
        stats = history.get_statistics()
        print(f"\nСтатистика обзвонов:")
        print(f"  Всего записей: {stats['total']}")
        print(f"  Ответили: {stats['answered']}")
        print(f"  Не ответили: {stats['not_answered']}")
        print(f"  Процент ответивших: {stats['answered_percentage']:.1f}%")

    except (ValueError, TypeError) as error:
        print(f"\n✗ Ошибка ввода: {error}")


if __name__ == "__main__":
    main()