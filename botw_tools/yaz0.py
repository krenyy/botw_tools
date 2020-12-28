import argparse
from pathlib import Path

import oead

from .common import read, write


def guess_dst(_yaz0: bool, dst: Path) -> Path:
    return (
        dst.with_suffix(f".s{dst.suffix[1:]}")
        if _yaz0
        else dst.with_suffix(f".{dst.suffix[2:]}")
    )


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


def yaz(args: argparse.Namespace, data: bytes) -> None:
    write(
        data=oead.yaz0.compress(data),
        src=args.src,
        dst=args.dst,
        condition=True,
        function=guess_dst,
    )
    return


def unyaz(args: argparse.Namespace, data: bytes) -> None:
    write(
        data=oead.yaz0.decompress(data),
        src=args.src,
        dst=args.dst,
        condition=False,
        function=guess_dst,
    )
    return


def main() -> None:
    args = parse_args()
    data = read(args.src)

    if data[:4] == b"Yaz0":
        return unyaz(args, data)

    return yaz(args, data)
