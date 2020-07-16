import argparse
from pathlib import Path

import oead

from .common import write_stdout, read_stdin


def guess_dst(_yaz0: bool, path: Path) -> Path:
    if _yaz0:
        return path.with_suffix(f".s{path.suffix[1:]}")
    return path.with_suffix(f".{path.suffix[2:]}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="De/compress a file using Yaz-0")

    parser.add_argument(
        "src",
        type=Path,
        nargs="?",
        help="Source file (reads from stdin if empty or '-')",
    )
    parser.add_argument(
        "dst",
        type=Path,
        nargs="?",
        help="Destination file (writes to stdout if empty or '-', '!!' to guess filename)",
    )

    return parser.parse_args()


def yaz(args: argparse.Namespace, data: bytes) -> int:
    compressed = oead.yaz0.compress(data)

    if not args.dst or args.dst.name == "-":
        write_stdout(compressed)
        return 0

    if args.dst.name == "!!":
        args.dst = guess_dst(True, args.src)

    args.dst.write_bytes(compressed)
    write_stdout(f"{args.dst.name}\n".encode("utf-8"))
    return 0


def unyaz(args: argparse.Namespace, data: bytes) -> int:
    decompressed = oead.yaz0.decompress(data)

    if not args.dst or args.dst.name == "-":
        write_stdout(decompressed)
        return 0

    if args.dst.name == "!!":
        args.dst = guess_dst(False, args.src)

    args.dst.write_bytes(decompressed)
    write_stdout(f"{args.dst.name}\n".encode("utf-8"))
    return 0


def main() -> int:
    args = parse_args()

    data = (
        read_stdin() if not args.src or args.src.name == "-" else args.src.read_bytes()
    )

    if data[:4] == b"Yaz0":
        return unyaz(args, data)
    else:
        return yaz(args, data)
