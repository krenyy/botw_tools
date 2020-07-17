import sys
from pathlib import Path
from typing import Callable, Optional


def read_stdin() -> bytes:
    try:
        return sys.stdin.buffer.read()
    except KeyboardInterrupt:
        write_stdout("\n".encode("utf-8"))
        raise SystemExit()


def write_stdout(data: bytes) -> int:
    try:
        return sys.stdout.buffer.write(data)
    except (KeyboardInterrupt, BrokenPipeError):
        raise SystemExit()


def read(src: Optional[Path]) -> bytes:
    if not src or src.name == "-":
        return read_stdin()
    elif src.is_file():
        return src.read_bytes()
    else:
        raise SystemExit(f"'{src.name}' doesn't exist or is not a file")


def write(
    data: bytes,
    src: Optional[Path],
    dst: Path,
    condition: Optional[bool],
    function: Optional[Callable],
) -> int:
    if not dst or dst.name == "-":
        return write_stdout(data)

    if (condition is not None) and (function is not None):
        if dst.name == "!!":
            dst = function(condition, src)

    dst.parent.mkdir(parents=True, exist_ok=True)
    ret = dst.write_bytes(data)
    write_stdout(f"Written '{dst.name}'\n".encode("utf-8"))

    return ret
