from pathlib import Path

from dagster import definitions, load_from_defs_folder
from .defs.resources import resources


@definitions
def defs():
    folder_defs = load_from_defs_folder(
        path_within_project=Path(__file__).parent,
    )
    return folder_defs.with_resources(resources())
