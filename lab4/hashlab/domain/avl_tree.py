from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, TypeVar

from .exceptions import DuplicateKeyError, KeyNotFoundError


ValueT = TypeVar('ValueT')


@dataclass(slots=True)
class _Node(Generic[ValueT]):
    key: str
    value: ValueT
    left: _Node[ValueT] | None = None
    right: _Node[ValueT] | None = None
    height: int = 1


class AVLTree(Generic[ValueT]):
    def __init__(self) -> None:
        self._root: _Node[ValueT] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    @property
    def height(self) -> int:
        return self._node_height(self._root)

    @property
    def root_value(self) -> ValueT | None:
        return None if self._root is None else self._root.value

    def is_empty(self) -> bool:
        return self._root is None

    def contains(self, key: str) -> bool:
        return self._find_node(self._root, key) is not None

    def get(self, key: str) -> ValueT:
        node = self._find_node(self._root, key)
        if node is None:
            raise KeyNotFoundError(f"Ключ '{key}' не найден в цепочке.")
        return node.value

    def insert(self, key: str, value: ValueT) -> None:
        self._root, inserted = self._insert(self._root, key, value)
        if not inserted:
            raise DuplicateKeyError(f"Ключ '{key}' уже существует в цепочке.")
        self._size += 1

    def replace(self, key: str, value: ValueT) -> None:
        self._root, replaced = self._replace(self._root, key, value)
        if not replaced:
            raise KeyNotFoundError(f"Ключ '{key}' не найден в цепочке.")

    def delete(self, key: str) -> ValueT:
        self._root, removed = self._delete(self._root, key)
        if removed is None:
            raise KeyNotFoundError(f"Ключ '{key}' не найден в цепочке.")
        self._size -= 1
        return removed

    def values(self) -> tuple[ValueT, ...]:
        return tuple(value for _, value in self.items())

    def items(self) -> tuple[tuple[str, ValueT], ...]:
        return tuple(self._inorder(self._root))

    def _find_node(self, node: _Node[ValueT] | None, key: str) -> _Node[ValueT] | None:
        current = node
        while current is not None:
            if key < current.key:
                current = current.left
                continue
            if key > current.key:
                current = current.right
                continue
            return current
        return None

    def _insert(
        self,
        node: _Node[ValueT] | None,
        key: str,
        value: ValueT,
    ) -> tuple[_Node[ValueT], bool]:
        if node is None:
            return _Node(key=key, value=value), True

        if key < node.key:
            node.left, inserted = self._insert(node.left, key, value)
        elif key > node.key:
            node.right, inserted = self._insert(node.right, key, value)
        else:
            return node, False

        return self._rebalance(node), inserted

    def _replace(
        self,
        node: _Node[ValueT] | None,
        key: str,
        value: ValueT,
    ) -> tuple[_Node[ValueT] | None, bool]:
        if node is None:
            return None, False

        if key < node.key:
            node.left, replaced = self._replace(node.left, key, value)
            if not replaced:
                return node, False
            return self._rebalance(node), True

        if key > node.key:
            node.right, replaced = self._replace(node.right, key, value)
            if not replaced:
                return node, False
            return self._rebalance(node), True

        node.value = value
        return node, True

    def _delete(
        self,
        node: _Node[ValueT] | None,
        key: str,
    ) -> tuple[_Node[ValueT] | None, ValueT | None]:
        if node is None:
            return None, None

        if key < node.key:
            node.left, removed = self._delete(node.left, key)
            if removed is None:
                return node, None
            return self._rebalance(node), removed

        if key > node.key:
            node.right, removed = self._delete(node.right, key)
            if removed is None:
                return node, None
            return self._rebalance(node), removed

        removed = node.value

        if node.left is None:
            return node.right, removed
        if node.right is None:
            return node.left, removed

        successor = self._min_node(node.right)
        node.key = successor.key
        node.value = successor.value
        node.right, _ = self._delete(node.right, successor.key)
        return self._rebalance(node), removed

    def _min_node(self, node: _Node[ValueT]) -> _Node[ValueT]:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def _inorder(self, node: _Node[ValueT] | None) -> Iterator[tuple[str, ValueT]]:
        if node is None:
            return
        yield from self._inorder(node.left)
        yield (node.key, node.value)
        yield from self._inorder(node.right)

    def _rebalance(self, node: _Node[ValueT]) -> _Node[ValueT]:
        self._update_height(node)
        balance = self._balance_factor(node)

        if balance > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        if balance < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _rotate_left(self, node: _Node[ValueT] | None) -> _Node[ValueT]:
        if node is None or node.right is None:
            raise ValueError('Левый поворот невозможен.')
        pivot = node.right
        node.right = pivot.left
        pivot.left = node
        self._update_height(node)
        self._update_height(pivot)
        return pivot

    def _rotate_right(self, node: _Node[ValueT] | None) -> _Node[ValueT]:
        if node is None or node.left is None:
            raise ValueError('Правый поворот невозможен.')
        pivot = node.left
        node.left = pivot.right
        pivot.right = node
        self._update_height(node)
        self._update_height(pivot)
        return pivot

    def _balance_factor(self, node: _Node[ValueT] | None) -> int:
        if node is None:
            return 0
        return self._node_height(node.left) - self._node_height(node.right)

    def _update_height(self, node: _Node[ValueT]) -> None:
        node.height = max(self._node_height(node.left), self._node_height(node.right)) + 1

    def _node_height(self, node: _Node[ValueT] | None) -> int:
        return 0 if node is None else node.height
