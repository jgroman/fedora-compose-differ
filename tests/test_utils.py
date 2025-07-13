from email.message import EmailMessage
import io
import logging
import pytest
import urllib.request
import urllib.response

from compose_diff.compose_diff_utils import (
    download_url,
    parse_compose_root,
    parse_streamed_rpms_json,
    URL_COMPOSE_ROOT,
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


def test_download_url(monkeypatch, mock_compose_root_content):
    def mock_urlopen(url):
        return urllib.response.addinfourl(
            fp=io.BytesIO(mock_compose_root_content.encode()),
            headers=EmailMessage(),
            url=url,
            code=200,
        )

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    compose_root_content = download_url(URL_COMPOSE_ROOT)
    assert compose_root_content == mock_compose_root_content


def test_parse_compose_root(mock_compose_root_content, mock_compose_root_versions):
    parse_result = parse_compose_root(mock_compose_root_content)

    assert parse_result == mock_compose_root_versions


def test_parse_streamed_rpms_json(monkeypatch, mock_rpms_json_content):
    def mock_urlopen(url):
        return urllib.response.addinfourl(
            fp=io.BytesIO(mock_rpms_json_content.encode()),
            headers=EmailMessage(),
            url=url,
            code=200,
        )

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
    packages = parse_streamed_rpms_json("xxx")
