# pytest 공통 fixture 정의 파일
#
# fixture는 테스트 실행 전에 필요한 준비물을 만들어주는 pytest 기능이다.
# 예를 들어 학생용 API를 테스트할 때마다 token과 base_url을 직접 준비하면
# 테스트 파일마다 같은 코드가 반복된다.
#
# 이 파일에 settings, student_client, teacher_client를 만들어두면
# 각 테스트 함수는 필요한 이름만 매개변수로 받아서 바로 사용할 수 있다.
#
# 실제 token/cookie/password 값은 코드에 직접 작성하지 않고 .env에서 불러온다.
# 공통 URL/org 값은 common_data.py에서 관리한다.

from __future__ import annotations

import pytest

from utils.api_client import APIClient
from utils.config import Settings, get_settings
from utils.test_data import common_data


@pytest.fixture(scope="session")
def settings() -> Settings:
    # session scope는 pytest 실행 1회 동안 한 번만 설정을 읽겠다는 뜻이다.
    # 환경 변수는 테스트 중 자주 바뀌지 않으므로 매 테스트마다 읽을 필요가 없다.
    return get_settings()


@pytest.fixture(scope="session")
def student_client(settings: Settings) -> APIClient:
    # 수강생 권한으로 호출할 API client.
    # test_student.py에서 주로 사용한다.
    return APIClient(
        base_url=common_data.base_classroom_url,
        token=settings.token,
        org_name=common_data.org_student,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )


@pytest.fixture(scope="session")
def account_student_client(settings: Settings) -> APIClient:
    # api-account 서버 호출 시 사용
    return APIClient(
        base_url=common_data.base_account_url,
        token=settings.token,
        org_name=common_data.org_student,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )


@pytest.fixture(scope="session")
def dashboard_student_client(settings: Settings) -> APIClient:
    # api-dashboard 서버 호출 시 사용
    return APIClient(
        base_url=common_data.base_dashboard_url,
        token=settings.token,
        org_name=common_data.org_student,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )


@pytest.fixture(scope="session")
def course_student_client(settings: Settings) -> APIClient:
    # api-course 서버 호출 시 사용
    return APIClient(
        base_url=common_data.base_course_url,
        token=settings.token,
        org_name=common_data.org_student,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )


@pytest.fixture(scope="session")
def rest_student_client(settings: Settings) -> APIClient:
    # api-rest 서버 호출 시 사용
    return APIClient(
        base_url=common_data.base_rest_url,
        token=settings.token,
        org_name=common_data.org_student,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )


@pytest.fixture(scope="session")
def billing2_student_client(settings: Settings) -> APIClient:
    # api-billing2 서버 호출 시 사용
    return APIClient(
        base_url=common_data.base_billing2_url,
        token=settings.token,
        org_name=common_data.org_student,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )


@pytest.fixture(scope="session")
def channel_student_client(settings: Settings) -> APIClient:
    # api-channel 서버 호출 시 사용
    return APIClient(
        base_url=common_data.base_channel_url,
        token=settings.token,
        org_name=common_data.org_student,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )


@pytest.fixture(scope="session")
def community_student_client(settings: Settings) -> APIClient:
    # api-community 서버 호출 시 사용
    return APIClient(
        base_url=common_data.base_community_url,
        token=settings.token,
        org_name=common_data.org_student,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )


@pytest.fixture(scope="session")
def notification_student_client(settings: Settings) -> APIClient:
    # api-notification 서버 호출 시 사용
    return APIClient(
        base_url=common_data.base_notification_url,
        token=settings.token,
        org_name=common_data.org_student,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )


@pytest.fixture(scope="session")
def org_student_client(settings: Settings) -> APIClient:
    # api-org 서버 호출 시 사용
    return APIClient(
        base_url=common_data.base_org_url,
        token=settings.token,
        org_name=common_data.org_student,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )


@pytest.fixture(scope="session")
def file_student_client(settings: Settings) -> APIClient:
    # api-file 서버 호출 시 사용
    return APIClient(
        base_url=common_data.base_file_url,
        token=settings.token,
        org_name=common_data.org_student,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )


@pytest.fixture(scope="session")
def teacher_client(settings: Settings) -> APIClient:
    # 교육자 권한으로 호출할 API client.
    # test_teacher.py나 권한 경계 테스트에서 사용한다.
    return APIClient(
        base_url=common_data.base_classroom_url,
        token=settings.token,
        org_name=common_data.org_teacher,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )


@pytest.fixture(scope="session")
def rest_teacher_client(settings: Settings) -> APIClient:
    # 교육자 권한으로 호출할 API client.
    # test_teacher.py나 권한 경계 테스트에서 사용한다.
    return APIClient(
        base_url=common_data.base_rest_url,
        token=settings.token,
        org_name=common_data.org_teacher,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )