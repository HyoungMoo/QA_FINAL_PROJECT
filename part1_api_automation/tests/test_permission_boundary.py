# 권한 경계 테스트

import pytest
from utils.test_data import common_data
from utils.test_data.student_material_data import (
    teacher_course_case, lecture_case
)

DT_START = "2026-04-16T15:00:00.000Z"
DT_END = "2026-06-14T14:59:59.999Z"

pytestmark = pytest.mark.auth


# boundary_1
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
@pytest.mark.smoke
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


# boundary_2
@pytest.mark.p0
def test_student_cannot_change_lecture_page_visibility(rest_student_client):
    # 우선순위 : P0
    # TC ID: TC-TEACHER_COURSE-022
    # 학생 권한으로 수업자료 공개 상태 변경 API 호출 시 권한 오류가 반환되는지 검증

    # Given
    # 학생 권한으로 수업자료 공개 상태 변경 payload
    payload = {
        "lecture_page_ids": teacher_course_case[
            "lecture_page_id"
        ],
        "is_opened": "false",
    }

    # When
    # 학생 권한으로 교육자 전용 공개 상태 변경 API 호출
    response = rest_student_client.request(
        "POST",
        f"/org/{common_data.org_student}/lecture_page/visibility/edit/bulk/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 여부 검증
    assert response.status_code == 200, (
        f"학생 권한 수업자료 공개 상태 변경 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 권한 부족 실패 여부 검증
    assert body["_result"]["status"] == "fail", (
        f"학생 권한 요청이 실패하지 않음: {body}"
    )

    # 권한 부족 에러 코드 검증
    assert body["fail_code"] == "insufficient_permission", (
        f"권한 부족 에러 코드 불일치: {body}"
    )

    # 권한 부족 에러 메시지 검증
    assert body["fail_message"] == "you should be HeadTA or above", (
        f"권한 부족 에러 메시지 불일치: {body}"
    )

@pytest.mark.p0
def test_student_cannot_edit_lecture(rest_student_client):
    # 우선순위 : P0
    # TC ID: TC-TEACHER_COURSE-023
    # 학생 권한으로 수업 수정 API 호출 시 권한 오류가 반환되는지 검증

    # Given
    # 학생 권한으로 수업 수정 payload
    payload = {
        "course_id": lecture_case["week1_course_id"],
        "title": "API_PERMISSION_TEST",
        "description": "API_PERMISSION_TEST",
        "lecture_type": 0,
        "teaching_datetime": 1779894000000,
        "is_opened": "false",
        "is_preview": "false",
    }

    # When
    # 학생 권한으로 교육자 전용 수업 수정 API 호출
    response = rest_student_client.request(
        "POST",
        f"/org/{common_data.org_student}/lecture/edit/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 여부 검증
    assert response.status_code == 200, (
        f"학생 권한 수업 수정 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 권한 부족 실패 여부 검증
    assert body["_result"]["status"] == "fail", (
        f"학생 권한 수업 수정 요청이 실패하지 않음: {body}"
    )

    # 권한 부족 에러 코드 검증
    assert body["fail_code"] == "insufficient_permission", (
        f"권한 부족 에러 코드 불일치: {body}"
    )

    # 권한 부족 에러 메시지 검증
    assert body["fail_message"] == "you should be HeadTA or above", (
        f"권한 부족 에러 메시지 불일치: {body}"
    )

@pytest.mark.p0
def test_student_cannot_delete_lecture_page(rest_student_client):
    # 우선순위 : P0
    # TC ID: TC-TEACHER_COURSE-024
    # 학생 권한으로 수업자료 삭제 API 호출 시 권한 오류가 반환되는지 검증

    # Given
    # 학생 권한으로 수업자료 삭제 payload
    payload = {
        "lecture_page_ids": lecture_case[
            "week1_2lecture_page_id"
        ],
    }

    # When
    # 학생 권한으로 교육자 전용 수업자료 삭제 API 호출
    response = rest_student_client.request(
        "POST",
        f"/org/{common_data.org_student}/lecture_page/delete/bulk/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 여부 검증
    assert response.status_code == 200, (
        f"학생 권한 수업자료 삭제 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 권한 부족 실패 여부 검증
    assert body["_result"]["status"] == "fail", (
        f"학생 권한 수업자료 삭제 요청이 실패하지 않음: {body}"
    )

    # 권한 부족 에러 코드 검증
    assert body["fail_code"] == "insufficient_permission", (
        f"권한 부족 에러 코드 불일치: {body}"
    )

    # 권한 부족 에러 메시지 검증
    assert body["fail_message"] == "you should be HeadTA or above", (
        f"권한 부족 에러 메시지 불일치: {body}"
    )

@pytest.mark.p0
def test_student_cannot_clone_lecture(rest_student_client):
    # 우선순위 : P0
    # TC ID: TC-TEACHER_COURSE-026
    # 학생 권한으로 수업 복제 API 호출 시 권한 오류가 반환되는지 검증

    # Given
    # 학생 권한으로 수업 복제 payload
    payload = {
        "lecture_id": lecture_case["week1_2lecture_id"],
        "target_course_id": lecture_case["week1_course_id"],
    }

    # When
    # 학생 권한으로 교육자 전용 수업 복제 API 호출
    response = rest_student_client.request(
        "POST",
        f"/org/{common_data.org_student}/lecture/clone/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 여부 검증
    assert response.status_code == 200, (
        f"학생 권한 수업 복제 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 권한 부족 실패 여부 검증
    assert body["_result"]["status"] == "fail", (
        f"학생 권한 수업 복제 요청이 실패하지 않음: {body}"
    )

    # 권한 부족 에러 코드 검증
    assert body["fail_code"] == "insufficient_permission", (
        f"권한 부족 에러 코드 불일치: {body}"
    )

    # 권한 부족 에러 메시지 검증
    assert body["fail_message"] == "you should be HeadTA or above", (
        f"권한 부족 에러 메시지 불일치: {body}"
    )

@pytest.mark.p1
def test_student_cannot_move_lecture_page(rest_student_client):
    # 우선순위 : P1
    # TC ID: TC-TEACHER_COURSE-025
    # 학생 권한으로 수업자료 순서 변경 API 호출 시 권한 오류가 반환되는지 검증

    # Given
    # 학생 권한으로 수업자료 순서 변경 payload
    payload = {
        "lecture_page_id": lecture_case[
            "week1_2lecture_page_id"
        ],
        "locator_type": 0,
        "new_order_no": 1,
    }

    # When
    # 학생 권한으로 교육자 전용 수업자료 순서 변경 API 호출
    response = rest_student_client.request(
        "POST",
        f"/org/{common_data.org_student}/lecture_page/move/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 여부 검증
    assert response.status_code == 200, (
        f"학생 권한 수업자료 순서 변경 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 권한 부족 실패 여부 검증
    assert body["_result"]["status"] == "fail", (
        f"학생 권한 수업자료 순서 변경 요청이 실패하지 않음: {body}"
    )

    # 권한 부족 에러 코드 검증
    assert body["fail_code"] == "insufficient_permission", (
        f"권한 부족 에러 코드 불일치: {body}"
    )

    # 권한 부족 에러 메시지 검증
    assert body["fail_message"] == "you should be HeadTA or above", (
        f"권한 부족 에러 메시지 불일치: {body}"
    )

# boundary_3
class TestSchedulePermission:

    @pytest.mark.p0
    def test_student_cannot_create_schedule(self, student_client):
        # 우선순위: P0
        # TC ID: TC-SCH-016
        # Given: 학습자 토큰, 일정 생성 요청 데이터
        # When: POST /schedule 호출
        # Then: 403 응답 (학습자는 생성 권한 없음)

        response = student_client.request(
            "POST",
            "/schedule",
            json={
                "classroom_id": common_data.student_classroom_id,
                "summary": "test",
                "dt_start": "2026-05-20T09:00:00.000Z",
                "dt_end": "2026-05-20T10:00:00.000Z",
            },
        )

        assert response.status_code == 403, (
            f"학습자 토큰으로 일정 생성 시 403이 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

    @pytest.mark.p0
    @pytest.mark.parametrize("method,extra_body", [
        pytest.param("PATCH", {"summary": "hacked"}, id="TC-SCH-017-update"),
        pytest.param("DELETE", {}, id="TC-SCH-018-delete"),
    ])
    def test_student_cannot_modify_schedule(self, student_client, method, extra_body):
        # 우선순위: P0
        # TC ID: TC-SCH-017 (PATCH), TC-SCH-018 (DELETE)
        # Given: 학습자 토큰, 기존 일정 ID
        # When: PATCH 또는 DELETE /schedule/{id} 호출
        # Then: 403 응답 (학습자는 수정/삭제 권한 없음)

        list_response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.student_classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 40,
            },
        )
        schedules = list_response.json()
        if not schedules:
            pytest.skip("조회된 일정이 없어 테스트를 건너뜁니다.")

        schedule_id = schedules[0]["id"]

        body = {"classroom_id": common_data.student_classroom_id, **extra_body}
        response = student_client.request(method, f"/schedule/{schedule_id}", json=body)

        assert response.status_code == 403, (
            f"학습자 토큰으로 {method} 요청 시 403이 아닌 응답이 반환되었습니다. "
            f"schedule_id={schedule_id}, "
            f"status_code={response.status_code}, response={response.text}"
        )
