import argparse
from pathlib import Path

import oead

from .common import read_stdin, write_stdout


def guess_dst(_byml: bool, path: Path) -> Path:
    if _byml:
        if "mubin.yml" in path.name:
            return path.with_name(".".join(path.name.split(".")[:2]))
        return path.with_suffix(f".b{path.suffix[1:]}")
    if "mubin" in path.suffix:
        return path.with_suffix(".mubin.yml")
    return path.with_suffix(f".{path.suffix[2:]}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert between BYML and YML")

    parser.add_argument(
        "-b", "--big_endian", action="store_true", help="Use big endian (Wii U)"
    )
    parser.add_argument(
        "src",
        type=Path,
        nargs="?",
        help="Source BYML or YML file (reads from stdin if empty or '-')",
    )
    parser.add_argument(
        "dst",
        type=Path,
        nargs="?",
        help="Destination AAMP or YML file (writes to stdout if empty or '-', '!!' to guess filename)",
    )

    return parser.parse_args()


def byml_to_yml(args: argparse.Namespace, data: bytes) -> int:
    out = oead.byml.to_text(oead.byml.from_binary(data)).encode("utf-8")

    if not args.dst or args.dst.name == "-":
        write_stdout(out)
        return 0

    if args.dst.name == "!!":
        args.dst = guess_dst(False, args.src)

    args.dst.write_bytes(out)
    write_stdout(f"{args.dst.name}\n".encode("utf-8"))
    return 0


def yml_to_byml(args: argparse.Namespace, data: bytes) -> int:
    data = oead.byml.to_binary(
        oead.byml.from_text(data.decode("utf-8")), args.big_endian
    )

    if not args.dst or args.dst.name == "-":
        write_stdout(data)
        return 0

    if args.dst.name == "!!":
        args.dst = guess_dst(True, args.src)

    args.dst.write_bytes(data)
    write_stdout(f"{args.dst.name}\n".encode("utf-8"))
    return 0


def main() -> int:
    args = parse_args()

    data = (
        read_stdin() if not args.src or args.src.name == "-" else args.src.read_bytes()
    )

    if data[:4] == b"Yaz0":
        raise SystemExit("File is Yaz-0 compressed")
    if data[:2] in (b"BY", b"YB"):
        return byml_to_yml(args, data)
    else:
        return yml_to_byml(args, data)
