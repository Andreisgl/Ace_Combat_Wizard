'''Qt-free CLI: browse asset types and dump raw bytes without exporting
files or opening the GUI. Only imports asset_classes/game_registry/
hex_format - never PySide6 - so this runs in any plain Python environment,
including one that doesn't have the GUI's dependencies installed.

Invoked via the dispatcher in gui_main.py: `python gui_main.py --cli ...`.'''
import argparse
import os
import sys

import game_registry
from asset_classes import CASTABLE_TYPES, Container
from hex_format import MAX_PREVIEW_BYTES, format_hex_dump

_CASTABLE_BY_NAME = {cls.__name__: cls for _, cls in CASTABLE_TYPES}


def _open_project(project_arg: str):
    path = project_arg if os.path.isdir(project_arg) else os.path.join(
        game_registry.default_projects_root(), project_arg)
    try:
        return game_registry.open_project(path)
    except game_registry.ProjectIOError as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)


def resolve_path(project, path_str: str):
    '''Walks project.DATA_PAC via slash-separated integer children dict
    keys (e.g. "3/19/9") - the real internal indices, not a tree view's
    positional row numbers. Empty string / "/" means DATA_PAC itself.'''
    asset = project.DATA_PAC
    path_str = (path_str or '').strip('/')
    if not path_str:
        return asset

    for part in path_str.split('/'):
        if not isinstance(asset, Container):
            raise ValueError(f"'{asset.name}' is not a container - can't descend into '{part}'")
        try:
            index = int(part)
        except ValueError:
            raise ValueError(f"'{part}' is not a valid index") from None
        if index not in asset.children:
            raise ValueError(f"No child at index {index} under '{asset.name}'")
        asset = asset.children[index]

    return asset


def _lookup_type(name: str):
    if name not in _CASTABLE_BY_NAME:
        available = ', '.join(sorted(_CASTABLE_BY_NAME))
        raise ValueError(f"Unknown type '{name}'. Available: {available}")
    return _CASTABLE_BY_NAME[name]


def _print_ls(asset):
    print(f'{asset.name}  {asset.display_type}  {asset.size:,} bytes')
    if not isinstance(asset, Container):
        return
    print(f'  ({len(asset.children)} children)')
    for index, child in asset.children.items():
        print(f'  {index:<6} {child.name:<40} {child.display_type:<30} {child.size:>10,} bytes')


def _cmd_ls(project, args):
    _print_ls(resolve_path(project, args.path))


def _cmd_hex(project, args):
    asset = resolve_path(project, args.path)
    data = asset.get_raw_data()

    start = args.offset
    end = len(data) if args.length is None else min(start + args.length, len(data))
    chunk = data[start:end]

    truncated = args.length is None and len(chunk) > MAX_PREVIEW_BYTES
    if truncated:
        chunk = chunk[:MAX_PREVIEW_BYTES]

    print(f'{asset.name}  ({asset.display_type}, {len(data):,} bytes total)')
    print(format_hex_dump(chunk))
    if truncated:
        print(f'... truncated, showing first {MAX_PREVIEW_BYTES:,} of {len(data) - start:,} '
              f'remaining bytes (use --length to see more)')


def _cmd_cast(project, args):
    asset = resolve_path(project, args.path)
    target_class = _lookup_type(args.type_name)
    new_asset = asset.cast_to(target_class)
    _print_ls(new_asset)


def _cmd_export(project, args):
    asset = resolve_path(project, args.path)
    with open(args.output_file, 'wb') as file:
        file.write(asset.get_raw_data())
    print(f"Wrote {asset.size:,} bytes to '{args.output_file}'")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='gui_main.py --cli', description='Ace Combat Wizard CLI')
    parser.add_argument('project', help='Project name (under ./projects) or a full project folder path')
    parser.add_argument(
        '--cast', action='append', default=[], metavar='PATH:TYPE',
        help='Cast an asset to TYPE before running the command (repeatable, applied in order)')

    subparsers = parser.add_subparsers(dest='command', required=True)

    ls_parser = subparsers.add_parser('ls', help="List a container's children")
    ls_parser.add_argument('path', nargs='?', default='')
    ls_parser.set_defaults(func=_cmd_ls)

    hex_parser = subparsers.add_parser('hex', help="Hex-dump an asset's raw bytes")
    hex_parser.add_argument('path')
    hex_parser.add_argument('--offset', type=int, default=0)
    hex_parser.add_argument('--length', type=int, default=None)
    hex_parser.set_defaults(func=_cmd_hex)

    cast_parser = subparsers.add_parser('cast', help='Cast an asset to a different type, then list it')
    cast_parser.add_argument('path')
    cast_parser.add_argument('type_name', metavar='type')
    cast_parser.set_defaults(func=_cmd_cast)

    export_parser = subparsers.add_parser('export', help="Save an asset's raw bytes to a file")
    export_parser.add_argument('path')
    export_parser.add_argument('output_file')
    export_parser.set_defaults(func=_cmd_export)

    return parser


def main(argv: list[str]):
    args = _build_parser().parse_args(argv)
    project = _open_project(args.project)

    for cast_spec in args.cast:
        cast_path, sep, type_name = cast_spec.partition(':')
        if not sep:
            print(f"Error: --cast expects PATH:TYPE, got '{cast_spec}'", file=sys.stderr)
            sys.exit(1)
        try:
            resolve_path(project, cast_path).cast_to(_lookup_type(type_name))
        except (ValueError, KeyError) as exc:
            print(f'Error casting {cast_path!r}: {exc}', file=sys.stderr)
            sys.exit(1)

    try:
        args.func(project, args)
    except (ValueError, KeyError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
