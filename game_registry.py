'''Registry of supported games, and the project lifecycle operations (open,
create, duplicate) that depend on knowing which Project subclass a given
game id maps to.

Kept separate from asset_classes.py so "which games exist" stays a small,
Qt-free, easily-scanned concern - adding a future AC5Project is a matter of
defining the class (with GAME_ID/DISPLAY_NAME/REQUIRED_SOURCE_FILES class
attributes, see ACZProject) and adding one line to GAME_REGISTRY, with no
changes needed to any dialog code.'''
import json
import os
import shutil

from asset_classes import ACZProject, Project

GAME_REGISTRY: dict[str, type[Project]] = {
    ACZProject.GAME_ID: ACZProject,
}


class ProjectIOError(Exception):
    '''Base class for project open/create/duplicate failures - callers in
    the GUI layer catch this (not bare Exception) to show a message box
    instead of letting a raw parsing exception crash the app.'''


class ProjectLoadError(ProjectIOError):
    pass


class ProjectCreateError(ProjectIOError):
    pass


def default_projects_root() -> str:
    '''The repo's ./projects folder - single source of truth, reused by
    app.py, MainWindow, and both project dialogs instead of each
    recomputing the repo-root-relative path themselves.'''
    repo_root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(repo_root, 'projects')


def list_games() -> list[tuple[str, str]]:
    '''[(game_id, display_name), ...] for populating a game-choice combo box.'''
    return [(game_id, project_class.DISPLAY_NAME) for game_id, project_class in GAME_REGISTRY.items()]


def open_project(project_folder_path: str) -> Project:
    '''Opens an existing project folder, dispatching to the right Project
    subclass based on the "game" id recorded in its project.ACW. Never lets
    a raw exception escape - any failure (missing/corrupt ACW, unknown game
    id, missing source files) is wrapped as a ProjectLoadError so callers can
    show a clean error message instead of crashing.'''
    metadata = Project.read_acw_metadata(project_folder_path)
    if metadata is None:
        raise ProjectLoadError(f'"{project_folder_path}" does not contain a valid project.ACW.')

    game_id = metadata.get('game')
    project_class = GAME_REGISTRY.get(game_id)
    if project_class is None:
        raise ProjectLoadError(f'"{project_folder_path}" has an unknown game type: {game_id!r}.')

    try:
        return project_class(project_folder_path=project_folder_path)
    except Exception as exc:
        raise ProjectLoadError(f'Failed to open project at "{project_folder_path}": {exc}') from exc


def create_project(projects_root: str, name: str, game_id: str, source_file_paths: list[str]) -> Project:
    '''Creates a brand-new project under `projects_root`: validates the
    selected source files exactly match the chosen game's required set,
    copies them into the new project's source/ folder, then constructs it.
    The folder/files are fully in place before the Project subclass is ever
    constructed, so its normal (non-defensive) file-reading __init__ can
    assume its required files already exist.'''
    project_class = GAME_REGISTRY.get(game_id)
    if project_class is None:
        raise ProjectCreateError(f'Unknown game type: {game_id!r}.')

    required = {filename.lower() for filename in project_class.REQUIRED_SOURCE_FILES}
    selected = {os.path.basename(path).lower() for path in source_file_paths}
    if selected != required:
        missing = sorted(required - selected)
        extra = sorted(selected - required)
        problems = []
        if missing:
            problems.append(f'missing: {", ".join(missing)}')
        if extra:
            problems.append(f'unexpected: {", ".join(extra)}')
        raise ProjectCreateError(
            f'{project_class.DISPLAY_NAME} projects need exactly these source files: '
            f'{", ".join(project_class.REQUIRED_SOURCE_FILES)} ({"; ".join(problems)}).'
        )

    folder_name = _sanitize_folder_name(name)
    if not folder_name:
        raise ProjectCreateError('Project name must contain at least one valid character.')

    dest = os.path.join(projects_root, folder_name)
    if os.path.exists(dest):
        raise ProjectCreateError(f'A project folder already exists at "{dest}".')

    source_dest = os.path.join(dest, 'source')
    os.makedirs(source_dest)
    try:
        # Normalize each copied file to the registry's canonical filename
        # casing (e.g. always DATA.PAC), regardless of how it was cased on
        # the source disk, so ACZProject's fixed-case path lookups work.
        canonical_by_lower = {filename.lower(): filename for filename in project_class.REQUIRED_SOURCE_FILES}
        for path in source_file_paths:
            canonical_name = canonical_by_lower[os.path.basename(path).lower()]
            shutil.copy2(path, os.path.join(source_dest, canonical_name))

        return project_class(project_folder_path=dest, name=name)
    except Exception as exc:
        shutil.rmtree(dest, ignore_errors=True)
        raise ProjectCreateError(f'Failed to create project "{name}": {exc}') from exc


def duplicate_project(project: Project, new_name: str, projects_root: str) -> Project:
    '''"Save As": copies the project's whole folder (source/, and output/
    once that exists) to a new name under `projects_root`, updates the
    copy's project_name, and reopens it.'''
    folder_name = _sanitize_folder_name(new_name)
    if not folder_name:
        raise ProjectCreateError('Project name must contain at least one valid character.')

    dest = os.path.join(projects_root, folder_name)
    if os.path.exists(dest):
        raise ProjectCreateError(f'A project folder already exists at "{dest}".')

    try:
        shutil.copytree(project.folder_path, dest)

        acw_path = os.path.join(dest, Project.ACW_FILENAME)
        with open(acw_path, 'r') as flag_file:
            data = json.load(flag_file)
        data['project_name'] = new_name
        with open(acw_path, 'w') as flag_file:
            json.dump(data, flag_file)
    except Exception as exc:
        shutil.rmtree(dest, ignore_errors=True)
        raise ProjectCreateError(f'Failed to save project as "{new_name}": {exc}') from exc

    return open_project(dest)


def _sanitize_folder_name(name: str) -> str:
    '''Strips characters that are illegal in Windows folder names and
    collapses surrounding whitespace, for deriving a new project's folder
    name from its (freely-typed) display name.'''
    illegal = '<>:"/\\|?*'
    cleaned = ''.join(char for char in name if char not in illegal)
    return cleaned.strip()
