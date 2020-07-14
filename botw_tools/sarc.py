import sys
from pathlib import Path
import argparse
import oead


def read_sarc(sarc: Path):
    if sarc.stem == "-":
        with sys.stdin.buffer as stdin:
            data = stdin.read()

    elif sarc.is_file():
        data = sarc.read_bytes()

    else:
        print(f"'{sarc.name}' doesn't exist")

        raise SystemExit(1)

    data = oead.yaz0.decompress(data) if data[:4] == b"Yaz0" else data

    if data[:4] != b"SARC":
        raise SystemExit("Invalid SARC file!")

    return oead.Sarc(data)


def sarc_extract(args: argparse.Namespace):
    sarc = read_sarc(args.sarc)

    for file in sarc.get_files():
        path = (
            (args.folder / file.name)
            if args.folder and args.folder.stem != "-"
            else (args.sarc.parent / args.sarc.stem / file.name)
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(bytes(file.data))
        print(
            f"{args.folder.stem}/{file.name}"
            if args.folder and args.folder.stem != "-"
            else f"{args.sarc.stem}/{file.name}"
        )


def sarc_list(args: argparse.Namespace):
    sarc = read_sarc(args.sarc)

    for file in sarc.get_files():
        print(f"{file.name}{f' [{hex(len(file.data))}]' if args.show_sizes else ''}")


def sarc_create(args: argparse.Namespace):
    sarc = oead.SarcWriter(
        oead.Endianness.Big if args.big_endian else oead.Endianness.Little
    )

    for file in args.folder.glob("**/*.*"):
        sarc.files[str(file)[len(str(args.folder)) + 1 :]] = oead.Bytes(
            file.read_bytes()
        )

    if not args.sarc or args.sarc.stem == "!!":
        args.sarc = args.folder.with_suffix(".sbactorpack" if args.yaz0 else ".pack")

    data = sarc.write()[1]
    data = (
        oead.yaz0.compress(data)
        if (args.sarc.suffix.startswith(".s") and not args.sarc.suffix == ".sarc")
        or args.yaz0
        else data
    )

    if args.sarc.stem == "-":
        with sys.stdout.buffer as stdout:
            stdout.write(data)

    else:
        args.sarc.write_bytes(data)
        print(args.sarc.name)


def sarc_update(args: argparse.Namespace):
    sarc = oead.SarcWriter.from_sarc(read_sarc(args.sarc))

    for file in args.folder.glob("**/*.*"):
        sarc.files[str(file)[len(str(args.folder)) + 1 :]] = oead.Bytes(
            file.read_bytes()
        )

    data = sarc.write()[1]
    data = oead.yaz0.compress(data) if args.sarc.suffix.startswith(".s") else data

    if args.sarc.stem == "-":
        with sys.stdout.buffer as stdout:
            stdout.write(data)

    args.sarc.write_bytes(data)


def sarc_remove(args: argparse.Namespace):
    sarc = oead.SarcWriter.from_sarc(read_sarc(args.sarc))

    for file in sarc.files.items():
        if file[0] in args.files:
            del sarc.files[file[0]]

    data = sarc.write()[1]
    data = oead.yaz0.compress(data) if args.sarc.suffix.startswith(".s") else data

    if args.sarc.stem == "-":
        with sys.stdout.buffer as stdout:
            stdout.write(data)

    else:
        args.sarc.write_bytes(data)


def parse_args():
    parser = argparse.ArgumentParser(description="Manipulate SARC archives")

    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand")
    subparsers.required = True

    subparser_extract = subparsers.add_parser(
        "extract", help="Extract SARC archive", aliases=["x"]
    )
    subparser_extract.add_argument("sarc", type=Path, help="SARC archive to extract")
    subparser_extract.add_argument(
        "folder", type=Path, nargs="?", help="Destination folder"
    )
    subparser_extract.set_defaults(func=sarc_extract)

    subparser_list = subparsers.add_parser(
        "list", help="List contents of SARC archive", aliases=["l"]
    )
    subparser_list.add_argument("sarc", type=Path, help="SARC to list contents of")
    subparser_list.add_argument(
        "-s", "--show_sizes", action="store_true", help="Show sizes of files"
    )
    subparser_list.set_defaults(func=sarc_list)

    subparser_create = subparsers.add_parser(
        "create", help="Create a SARC archive from a folder", aliases=["c"]
    )
    subparser_create.add_argument(
        "-y", "--yaz0", action="store_true", help="Force Yaz-0 compression"
    )
    subparser_create.add_argument(
        "-b", "--big_endian", action="store_true", help="Use big endian (Wii U)"
    )
    subparser_create.add_argument("folder", type=Path, help="Folder to convert to SARC")
    subparser_create.add_argument(
        "sarc", type=Path, nargs="?", help="Destination SARC archive"
    )
    subparser_create.set_defaults(func=sarc_create)

    subparser_update = subparsers.add_parser(
        "update", help="Update a SARC archive from a folder", aliases=["u"]
    )
    subparser_update.add_argument("sarc", type=Path, help="SARC to update")
    subparser_update.add_argument(
        "folder", type=Path, help="Folder to update the SARC from"
    )
    subparser_update.set_defaults(func=sarc_update)

    subparser_delete = subparsers.add_parser(
        "remove", help="Remove files from SARC", aliases=["r"]
    )
    subparser_delete.add_argument("sarc", type=Path, help="SARC to remove files from")
    subparser_delete.add_argument(
        "files", type=str, nargs="+", help="Files to remove from the SARC"
    )
    subparser_delete.set_defaults(func=sarc_remove)

    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)
