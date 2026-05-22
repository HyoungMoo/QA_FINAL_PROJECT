# 권한 경계 관련 테스트를 작성하는 파일
# 고현우

from utils.test_data import common_data
from utils.test_data.student_material_data import (
    teacher_course_case, lecture_case
)


def test_student_cannot_change_lecture_page_visibility(rest_student_client):
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


def test_student_cannot_edit_lecture(rest_student_client):
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


def test_student_cannot_delete_lecture_page(rest_student_client):
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



def test_student_cannot_move_lecture_page(rest_student_client):
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



def test_student_cannot_clone_lecture(rest_student_client):
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