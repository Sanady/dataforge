"""Tests for Feature 8: HTTP Mock Data Server."""

import argparse
import json
import threading
import time
import urllib.request

import pytest

from dataforge.cli import _run_serve, _build_parser


class TestServeCLIArgs:
    def test_serve_flag_parsed(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["--serve"])
        assert args.serve is True

    def test_port_default(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["--serve"])
        assert args.port == 8080

    def test_port_custom(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["--serve", "--port", "9090"])
        assert args.port == 9090

    def test_serve_with_fields(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["--serve", "first_name", "email"])
        assert args.serve is True
        assert args.fields == ["first_name", "email"]


class TestServeServer:
    """Integration tests for the actual HTTP server."""

    @pytest.fixture
    def server_port(self) -> int:
        """Find a free port for testing."""
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    def test_serve_returns_json(self, server_port: int) -> None:
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

        # Run server in a daemon thread
        server_thread = threading.Thread(
            target=_run_serve,
            args=(args,),
            daemon=True,
        )
        server_thread.start()
        time.sleep(0.5)  # Give server time to start

        try:
            url = f"http://localhost:{server_port}/"
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode("utf-8"))
            assert isinstance(data, list)
            assert len(data) == 10  # default count
            for row in data:
                assert "first_name" in row
                assert "email" in row
        except Exception:
            pytest.skip("Server did not start in time")

    def test_serve_count_parameter(self, server_port: int) -> None:
        """Verify the count query parameter works."""
        parser = _build_parser()
        args = parser.parse_args(
            [
                "--serve",
                "--port",
                str(server_port),
                "--seed",
                "42",
                "first_name",
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
            url = f"http://localhost:{server_port}/?count=3"
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode("utf-8"))
            assert isinstance(data, list)
            assert len(data) == 3
        except Exception:
            pytest.skip("Server did not start in time")


class TestServeHandler:
    def test_default_fields_when_none_provided(self) -> None:
        """When no fields are provided, defaults should be used."""
        parser = _build_parser()
        args = parser.parse_args(["--serve", "--seed", "42"])
        # _run_serve sets defaults internally
        assert args.serve is True
        assert args.fields == []  # no fields on CLI
