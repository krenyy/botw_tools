import argparse
from pathlib import Path

import oead

from .common import write_stdout, read_stdin


def guess_dst(_aamp: bool, path: Path) -> Path:
    if _aamp:
        return (
            path.with_name(f"{path.stem}.aamp")
            if path.name.count(".") < 2
            else path.with_name(
                f"{path.name.split('.')[0]}.b{path.name.split('.')[-2]}"
            )
        )
    return path.with_suffix(f".{path.suffix[2:]}.yml")


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

    if not args.dst or args.dst.name == "-":
        write_stdout(out)
        return 0

    elif args.dst.name == "!!":
        args.dst = guess_dst(False, args.src)

    args.dst.write_bytes(out)
    write_stdout(f"{args.dst.name}\n".encode("utf-8"))
    return 0


def yml_to_aamp(args: argparse.Namespace, data: bytes) -> int:
    out = oead.aamp.ParameterIO.from_text(data.decode("utf-8")).to_binary()

    if not args.dst or args.dst.name == "-":
        write_stdout(out)
        return 0

    if args.dst.name == "!!":
        args.dst = guess_dst(True, args.src)

    args.dst.write_bytes(out)
    write_stdout(f"{args.dst.name}\n".encode("utf-8"))
    return 0


def main() -> int:
    args = parse_args()

    data = (
        read_stdin() if not args.src or args.src.name == "-" else args.src.read_bytes()
    )

    if data[:4] == b"AAMP":
        return aamp_to_yml(args, data)
    elif data[:3] == b"!io":
        return yml_to_aamp(args, data)
    else:
        raise SystemExit("Invalid file")
