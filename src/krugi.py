import re
from dateutil import parser
from datetime import datetime
import dateparser
import os


KRUGI: dict[str, str] = {}
DEVICES = ('md', 'txt')
FOLDERS_PATH = 'static/krugi/'
HELLO_KEY = 'hello'


def get_hello_text(device: str) -> str:
    key = HELLO_KEY + device
    if key not in KRUGI:
        path = FOLDERS_PATH + device + f'/{HELLO_KEY}.{device}'
        with open(path, 'r', encoding='utf-8') as file:
            KRUGI[key] = file.read()
    return KRUGI[key]


def get_krug_text(number: int, device: str):
    assert 1 <= int(number) <= 7
    number = str(number)

    key = number + device
    if key not in KRUGI:
        path = FOLDERS_PATH + device + f'/{number}.{device}'
        with open(path, 'r', encoding='utf-8') as file:
            KRUGI[key] = file.read()

    return KRUGI[key]


def parse_birth_date(input_str: str) -> datetime | None:
    """
    Пытается распарсить дату из произвольной строки с цифрами и спецсимволами.
    Возвращает datetime или None, если не удалось распознать.
    """
    # Удаляем мусорные символы кроме цифр и возможных разделителей
    cleaned = re.sub(r'[^\d\s\-./]', '', input_str.strip())

    # Пробуем найти возможные шаблоны дат с различными разделителями
    date_patterns = [
        r'\b\d{1,2}[-/.\s]\d{1,2}[-/.\s]\d{2,4}\b',  # 31-12-1990 или 31.12.90
        r'\b\d{4}[-/.\s]\d{1,2}[-/.\s]\d{1,2}\b',    # 1990-12-31
        r'\b\d{1,2}[-/.\s]\d{4}[-/.\s]\d{1,2}\b',    # 31-1990-12
        r'\b\d{8}\b',                               # 31121990
        r'\b\d{6,8}\b'                              # 311290 или 1231990
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, cleaned)
        for match in matches:
            try:
                dt = parser.parse(match, dayfirst=True, yearfirst=False)
                # Проверка, что дата разумная (не в будущем, возраст < 120)
                today = datetime.now()
                if dt <= today and (today.year - dt.year) < 120:
                    return dt
            except Exception:
                continue

    # Последняя попытка — спарсить всю строку целиком
    try:
        dt = parser.parse(cleaned, dayfirst=True)
        today = datetime.now()
        if dt <= today and (today.year - dt.year) < 120:
            return dt
    except Exception:
        return None

    return None


def weekday(year: int, month: int, day: int) -> int:
    if month < 3:
        year -= 1
        month += 10
    else:
        month -= 2
    return (day + 31 * month // 12 + year + year // 4 - year // 100 + year // 400) % 7


def my_krug(birth_date: str, device: str) -> tuple[int, str]:
    valid_date = parse_birth_date(birth_date)
    if not valid_date:
        valid_date = dateparser.parse(birth_date)
    if not valid_date:
        raise ValueError(f"Не распознан формат даты -> {birth_date}")

    krug_number = weekday(
        valid_date.year,
        valid_date.month,
        valid_date.day
    ) + 1

    return krug_number, get_krug_text(krug_number, device)
