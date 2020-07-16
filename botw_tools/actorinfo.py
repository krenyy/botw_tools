import argparse
import bisect
from pathlib import Path
from typing import Union
from zlib import crc32

import oead

from .common import write, read, write_stdout


def read_actorinfo(args: argparse.Namespace) -> oead.byml.Hash:
    data = read(src=args.actorinfo)

    args.yaz0 = False
    if data[:4] == b"Yaz0":
        data = oead.yaz0.decompress(data)
        args.yaz0 = True

    if data[:2] not in (b"BY", b"YB"):
        raise SystemExit(f"Invalid file")

    args.big_endian = True if data[:2] == b"BY" else False

    actorinfo = oead.byml.from_binary(data)

    if ("Actors", "Hashes") != tuple(actorinfo.keys()):
        raise SystemExit("Invalid file")

    return actorinfo


def write_actorinfo(args: argparse.Namespace, actorinfo: oead.byml.Hash) -> int:
    data = oead.byml.to_binary(actorinfo, args.big_endian)
    data = oead.yaz0.compress(data) if args.yaz0 else data

    return write(data=data, dst=args.actorinfo)


def convert_hash(x: int) -> Union[oead.S32, oead.U32]:
    return oead.U32(x) if x > 0x80000000 else oead.S32(x)


def actorinfo_get(args: argparse.Namespace):
    actorinfo = read_actorinfo(args)
    entry_hash = crc32(args.entry_name.encode())

    if convert_hash(entry_hash) not in actorinfo["Hashes"]:
        raise SystemExit(f"'{args.entry_name}' doesn't exist in this file")

    entry_index = list(actorinfo["Hashes"]).index(
        oead.U32(entry_hash) if entry_hash > 0x80000000 else oead.S32(entry_hash)
    )

    entry = actorinfo["Actors"][entry_index]

    try:
        write_stdout(oead.byml.to_text(entry[args.key] if args.key else entry).encode('utf-8'))
    except KeyError:
        raise SystemExit(f"Key '{args.key}' doesn't exist in '{args.entry_name}'")


def duplicate_entry(entry: Union[oead.byml.Array, oead.byml.Hash]):
    entry = (
        oead.byml.Hash(dict(entry))
        if isinstance(entry, oead.byml.Hash)
        else oead.byml.Array(list(entry))
    )

    for k, v in entry.items():
        if isinstance(v, oead.byml.Hash) or isinstance(v, oead.byml.Array):
            entry[k] = duplicate_entry(v)

    return entry


def actorinfo_duplicate(args: argparse.Namespace) -> int:
    actorinfo = read_actorinfo(args)

    entry_hash_from = crc32(args.entry_name_from.encode())

    if convert_hash(entry_hash_from) not in actorinfo["Hashes"]:
        raise SystemExit(f"'{args.entry_name_from}' doesn't exist in this file")

    entry_index_from = list(actorinfo["Hashes"]).index(
        oead.U32(entry_hash_from)
        if entry_hash_from > 0x80000000
        else oead.S32(entry_hash_from)
    )

    entry = duplicate_entry(actorinfo["Actors"][entry_index_from])
    entry["name"] = args.entry_name_to

    entry_hash_to = crc32(args.entry_name_to.encode())

    if convert_hash(entry_hash_to) in actorinfo["Hashes"]:
        raise SystemExit(f"'{args.entry_name_to}' already exists")

    entry_index_to = bisect.bisect([int(x) for x in actorinfo["Hashes"]], entry_hash_to)
    actorinfo["Hashes"].insert(entry_index_to, convert_hash(entry_hash_to))
    actorinfo["Actors"].insert(entry_index_to, entry)

    write_stdout(f"{args.entry_name_from} -> {args.entry_name_to}".encode(
        'utf-8')) if args.actorinfo and args.actorinfo.name != '-' else None
    write_actorinfo(args, actorinfo)
    return 0


def actorinfo_edit(args: argparse.Namespace) -> int:
    actorinfo = read_actorinfo(args)

    entry_hash = crc32(args.entry_name.encode())

    if convert_hash(entry_hash) not in actorinfo["Hashes"]:
        raise SystemExit(f"'{args.entry_name}' doesn't exist in this file")

    entry_index = list(actorinfo["Hashes"]).index(
        oead.U32(entry_hash) if entry_hash > 0x80000000 else oead.S32(entry_hash)
    )

    entry = actorinfo["Actors"][entry_index]

    try:
        value_before = entry[args.key]
    except KeyError:
        value_before = None
    entry[args.key] = args.value
    value_after = entry[args.key]

    write_stdout(f"{args.entry_name}['{args.key}']: '{value_before}' -> '{value_after}'".encode(
        'utf-8')) if args.actorinfo and args.actorinfo.name != '-' else None
    write_actorinfo(args, actorinfo)
    return 0


def actorinfo_remove(args: argparse.Namespace) -> int:
    actorinfo = read_actorinfo(args)

    entry_hash = crc32(args.entry_name.encode())

    if convert_hash(entry_hash) not in actorinfo["Hashes"]:
        raise SystemExit(f"'{args.entry_name}' doesn't exist in this file")

    entry_index = list(actorinfo["Hashes"]).index(
        oead.U32(entry_hash) if entry_hash > 0x80000000 else oead.S32(entry_hash)
    )

    if not args.key:
        actorinfo["Hashes"].pop(entry_index)
        actorinfo["Actors"].pop(entry_index)
        msg = f"{args.entry_name} removed".encode('utf-8')
    else:
        try:
            del actorinfo["Actors"][entry_index][args.key]
        except KeyError:
            raise SystemExit(f"Key '{args.key}' doesn't exist in '{args.entry_name}'")
        msg = f"{args.entry_name}['{args.key}'] removed".encode('utf-8')

    write_stdout(msg) if args.actorinfo and args.actorinfo.name != '-' else None
    write_actorinfo(args, actorinfo)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert between BYML and YML")

    parser.add_argument(
        "actorinfo",
        type=Path,
        help="Source BYML or YML file (reads from stdin if '-')",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand")
    subparsers.required = True

    subparser_get = subparsers.add_parser(
        "get", help="Get entry from ActorInfo", aliases=["g"]
    )
    subparser_get.add_argument("entry_name", type=str, help="Name of the entry")
    subparser_get.add_argument("key", type=str, nargs="?", help="Key")
    subparser_get.set_defaults(func=actorinfo_get)

    subparser_duplicate = subparsers.add_parser(
        "duplicate", help="Duplicate an entry in ActorInfo", aliases=["d"]
    )
    subparser_duplicate.add_argument(
        "entry_name_from", type=str, help="Name of the entry to duplicate from"
    )
    subparser_duplicate.add_argument(
        "entry_name_to", type=str, help="Name of the entry to duplicate to"
    )
    subparser_duplicate.set_defaults(func=actorinfo_duplicate)

    subparser_edit = subparsers.add_parser(
        "edit", help="Edit ActorInfo entry", aliases=["e"]
    )
    subparser_edit.add_argument(
        "entry_name", type=str, help="Name of the entry to edit"
    )
    subparser_edit.add_argument("key", type=str, help="Key to edit")
    subparser_edit.add_argument("value", help="Value")
    subparser_edit.set_defaults(func=actorinfo_edit)

    subparser_remove = subparsers.add_parser(
        "remove", help="Remove an entry from ActorInfo", aliases=["r"]
    )
    subparser_remove.add_argument(
        "entry_name", type=str, help="Name of the entry to remove"
    )
    subparser_remove.add_argument(
        "key", type=str, nargs="?", help="Name of the key to remove (entry stays)"
    )
    subparser_remove.set_defaults(func=actorinfo_remove)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)
