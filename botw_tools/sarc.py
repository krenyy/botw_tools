import argparse
from pathlib import Path
from typing import List

import oead

from .common import write_stdout, read, write


def read_sarc(src: Path) -> oead.Sarc:
    data = read(src=src)

    if data[:4] == b"Yaz0":
        raise SystemExit("File is Yaz-0 compressed")
    if data[:4] != b"SARC":
        raise SystemExit("Invalid file")

    return oead.Sarc(data)


def write_sarc(sarc: oead.SarcWriter, dst: Path) -> int:
    return write(data=sarc.write()[1], src=None, dst=dst, condition=None, function=None)


def sarc_create(args: argparse.Namespace) -> int:
    sarc = oead.SarcWriter(
        oead.Endianness.Big if args.big_endian else oead.Endianness.Little
    )

    if args.folder.name == "-":
        raise SystemExit("You cannot pipe in a folder")

    for f in args.folder.glob("**/*.*"):
        if f.is_file():
            sarc.files[f.as_posix()[len(args.folder.as_posix()) + 1 :]] = f.read_bytes()

    if args.sarc and args.sarc.name == "!!":
        args.sarc = args.folder.with_suffix(".pack")

    if args.sarc and args.sarc.name != "-":
        [write_stdout(f"{f}\n".encode("utf-8")) for f in sarc.files]

    write_sarc(sarc, args.sarc)
    return 0


def sarc_extract(args: argparse.Namespace) -> int:
    sarc = read_sarc(args.sarc)

    if (not args.folder or args.folder.name == "!!") and (
        args.sarc and args.sarc.name != "-"
    ):
        base = args.sarc.parent / args.sarc.stem
    elif args.folder and args.folder.name != "-":
        base = args.folder
    else:
        raise SystemExit(
            "You must provide a destination folder when using input from pipe"
        )

    if args.folder.exists():
        raise SystemExit(f"'{args.folder.name}' already exists")

    for file in sarc.get_files():
        path = base / file.name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(file.data)
        write_stdout(
            f"{path.absolute().as_posix()[len(Path.cwd().as_posix()) + 1:]}\n".encode(
                "utf-8"
            )
        )
    return 0


def sarc_list(args: argparse.Namespace) -> int:
    sarc = read_sarc(args.sarc)

    files: List[oead.File] = [f for f in sarc.get_files()]

    if files:
        for file in files:
            write_stdout(
                f"{file.name}{f' [{hex(len(file.data))} bytes]' if not args.hide_sizes else ''}\n".encode(
                    "utf-8"
                )
            )
    else:
        raise SystemExit(f"No files inside '{args.sarc.name}'")
    return 0


def sarc_update(args: argparse.Namespace) -> int:
    sarc = oead.SarcWriter.from_sarc(read_sarc(args.sarc))

    if not args.folder or args.folder.name == "-":
        raise SystemExit("You cannot pipe in a folder")

    if args.folder.exists():
        raise SystemExit(f"'{args.folder.name}' already exists")

    files = [f for f in args.folder.glob("**/*.*")]

    for f in files:
        key = f.as_posix()[len(args.folder.as_posix()) + 1 :]
        write_stdout(
            f"{'Updated' if key in sarc.files else 'Added'} '{key}'".encode("utf-8")
        ) if args.sarc and args.sarc.name != "-" else None
        sarc.files[key] = f.read_bytes()

    write_sarc(sarc, args.sarc)
    return 0


def sarc_remove(args: argparse.Namespace) -> int:
    sarc = oead.SarcWriter.from_sarc(read_sarc(args.sarc))

    if "-" in args.files:
        raise SystemExit("You cannot pipe in filenames to remove")

    if "*" in args.files:
        sarc.files.clear()
        write_stdout(
            f"Removed all files\n".encode("utf-8")
        ) if args.sarc and args.sarc.name != "-" else None
    else:
        for file in sarc.files:
            if file in args.files:
                del sarc.files[file]
                write_stdout(
                    f"Removed {file}\n".encode("utf-8")
                ) if args.sarc and args.sarc.name != "-" else None

    write_sarc(sarc, args.sarc)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manipulate SARC archives")

    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand")
    subparsers.required = True

    subparser_create = subparsers.add_parser(
        "create", help="Create a SARC archive from a folder", aliases=["c"]
    )
    subparser_create.add_argument(
        "-b", "--big_endian", action="store_true", help="Use big endian (Wii U)"
    )
    subparser_create.add_argument("folder", type=Path, help="Folder to convert to SARC")
    subparser_create.add_argument(
        "sarc",
        type=Path,
        nargs="?",
        help="Destination SARC archive (writes to stdout if empty or '-')",
    )
    subparser_create.set_defaults(func=sarc_create)

    subparser_extract = subparsers.add_parser(
        "extract", help="Extract SARC archive", aliases=["x"]
    )
    subparser_extract.add_argument(
        "sarc",
        type=Path,
        nargs="?",
        help="SARC archive to extract (reads from stdin if empty or '-')",
    )
    subparser_extract.add_argument(
        "folder",
        type=Path,
        nargs="?",
        help="Destination folder ('!!' to guess folder name)",
    )
    subparser_extract.set_defaults(func=sarc_extract)

    subparser_list = subparsers.add_parser(
        "list", help="List contents of SARC archive", aliases=["l"]
    )
    subparser_list.add_argument(
        "sarc",
        type=Path,
        nargs="?",
        help="SARC to list contents of (reads from stdin if empty or '-')",
    )
    subparser_list.add_argument(
        "-s", "--hide_sizes", action="store_true", help="Hide sizes of files"
    )
    subparser_list.set_defaults(func=sarc_list)

    subparser_update = subparsers.add_parser(
        "update", help="Update a SARC archive from a folder", aliases=["u"]
    )
    subparser_update.add_argument(
        "sarc",
        type=Path,
        nargs="?",
        help="SARC to update (reads from stdin if empty or '-', result will be written to stdout)",
    )
    subparser_update.add_argument(
        "folder", type=Path, help="Folder to update the SARC from"
    )
    subparser_update.set_defaults(func=sarc_update)

    subparser_remove = subparsers.add_parser(
        "remove", help="Remove files from SARC", aliases=["r"]
    )
    subparser_remove.add_argument(
        "sarc",
        type=Path,
        nargs="?",
        help="SARC to remove files from (reads from stdin if empty or '-', result will be written to stdout)",
    )
    subparser_remove.add_argument(
        "files", type=str, nargs="+", help="Files to remove from the SARC"
    )
    subparser_remove.set_defaults(func=sarc_remove)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)
