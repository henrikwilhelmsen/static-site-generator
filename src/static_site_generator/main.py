import shutil
from pathlib import Path

STATIC_DIR = Path(__file__).parent.parent.parent / "static"
PUBLIC_DIR = Path(__file__).parent.parent.parent / "public"


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
    copy_tree(STATIC_DIR, PUBLIC_DIR)
