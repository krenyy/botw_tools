import sys
from pathlib import Path
import argparse
import oead


def read_sarc(path: Path):
    if path.name == "-":
        with sys.stdin.buffer as stdin:
            data = stdin.read()

    elif path.is_file():
        data = path.read_bytes()

    else:
        print(f"SARC '{path.name}' doesn't exist")

        raise SystemExit(1)

    if data[:4] == b"Yaz0":
        raise SystemExit("File is Yaz-0 compressed")

    if data[:4] != b"SARC":
        raise SystemExit("Invalid SARC file!")

    return oead.Sarc(data)


def write_sarc(sarc: oead.SarcWriter, path: Path):
    data = sarc.write()[1]

    if path.name == "-":
        with sys.stdout.buffer as stdout:
            stdout.write(data)
    else:
        path.write_bytes(data)


def sarc_extract(args: argparse.Namespace):
    if not args.sarc:
        args.sarc = Path("-")

    sarc = read_sarc(args.sarc)

    for file in sarc.get_files():
        if args.folder and args.folder.name != "-":
            path = args.folder / file.name
            msg = f"{args.folder}/{file.name}"
        elif args.sarc and args.sarc.name != "-":
            path = args.sarc.parent / args.sarc.stem / file.name
            msg = f"{args.sarc.stem}/{file.name}"
        else:
            raise SystemExit("You must provide a destination folder when using input from pipe")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(bytes(file.data))
        print(msg)


def sarc_list(args: argparse.Namespace):
    if not args.sarc:
        args.sarc = Path("-")

    sarc = read_sarc(args.sarc)

    files = [f for f in sarc.get_files()]

    if files:
        for file in sarc.get_files():
            print(f"{file.name}{f' [{hex(len(file.data))}]' if args.show_sizes else ''}")
    else:
        print(f"No files inside '{args.sarc.name}'")


def sarc_create(args: argparse.Namespace):
    sarc = oead.SarcWriter(
        oead.Endianness.Big if args.big_endian else oead.Endianness.Little
    )

    if args.folder.name == "-":
        raise SystemExit("You cannot pipe in a folder")

    for file in args.folder.glob("**/*.*"):
        sarc.files[str(file)[len(str(args.folder)) + 1:]] = oead.Bytes(
            file.read_bytes()
        )

    if not args.sarc:
        args.sarc = Path("-")

    elif args.sarc.name == "!!":
        args.sarc = args.folder.with_suffix(".pack")

    write_sarc(sarc, args.sarc)

    if args.sarc.name != "-":
        print(args.sarc.name)


def sarc_update(args: argparse.Namespace):
    if not args.sarc:
        args.sarc = Path("-")

    sarc = oead.SarcWriter.from_sarc(read_sarc(args.sarc))

    if args.folder.name == "-":
        raise SystemExit("You cannot pipe in a folder")

    files = [f for f in args.folder.glob("**/*.*")]

    for f in files:
        sarc.files[str(f)[len(str(args.folder)) + 1:]] = oead.Bytes(
            f.read_bytes()
        )

    write_sarc(sarc, args.sarc)

    if args.sarc.name != "-":
        updated = '\n'.join([f"Updated {str(f)[len(str(args.folder)) + 1:]}" for f in files])
        print(updated)


def sarc_remove(args: argparse.Namespace):
    if not args.sarc:
        args.sarc = Path("-")

    sarc = oead.SarcWriter.from_sarc(read_sarc(args.sarc))

    if "-" in args.files:
        raise SystemExit("You cannot pipe in filenames to remove")

    removed_files = []

    if "*" in args.files:
        sarc.files.clear()
        removed_files.append("all")
    else:
        for file in sarc.files.items():
            if file[0] in args.files:
                del sarc.files[file[0]]
                removed_files.append(file[0])

    write_sarc(sarc, args.sarc)

    if args.sarc.name != "-":
        removed = '\n'.join([f"Removed {f}" for f in removed_files])
        print(removed if removed else "Nothing removed")


def parse_args():
    parser = argparse.ArgumentParser(description="Manipulate SARC archives")

    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand")
    subparsers.required = True

    subparser_extract = subparsers.add_parser(
        "extract", help="Extract SARC archive", aliases=["x"]
    )
    subparser_extract.add_argument("sarc", type=Path, nargs="?", help="SARC archive to extract (reads from stdin if empty or '-')")
    subparser_extract.add_argument(
        "folder", type=Path, nargs="?", help="Destination folder"
    )
    subparser_extract.set_defaults(func=sarc_extract)

    subparser_list = subparsers.add_parser(
        "list", help="List contents of SARC archive", aliases=["l"]
    )
    subparser_list.add_argument("sarc", type=Path, help="SARC to list contents of (reads from stdin if empty or '-')")
    subparser_list.add_argument(
        "-s", "--show_sizes", action="store_true", help="Show sizes of files"
    )
    subparser_list.set_defaults(func=sarc_list)

    subparser_create = subparsers.add_parser(
        "create", help="Create a SARC archive from a folder", aliases=["c"]
    )
    subparser_create.add_argument(
        "-b", "--big_endian", action="store_true", help="Use big endian (Wii U)"
    )
    subparser_create.add_argument("folder", type=Path, help="Folder to convert to SARC")
    subparser_create.add_argument(
        "sarc", type=Path, nargs="?", help="Destination SARC archive (writes to stdout if empty or '-')"
    )
    subparser_create.set_defaults(func=sarc_create)

    subparser_update = subparsers.add_parser(
        "update", help="Update a SARC archive from a folder", aliases=["u"]
    )
    subparser_update.add_argument("sarc", type=Path, help="SARC to update (reads from stdin if empty or '-', result will be written to stdout)")
    subparser_update.add_argument(
        "folder", type=Path, help="Folder to update the SARC from"
    )
    subparser_update.set_defaults(func=sarc_update)

    subparser_remove = subparsers.add_parser(
        "remove", help="Remove files from SARC", aliases=["r"]
    )
    subparser_remove.add_argument("sarc", type=Path, help="SARC to remove files from (reads from stdin if empty or '-', result will be written to stdout)")
    subparser_remove.add_argument(
        "files", type=str, nargs="+", help="Files to remove from the SARC"
    )
    subparser_remove.set_defaults(func=sarc_remove)

    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)
