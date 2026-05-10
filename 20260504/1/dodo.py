"""Doit tasks for MUD project."""

import os
import shutil
from pathlib import Path


PO_FILE = Path("mood/server/locales/ru/LC_MESSAGES/messages.po")
MO_FILE = Path("mood/server/locales/ru/LC_MESSAGES/messages.mo")

DOCS_HTML = Path("mood/docs/html")


DOIT_CONFIG = {
    "default_tasks": ["html"],
}


def clean_targets(task):
    """Remove task targets."""
    for target in task.targets:
        if os.path.exists(target):
            os.remove(target)


def clean_html():
    """Remove generated HTML documentation directory."""
    if DOCS_HTML.exists():
        shutil.rmtree(DOCS_HTML)


def clean_mo():
    """Remove compiled translation."""
    if MO_FILE.exists():
        MO_FILE.unlink()


def task_i18n_mo():
    """Compile ru translation."""
    return {
        "actions": [
            "pybabel compile "
            f"-i {PO_FILE} "
            f"-o {MO_FILE}"
        ],
        "file_dep": [str(PO_FILE)],
        "targets": [str(MO_FILE)],
        "clean": [clean_targets],
    }


def task_i18n():
    """Generate translation."""
    return {
        "actions": None,
        "task_dep": ["i18n_mo"],
        "clean": [clean_mo],
    }


def task_html():
    """Generate HTML documentation."""
    return {
        "actions": [
            "mkdir -p mood/docs/html",
            "python -m sphinx -b html docs/source mood/docs/html",
        ],
        "file_dep": [
            "docs/source/conf.py",
            "docs/source/index.rst",
            "docs/source/modules.rst",
            "docs/source/mood.rst",
            "docs/source/mood.client.rst",
            "docs/source/mood.common.rst",
            "docs/source/mood.server.rst",
        ],
        "targets": [
            "mood/docs/html/index.html",
        ],
        "clean": [clean_html],
    }


def task_test():
    """Run client-server tests."""
    return {
        "actions": [
            "python -m unittest discover .",
        ],
        "task_dep": [
            "i18n",
        ],
        "clean": [],
    }
