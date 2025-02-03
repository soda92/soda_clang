import shutil
from pathlib import Path

d = Path("tmp")

if d.exists() and d.is_dir():
    try:
        shutil.rmtree("tmp")
    except PermissionError:
        pass
elif d.is_file():
    d.unlink()

d.mkdir(exist_ok=True)
shutil.copy("2.c", d)
