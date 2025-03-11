import re
import string
from typing import List
from collections import Counter

def get_longest_diverse_words(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # извлечене слов
    words = re.findall(r"[A-Za-z\u00C0-\u017F]+", text)
    unique_words = set(words)

    # Ссортировка
    # уник символы длина по алф
    sorted_words = sorted(
        unique_words,
        key=lambda w: (len(set(w.lower())), len(w), w.lower()),
        reverse=True
    )
    return sorted_words[:10]

def get_rarest_char(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    if not text:
        return ''
    # частота симв
    counter = Counter(text)
    # мин симв
    rarest = min(counter.items(), key=lambda x: x[1])[0]
    return rarest


def count_punctuation_chars(file_path: str) -> int:
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    punctuation_set = set(string.punctuation)
    # заки препинания
    count = sum(1 for ch in text if ch in punctuation_set)
    return count

def count_non_ascii_chars(file_path: str) -> int:
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # не аски
    count = sum(1 for ch in text if ord(ch) > 127)
    return count


def get_most_common_non_ascii_char(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # фильтр не в аске
    non_ascii_chars = [ch for ch in text if ord(ch) > 127]
    if not non_ascii_chars:
        return ''
    counter = Counter(non_ascii_chars)
    most_common = counter.most_common(1)[0][0]
    return most_common


# Пример использования:
if __name__ == "__main__":
    file_path = '.venv/data.txt'
    print("10 самых 'разнообразных' слов:", get_longest_diverse_words(file_path))
    print("Самый редкий символ:", get_rarest_char(file_path))
    print("Количество знаков препинания:", count_punctuation_chars(file_path))
    print("Количество не-ASCII символов:", count_non_ascii_chars(file_path))
    print("Самый частый не-ASCII символ:", get_most_common_non_ascii_char(file_path))
