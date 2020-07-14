import argparse
import sys
from pathlib import Path
import oead


def guess_dst(_yaz0: bool, path: Path):
    if _yaz0:
        return path.with_suffix(f".s{path.suffix.lstrip('.')}")
    return path.with_suffix(f".{path.suffix.lstrip('.s')}")


def parse_args_unyaz():
    parser = argparse.ArgumentParser(description="Decompress a Yaz-0-compressed file")

    parser.add_argument(
        "-u", "--unsafe", action="store_true", help="Use unsafe decompress function"
    )
    parser.add_argument(
        "src",
        type=Path,
        nargs="?",
        help="Source Yaz-0 file (reads from stdin if empty)",
    )
    parser.add_argument(
        "dst",
        type=Path,
        nargs="?",
        help="Destination decompressed file (writes to stdout if empty)",
    )

    return parser.parse_args()


def parse_args_yaz():
    parser = argparse.ArgumentParser(description="Compress a file with Yaz-0")

    parser.add_argument(
        "src", type=Path, nargs="?", help="Source file (reads from stdin if empty)"
    )
    parser.add_argument(
        "dst",
        type=Path,
        nargs="?",
        help="Destination compressed file (writes to stdout if empty)",
    )

    return parser.parse_args()


def unyaz():
    args = parse_args_unyaz()

    if not args.src or args.src.stem == "-":
        with sys.stdin.buffer as stdin:
            data = stdin.read()
    else:
        data = args.src.read_bytes()

    decompressed = (
        oead.yaz0.decompress_unsafe if args.unsafe else oead.yaz0.decompress
    )(data)

    if not args.dst or args.dst.stem == "!!":
        args.dst = guess_dst(False, args.src)

    if args.dst.stem == "-":
        with sys.stdout.buffer as stdout:
            stdout.write(decompressed)

        return 0

    args.dst.write_bytes(decompressed)
    print(args.dst.name)

    return 0


def yaz():
    args = parse_args_yaz()

    if not args.src or args.src.stem == "-":
        with sys.stdin.buffer as stdin:
            data = stdin.read()
    else:
        data = args.src.read_bytes()

    compressed = oead.yaz0.compress(data)

    if not args.dst or args.dst.stem == "!!":
        args.dst = guess_dst(True, args.src)

    if args.dst.stem == "-":
        with sys.stdout.buffer as stdout:
            stdout.write(compressed)

        return 0

    args.dst.write_bytes(compressed)
    print(args.dst.name)

    return 0
