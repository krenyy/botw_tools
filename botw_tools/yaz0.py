import argparse
import sys
from pathlib import Path
import oead


def guess_dst(_yaz0: bool, path: Path):
    if _yaz0:
        return path.with_suffix(f".s{path.suffix.lstrip('.')}")
    return path.with_suffix(f".{path.suffix.lstrip('.s')}")


def parse_args():
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
        help="Destination file (writes to stdout if empty or '-')",
    )

    return parser.parse_args()


def yaz(args: argparse.Namespace, data: bytes):
    compressed = oead.yaz0.compress(data)

    if not args.dst or args.dst.name == "-":
        with sys.stdout.buffer as stdout:
            stdout.write(compressed)

    elif args.dst:
        if args.dst.name == "!!":
            args.dst = guess_dst(True, args.src)

        args.dst.write_bytes(compressed)
        print(args.dst.name)


def unyaz(args: argparse.Namespace, data: bytes):
    decompressed = oead.yaz0.decompress(data)

    if not args.dst or args.dst.name == "-":
        with sys.stdout.buffer as stdout:
            stdout.write(decompressed)

    elif args.dst:
        if args.dst.name == "!!":
            args.dst = guess_dst(False, args.src)

        args.dst.write_bytes(decompressed)
        print(args.dst.name)


def main():
    args = parse_args()

    if not args.src or args.src.name == "-":
        if not args.dst:
            args.dst = Path("-")
        with sys.stdin.buffer as stdin:
            data = stdin.read()
    else:
        data = args.src.read_bytes()

    if data[:4] == b"Yaz0":
        unyaz(args, data)

    else:
        yaz(args, data)
