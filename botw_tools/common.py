import sys


def read_stdin() -> bytes:
    try:
        return sys.stdin.buffer.read()
    except KeyboardInterrupt:
        write_stdout("\n".encode("utf-8"))
        raise SystemExit()


def write_stdout(data: bytes) -> int:
    try:
        return sys.stdout.buffer.write(data)
    except BrokenPipeError:
        raise SystemExit()
