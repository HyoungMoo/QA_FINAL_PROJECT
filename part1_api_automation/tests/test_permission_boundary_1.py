# 권한 경계 관련 테스트를 작성하는 파일
# 고범석

import pytest

from utils.test_data import common_data


def _assert_permission_denied_response(response, expected_status_code=403):
    """권한 부족 응답인지 확인한다."""
    body = response.json()

    assert response.status_code == expected_status_code, (
        f"권한 경계 API 응답 상태 코드가 기대값과 다릅니다. "
        f"expected={expected_status_code}, "
        f"actual={response.status_code}, body={body}"
    )

    assert isinstance(body, dict), (
        f"권한 부족 응답 body가 dict 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    assert "code" in body, (
        f"권한 부족 응답 body에 'code' 항목이 없습니다. "
        f"body_keys={list(body.keys())}"
    )

    assert body["code"] == "has_no_permission", (
        f"권한 부족 에러 코드가 기대값과 다릅니다. "
        f"actual={body.get('code')}, expected=has_no_permission, body={body}"
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
