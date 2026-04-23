from __future__ import annotations

import argparse
import sys
from typing import Callable, TextIO

from ..application.service import HashTableService
from ..domain.exceptions import HashTableError
from .formatter import (
    APP_TITLE,
    HELP_TEXT,
    render_diagnostics,
    render_entry,
    render_section,
    render_statistics,
    render_table,
)


InputFunc = Callable[[str], str]


def _println(output: TextIO, text: str = '') -> None:
    output.write(text + '\n')


def _ask(input_func: InputFunc, output: TextIO, prompt: str) -> str:
    if input_func is input and output is sys.stdout:
        return input_func(prompt)
    output.write(prompt)
    return input_func('')


def _menu_text(service: HashTableService) -> str:
    return '\n'.join(
        (
            APP_TITLE,
            f'Размер таблицы: {service.capacity}, записей: {service.size}',
            '',
            '1. Добавить запись',
            '2. Найти запись',
            '3. Обновить запись',
            '4. Удалить запись',
            '5. Показать всю таблицу',
            '6. Показать статистику',
            '7. Загрузить демонстрационные данные',
            '8. Очистить таблицу',
            '9. Справка',
            '0. Выход',
        )
    )


def _print_result(output: TextIO, title: str, body: str) -> None:
    _println(output, render_section(title, body))


def _handle_insert(service: HashTableService, input_func: InputFunc, output: TextIO) -> None:
    key = _ask(input_func, output, 'Введите ключ: ').strip()
    value = _ask(input_func, output, 'Введите данные: ').strip()
    diagnostics = service.inspect_key(key)
    collision = service.bucket_size(diagnostics.bucket_index) > 0
    entry = service.insert_record(key, value)
    body = '\n\n'.join(
        (
            render_diagnostics(diagnostics, collision=collision),
            render_entry(entry, title='Запись добавлена'),
        )
    )
    _print_result(output, 'Добавление записи', body)


def _handle_find(service: HashTableService, input_func: InputFunc, output: TextIO) -> None:
    key = _ask(input_func, output, 'Введите ключ для поиска: ').strip()
    entry = service.find_record(key)
    _print_result(output, 'Поиск записи', render_entry(entry, title='Запись найдена'))


def _handle_update(service: HashTableService, input_func: InputFunc, output: TextIO) -> None:
    key = _ask(input_func, output, 'Введите ключ для обновления: ').strip()
    value = _ask(input_func, output, 'Введите новые данные: ').strip()
    entry = service.update_record(key, value)
    _print_result(output, 'Обновление записи', render_entry(entry, title='Запись обновлена'))


def _handle_delete(service: HashTableService, input_func: InputFunc, output: TextIO) -> None:
    key = _ask(input_func, output, 'Введите ключ для удаления: ').strip()
    entry = service.delete_record(key)
    _print_result(output, 'Удаление записи', render_entry(entry, title='Запись удалена'))


def _handle_show_table(service: HashTableService, output: TextIO) -> None:
    _print_result(output, 'Содержимое таблицы', render_table(service.snapshot()))


def _handle_show_stats(service: HashTableService, output: TextIO) -> None:
    _print_result(output, 'Статистика', render_statistics(service.statistics()))


def _handle_load_demo(service: HashTableService, output: TextIO) -> None:
    inserted = service.load_demo_records()
    lines = [
        f'Загружено записей: {len(inserted)}',
        '',
        render_statistics(service.statistics()),
    ]
    _print_result(output, 'Демонстрационные данные', '\n'.join(lines))


def _handle_clear(service: HashTableService, output: TextIO) -> None:
    service.clear()
    _print_result(output, 'Очистка таблицы', 'Таблица очищена.')


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='hashlab',
        description='ЛР4: хеш-таблица с разрешением коллизий через AVL-деревья.',
    )
    parser.add_argument('--capacity', type=int, default=20, help='Количество корзин.')
    parser.add_argument('--base-address', type=int, default=0, help='Базовый адрес B.')
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Загрузить демонстрационные данные перед запуском меню.',
    )
    return parser


def run_console(
    argv: list[str] | None = None,
    input_func: InputFunc = input,
    output: TextIO | None = None,
) -> int:
    stream = output if output is not None else sys.stdout
    args = _build_parser().parse_args(argv)
    service = HashTableService(capacity=args.capacity, base_address=args.base_address)

    if args.demo:
        _handle_load_demo(service, stream)

    handlers = {
        '1': lambda: _handle_insert(service, input_func, stream),
        '2': lambda: _handle_find(service, input_func, stream),
        '3': lambda: _handle_update(service, input_func, stream),
        '4': lambda: _handle_delete(service, input_func, stream),
        '5': lambda: _handle_show_table(service, stream),
        '6': lambda: _handle_show_stats(service, stream),
        '7': lambda: _handle_load_demo(service, stream),
        '8': lambda: _handle_clear(service, stream),
        '9': lambda: _print_result(stream, 'Справка', HELP_TEXT),
    }

    while True:
        _println(stream, _menu_text(service))
        choice = _ask(input_func, stream, 'Выберите пункт меню: ').strip()
        if choice == '0':
            _println(stream, 'Завершение программы.')
            return 0

        handler = handlers.get(choice)
        if handler is None:
            _println(stream, 'Неизвестная команда.')
            continue

        try:
            handler()
        except HashTableError as error:
            _println(stream, f'Ошибка: {error}')
        except Exception as error:  # noqa: BLE001 - console boundary
            _println(stream, f'Непредвиденная ошибка: {error}')


def main(
    argv: list[str] | None = None,
    input_func: InputFunc = input,
    output: TextIO | None = None,
) -> int:
    return run_console(argv=argv, input_func=input_func, output=output)


if __name__ == '__main__':
    raise SystemExit(main())
