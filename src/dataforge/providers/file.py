"""File provider — generates fake file names, extensions, MIME types, paths."""

from typing import Literal, overload

from dataforge.providers.base import BaseProvider

_FILE_EXTENSIONS: tuple[tuple[str, str, str], ...] = (
    # (extension, mime_type, category)
    ("txt", "text/plain", "text"),
    ("csv", "text/csv", "text"),
    ("html", "text/html", "text"),
    ("css", "text/css", "text"),
    ("js", "application/javascript", "text"),
    ("json", "application/json", "text"),
    ("xml", "application/xml", "text"),
    ("yaml", "application/x-yaml", "text"),
    ("md", "text/markdown", "text"),
    ("py", "text/x-python", "text"),
    ("pdf", "application/pdf", "document"),
    ("doc", "application/msword", "document"),
    (
        "docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "document",
    ),
    ("xls", "application/vnd.ms-excel", "document"),
    (
        "xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "document",
    ),
    ("ppt", "application/vnd.ms-powerpoint", "document"),
    (
        "pptx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "document",
    ),
    ("jpg", "image/jpeg", "image"),
    ("jpeg", "image/jpeg", "image"),
    ("png", "image/png", "image"),
    ("gif", "image/gif", "image"),
    ("svg", "image/svg+xml", "image"),
    ("webp", "image/webp", "image"),
    ("bmp", "image/bmp", "image"),
    ("ico", "image/x-icon", "image"),
    ("mp3", "audio/mpeg", "audio"),
    ("wav", "audio/wav", "audio"),
    ("ogg", "audio/ogg", "audio"),
    ("flac", "audio/flac", "audio"),
    ("mp4", "video/mp4", "video"),
    ("avi", "video/x-msvideo", "video"),
    ("mkv", "video/x-matroska", "video"),
    ("webm", "video/webm", "video"),
    ("mov", "video/quicktime", "video"),
    ("zip", "application/zip", "archive"),
    ("tar", "application/x-tar", "archive"),
    ("gz", "application/gzip", "archive"),
    ("rar", "application/vnd.rar", "archive"),
    ("7z", "application/x-7z-compressed", "archive"),
)

_FILE_WORDS: tuple[str, ...] = (
    "report",
    "document",
    "data",
    "output",
    "results",
    "summary",
    "analysis",
    "backup",
    "archive",
    "config",
    "settings",
    "log",
    "readme",
    "notes",
    "draft",
    "final",
    "temp",
    "test",
    "sample",
    "example",
    "demo",
    "project",
    "image",
    "photo",
    "video",
    "audio",
    "music",
    "export",
    "import",
    "invoice",
    "receipt",
    "budget",
    "plan",
    "schedule",
    "index",
    "main",
    "app",
    "module",
    "utils",
    "core",
)

_DIR_PARTS: tuple[str, ...] = (
    "home",
    "user",
    "documents",
    "downloads",
    "Desktop",
    "projects",
    "src",
    "var",
    "tmp",
    "opt",
    "data",
    "lib",
    "etc",
    "config",
    "logs",
    "backup",
    "media",
    "images",
    "videos",
    "music",
)


_FILE_CATEGORIES: tuple[str, ...] = (
    "text",
    "document",
    "image",
    "audio",
    "video",
    "archive",
)


class FileProvider(BaseProvider):
    """Generates fake file names, extensions, MIME types, and file paths.

    Parameters
    ----------
    engine : RandomEngine
        The shared random engine instance.
    """

    __slots__ = ()

    _provider_name = "file"
    _locale_modules = ()
    _field_map = {
        "file_name": "file_name",
        "file_extension": "file_extension",
        "mime_type": "mime_type",
        "file_path": "file_path",
        "file_category": "file_category",
    }

    # ------------------------------------------------------------------
    # Scalar helpers
    # ------------------------------------------------------------------

    def _one_ext_record(self) -> tuple[str, str, str]:
        return self._engine.choice(_FILE_EXTENSIONS)

    def _one_file_name(self) -> str:
        word = self._engine.choice(_FILE_WORDS)
        ext, _, _ = self._one_ext_record()
        return f"{word}.{ext}"

    def _one_file_path(self) -> str:
        depth = self._engine.random_int(1, 4)
        parts = [self._engine.choice(_DIR_PARTS) for _ in range(depth)]
        name = self._one_file_name()
        return "/" + "/".join(parts) + "/" + name

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @overload
    def file_name(self) -> str: ...
    @overload
    def file_name(self, count: Literal[1]) -> str: ...
    @overload
    def file_name(self, count: int) -> str | list[str]: ...
    def file_name(self, count: int = 1) -> str | list[str]:
        """Generate a random file name (e.g. ``"report.pdf"``).

        Parameters
        ----------
        count : int
            Number of file names to generate.
        """
        if count == 1:
            return self._one_file_name()
        return [self._one_file_name() for _ in range(count)]

    @overload
    def file_extension(self) -> str: ...
    @overload
    def file_extension(self, count: Literal[1]) -> str: ...
    @overload
    def file_extension(self, count: int) -> str | list[str]: ...
    def file_extension(self, count: int = 1) -> str | list[str]:
        """Generate a random file extension (e.g. ``"pdf"``, ``"jpg"``).

        Parameters
        ----------
        count : int
            Number of extensions to generate.
        """
        if count == 1:
            return self._one_ext_record()[0]
        return [self._one_ext_record()[0] for _ in range(count)]

    @overload
    def mime_type(self) -> str: ...
    @overload
    def mime_type(self, count: Literal[1]) -> str: ...
    @overload
    def mime_type(self, count: int) -> str | list[str]: ...
    def mime_type(self, count: int = 1) -> str | list[str]:
        """Generate a random MIME type (e.g. ``"application/pdf"``).

        Parameters
        ----------
        count : int
            Number of MIME types to generate.
        """
        if count == 1:
            return self._one_ext_record()[1]
        return [self._one_ext_record()[1] for _ in range(count)]

    @overload
    def file_path(self) -> str: ...
    @overload
    def file_path(self, count: Literal[1]) -> str: ...
    @overload
    def file_path(self, count: int) -> str | list[str]: ...
    def file_path(self, count: int = 1) -> str | list[str]:
        """Generate a random Unix file path (e.g. ``"/home/user/report.pdf"``).

        Parameters
        ----------
        count : int
            Number of file paths to generate.
        """
        if count == 1:
            return self._one_file_path()
        return [self._one_file_path() for _ in range(count)]

    @overload
    def file_category(self) -> str: ...
    @overload
    def file_category(self, count: Literal[1]) -> str: ...
    @overload
    def file_category(self, count: int) -> str | list[str]: ...
    def file_category(self, count: int = 1) -> str | list[str]:
        """Generate a random file category (e.g. ``"image"``, ``"document"``).

        Parameters
        ----------
        count : int
            Number of categories to generate.
        """
        categories = _FILE_CATEGORIES
        if count == 1:
            return self._engine.choice(categories)
        return self._engine.choices(categories, count)
