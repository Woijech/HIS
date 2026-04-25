from ..domain.models import BucketSnapshot, HashTableEntry, KeyDiagnostics, TableStatistics


APP_TITLE = 'Лабораторная работа №4. Хеш-таблица с цепочками в виде AVL-деревьев'
SEPARATOR = '=' * 78

HELP_TEXT = (
    'Формула из методички:\n'
    '- числовое значение ключа V вычисляется по первым двум буквам;\n'
    '- используется русский алфавит из 33 букв: А=0, Б=1, ..., Я=32;\n'
    '- формула адреса: h(V) = V mod H + B.\n'
    '\n'
    'Архитектура решения:\n'
    '- domain: хеширование, AVL-дерево, хеш-таблица и модели;\n'
    '- application: сервис сценариев использования и демо-данные;\n'
    '- presentation: консольное меню и форматирование вывода.\n'
    '\n'
    'Коллизии разрешаются цепочками, где каждая корзина представляет собой '
    'сбалансированное AVL-дерево.\n'
)


def render_section(title: str, body: str) -> str:
    return f'{SEPARATOR}\n{title}\n{SEPARATOR}\n{body}'.rstrip()


def render_diagnostics(diagnostics: KeyDiagnostics, collision: bool | None = None) -> str:
    lines = [
        f"Ключ: {diagnostics.key}",
        f'V(K): {diagnostics.numeric_value}',
        f'h(V): {diagnostics.hash_address}',
        f'Индекс корзины: {diagnostics.bucket_index}',
    ]
    if collision is not None:
        lines.append(f"Коллизия при вставке: {'да' if collision else 'нет'}")
    return '\n'.join(lines)


def render_entry(entry: HashTableEntry, title: str = 'Запись') -> str:
    return '\n'.join(
        (
            title,
            f'Ключ: {entry.key}',
            f'Данные: {entry.value}',
            f'V(K): {entry.numeric_value}',
            f'h(V): {entry.hash_address}',
        )
    )


def render_bucket(bucket: BucketSnapshot) -> str:
    header = (
        f'Адрес {bucket.hash_address} '
        f'(bucket={bucket.bucket_index}, size={bucket.size}, '
        f'height={bucket.height}, root={bucket.root_key or "-"})'
    )
    if not bucket.entries:
        return f'{header}\n  пусто'

    lines = [header]
    for entry in bucket.entries:
        lines.append(
            '  - '
            f'{entry.key}: {entry.value} '
            f'[V={entry.numeric_value}, h={entry.hash_address}]'
        )
    return '\n'.join(lines)


def render_table(buckets: tuple[BucketSnapshot, ...]) -> str:
    if not buckets:
        return 'Таблица не инициализирована.'
    return '\n\n'.join(render_bucket(bucket) for bucket in buckets)


def render_statistics(stats: TableStatistics) -> str:
    return '\n'.join(
        (
            f'Размер таблицы: {stats.capacity}',
            f'Количество записей: {stats.size}',
            f'Занятые корзины: {stats.used_buckets}',
            f'Пустые корзины: {stats.empty_buckets}',
            f'Корзины с коллизиями: {stats.collision_buckets}',
            f'Количество коллизий: {stats.collisions}',
            f'Максимальная длина цепочки: {stats.max_chain_length}',
            f'Максимальная высота AVL-дерева: {stats.max_tree_height}',
            f'Коэффициент заполнения: {stats.load_factor:.2f}',
        )
    )
