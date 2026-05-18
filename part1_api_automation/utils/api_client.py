# requests 기반 API 호출 래퍼, header/token/호출 제한 처리
#
# 테스트 파일마다 requests.get(), headers, timeout을 직접 쓰면
# 같은 코드가 계속 반복되고, 누군가는 header를 빠뜨릴 수 있다.
#
# 이 파일은 API 호출 방식을 한 곳에 모아두기 위한 공통 도구다.
# 테스트 파일에서는 student_client.get("/schedule")처럼 간단히 호출하고,
# token/header/base_url/timeout 같은 공통 처리는 이 클래스가 담당한다.

from __future__ import annotations

import time
from typing import Any
from urllib.parse import urljoin

import requests


class APIClient:
    """API 테스트에서 공통으로 사용할 requests.Session 래퍼.

    Session을 쓰면 매 요청마다 header를 새로 만들지 않아도 되고,
    같은 설정을 유지한 채 여러 API를 호출할 수 있다.
    """

    def __init__(
        self,
        base_url: str,
        token: str | None,
        org_name: str,
        timeout: float,
        min_interval: float,
    ) -> None:
        # base_url은 마지막에 "/"가 있든 없든 같은 방식으로 동작하게 맞춘다.
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.min_interval = min_interval
        self._last_request_at = 0.0

        # 모든 요청에 공통으로 들어갈 header를 한 번만 설정한다.
        # .env의 token 값이 "Bearer ..." 형태이면 그대로 쓰고,
        # 순수 토큰 값이면 여기서 Bearer를 붙인다.
        self.session = requests.Session()
        headers: dict[str, str] = {
            "x-elice-org-name-short": org_name,
            "Accept": "application/json",
        }
        if token:
            headers["Authorization"] = token if token.startswith("Bearer ") else f"Bearer {token}"
        self.session.headers.update(headers)

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        # 운영 서비스에 너무 빠르게 연속 요청을 보내지 않도록 최소 간격을 둔다.
        self._wait_for_rate_limit()
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, self._build_url(path), **kwargs)

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        # 테스트 코드에서는 이 메서드를 가장 많이 사용할 예정이다.
        return self.request("GET", path, **kwargs)

    def _build_url(self, path: str) -> str:
        # base_url과 endpoint path를 안전하게 합친다.
        return urljoin(self.base_url, path.lstrip("/"))

    def _wait_for_rate_limit(self) -> None:
        # 마지막 요청 이후 충분한 시간이 지나지 않았다면 잠깐 대기한다.
        # 이 값은 .env의 MIN_REQUEST_INTERVAL_SECONDS로 조정할 수 있다.
        elapsed = time.monotonic() - self._last_request_at
        wait_seconds = self.min_interval - elapsed
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        self._last_request_at = time.monotonic()
