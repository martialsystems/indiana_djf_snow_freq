# Copyright (c) 2026 Martial Systems LLC
"""Injectable GET."""

from __future__ import annotations

import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from snowfreq.config import USER_AGENT
from snowfreq.errors import FetchError

GetBytes = Callable[[str], bytes]


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, HTTPError):
        return int(getattr(exc, "code", 0) or 0) >= 500
    return isinstance(exc, (URLError, TimeoutError, ConnectionResetError, ConnectionError))


def get_bytes(url: str, *, timeout: int = 90, attempts: int = 6) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    last: BaseException | None = None
    for i in range(attempts):
        try:
            with urlopen(req, timeout=timeout) as resp:
                code = int(getattr(resp, "status", 200) or 200)
                body = resp.read()
                if code == 404 or not body:
                    raise FetchError(f"GET empty or 404: {url}")
                return body
        except HTTPError as exc:
            last = exc
            code = int(getattr(exc, "code", 0) or 0)
            if code == 404:
                raise FetchError(f"GET empty or 404: {url}") from exc
            if not _is_retryable(exc) or i == attempts - 1:
                raise FetchError(f"GET failed: {url}: {exc}") from exc
        except (URLError, TimeoutError, ConnectionResetError, ConnectionError) as exc:
            last = exc
            if i == attempts - 1:
                raise FetchError(f"GET failed: {url}: {exc}") from exc
        time.sleep(min(2 ** i, 8))
    raise FetchError(f"GET failed: {url}: {last}")
