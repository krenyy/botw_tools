import argparse

import oead
from pathlib import Path
import sys


def guess_dst(_aamp: bool, path: Path):
    if _aamp:
        return path.with_suffix("").with_suffix(
            f".b{path.name.split('.')[-2].lstrip('.')}"
        )
    return path.with_suffix(f".{path.suffix[2:]}.yml")


def parse_args():
    parser = argparse.ArgumentParser(description="Convert between AAMP and YML")

    parser.add_argument(
        "src",
        type=Path,
        nargs="?",
        help="Source AAMP or YML file (reads from stdin if empty)",
    )
    parser.add_argument(
        "dst",
        type=Path,
        nargs="?",
        help="Destination AAMP or YML file (writes to stdout if empty)",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if not args.src or args.src.stem == "-":
        with sys.stdin.buffer as stdin:
            data = stdin.read()
    else:
        data = args.src.read_bytes()

    if data[:4] == b"AAMP":

        pio = oead.aamp.ParameterIO.from_binary(data)
        out = pio.to_text()

        if not args.dst or args.dst.stem == "-":
            print(out)

            return 0

        elif args.dst:

            if args.dst.stem == "!!":
                args.dst = guess_dst(False, args.src)

            args.dst.write_text(out)

            return 0

    pio = oead.aamp.ParameterIO.from_text(data.decode())
    out = pio.to_binary()

    if not args.dst or args.dst.stem == "-":
        print(bytes(out))

        return 0

    elif args.dst:

        if args.dst.stem == "!!":
            args.dst = guess_dst(True, args.src)

        args.dst.write_bytes(out)

        return 0
