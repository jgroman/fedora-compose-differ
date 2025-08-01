import asyncio
from email.message import EmailMessage
import io
import logging
import pytest
import urllib.request
import urllib.response

from compose_diff.utils import (
    diff_packages,
    download_url,
    parse_compose_root,
    parse_streamed_rpms_json,
    PackageModel,
    PkgChangedModel,
)


@pytest.fixture
def mock_compose_root_content() -> str:
    MOCK_COMPOSE_ROOT_FILEPATH = "./tests/testdata/compose_rawhide_index.html"

    try:
        with open(MOCK_COMPOSE_ROOT_FILEPATH, "r") as testfile:
            testfile_content = testfile.read()
            return testfile_content
    except Exception as err:
        logging.error(f"Failed to read '{MOCK_COMPOSE_ROOT_FILEPATH}': {str(err)}")
        return ""


@pytest.fixture
def mock_rpms_json_content() -> str:
    MOCK_RPMS_JSON_FILEPATH = "./tests/testdata/sample_rpms.json"
    try:
        with open(MOCK_RPMS_JSON_FILEPATH, "r") as mockfile:
            mockfile_content = mockfile.read()
            return mockfile_content
    except Exception as err:
        logging.error(f"Failed to read '{MOCK_RPMS_JSON_FILEPATH}': {str(err)}")
        return ""


@pytest.fixture
def mock_compose_root_versions() -> list[str]:
    return [
        "20250626.n.0",
        "20250627.n.0",
        "20250629.n.0",
        "20250704.n.0",
        "20250704.n.1",
        "20250705.n.0",
        "20250706.n.0",
        "20250707.n.0",
        "20250708.n.0",
        "20250709.n.0",
        "20250710.n.0",
        "latest",
    ]


@pytest.fixture
def mock_packages_from() -> dict[str, str]:
    return {
        "package_no_change_1": "1",
        "package_removed_1": "1",
        "package_changed_1": "1",
        "package_no_change_2": "1",
        "package_removed_2": "1",
        "package_changed_2": "1",
    }


@pytest.fixture
def mock_packages_to() -> dict[str, str]:
    return {
        "package_no_change_1": "1",
        "package_added_1": "1",
        "package_changed_1": "2",
        "package_no_change_2": "1",
        "package_added_2": "1",
        "package_changed_2": "2",
    }


def test_download_url(monkeypatch, mock_compose_root_content):
    """Test download_url()"""

    def mock_urlopen(url):
        return urllib.response.addinfourl(
            fp=io.BytesIO(mock_compose_root_content.encode()),
            headers=EmailMessage(),
            url=url,
            code=200,
        )

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    compose_root_content = download_url("mock-root-url")
    assert compose_root_content == mock_compose_root_content


def test_parse_compose_root(mock_compose_root_content, mock_compose_root_versions):
    """Test parse_compose_root()"""
    parse_result = parse_compose_root(mock_compose_root_content)

    assert parse_result == mock_compose_root_versions


def test_parse_streamed_rpms_json(monkeypatch, mock_rpms_json_content):
    """Test parse_streamed_rpms_json()"""

    def mock_urlopen(url):
        return urllib.response.addinfourl(
            fp=io.BytesIO(mock_rpms_json_content.encode()),
            headers=EmailMessage(),
            url=url,
            code=200,
        )

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
    packages = asyncio.run(parse_streamed_rpms_json("mock-rpms.json-url"))

    assert packages == {
        "0ad": "0:0.0.26-30",
        "0ad-data": "0:0.0.26-11",
        "0install": "0:2.18-4",
        "0xFFFF": "0:0.10-13",
        "2048-cli": "0:0.9.1-23",
    }


def test_diff_packages(mock_packages_from, mock_packages_to):
    """Test diff_packages()"""

    diff = diff_packages(mock_packages_from, mock_packages_to)

    expected_removed = [
        PackageModel(name="package_removed_1", version="1"),
        PackageModel(name="package_removed_2", version="1"),
    ]

    assert diff.removed == expected_removed

    expected_added = [
        PackageModel(name="package_added_1", version="1"),
        PackageModel(name="package_added_2", version="1"),
    ]

    assert diff.added == expected_added

    expected_changed = [
        PkgChangedModel(name="package_changed_1", version_from="1", version_to="2"),
        PkgChangedModel(name="package_changed_2", version_from="1", version_to="2"),
    ]

    assert diff.changed == expected_changed
