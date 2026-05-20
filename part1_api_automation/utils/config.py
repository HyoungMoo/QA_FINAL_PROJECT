# .env 환경 변수 로딩, base_url/token/id 설정 관리
#
# API 테스트에는 토큰, 클래스 ID, 조직명처럼 사람마다 다르거나
# Git에 올리면 안 되는 값이 필요하다.
#
# 이런 값을 테스트 코드에 직접 적으면 다음 문제가 생긴다.
# - 실제 토큰이 Git에 올라갈 수 있다.
# - 팀원마다 다른 값을 코드에서 계속 수정해야 한다.
# - base_url, classroom_id 같은 값이 여러 파일에 흩어져 관리가 어렵다.
#
# 그래서 실제 값은 로컬의 .env 파일에 두고,
# 테스트 코드는 이 파일을 통해 필요한 설정만 읽어오도록 한다.

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """API 테스트 실행에 필요한 공통 설정값 묶음.

    dataclass를 쓰면 여러 설정값을 하나의 객체로 묶어서 다룰 수 있다.
    예: settings.student_token, settings.classroom_id

    frozen=True는 테스트 실행 중 설정값이 실수로 바뀌지 않게 막기 위한 옵션이다.
    """
    token: str
    student_id: str
    request_timeout_seconds: float


def get_settings() -> Settings:
    """환경 변수에서 테스트 설정을 읽어 Settings 객체로 만든다.

    테스트 파일이나 conftest.py에서는 이 함수만 호출하면
    필요한 환경 설정을 한 번에 가져올 수 있다.
    """
    return Settings(
        token=_get_env("token"),
        student_id=_get_env("student_id"),
        request_timeout_seconds=_get_float_env(
            "request_timeout_seconds", 10.0,),
    )

def _get_env(name: str, default: str | None = None) -> str:
    """문자열 환경 변수를 읽는다.

    필수 값이 비어 있으면 테스트를 애매하게 실패시키지 않고,
    어떤 환경 변수가 빠졌는지 바로 알 수 있도록 에러를 발생시킨다.
    """
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"환경 변수 {name} 값이 필요합니다.")

    return value


def _get_float_env(name: str, default: float) -> float:
    """숫자형 환경 변수를 읽는다.

    .env의 값은 문자열로 읽히기 때문에 timeout, 요청 간격 같은 값은
    float으로 변환해서 사용한다.
    값이 없으면 안전한 기본값을 사용한다.
    """
    value = os.getenv(name)
    if value is None or value == "":
        return default

    return float(value)
