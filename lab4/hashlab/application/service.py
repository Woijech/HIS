from __future__ import annotations

from typing import Final

from ..domain.hash_table import HashTable
from ..domain.models import BucketSnapshot, HashTableEntry, KeyDiagnostics, TableStatistics


DEMO_RECORDS: Final[tuple[tuple[str, str], ...]] = (
    ('Алгоритм', 'Конечная последовательность шагов для решения задачи.'),
    ('Алфавит', 'Набор символов, используемых для представления данных.'),
    ('Аллокация', 'Выделение памяти под данные или объекты программы.'),
    ('База данных', 'Организованная совокупность взаимосвязанных данных.'),
    ('Байт', 'Базовая единица хранения информации, обычно равная 8 битам.'),
    ('Барьер', 'Механизм синхронизации потоков или процессов.'),
    ('Вектор', 'Последовательность элементов, доступных по индексу.'),
    ('Граф', 'Структура данных из вершин и рёбер между ними.'),
    ('Дерево', 'Иерархическая структура данных без циклов.'),
    ('Кэш', 'Быстрая память для хранения часто используемых данных.'),
    ('Матрица', 'Прямоугольная таблица чисел или коэффициентов.'),
    ('Рекурсия', 'Приём, при котором функция вызывает саму себя.'),
)


class HashTableService:
    def __init__(self, capacity: int = 20, base_address: int = 0) -> None:
        self._table = HashTable[str](capacity=capacity, base_address=base_address)

    @property
    def capacity(self) -> int:
        return self._table.capacity

    @property
    def size(self) -> int:
        return self._table.size

    def inspect_key(self, key: str) -> KeyDiagnostics:
        return self._table.inspect_key(key)

    def bucket_size(self, bucket_index: int) -> int:
        return self._table.bucket_size(bucket_index)

    def insert_record(self, key: str, value: str) -> HashTableEntry[str]:
        return self._table.insert(key, value)

    def find_record(self, key: str) -> HashTableEntry[str]:
        return self._table.get(key)

    def update_record(self, key: str, value: str) -> HashTableEntry[str]:
        return self._table.update(key, value)

    def delete_record(self, key: str) -> HashTableEntry[str]:
        return self._table.delete(key)

    def clear(self) -> None:
        self._table.clear()

    def snapshot(self) -> tuple[BucketSnapshot[str], ...]:
        return self._table.snapshot()

    def statistics(self) -> TableStatistics:
        return self._table.statistics()

    def load_demo_records(self) -> tuple[HashTableEntry[str], ...]:
        inserted: list[HashTableEntry[str]] = []
        for key, value in DEMO_RECORDS:
            inserted.append(self.insert_record(key, value))
        return tuple(inserted)
