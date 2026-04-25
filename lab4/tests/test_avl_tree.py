import unittest

from hashlab.domain.avl_tree import AVLTree
from hashlab.domain.exceptions import DuplicateKeyError, KeyNotFoundError


class TestAVLTree(unittest.TestCase):
    def test_tree_balances_left_left_rotation(self) -> None:
        tree = AVLTree()
        tree.insert('m', 1)
        tree.insert('l', 2)
        tree.insert('k', 3)

        self.assertEqual(tree.root_value, 2)
        self.assertEqual(tree.height, 2)
        self.assertEqual(tree.items(), (('k', 3), ('l', 2), ('m', 1)))

    def test_tree_balances_right_left_rotation(self) -> None:
        tree = AVLTree()
        tree.insert('a', 1)
        tree.insert('c', 2)
        tree.insert('b', 3)

        self.assertEqual(tree.root_value, 3)
        self.assertEqual(tree.height, 2)
        self.assertEqual(tree.items(), (('a', 1), ('b', 3), ('c', 2)))

    def test_tree_balances_right_right_rotation(self) -> None:
        tree = AVLTree()
        tree.insert('a', 1)
        tree.insert('b', 2)
        tree.insert('c', 3)

        self.assertEqual(tree.root_value, 2)
        self.assertEqual(tree.height, 2)
        self.assertEqual(tree.items(), (('a', 1), ('b', 2), ('c', 3)))

    def test_tree_balances_left_right_rotation(self) -> None:
        tree = AVLTree()
        tree.insert('c', 1)
        tree.insert('a', 2)
        tree.insert('b', 3)

        self.assertEqual(tree.root_value, 3)
        self.assertEqual(tree.height, 2)
        self.assertEqual(tree.items(), (('a', 2), ('b', 3), ('c', 1)))

    def test_replace_and_delete_work_correctly(self) -> None:
        tree = AVLTree()
        tree.insert('b', 'beta')
        tree.insert('a', 'alpha')
        tree.insert('c', 'gamma')

        tree.replace('b', 'BETA')
        removed = tree.delete('a')

        self.assertEqual(removed, 'alpha')
        self.assertEqual(tree.get('b'), 'BETA')
        self.assertEqual(tree.items(), (('b', 'BETA'), ('c', 'gamma')))

    def test_duplicate_and_missing_keys_raise_errors(self) -> None:
        tree = AVLTree()
        tree.insert('x', 1)

        with self.assertRaises(DuplicateKeyError):
            tree.insert('x', 2)
        with self.assertRaises(KeyNotFoundError):
            tree.get('y')
        with self.assertRaises(KeyNotFoundError):
            tree.delete('y')

    def test_replace_missing_key_raises_error(self) -> None:
        tree = AVLTree()

        with self.assertRaises(KeyNotFoundError):
            tree.replace('missing', 'value')

    def test_delete_node_with_two_children_keeps_tree_sorted(self) -> None:
        tree = AVLTree()
        for key in ('d', 'b', 'f', 'a', 'c', 'e', 'g'):
            tree.insert(key, key.upper())

        removed = tree.delete('d')

        self.assertEqual(removed, 'D')
        self.assertEqual(tree.items(), (
            ('a', 'A'),
            ('b', 'B'),
            ('c', 'C'),
            ('e', 'E'),
            ('f', 'F'),
            ('g', 'G'),
        ))

    def test_delete_missing_key_inside_subtrees_keeps_tree_unchanged(self) -> None:
        tree = AVLTree()
        tree.insert('b', 2)
        tree.insert('a', 1)
        tree.insert('c', 3)

        with self.assertRaises(KeyNotFoundError):
            tree.delete('aa')
        with self.assertRaises(KeyNotFoundError):
            tree.delete('d')

        self.assertEqual(tree.items(), (('a', 1), ('b', 2), ('c', 3)))

    def test_delete_node_with_only_left_child(self) -> None:
        tree = AVLTree()
        tree.insert('b', 2)
        tree.insert('a', 1)

        removed = tree.delete('b')

        self.assertEqual(removed, 2)
        self.assertEqual(tree.items(), (('a', 1),))

    def test_delete_node_from_right_subtree(self) -> None:
        tree = AVLTree()
        tree.insert('b', 2)
        tree.insert('a', 1)
        tree.insert('c', 3)

        removed = tree.delete('c')

        self.assertEqual(removed, 3)
        self.assertEqual(tree.items(), (('a', 1), ('b', 2)))

    def test_rotation_helpers_reject_invalid_nodes(self) -> None:
        tree = AVLTree()

        with self.assertRaises(ValueError):
            tree._rotate_left(None)
        with self.assertRaises(ValueError):
            tree._rotate_right(None)
        self.assertEqual(tree._balance_factor(None), 0)


if __name__ == '__main__':
    unittest.main()
