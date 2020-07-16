import argparse
from pathlib import Path

import oead

from .common import write, read


def guess_dst(_aamp: bool, dst: Path) -> Path:
    return (
        dst.with_name(f"{dst.stem}.aamp")
        if dst.name.count(".") < 2
        else dst.with_name(
            f"{dst.name.split('.')[0]}.b{dst.name.split('.')[-2]}"
        )
    ) if _aamp else dst.with_suffix(f".{dst.suffix[2:]}.yml")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert between AAMP and YML")

    parser.add_argument(
        "src",
        type=Path,
        nargs="?",
        help="Source AAMP or YML file (reads from stdin if empty or '-')",
    )
    parser.add_argument(
        "dst",
        type=Path,
        nargs="?",
        help="Destination AAMP or YML file (writes to stdout if empty or '-', '!!' to guess filename)",
    )

    return parser.parse_args()


def aamp_to_yml(args: argparse.Namespace, data: bytes) -> int:
    out = oead.aamp.ParameterIO.from_binary(data).to_text().encode("utf-8")
    write(data=out, src=args.src, dst=args.dst, condition=False, function=guess_dst)

    return 0


def yml_to_aamp(args: argparse.Namespace, data: bytes) -> int:
    out = oead.aamp.ParameterIO.from_text(data.decode("utf-8")).to_binary()
    write(data=out, src=args.src, dst=args.dst, condition=True, function=guess_dst)

    return 0


def main() -> int:
    args = parse_args()
    data = read(src=args.src)

    if data[:4] == b"AAMP":
        return aamp_to_yml(args, data)
    elif data[:3] == b"!io":
        return yml_to_aamp(args, data)
    else:
        raise SystemExit("Invalid file")
