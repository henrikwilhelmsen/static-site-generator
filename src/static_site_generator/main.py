# Copyright (C) 2026 Henrik Wilhelmsen.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at <https://mozilla.org/MPL/2.0/>.

import shutil
import sys
from pathlib import Path

from static_site_generator.parsing import generate_pages

PROJECT_DIR = Path(__file__).parent.parent.parent
STATIC_DIR = PROJECT_DIR / "static"
PUBLIC_DIR = PROJECT_DIR / "public"
DOCS_DIR = PROJECT_DIR / "docs"
CONTENT_DIR = PROJECT_DIR / "content"
HTML_TEMPLATE = PROJECT_DIR / "template.html"


def _copy(src: Path, dst: Path) -> None:
    if src.is_file():
        dst.parent.mkdir(exist_ok=True, parents=True)
        shutil.copy2(src, dst)

    if src.is_dir():
        for p in src.glob("*"):
            _copy(src=p, dst=dst / p.name)


# Assignment says to implement this, instead of using shutil.copytree, so here we are
def copy_tree(src: Path, dst: Path) -> None:
    """Copy the given source directory to the given destionation directory."""
    if not src.is_dir():
        raise ValueError

    if dst.exists():
        if not dst.is_dir():
            raise ValueError

        shutil.rmtree(dst)

    _copy(src, dst)


def main() -> None:
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    copy_tree(STATIC_DIR, DOCS_DIR)
    generate_pages(
        source_dir=CONTENT_DIR,
        target_dir=DOCS_DIR,
        template_file=HTML_TEMPLATE,
        basepath=basepath,
    )
