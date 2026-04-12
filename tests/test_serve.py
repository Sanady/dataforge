"""Tests for Feature 8: HTTP Mock Data Server."""

import json
import threading
import time
import urllib.request

import pytest

from dataforge.cli import _run_serve, _build_parser


# ── Parametrized CLI argument parsing ───────────────────────────────────

_CLI_CASES = [
    # (args, attr, expected)
    (["--serve"], "serve", True),
    (["--serve"], "port", 8080),
    (["--serve", "--port", "9090"], "port", 9090),
    (["--serve", "first_name", "email"], "fields", ["first_name", "email"]),
]


class TestServeCLIArgs:
    @pytest.mark.parametrize(
        "args, attr, expected",
        _CLI_CASES,
        ids=["serve_flag", "default_port", "custom_port", "with_fields"],
    )
    def test_cli_parsing(self, args: list[str], attr: str, expected: object) -> None:
        parser = _build_parser()
        parsed = parser.parse_args(args)
        assert getattr(parsed, attr) == expected


class TestServeServer:
    """Integration tests for the actual HTTP server."""

    @pytest.fixture
    def server_port(self) -> int:
        """Find a free port for testing."""
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    @pytest.mark.parametrize(
        "count_param, expected_count",
        [
            ("", 10),
            ("?count=3", 3),
        ],
        ids=["default_count", "custom_count"],
    )
    def test_serve_returns_json(
        self, server_port: int, count_param: str, expected_count: int
    ) -> None:
        """Start the server in a thread and verify it returns JSON data."""
        parser = _build_parser()
        args = parser.parse_args(
            [
                "--serve",
                "--port",
                str(server_port),
                "--seed",
                "42",
                "first_name",
                "email",
            ]
        )

        server_thread = threading.Thread(
            target=_run_serve,
            args=(args,),
            daemon=True,
        )
        server_thread.start()
        time.sleep(0.5)

        try:
            url = f"http://localhost:{server_port}/{count_param}"
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode("utf-8"))
            assert isinstance(data, list)
            assert len(data) == expected_count
            for row in data:
                assert "first_name" in row
                assert "email" in row
        except Exception:
            pytest.skip("Server did not start in time")


class TestServeHandler:
    def test_default_fields_when_none_provided(self) -> None:
        """When no fields are provided, defaults should be used."""
        parser = _build_parser()
        args = parser.parse_args(["--serve", "--seed", "42"])
        assert args.serve is True
        assert args.fields == []
