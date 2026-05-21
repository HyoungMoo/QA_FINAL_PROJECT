import pytest
from utils.test_data import common_data
from utils.test_data.student_material_data import (
    teacher_course_case,
)

def test_teacher_can_change_lecture_page_visibility(
    rest_teacher_client,
):
    # Given
    # 수업자료의 공개 상태를 조회한다.
    get_response = rest_teacher_client.get(
        f"/org/{common_data.org_teacher}/lecture_page/get/",
        params={
            "lecture_page_id": teacher_course_case[
                "lecture_page_id"
            ],
        },
    )

    get_body = get_response.json()

    # 조회 API 정상 응답 검증
    assert get_response.status_code == 200
    assert get_body["_result"]["status"] == "ok", (
        f"lecture_page 조회 실패: {get_body}"
    )

    # 현재 공개 상태 값 조회
    current_is_opened = get_body["lecture_page"]["is_opened"]

    # 현재 상태의 반대값으로 변경 요청 payload 생성
    # 공개(true) -> 비공개(false)
    # 비공개(false) -> 공개(true)
    payload = {
        "lecture_page_ids": teacher_course_case[
            "lecture_page_id"
        ],
        "is_opened": str(not current_is_opened).lower(),
    }

    # When
    # 수업자료 공개 상태 변경 API 호출
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture_page/visibility/edit/bulk/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 자체 응답 성공 여부 검증
    assert response.status_code == 200, (
        f"lecture_page 조회 HTTP 응답 실패: "
        f"status_code={get_response.status_code}, body={get_body}"
    )

    # 실제 API 비즈니스 로직 성공 여부 검증
    # 해당 프로젝트 API는 실패해도 HTTP 200을 반환하는 경우가 있으므로
    # 반드시 _result.status 값을 추가 검증해야 한다.
    assert body["_result"]["status"] == "ok", (
        f"수업자료 공개 상태 변경 실패: {body}"
    )


def test_teacher_can_create_lecture(rest_teacher_client):
    # Given
    # 교육자 권한 수업 생성 payload
    payload = {
        "course_id": teacher_course_case["course_id"],
        "title": "API_CREATE_TEST",
        "description": "API_CREATE_TEST",
        "lecture_type": 0,
        "teaching_datetime": 1779894000000,
        "is_opened": "false",
        "is_preview": "false",
    }

    # When
    # lecture_id 없이 호출 시 새 수업 생성
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture/edit/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 성공 여부 검증
    assert response.status_code == 200, (
        f"수업 생성 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 성공 여부 검증
    assert body["_result"]["status"] == "ok", (
        f"수업 생성 실패: {body}"
    )

    # 생성된 lecture_id 반환 여부 검증
    assert "lecture_id" in body, (
        f"수업 생성 응답에 lecture_id 없음: {body}"
    )

from utils.test_data import common_data
from utils.test_data.student_material_data import (
    teacher_course_case,
)


def test_teacher_can_edit_lecture_title(rest_teacher_client):
    # Given
    # 기존 수업 정보 조회
    get_response = rest_teacher_client.get(
        f"/org/{common_data.org_teacher}/lecture/get/",
        params={
            "lecture_id": teacher_course_case["lecture_id"],
        },
    )

    get_body = get_response.json()

    # 수업 조회 HTTP 응답 성공 여부 검증
    assert get_response.status_code == 200, (
        f"수업 조회 HTTP 응답 실패: "
        f"status_code={get_response.status_code}, body={get_body}"
    )

    # 수업 조회 비즈니스 로직 성공 여부 검증
    assert get_body["_result"]["status"] == "ok", (
        f"수업 조회 실패: {get_body}"
    )

    lecture = get_body["lecture"]

    # 기존 상태값 유지 + title만 변경
    payload = {
        "lecture_id": teacher_course_case["lecture_id"],
        "course_id": teacher_course_case["course_id"],
        "title": "API_SSS",
        "description": lecture["description"],
        "lecture_type": lecture["lecture_type"],
        "teaching_datetime": lecture["teaching_datetime"],
        "is_opened": str(lecture["is_opened"]).lower(),
        "is_preview": str(lecture["is_preview"]).lower(),
    }

    # When
    # 기존 상태 유지 후 title만 수정
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture/edit/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 성공 여부 검증
    assert response.status_code == 200, (
        f"수업 제목 수정 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 성공 여부 검증
    assert body["_result"]["status"] == "ok", (
        f"수업 제목 수정 실패: {body}"
    )

    # 수정 대상 lecture_id 유지 여부 검증
    assert body["lecture_id"] == teacher_course_case["lecture_id"], (
        f"수정된 lecture_id 불일치: {body}"
    )




def test_teacher_can_move_lecture_page(rest_teacher_client):
    # Given
    # 수업자료 목록 조회
    list_response = rest_teacher_client.get(
        f"/org/{common_data.org_teacher}/lecture_page/list/",
        params={
            "lecture_id": teacher_course_case["lecture_id"],
            "locator_type": 0,
            "offset": 0,
            "count": 50,
        },
    )

    list_body = list_response.json()

    # 수업자료 목록 조회 HTTP 응답 성공 여부 검증
    assert list_response.status_code == 200, (
        f"수업자료 목록 조회 HTTP 응답 실패: "
        f"status_code={list_response.status_code}, body={list_body}"
    )

    # 수업자료 목록 조회 비즈니스 로직 성공 여부 검증
    assert list_body["_result"]["status"] == "ok", (
        f"수업자료 목록 조회 실패: {list_body}"
    )

    lecture_pages = list_body["lecture_pages"]

    # 테스트 대상 수업자료의 현재 위치 확인
    target_index = next(
        index
        for index, page in enumerate(lecture_pages)
        if page["id"] == teacher_course_case[
            "move_lecture_page_id"
        ]
    )

    # 현재 첫 번째면 두 번째로, 아니면 첫 번째로 이동
    new_order_no = 2 if target_index == 0 else 1

    # 수업자료 순서 변경 payload
    payload = {
        "lecture_page_id": teacher_course_case[
            "move_lecture_page_id"
        ],
        "locator_type": 0,
        "new_order_no": new_order_no,
    }

    # When
    # 수업자료 순서 변경 API 호출
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture_page/move/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 성공 여부 검증
    assert response.status_code == 200, (
        f"수업자료 순서 변경 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 성공 여부 검증
    assert body["_result"]["status"] == "ok", (
        f"수업자료 순서 변경 실패: {body}"
    )


def test_teacher_can_delete_lecture_page(rest_teacher_client):
    # Given
    # 삭제 대상 수업자료 목록 조회
    list_response = rest_teacher_client.get(
        f"/org/{common_data.org_teacher}/lecture_page/list/",
        params={
            "lecture_id": teacher_course_case["delete_lecture_id"],
            "locator_type": 0,
            "offset": 0,
            "count": 50,
        },
    )

    list_body = list_response.json()

    # 수업자료 목록 조회 HTTP 응답 성공 여부 검증
    assert list_response.status_code == 200, (
        f"수업자료 목록 조회 HTTP 응답 실패: "
        f"status_code={list_response.status_code}, body={list_body}"
    )

    # 수업자료 목록 조회 비즈니스 로직 성공 여부 검증
    assert list_body["_result"]["status"] == "ok", (
        f"수업자료 목록 조회 실패: {list_body}"
    )

    lecture_pages = list_body["lecture_pages"]

    # 삭제 대상 없으면 테스트 제외
    if not lecture_pages:
        pytest.skip("삭제 가능한 수업자료 없음")

    target_lecture_page_id = lecture_pages[-1]["id"]

    payload = {
        "lecture_page_ids": target_lecture_page_id,
    }

    # When
    # 수업자료 삭제 API 호출
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture_page/delete/bulk/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 성공 여부 검증
    assert response.status_code == 200, (
        f"수업자료 삭제 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 성공 여부 검증
    assert body["_result"]["status"] == "ok", (
        f"수업자료 삭제 실패: {body}"
    )


def test_teacher_can_clone_lecture(rest_teacher_client):
    # Given
    # 수업 복제 payload
    payload = {
        "lecture_id": teacher_course_case["copy_lecture_id"],
        "target_course_id": teacher_course_case["copy_course_id"],
    }

    # When
    # 수업 복제 API 호출
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture/clone/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 성공 여부 검증
    assert response.status_code == 200, (
        f"수업 복제 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 성공 여부 검증
    assert body["_result"]["status"] == "ok", (
        f"수업 복제 실패: {body}"
    )

    # 복제된 lecture_id 반환 여부 검증
    assert body["lecture_id"], (
        f"복제된 lecture_id 없음: {body}"
    )



def test_teacher_can_create_material_quiz(rest_teacher_client):
    # Given
    # 퀴즈 학습자료 생성 payload
    payload = {
        "lecture_id": teacher_course_case["quiz_lecture_id"],
        "lecture_page_id": "undefined",
        "id": "undefined",
        "title": "API_QUIZ_CREATE_TEST",
        "description": "",
        "is_opened": "false",
        "is_for_stats": "true",
        "difficulty_type": 10,
        "question_title": "Untitled Quiz",
        "question_description": "",
        "option_type": 0,
        "options_default": '[{"title":"","content":"Apple"},{"title":"","content":"Banana"}]',
        "answer_info_default": "[0]",
        "answer_info": "[0]",
        "is_auto_grade": "true",
        "explanation_info": '{"is_enabled":false,"value":""}',
        "options_set_enabled": "false",
    }

    # When
    # 퀴즈 학습자료 생성 API 호출
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/material_quiz/edit/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 성공 여부 검증
    assert response.status_code == 200, (
        f"퀴즈 학습자료 생성 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 성공 여부 검증
    assert body["_result"]["status"] == "ok", (
        f"퀴즈 학습자료 생성 실패: {body}"
    )

    # 생성된 퀴즈 ID 반환 여부 검증
    assert body["material_quiz_id"], (
        f"생성된 material_quiz_id 없음: {body}"
    )



def test_teacher_can_reset_material_quiz_response(rest_teacher_client):
    # Given
    # 제출 기록 생성을 위한 퀴즈 1번 선택 payload
    submit_payload = {
        "material_quiz_id": teacher_course_case[
            "material_quiz_id"
        ],
        "answer": "[0]",
    }

    # 선생 권한 퀴즈 제출 API 호출
    submit_response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/material_quiz/response/add/",
        data=submit_payload,
    )

    submit_body = submit_response.json()

    # 퀴즈 제출 HTTP 응답 성공 여부 검증
    assert submit_response.status_code == 200, (
        f"퀴즈 제출 HTTP 응답 실패: "
        f"status_code={submit_response.status_code}, "
        f"body={submit_body}"
    )

    # 퀴즈 제출 API 비즈니스 로직 성공 여부 검증
    assert submit_body["_result"]["status"] == "ok", (
        f"퀴즈 제출 실패: {submit_body}"
    )

    # When
    # 퀴즈 제출 기록 초기화 parameter
    params = {
        "material_quiz_id": teacher_course_case[
            "material_quiz_id"
        ],
    }

    # 퀴즈 제출 기록 초기화 API 호출
    reset_response = rest_teacher_client.get(
        f"/org/{common_data.org_teacher}/material_quiz/response/reset/",
        params=params,
    )

    reset_body = reset_response.json()

    # Then
    # 초기화 HTTP 응답 성공 여부 검증
    assert reset_response.status_code == 200, (
        f"퀴즈 제출 기록 초기화 HTTP 응답 실패: "
        f"status_code={reset_response.status_code}, "
        f"body={reset_body}"
    )

    # 초기화 API 비즈니스 로직 성공 여부 검증
    assert reset_body["_result"]["status"] == "ok", (
        f"퀴즈 제출 기록 초기화 실패: {reset_body}"
    )


def test_teacher_can_add_course_to_classroom(teacher_client):
    # Given
    # 클래스룸 과목 추가 payload
    payload = {
        "original_course_ids": [
            teacher_course_case["add_course_id"]
        ],
    }

    # When
    # 클래스룸 과목 추가 API 호출
    response = teacher_client.request(
        "POST",
        f"/v2/classroom/{common_data.teacher_classroom_id}/course/bulk",
        json=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 성공 여부 검증
    assert response.status_code == 200, (
        f"클래스룸 과목 추가 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 비동기 작업 task_id 반환 여부 검증
    assert body["task_id"], (
        f"클래스룸 과목 추가 task_id 반환 실패: {body}"
    )



def test_teacher_can_reorder_course(teacher_client):
    # Given
    # 현재 과목 목록 조회
    list_response = teacher_client.get(
        f"/classroom/{common_data.teacher_classroom_id}/course",
        params={
            "skip": 0,
            "count": 100,
        },
    )

    list_body = list_response.json()

    # 과목 목록 조회 HTTP 응답 성공 여부 검증
    assert list_response.status_code == 200, (
        f"과목 목록 조회 HTTP 응답 실패: "
        f"status_code={list_response.status_code}, "
        f"body={list_body}"
    )

    # 현재 순서 기준 course_id 추출
    course_ids = [
        course["course_id"]
        for course in list_body
    ]

    # 3번째, 4번째 과목 순서 변경
    course_ids[2], course_ids[3] = (
        course_ids[3],
        course_ids[2],
    )

    payload = {
        "course_ids": course_ids,
    }

    # When
    # 과목 순서 변경 API 호출
    response = teacher_client.request(
        "POST",
        f"/classroom/{common_data.teacher_classroom_id}/course/reorder",
        json=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 성공 여부 검증
    assert response.status_code == 200, (
        f"과목 순서 변경 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 응답 body 반환 여부 검증
    assert body == {}, (
        f"과목 순서 변경 응답 body가 예상 결과와 다름: {body}"
    )
