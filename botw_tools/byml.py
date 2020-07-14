import argparse
import sys
from pathlib import Path
from .yaz0 import guess_dst as yaz0_guess_dst
import oead


def guess_dst(_byml: bool, path: Path):
    if _byml:
        if "mubin.yml" in path.name:
            return path.with_name(".".join(path.name.split(".")[:2]))
        return path.with_suffix(f".b{path.suffix.lstrip('.')}")
    if "mubin" in path.suffix:
        return path.with_suffix(".mubin.yml")
    return path.with_suffix(f".{path.suffix.lstrip('.b')}")


def parse_args():
    parser = argparse.ArgumentParser(description="Convert between BYML and YML")

    parser.add_argument(
        "-y", "--yaz0", action="store_true", help="Force Yaz-0 compression"
    )
    parser.add_argument(
        "-b", "--big_endian", action="store_true", help="Use big endian (Wii U)"
    )
    parser.add_argument(
        "src",
        type=Path,
        nargs="?",
        help="Source BYML or YML file (reads from stdin if empty)",
    )
    parser.add_argument(
        "dst",
        type=Path,
        nargs="?",
        help="Destination AAMP or YML file (writes to stdout if empty)",
    )

    return parser.parse_args()


def byml_to_yml(args: argparse.Namespace, data: bytes):
    _byml = oead.byml.from_binary(data)

    if not args.dst or args.dst.stem == "-":
        print(oead.byml.to_text(_byml))

    elif args.dst:
        if args.dst.stem == "!!":
            args.dst = guess_dst(False, yaz0_guess_dst(False, args.src))

        args.dst.write_text(oead.byml.to_text(_byml))
        print(args.dst.name)


def yml_to_byml(args: argparse.Namespace, data: bytes):
    _byml = oead.byml.from_text(data.decode())

    data = oead.byml.to_binary(_byml, args.big_endian)

    if not args.dst or args.dst.stem == "-":
        with sys.stdout.buffer as stdout:
            stdout.write(oead.yaz0.compress(data) if True else data)

    elif args.dst:
        if args.dst.stem == "!!":
            guessed = guess_dst(True, args.src)
            args.dst = yaz0_guess_dst(True, guessed) if args.yaz0 else guessed

        args.dst.write_bytes(
            oead.yaz0.compress(data)
            if args.dst.suffix.startswith(".s") or args.yaz0
            else data
        )
        print(args.dst.name)


def main():
    args = parse_args()

    if not args.src or args.src.stem == "-":
        with sys.stdin.buffer as stdin:
            data = stdin.read()
    else:
        data = args.src.read_bytes()

    if data[:4] == b"Yaz0":
        data = oead.yaz0.decompress(data)

    if data[:2] in (b"BY", b"YB"):
        byml_to_yml(args, data)

    else:
        yml_to_byml(args, data)
