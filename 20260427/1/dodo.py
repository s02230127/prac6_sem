import shutil
from pathlib import Path

from doit.task import clean_targets


DOIT_CONFIG = {
    "default_tasks": ["html"],
}


PO_FILE = Path("mood/server/locales/ru/LC_MESSAGES/messages.po")
MO_FILE = Path("mood/server/locales/ru/LC_MESSAGES/messages.mo")

DOCS_SOURCE = Path("docs/source")
DOCS_BUILD = Path("docs/build")
HTML_INDEX = DOCS_BUILD / "html" / "index.html"


def remove_docs_build():
    """Remove docs."""
    if DOCS_BUILD.exists():
        shutil.rmtree(DOCS_BUILD)


def task_i18n_mo():
    """Compile ru translation."""
    return {
        'actions': [
            'pybabel compile -i mood/server/locales/ru/LC_MESSAGES/messages.po '
            '-o mood/server/locales/ru/LC_MESSAGES/messages.mo'
        ],
        'file_dep': [PO_FILE],
        'targets': [MO_FILE],
        'clean': [clean_targets],
    }


def task_i18n():
    """Generate translation."""
    return {
        "actions": None,
        "task_dep": ["i18n_mo"],
    }


def task_html():
    """Generate HTML documentation."""
    return {
        "actions": [
            f"sphinx-build -M html {DOCS_SOURCE} {DOCS_BUILD}",
        ],
        "file_dep": [
            "docs/source/conf.py",
            "docs/source/index.rst",
        ],
        "targets": [HTML_INDEX],
        "clean": [remove_docs_build],
    }


def task_test():
    """Run client and server tests."""
    return {
        "actions": [
            "python -m unittest test_client.py test_server.py",
        ],
        "task_dep": ["i18n"],
    }
