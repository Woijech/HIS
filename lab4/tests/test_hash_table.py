import unittest

from hashlab.application.service import DEMO_RECORDS
from hashlab.domain.exceptions import DuplicateKeyError, InvalidKeyError, KeyNotFoundError
from hashlab.domain.hash_table import HashTable


class TestHashTable(unittest.TestCase):
    def setUp(self) -> None:
        self.table = HashTable(capacity=20)

    def test_insert_and_get_return_full_entry(self) -> None:
        entry = self.table.insert('Алгоритм', 'Описание алгоритма')

        self.assertEqual(entry.key, 'Алгоритм')
        self.assertEqual(entry.value, 'Описание алгоритма')
        self.assertEqual(entry.numeric_value, 12)
        self.assertEqual(entry.hash_address, 12)
        self.assertEqual(self.table.get('алгоритм'), entry)

    def test_duplicate_key_is_rejected_case_insensitively(self) -> None:
        self.table.insert('Алгоритм', 'Описание алгоритма')

        with self.assertRaises(DuplicateKeyError):
            self.table.insert('  алгоритм ', 'Другое описание')

    def test_collisions_are_stored_in_same_bucket_avl_tree(self) -> None:
        first = self.table.insert('Алгоритм', 'A')
        second = self.table.insert('Алфавит', 'B')
        third = self.table.insert('Аллокация', 'C')

        bucket = self.table.bucket_snapshot(first.hash_address)

        self.assertEqual(first.hash_address, second.hash_address)
        self.assertEqual(second.hash_address, third.hash_address)
        self.assertEqual(bucket.size, 3)
        self.assertEqual(bucket.height, 2)
        self.assertEqual([entry.key for entry in bucket.entries], ['Алгоритм', 'Аллокация', 'Алфавит'])

    def test_update_preserves_hashing_metadata(self) -> None:
        original = self.table.insert('Байт', '8 бит')
        updated = self.table.update('байт', 'Минимальная адресуемая единица памяти')

        self.assertEqual(updated.key, original.key)
        self.assertEqual(updated.numeric_value, original.numeric_value)
        self.assertEqual(updated.hash_address, original.hash_address)
        self.assertEqual(updated.value, 'Минимальная адресуемая единица памяти')

    def test_delete_removes_entry(self) -> None:
        self.table.insert('Дерево', 'Иерархия')
        removed = self.table.delete('дерево')

        self.assertEqual(removed.key, 'Дерево')
        self.assertFalse(self.table.contains('дерево'))
        with self.assertRaises(KeyNotFoundError):
            self.table.get('дерево')

    def test_table_rejects_invalid_configuration(self) -> None:
        with self.assertRaises(ValueError):
            HashTable(capacity=0)
        with self.assertRaises(ValueError):
            HashTable(capacity=5, base_address=-1)

    def test_base_address_is_used_in_hash_address(self) -> None:
        table = HashTable(capacity=20, base_address=100)
        entry = table.insert('Алгоритм', 'A')

        self.assertEqual(table.base_address, 100)
        self.assertEqual(entry.hash_address, 112)
        self.assertEqual(table.bucket_snapshot(12).hash_address, 112)

    def test_clear_removes_all_records(self) -> None:
        self.table.insert('Байт', '8 бит')
        self.table.clear()

        self.assertEqual(self.table.size, 0)
        self.assertEqual(self.table.statistics().used_buckets, 0)

    def test_invalid_key_and_bucket_errors_are_reported(self) -> None:
        self.assertFalse(self.table.contains(''))
        with self.assertRaises(InvalidKeyError):
            self.table.inspect_key(None)
        with self.assertRaises(IndexError):
            self.table.bucket_size(99)

    def test_missing_update_and_delete_raise_domain_error(self) -> None:
        with self.assertRaises(KeyNotFoundError):
            self.table.update('Байт', 'новое значение')
        with self.assertRaises(KeyNotFoundError):
            self.table.delete('Байт')

    def test_out_of_range_hash_address_is_rejected(self) -> None:
        class BadAddressStrategy:
            def to_address(self, numeric_value: int, capacity: int, base_address: int = 0) -> int:
                return base_address + capacity

        table = HashTable(capacity=5, address_strategy=BadAddressStrategy())

        with self.assertRaises(InvalidKeyError):
            table.inspect_key('Алгоритм')

    def test_statistics_match_demo_dataset_requirements(self) -> None:
        for key, value in DEMO_RECORDS:
            self.table.insert(key, value)

        stats = self.table.statistics()

        self.assertEqual(stats.capacity, 20)
        self.assertEqual(stats.size, len(DEMO_RECORDS))
        self.assertGreaterEqual(stats.collisions, 4)
        self.assertGreaterEqual(stats.collision_buckets, 2)
        self.assertGreaterEqual(stats.max_chain_length, 3)
        self.assertAlmostEqual(stats.load_factor, len(DEMO_RECORDS) / 20)


if __name__ == '__main__':
    unittest.main()
