"""
compose_diff utils module
"""

import logging
import re
import sys
from urllib import request

try:
    import ijson
except ImportError:
    logging.error("Module 'ijson' is not available. Please install it first.")
    sys.exit(1)

try:
    from pydantic import BaseModel
except ImportError:
    logging.error("Module 'pydantic' is not available. Please install it first.")
    sys.exit(1)


URL_COMPOSE_ROOT = "https://kojipkgs.fedoraproject.org/compose/rawhide/"
RE_COMPOSE_VERSION_PATTERN = r"<a href=\"Fedora-Rawhide-(\d+\.\S\.\d+)/\">"
RE_LATEST_VERSION_PATTERN = r"<a href=\"latest-Fedora-Rawhide/\">"

URL_RPMS_JSON_TEMPLATE = "{url_root}{full_version}/compose/metadata/rpms.json"

logger = logging.getLogger()


class PackageModel(BaseModel):
    """Package pydantic model"""

    name: str
    version: str


class PkgChangedModel(BaseModel):
    """Package diff changed package pydantic model"""

    name: str
    version_from: str
    version_to: str


class PkgDiffModel(BaseModel):
    """Package diff root pydantic model"""

    removed: list[PackageModel]
    added: list[PackageModel]
    changed: list[PkgChangedModel]


def download_url(url_root) -> str:
    """Download URL contents"""

    logger.debug(f"Downloading from '{url_root}'")
    try:
        with request.urlopen(url_root) as root_index:
            root_html = root_index.read().decode("utf-8")
    except Exception as err:
        logger.error(f"{err}")
        raise

    return root_html


def parse_compose_root(root_html: str) -> list[str]:
    """Parse string for compose versions"""

    compose_versions: list[str] = [
        v.groups()[0]
        for v in re.finditer(RE_COMPOSE_VERSION_PATTERN, root_html)
        if v.groups()
    ]

    if re.search(RE_LATEST_VERSION_PATTERN, root_html):
        compose_versions.append("latest")
    return compose_versions


def get_rpms_json_url(version: str) -> str:
    """Generate rpms.json URL for given compose version"""

    return URL_RPMS_JSON_TEMPLATE.format(
        url_root=URL_COMPOSE_ROOT,
        full_version=f"Fedora-Rawhide-{version}"
        if version != "latest"
        else "latest-Fedora-Rawhide",
    )


def parse_streamed_rpms_json(url_json: str, arch: str = "x86_64") -> dict[str, str]:
    """Parse rpms.json during its download"""

    logger.debug(f"Streaming rpms.json from '{url_json}'")
    try:
        jsonfile = request.urlopen(url_json)
        result: dict[str, str] = dict()
        for nevra, _ in ijson.kvitems(jsonfile, f"payload.rpms.Everything.{arch}"):
            name = nevra.rsplit("-", 2)[0]
            version = "-".join(nevra.rsplit("-", 2)[1:]).rsplit(".", 2)[0]
            result[name] = version
        return result
    except Exception as err:
        logger.error(f"{err}")
        raise


def diff_packages(dict_from: dict[str, str], dict_to: dict[str, str]) -> PkgDiffModel:
    """Compute package diff from two compose builds package lists"""

    logger.debug("Computing package diff")
    return PkgDiffModel(
        removed=[
            PackageModel(name=name, version=version)
            for (name, version) in dict_from.items()
            if name not in dict_to
        ],
        added=[
            PackageModel(name=name, version=version)
            for (name, version) in dict_to.items()
            if name not in dict_from
        ],
        changed=[
            PkgChangedModel(
                name=name,
                version_from=dict_from[name],
                version_to=dict_to[name],
            )
            for name in dict_to
            if name in dict_from and dict_from[name] != dict_to[name]
        ],
    )
