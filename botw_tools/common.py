import sys


def read_stdin() -> bytes:
    with sys.stdin.buffer as stdin:
        return stdin.read()


def write_stdout(data: bytes) -> int:
    with sys.stdout.buffer as stdout:
        return stdout.write(data)
