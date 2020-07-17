import argparse
from pathlib import Path

import oead

from .common import read_stdin, write_stdout, write, read


def guess_dst(_byml: bool, dst: Path) -> Path:
    if "mubin" in dst.name:
        return (
            dst.with_name(".".join(dst.name.split(".")[:2]))
            if _byml
            else dst.with_suffix(".mubin.yml")
        )
    else:
        return (
            dst.with_suffix(f".b{dst.suffix[1:]}")
            if _byml
            else dst.with_suffix(f".{dst.suffix[2:]}")
        )


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
    write(data=out, src=args.src, dst=args.dst, condition=True, function=guess_dst)

    return 0


def yml_to_byml(args: argparse.Namespace, data: bytes) -> int:
    try:
        out = oead.byml.to_binary(
            oead.byml.from_text(data.decode("utf-8")), args.big_endian
        )
    except Exception:
        raise SystemExit("Invalid file")

    write(data=out, src=args.src, dst=args.dst, condition=True, function=guess_dst)

    return 0


def main() -> int:
    args = parse_args()
    data = read(args.src)
    data = oead.yaz0.decompress(data) if data[:4] == b"Yaz0" else data

    if data[:2] in (b"BY", b"YB"):
        return byml_to_yml(args, data)
    else:
        return yml_to_byml(args, data)
