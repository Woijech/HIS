from __future__ import annotations

import unittest

from hashlab.domain.avl_tree import AVLTree
from hashlab.domain.exceptions import DuplicateKeyError, KeyNotFoundError


class TestAVLTree(unittest.TestCase):
    def test_tree_balances_left_left_rotation(self) -> None:
        tree = AVLTree[int]()
        tree.insert('m', 1)
        tree.insert('l', 2)
        tree.insert('k', 3)

        self.assertEqual(tree.root_value, 2)
        self.assertEqual(tree.height, 2)
        self.assertEqual(tree.items(), (('k', 3), ('l', 2), ('m', 1)))

    def test_tree_balances_right_left_rotation(self) -> None:
        tree = AVLTree[int]()
        tree.insert('a', 1)
        tree.insert('c', 2)
        tree.insert('b', 3)

        self.assertEqual(tree.root_value, 3)
        self.assertEqual(tree.height, 2)
        self.assertEqual(tree.items(), (('a', 1), ('b', 3), ('c', 2)))

    def test_replace_and_delete_work_correctly(self) -> None:
        tree = AVLTree[str]()
        tree.insert('b', 'beta')
        tree.insert('a', 'alpha')
        tree.insert('c', 'gamma')

        tree.replace('b', 'BETA')
        removed = tree.delete('a')

        self.assertEqual(removed, 'alpha')
        self.assertEqual(tree.get('b'), 'BETA')
        self.assertEqual(tree.items(), (('b', 'BETA'), ('c', 'gamma')))

    def test_duplicate_and_missing_keys_raise_errors(self) -> None:
        tree = AVLTree[int]()
        tree.insert('x', 1)

        with self.assertRaises(DuplicateKeyError):
            tree.insert('x', 2)
        with self.assertRaises(KeyNotFoundError):
            tree.get('y')
        with self.assertRaises(KeyNotFoundError):
            tree.delete('y')


if __name__ == '__main__':
    unittest.main()
