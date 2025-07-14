import argparse
from importlib.metadata import version
import logging
import sys

from .utils import (
    diff_packages,
    download_url,
    get_rpms_json_url,
    parse_compose_root,
    parse_streamed_rpms_json,
    URL_COMPOSE_ROOT,
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)8s] %(filename)s,%(lineno)d: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()

try:
    __version__ = version("compose_diff")
except ImportError:
    __version__ = "0.0.0.dev"

def main():


    top_parser = argparse.ArgumentParser(
        prog="compose_diff",
        description="Fedora Rawhide compose differ",
    )
    top_parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = top_parser.add_subparsers(dest="action", title="actions")

    list_parser = subparsers.add_parser(
        "list",
        help="List available compose versions",
        description=f"List available compose versions at {URL_COMPOSE_ROOT}",
    )

    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare compose versions",
        usage="compose_diff compare [-h] [-a {aarch64, x86_64}] [-j] VERSION-FROM [VERSION-TO]",
        description="""Compare compose versions between VERSION-FROM and VERSION-TO. If
            VERSION-TO is not specified, the default value "latest" will be used instead.
        """,
    )
    compare_parser.add_argument("ver", type=str, nargs="+", metavar="VERSION")
    compare_parser.add_argument(
        "-a",
        "--arch",
        type=str,
        choices=["aarch64, x86_64"],
        default="x86_64",
        help="requested CPU architecture (default: %(default)s)",
    )
    compare_parser.add_argument(
        "-j", 
        "--json-output", 
        action="store_true", 
        help="Machine readable output in JSON format",
    )

    args = top_parser.parse_args()

    if not args.action:
        top_parser.print_help()
        sys.exit()

    if args.action == "list":
        try:
            url_contents = download_url(URL_COMPOSE_ROOT)
            compose_versions = parse_compose_root(url_contents)
            if compose_versions:
                print("Available Rawhide composes:")
                for version in compose_versions:
                    print(f"    {version}")
            else:
                print(f"No Rawhide composes found at {URL_COMPOSE_ROOT}")
        except Exception:
            logger.critical(f"Failed to download composes from {URL_COMPOSE_ROOT}")
            sys.exit(1)

        sys.exit(0)

    if args.action == "compare":
        logger.debug(f"ver: {args.ver}, arch: {args.arch}, json_output: {args.json_output}")
        version_from: str = args.ver[0]
        version_to: str = "latest" if len(args.ver) == 1 else args.ver[1]
        logger.debug(f"Requested diff from '{version_from}' to '{version_to}'")

        if version_from == version_to:
            print("Warning: Compose versions are identical. Package diff is empty.")
            sys.exit(0)

        # Version strings are compared lexicographically, this works also for
        # "latest" version since it is "newer" than anything startting with numbers :)
        if version_from > version_to:
            print("Error: Compose VERSION-FROM is newer than VERSION-TO")
            sys.exit(1)

        url_rpms_json_from = get_rpms_json_url(version_from)
        print(f"Please wait, downloading '{version_from}' version rpms.json")
        try:
            packages_from = parse_streamed_rpms_json(url_rpms_json_from, arch=args.arch)
        except Exception:
            logger.critical(
                f"Failed to process compose '{version_from}' rpms.json from '{url_rpms_json_from}'"
            )
            sys.exit(1)

        url_rpms_json_to = get_rpms_json_url(version_to)
        print(f"Please wait, downloading '{version_to}' version rpms.json")
        try:
            packages_to = parse_streamed_rpms_json(url_rpms_json_to, arch=args.arch)
        except Exception:
            logger.critical(
                f"Failed to process compose '{version_to}' rpms.json from {url_rpms_json_to}"
            )
            sys.exit(1)

        pkg_diff = diff_packages(packages_from, packages_to)

        if not args.json_output:
            # Human readable output
            print(
                f"======= {args.arch} package diff from {version_from} to {version_to} ======="
            )
            print("==== Packages REMOVED")
            for pkg_removed in pkg_diff.removed:
                print(f"     {pkg_removed.name} REMOVED  ({pkg_removed.version})")
            print("==== Packages ADDED")
            for pkg_added in pkg_diff.added:
                print(f"     {pkg_added.name} ADDED  ({pkg_added.version})")
            print("==== Packages CHANGED")
            for pkg_changed in pkg_diff.changed:
                print(
                    f"     {pkg_changed.name} CHANGED  ({pkg_changed.version_from} -> {pkg_changed.version_to})"
                )

        else:
            # Machine readdable output
            print(pkg_diff.model_dump_json(indent=4))

if __name__ == "__main__":
    main()
