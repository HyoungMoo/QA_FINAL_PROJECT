# 권한 경계 관련 테스트를 작성하는 파일
# 고범석

import pytest

from utils.test_data import common_data


def _assert_permission_denied_response(response, expected_status_code=403):
    """Assert that the response is a permission-denied JSON error."""
    assert response.status_code == expected_status_code, (
        f"Permission boundary status code mismatch. "
        f"expected={expected_status_code}, "
        f"actual={response.status_code}, response={response.text}"
    )

    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type, (
        f"Response Content-Type is not JSON. "
        f"content_type={content_type}, response={response.text}"
    )

    body = response.json()

    assert isinstance(body, dict), (
        f"Permission-denied response body is not dict. "
        f"type={type(body).__name__}, body={body}"
    )

    required_error_keys = [
        "code",
        "message",
        "detail",
    ]
    missing_error_keys = [
        key for key in required_error_keys
        if key not in body
    ]

    assert not missing_error_keys, (
        f"Permission-denied response is missing required error keys. "
        f"missing_keys={missing_error_keys}, "
        f"body_keys={list(body.keys())}"
    )

    assert isinstance(body["code"], str), (
        f"code is not str. "
        f"type={type(body['code']).__name__}, value={body['code']}"
    )

    assert body["code"] == "has_no_permission", (
        f"Permission-denied error code mismatch. "
        f"actual={body.get('code')}, expected=has_no_permission, body={body}"
    )

    assert isinstance(body["message"], str), (
        f"message is not str. "
        f"type={type(body['message']).__name__}, value={body['message']}"
    )

    assert body["message"].strip() != "", (
        f"message is empty. message={body['message']!r}"
    )

    assert body["detail"] is None or isinstance(body["detail"], (str, dict, list)), (
        f"detail is not None, str, dict, or list. "
        f"type={type(body['detail']).__name__}, value={body['detail']}"
    )

    return body



@pytest.mark.p1
@pytest.mark.auth
def test_student_cannot_get_classroom_ticket_info(student_client):
    # 우선순위 : P1
    # TC ID: TC_PERMISSION_BOUNDARY_001
    # 학습자 권한으로 클래스룸 티켓 정보 조회 API 접근 시 차단되는지 확인한다.
    # Given-When-Then
        # Given : 학습자 권한 토큰, 학습자 클래스룸 ID 보유
        # When : 클래스룸 티켓 정보 조회 API 호출
        # Then : 권한 없음 응답인지 확인
    # 입력값 : student_classroom_id

    # Given : 학습자 권한 토큰, 학습자 클래스룸 ID 보유
    classroom_id = common_data.student_classroom_id

    # When : 클래스룸 티켓 정보 조회 API 호출
    response = student_client.get(
        f"/classroom/{classroom_id}/classroom_ticket/info"
    )

    # Then : 권한 없음 응답인지 확인
    body = _assert_permission_denied_response(response)

    print("")
    print("")
    print("TC_NO:TC_PERMISSION_BOUNDARY_001")
    print("status_code", response.status_code)
    print("(클래스룸 ID)classroom_id:", classroom_id)
    print("(에러 코드)code:", body["code"])
    print("(에러 메시지)message:", body.get("message"))


@pytest.mark.p1
@pytest.mark.auth
def test_student_cannot_update_classroom_name(student_client):
    # 우선순위 : P1
    # TC ID: TC_PERMISSION_BOUNDARY_002
    # 학습자 권한으로 클래스룸 이름 수정 API 접근 시 차단되는지 확인한다.
    # Given-When-Then
        # Given : 학습자 권한 토큰, 학습자 클래스룸 ID 보유
        # When : 클래스룸 이름 수정 API 호출
        # Then : 권한 없음 응답인지 확인
    # 입력값 : student_classroom_id, name

    # Given : 학습자 권한 토큰, 학습자 클래스룸 ID 보유
    classroom_id = common_data.student_classroom_id
    payload = {
        "name": "API_PERMISSION_BOUNDARY_TEST",
    }

    # When : 클래스룸 이름 수정 API 호출
    response = student_client.request(
        "PATCH",
        f"/classroom/{classroom_id}",
        json=payload,
    )

    # Then : 권한 없음 응답인지 확인
    body = _assert_permission_denied_response(response)

    print("")
    print("")
    print("TC_NO:TC_PERMISSION_BOUNDARY_002")
    print("status_code", response.status_code)
    print("(클래스룸 ID)classroom_id:", classroom_id)
    print("(에러 코드)code:", body["code"])
    print("(에러 메시지)message:", body.get("message"))


@pytest.mark.p1
@pytest.mark.auth
def test_student_cannot_get_classroom_member_count(student_client):
    # 우선순위 : P1
    # TC ID: TC_PERMISSION_BOUNDARY_003
    # 학습자 권한으로 클래스룸 멤버 수 조회 API 접근 시 차단되는지 확인한다.
    # Given-When-Then
        # Given : 학습자 권한 토큰, 학습자 클래스룸 ID 보유
        # When : 클래스룸 멤버 수 조회 API 호출
        # Then : 권한 없음 응답인지 확인
    # 입력값 : student_classroom_id

    # Given : 학습자 권한 토큰, 학습자 클래스룸 ID 보유
    classroom_id = common_data.student_classroom_id
    params = {
        "classroom_id": classroom_id,
    }

    # When : 클래스룸 멤버 수 조회 API 호출
    response = student_client.get(
        "/member/count",
        params=params,
    )

    # Then : 권한 없음 응답인지 확인
    body = _assert_permission_denied_response(response)

    print("")
    print("")
    print("TC_NO:TC_PERMISSION_BOUNDARY_003")
    print("status_code", response.status_code)
    print("(클래스룸 ID)classroom_id:", classroom_id)
    print("(에러 코드)code:", body["code"])
    print("(에러 메시지)message:", body.get("message"))
