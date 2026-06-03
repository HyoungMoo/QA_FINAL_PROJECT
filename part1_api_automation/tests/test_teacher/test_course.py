import pytest
from utils.test_data import common_data
from utils.test_data.student_material_data import (
    teacher_course_case,
)

pytestmark = pytest.mark.teacher

### Positive Test


@pytest.mark.p0
def test_teacher_can_create_lecture(rest_teacher_client):
    # 우선순위 : P0
    # TC ID: TC-TEACHER_COURSE-002
    # 교육자 권한 수업 생성 API 테스트.

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


    created_lecture_id = body["lecture_id"]

    # 생성된 수업 삭제(원복)
    rollback_response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture/delete/",
        data={
            "lecture_id": created_lecture_id,
        },
    )

    rollback_body = rollback_response.json()

    # 원복 HTTP 응답 성공 여부 검증
    assert rollback_response.status_code == 200, (
        f"수업 삭제 HTTP 응답 실패: "
        f"status_code={rollback_response.status_code}, "
        f"body={rollback_body}"
    )

    # 원복 API 비즈니스 로직 성공 여부 검증
    assert rollback_body["_result"]["status"] == "ok", (
        f"수업 삭제 실패: {rollback_body}"
    )

@pytest.mark.p0
def test_teacher_can_edit_lecture(rest_teacher_client):
    # 우선순위 : P0
    # TC ID: TC-TEACHER_COURSE-003
    # 교육자 권한 수업 수정 API 테스트.

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

    # 수업 수정 payload
    payload = {
        "lecture_id": teacher_course_case["lecture_id"],
        "course_id": teacher_course_case["course_id"],
        "title": "API_EDIT_TEST",
        "description": "API_EDIT_TEST",
        "lecture_type": 0,
        "teaching_datetime": 1779894000000,
        "is_opened": "false",
        "is_preview": "false",
    }

    # When
    # 임의 값으로 수업 정보 수정
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture/edit/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 성공 여부 검증
    assert response.status_code == 200, (
        f"수업 수정 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 성공 여부 검증
    assert body["_result"]["status"] == "ok", (
        f"수업 수정 실패: {body}"
    )

    # 수정 대상 lecture_id 유지 여부 검증
    assert body["lecture_id"] == teacher_course_case["lecture_id"], (
        f"수정된 lecture_id 불일치: {body}"
    )

    # 원복 API 호출
    rollback_response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture/edit/",
        data={
            "lecture_id": teacher_course_case["lecture_id"],
            "course_id": teacher_course_case["course_id"],
            "title": lecture["title"],
            "description": lecture["description"],
            "lecture_type": lecture["lecture_type"],
            "teaching_datetime": lecture["teaching_datetime"],
            "is_opened": str(lecture["is_opened"]).lower(),
            "is_preview": str(lecture["is_preview"]).lower(),
        },
    )

    rollback_body = rollback_response.json()

    # 원복 HTTP 응답 성공 여부 검증
    assert rollback_response.status_code == 200, (
        f"수업 정보 원복 HTTP 응답 실패: "
        f"status_code={rollback_response.status_code}, "
        f"body={rollback_body}"
    )

    # 원복 API 비즈니스 로직 성공 여부 검증
    assert rollback_body["_result"]["status"] == "ok", (
        f"수업 정보 원복 실패: {rollback_body}"
    )

@pytest.mark.p0
def test_teacher_can_change_lecture_page_visibility(
    rest_teacher_client,
):
    # 우선순위 : P0
    # TC ID: TC-TEACHER_COURSE-001
    # 수업자료 공개/비공개 상태 변경 API 테스트.

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

    rollback_response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture_page/visibility/edit/bulk/",
        data={
            "lecture_page_ids": teacher_course_case[
                "lecture_page_id"
            ],
            "is_opened": str(current_is_opened).lower(),
        },
    )

    rollback_body = rollback_response.json()

    # 원복 HTTP 응답 성공 여부 검증
    assert rollback_response.status_code == 200, (
        f"수업자료 공개 상태 원복 HTTP 응답 실패: "
        f"status_code={rollback_response.status_code}, "
        f"body={rollback_body}"
    )

    # 원복 API 비즈니스 로직 성공 여부 검증
    assert rollback_body["_result"]["status"] == "ok", (
        f"수업자료 공개 상태 원복 실패: {rollback_body}"
    )

@pytest.mark.p0
def test_teacher_can_create_material_quiz(rest_teacher_client):
    # 우선순위 : P0
    # TC ID: TC-TEACHER_COURSE-008
    # 퀴즈 학습자료 생성 API 테스트.

    # Given
    # 퀴즈 학습자료 생성 payload
    payload = {
        "lecture_id": teacher_course_case["lecture_id"],
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

    created_material_quiz_id = None
    target_lecture_page_id = None

    try:
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

        # 생성된 퀴즈 ID 저장
        created_material_quiz_id = body["material_quiz_id"]

        # 원복에 필요한 lecture_page_id 확인을 위한 수업자료 목록 조회
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
            f"퀴즈 생성 후 수업자료 목록 조회 HTTP 응답 실패: "
            f"status_code={list_response.status_code}, body={list_body}"
        )

        # 수업자료 목록 조회 비즈니스 로직 성공 여부 검증
        assert list_body["_result"]["status"] == "ok", (
            f"퀴즈 생성 후 수업자료 목록 조회 실패: {list_body}"
        )

        lecture_pages = list_body["lecture_pages"]

        # 생성한 퀴즈 자료와 연결된 수업자료를 목록에서 찾는다.
        created_page = next(
            (
                page
                for page in lecture_pages
                if page["material_id"] == created_material_quiz_id
            ),
            None,
        )

        # 생성한 퀴즈 자료가 실제 수업자료 목록에 추가되었는지 검증
        assert created_page is not None, (
            f"생성된 퀴즈 수업자료를 목록에서 찾을 수 없습니다: "
            f"material_quiz_id={created_material_quiz_id}, "
            f"lecture_pages={lecture_pages}"
        )

        # 삭제 원복에 사용할 수업자료 ID 저장
        target_lecture_page_id = created_page["id"]

    finally:
        # 생성된 퀴즈 수업자료가 남아 있지 않도록 삭제 처리
        if target_lecture_page_id is not None:
            rollback_response = rest_teacher_client.request(
                "POST",
                f"/org/{common_data.org_teacher}/lecture_page/delete/bulk/",
                data={
                    "lecture_page_ids": target_lecture_page_id,
                },
            )

            rollback_body = rollback_response.json()

            # 퀴즈 수업자료 삭제 HTTP 응답 성공 여부 검증
            assert rollback_response.status_code == 200, (
                f"퀴즈 수업자료 삭제 HTTP 응답 실패: "
                f"status_code={rollback_response.status_code}, "
                f"body={rollback_body}"
            )

            # 퀴즈 수업자료 삭제 비즈니스 로직 성공 여부 검증
            assert rollback_body["_result"]["status"] == "ok", (
                f"퀴즈 수업자료 삭제 실패: {rollback_body}"
            )

@pytest.mark.p0
def test_teacher_can_edit_material_pdf(rest_teacher_client):
    # 우선순위 : P0
    # TC ID: TC-TEACHER_COURSE-014
    # PDF 학습자료 메타데이터 수정 및 원복 API 테스트.

    # Given
    # 기존 PDF 학습자료 정보 조회
    get_response = rest_teacher_client.get(
        f"/org/{common_data.org_teacher}/material_pdf/get/",
        params={
            "material_pdf_id": teacher_course_case["pdf_material_id"],
        },
    )

    get_body = get_response.json()

    # PDF 학습자료 조회 HTTP 응답 성공 여부 검증
    assert get_response.status_code == 200, (
        f"PDF 학습자료 조회 HTTP 응답 실패: "
        f"status_code={get_response.status_code}, body={get_body}"
    )

    # PDF 학습자료 조회 비즈니스 로직 성공 여부 검증
    assert get_body["_result"]["status"] == "ok", (
        f"PDF 학습자료 조회 실패: {get_body}"
    )

    material_pdf = get_body["material_pdf"]

    # 기존 PDF 학습자료 제목/설명 저장
    original_title = material_pdf["title"]
    original_description = material_pdf["description"]

    # 기존 수업자료 공개/통계 상태 조회
    lecture_page_response = rest_teacher_client.get(
        f"/org/{common_data.org_teacher}/lecture_page/get/",
        params={
            "lecture_page_id": teacher_course_case[
                "pdf_lecture_page_id"
            ],
        },
    )

    lecture_page_body = lecture_page_response.json()

    # 수업자료 조회 HTTP 응답 성공 여부 검증
    assert lecture_page_response.status_code == 200, (
        f"PDF 수업자료 조회 HTTP 응답 실패: "
        f"status_code={lecture_page_response.status_code}, "
        f"body={lecture_page_body}"
    )

    # 수업자료 조회 비즈니스 로직 성공 여부 검증
    assert lecture_page_body["_result"]["status"] == "ok", (
        f"PDF 수업자료 조회 실패: {lecture_page_body}"
    )

    lecture_page = lecture_page_body["lecture_page"]

    # PDF 수정 API 필수값이므로 기존 값을 그대로 사용
    original_is_opened = lecture_page["is_opened"]
    original_is_for_stats = lecture_page["is_for_stats"]

    # 수정 검증용 PDF 학습자료 값
    edited_title = "API_PDF_EDIT_TEST"
    edited_description = "API_PDF_EDIT_TEST"

    try:
        # When
        # PDF 학습자료 제목/설명 수정 API 호출
        response = rest_teacher_client.request(
            "POST",
            f"/org/{common_data.org_teacher}/material_pdf/edit/",
            data={
                "lecture_page_id": teacher_course_case[
                    "pdf_lecture_page_id"
                ],
                "lecture_id": teacher_course_case["pdf_lecture_id"],
                "material_pdf_id": teacher_course_case[
                    "pdf_material_id"
                ],
                "id": teacher_course_case["pdf_material_id"],
                "title": edited_title,
                "description": edited_description,
                "is_opened": str(original_is_opened).lower(),
                "is_for_stats": str(original_is_for_stats).lower(),
                "locator_types": 0,
            },
        )

        body = response.json()

        # Then
        # PDF 학습자료 수정 HTTP 응답 성공 여부 검증
        assert response.status_code == 200, (
            f"PDF 학습자료 수정 HTTP 응답 실패: "
            f"status_code={response.status_code}, body={body}"
        )

        # PDF 학습자료 수정 비즈니스 로직 성공 여부 검증
        assert body["_result"]["status"] == "ok", (
            f"PDF 학습자료 수정 실패: {body}"
        )

        # 수정된 PDF 학습자료 ID 반환 여부 검증
        assert body["material_pdf_id"], (
            f"수정된 material_pdf_id 반환 실패: {body}"
        )

        # 수정 결과 확인을 위한 PDF 학습자료 재조회
        edited_get_response = rest_teacher_client.get(
            f"/org/{common_data.org_teacher}/material_pdf/get/",
            params={
                "material_pdf_id": teacher_course_case["pdf_material_id"],
            },
        )

        edited_get_body = edited_get_response.json()

        # PDF 학습자료 재조회 HTTP 응답 성공 여부 검증
        assert edited_get_response.status_code == 200, (
            f"PDF 학습자료 수정 후 조회 HTTP 응답 실패: "
            f"status_code={edited_get_response.status_code}, "
            f"body={edited_get_body}"
        )

        # PDF 학습자료 재조회 비즈니스 로직 성공 여부 검증
        assert edited_get_body["_result"]["status"] == "ok", (
            f"PDF 학습자료 수정 후 조회 실패: {edited_get_body}"
        )

        edited_material_pdf = edited_get_body["material_pdf"]

        # PDF 학습자료 제목 수정 반영 여부 검증
        assert edited_material_pdf["title"] == edited_title, (
            f"PDF 학습자료 제목 수정 결과가 반영되지 않았습니다: "
            f"expected={edited_title}, "
            f"actual={edited_material_pdf['title']}"
        )

        # PDF 학습자료 설명 수정 반영 여부 검증
        assert edited_material_pdf["description"] == edited_description, (
            f"PDF 학습자료 설명 수정 결과가 반영되지 않았습니다: "
            f"expected={edited_description}, "
            f"actual={edited_material_pdf['description']}"
        )

    finally:
        # 기존 PDF 학습자료 제목/설명으로 원복
        rollback_response = rest_teacher_client.request(
            "POST",
            f"/org/{common_data.org_teacher}/material_pdf/edit/",
            data={
                "lecture_page_id": teacher_course_case[
                    "pdf_lecture_page_id"
                ],
                "lecture_id": teacher_course_case["pdf_lecture_id"],
                "material_pdf_id": teacher_course_case[
                    "pdf_material_id"
                ],
                "id": teacher_course_case["pdf_material_id"],
                "title": original_title,
                "description": original_description,
                "is_opened": str(original_is_opened).lower(),
                "is_for_stats": str(original_is_for_stats).lower(),
                "locator_types": 0,
            },
        )

        rollback_body = rollback_response.json()

        # PDF 학습자료 원복 HTTP 응답 성공 여부 검증
        assert rollback_response.status_code == 200, (
            f"PDF 학습자료 원복 HTTP 응답 실패: "
            f"status_code={rollback_response.status_code}, "
            f"body={rollback_body}"
        )

        # PDF 학습자료 원복 비즈니스 로직 성공 여부 검증
        assert rollback_body["_result"]["status"] == "ok", (
            f"PDF 학습자료 원복 실패: {rollback_body}"
        )

@pytest.mark.p1
def test_teacher_can_delete_lecture_page(rest_teacher_client):
    # 우선순위 : P0
    # TC ID: TC-TEACHER_COURSE-005
    # 수업자료 삭제 API 테스트.

    # Given
    # 삭제 검증용 퀴즈 수업자료 생성 payload
    create_payload = {
        "lecture_id": teacher_course_case["lecture_id"],
        "lecture_page_id": "undefined",
        "id": "undefined",
        "title": "API_DELETE_TEST",
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

    # 삭제할 테스트 수업자료 생성을 위한 퀴즈 생성 API 호출
    create_response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/material_quiz/edit/",
        data=create_payload,
    )

    create_body = create_response.json()

    # 삭제 검증용 수업자료 생성 HTTP 응답 성공 여부 검증
    assert create_response.status_code == 200, (
        f"삭제 검증용 수업자료 생성 HTTP 응답 실패: "
        f"status_code={create_response.status_code}, body={create_body}"
    )

    # 삭제 검증용 수업자료 생성 비즈니스 로직 성공 여부 검증
    assert create_body["_result"]["status"] == "ok", (
        f"삭제 검증용 수업자료 생성 실패: {create_body}"
    )

    # 생성된 퀴즈 수업자료 ID 반환 여부 검증
    assert create_body["material_quiz_id"], (
        f"삭제 검증용 수업자료 ID 반환 실패: {create_body}"
    )

    # 생성 API 응답에서 반환된 퀴즈 자료 ID 저장
    created_material_quiz_id = create_body["material_quiz_id"]

    # 삭제 API에 사용할 수업자료 ID 초기화
    target_lecture_page_id = None

    try:
        # 생성된 퀴즈 자료가 연결된 수업자료 ID 확인을 위한 목록 조회
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

        # 생성한 퀴즈 자료와 연결된 수업자료를 목록에서 찾는다.
        created_page = next(
            (
                page
                for page in lecture_pages
                if page["material_id"] == created_material_quiz_id
            ),
            None,
        )

        # 생성한 퀴즈 자료가 실제 수업자료 목록에 추가되었는지 검증
        assert created_page is not None, (
            f"생성된 삭제 검증용 수업자료를 목록에서 찾을 수 없습니다: "
            f"material_quiz_id={created_material_quiz_id}, "
            f"lecture_pages={lecture_pages}"
        )

        # 삭제 API 요청에 사용할 수업자료 ID 저장
        target_lecture_page_id = created_page["id"]

        # When
        # 생성한 수업자료 삭제 API 호출
        response = rest_teacher_client.request(
            "POST",
            f"/org/{common_data.org_teacher}/lecture_page/delete/bulk/",
            data={
                "lecture_page_ids": target_lecture_page_id,
            },
        )

        body = response.json()

        # Then
        # 수업자료 삭제 HTTP 응답 성공 여부 검증
        assert response.status_code == 200, (
            f"수업자료 삭제 HTTP 응답 실패: "
            f"status_code={response.status_code}, body={body}"
        )

        # 수업자료 삭제 비즈니스 로직 성공 여부 검증
        assert body["_result"]["status"] == "ok", (
            f"수업자료 삭제 실패: {body}"
        )

        # 삭제 결과 확인을 위한 수업자료 목록 재조회
        deleted_check_response = rest_teacher_client.get(
            f"/org/{common_data.org_teacher}/lecture_page/list/",
            params={
                "lecture_id": teacher_course_case["lecture_id"],
                "locator_type": 0,
                "offset": 0,
                "count": 50,
            },
        )

        deleted_check_body = deleted_check_response.json()

        # 삭제 후 수업자료 목록 조회 HTTP 응답 성공 여부 검증
        assert deleted_check_response.status_code == 200, (
            f"수업자료 삭제 후 목록 조회 HTTP 응답 실패: "
            f"status_code={deleted_check_response.status_code}, "
            f"body={deleted_check_body}"
        )

        # 삭제 후 수업자료 목록 조회 비즈니스 로직 성공 여부 검증
        assert deleted_check_body["_result"]["status"] == "ok", (
            f"수업자료 삭제 후 목록 조회 실패: {deleted_check_body}"
        )

        deleted_check_pages = deleted_check_body["lecture_pages"]

        # 삭제한 수업자료가 목록에서 사라졌는지 검증
        assert all(
            page["id"] != target_lecture_page_id
            for page in deleted_check_pages
        ), (
            f"삭제한 수업자료가 목록에 남아 있습니다: "
            f"lecture_page_id={target_lecture_page_id}, "
            f"lecture_pages={deleted_check_pages}"
        )

    finally:
        # 테스트 중간 실패로 수업자료가 남아 있을 경우를 대비한 정리 작업
        if target_lecture_page_id is not None:
            rest_teacher_client.request(
                "POST",
                f"/org/{common_data.org_teacher}/lecture_page/delete/bulk/",
                data={
                    "lecture_page_ids": target_lecture_page_id,
                },
            )





@pytest.mark.p1
def test_teacher_can_clone_lecture(rest_teacher_client):
    # 우선순위 : P1
    # TC ID: TC-TEACHER_COURSE-007
    # 수업 복제 API 테스트.

    # Given
    # 수업 복제 payload
    payload = {
        "lecture_id": teacher_course_case["lecture_id"],
        "target_course_id": teacher_course_case["course_id"],
    }

    cloned_lecture_id = None

    try:
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

        # 원복을 위해 복제된 수업 ID 저장
        cloned_lecture_id = body["lecture_id"]

    finally:
        # 복제된 수업이 남아 있지 않도록 삭제 처리
        if cloned_lecture_id is not None:
            rollback_response = rest_teacher_client.request(
                "POST",
                f"/org/{common_data.org_teacher}/lecture/delete/",
                data={
                    "lecture_id": cloned_lecture_id,
                },
            )

            rollback_body = rollback_response.json()

            # 복제 수업 삭제 HTTP 응답 성공 여부 검증
            assert rollback_response.status_code == 200, (
                f"복제 수업 삭제 HTTP 응답 실패: "
                f"status_code={rollback_response.status_code}, "
                f"body={rollback_body}"
            )

            # 복제 수업 삭제 비즈니스 로직 성공 여부 검증
            assert rollback_body["_result"]["status"] == "ok", (
                f"복제 수업 삭제 실패: {rollback_body}"
            )

@pytest.mark.p1
def test_teacher_can_move_lecture_page(rest_teacher_client):
    # 우선순위 : P1
    # TC ID: TC-TEACHER_COURSE-004
    # 수업자료 순서 변경 API 테스트.

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

    # 순서 변경은 최소 2개 이상의 수업자료가 있어야 가능
    if len(lecture_pages) < 2:
        pytest.skip("순서 변경 테스트를 위해 수업자료가 2개 이상 필요합니다.")

    # 목록의 첫 번째 수업자료를 테스트 대상으로 선택
    target_lecture_page_id = lecture_pages[0]["id"]

    original_order_no = 1
    new_order_no = 2

    try:
        # When
        # 첫 번째 수업자료를 두 번째로 이동
        response = rest_teacher_client.request(
            "POST",
            f"/org/{common_data.org_teacher}/lecture_page/move/",
            data={
                "lecture_page_id": target_lecture_page_id,
                "locator_type": 0,
                "new_order_no": new_order_no,
            },
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

        # 순서 변경 결과 확인을 위한 수업자료 목록 재조회
        moved_list_response = rest_teacher_client.get(
            f"/org/{common_data.org_teacher}/lecture_page/list/",
            params={
                "lecture_id": teacher_course_case["lecture_id"],
                "locator_type": 0,
                "offset": 0,
                "count": 50,
            },
        )

        moved_list_body = moved_list_response.json()

        assert moved_list_response.status_code == 200, (
            f"수업자료 순서 변경 후 목록 조회 HTTP 응답 실패: "
            f"status_code={moved_list_response.status_code}, "
            f"body={moved_list_body}"
        )

        assert moved_list_body["_result"]["status"] == "ok", (
            f"수업자료 순서 변경 후 목록 조회 실패: {moved_list_body}"
        )

        moved_lecture_pages = moved_list_body["lecture_pages"]

        assert moved_lecture_pages[new_order_no - 1]["id"] == target_lecture_page_id, (
            f"수업자료 순서 변경 결과가 반영되지 않았습니다: "
            f"expected_order_no={new_order_no}, "
            f"lecture_page_id={target_lecture_page_id}, "
            f"lecture_pages={moved_lecture_pages}"
        )

    finally:
        # 원래 순서인 첫 번째로 원복
        rollback_response = rest_teacher_client.request(
            "POST",
            f"/org/{common_data.org_teacher}/lecture_page/move/",
            data={
                "lecture_page_id": target_lecture_page_id,
                "locator_type": 0,
                "new_order_no": original_order_no,
            },
        )

        rollback_body = rollback_response.json()

        assert rollback_response.status_code == 200, (
            f"수업자료 순서 원복 HTTP 응답 실패: "
            f"status_code={rollback_response.status_code}, "
            f"body={rollback_body}"
        )

        assert rollback_body["_result"]["status"] == "ok", (
            f"수업자료 순서 원복 실패: {rollback_body}"
        )

@pytest.mark.p1
def test_teacher_can_reset_material_quiz_response(rest_teacher_client):
    # 우선순위 : P1
    # TC ID: TC-TEACHER_COURSE-010
    # 퀴즈 제출 기록 초기화 API 테스트.

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

@pytest.mark.p1
def test_teacher_can_add_course_to_classroom(
    teacher_client,
    rest_teacher_client,
):
    # 우선순위 : P1
    # TC ID: TC-TEACHER_COURSE-013
    # 클래스룸 과목 추가 API 테스트.

    # Given
    # 클래스룸 과목 추가 payload
    payload = {
        "original_course_ids": [
            teacher_course_case["add_course_id"]
        ],
    }

    created_course_id = None

    try:
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

        task_id = body["task_id"]

        # 비동기 작업 상태 확인
        task_body = None

        for _ in range(10):
            task_response = rest_teacher_client.get(
                "/global/task/get/",
                params={
                    "task_id": task_id,
                },
            )

            task_body = task_response.json()

            # 작업 상태 조회 HTTP 응답 성공 여부 검증
            assert task_response.status_code == 200, (
                f"과목 추가 작업 상태 조회 HTTP 응답 실패: "
                f"status_code={task_response.status_code}, "
                f"body={task_body}"
            )

            # 작업 상태 조회 비즈니스 로직 성공 여부 검증
            assert task_body["_result"]["status"] == "ok", (
                f"과목 추가 작업 상태 조회 실패: {task_body}"
            )

            # 작업이 완료되면 진행 상태 목록에서 생성된 과목 ID 확인
            progress_response = teacher_client.get(
                f"/v2/classroom/{common_data.teacher_classroom_id}/course/progress",
                params={
                    "skip": 0,
                    "count": 40,
                },
            )

            progress_body = progress_response.json()

            assert progress_response.status_code == 200, (
                f"과목 추가 진행 상태 목록 조회 HTTP 응답 실패: "
                f"status_code={progress_response.status_code}, "
                f"body={progress_body}"
            )

            if progress_body:
                created_course_id = progress_body[0]["course_id"]
                break

        # 생성된 과목 ID 반환 여부 검증
        assert created_course_id is not None, (
            f"추가된 과목 course_id를 찾을 수 없습니다: "
            f"task_id={task_id}, "
            f"task_body={task_body}"
        )

    finally:
        # 테스트로 추가된 과목이 남아 있지 않도록 삭제 처리
        if created_course_id is not None:
            rollback_response = teacher_client.request(
                "DELETE",
                f"/classroom/{common_data.teacher_classroom_id}/course/{created_course_id}",
            )

            rollback_body = (
                rollback_response.json()
                if rollback_response.text
                else {}
            )

            # 추가된 과목 삭제 HTTP 응답 성공 여부 검증
            assert rollback_response.status_code == 200, (
                f"추가된 클래스룸 과목 삭제 HTTP 응답 실패: "
                f"status_code={rollback_response.status_code}, "
                f"body={rollback_body}"
            )

@pytest.mark.p1
def test_teacher_can_reorder_course(teacher_client):
    # 우선순위 : P1
    # TC ID: TC-TEACHER_COURSE-012
    # 클래스룸 과목 순서 변경 API 테스트.

    reorder_success = False
    changed_result_course_ids = []

    for _ in range(20):
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

        # 순서 변경 테스트를 위해 과목이 4개 이상인지 검증
        if len(list_body) < 4:
            pytest.skip("과목 순서 변경 테스트를 위해 과목이 4개 이상 필요합니다.")

        # 현재 순서 기준 course_id 추출
        original_course_ids = [
            course["course_id"]
            for course in list_body
        ]

        # 원본 순서를 복사하여 변경할 순서 생성
        changed_course_ids = original_course_ids.copy()

        # 3번째, 4번째 과목 순서 변경
        first_target_course_id = changed_course_ids[2]
        second_target_course_id = changed_course_ids[3]

        changed_course_ids[2], changed_course_ids[3] = (
            changed_course_ids[3],
            changed_course_ids[2],
        )

        # When
        # 과목 순서 변경 API 호출
        response = teacher_client.request(
            "POST",
            f"/classroom/{common_data.teacher_classroom_id}/course/reorder",
            json={
                "course_ids": changed_course_ids,
            },
        )

        body = response.json()

        # 병렬 실행 중 과목 구성이 변경된 경우 현재 목록 기준으로 재시도
        if response.status_code == 409:
            continue

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

        # 순서 변경 결과 확인을 위한 과목 목록 재조회
        changed_list_response = teacher_client.get(
            f"/classroom/{common_data.teacher_classroom_id}/course",
            params={
                "skip": 0,
                "count": 100,
            },
        )

        changed_list_body = changed_list_response.json()

        # 순서 변경 후 과목 목록 조회 HTTP 응답 성공 여부 검증
        assert changed_list_response.status_code == 200, (
            f"과목 순서 변경 후 목록 조회 HTTP 응답 실패: "
            f"status_code={changed_list_response.status_code}, "
            f"body={changed_list_body}"
        )

        # 변경된 순서가 목록에 반영되었는지 검증
        changed_result_course_ids = [
            course["course_id"]
            for course in changed_list_body
        ]

        assert first_target_course_id in changed_result_course_ids, (
            f"순서 변경 대상 과목이 목록에 없습니다: "
            f"course_id={first_target_course_id}, "
            f"actual={changed_result_course_ids}"
        )

        assert second_target_course_id in changed_result_course_ids, (
            f"순서 변경 대상 과목이 목록에 없습니다: "
            f"course_id={second_target_course_id}, "
            f"actual={changed_result_course_ids}"
        )

        first_target_index = changed_result_course_ids.index(first_target_course_id)
        second_target_index = changed_result_course_ids.index(second_target_course_id)

        assert second_target_index < first_target_index, (
            f"과목 순서 변경 결과가 반영되지 않았습니다. "
            f"expected_order={[second_target_course_id, first_target_course_id]}, "
            f"actual={changed_result_course_ids}"
        )

        reorder_success = True
        break

    assert reorder_success is True, (
        f"과목 순서 변경 실패: "
        f"expected={changed_course_ids}, "
        f"actual={changed_result_course_ids}"
    )

    rollback_success = False

    for _ in range(20):
        # 원래 과목 순서로 복원하기 전 현재 과목 목록 재조회
        rollback_list_response = teacher_client.get(
            f"/classroom/{common_data.teacher_classroom_id}/course",
            params={
                "skip": 0,
                "count": 100,
            },
        )

        rollback_list_body = rollback_list_response.json()

        # 원복 전 과목 목록 조회 HTTP 응답 성공 여부 검증
        assert rollback_list_response.status_code == 200, (
            f"과목 순서 원복 전 목록 조회 HTTP 응답 실패: "
            f"status_code={rollback_list_response.status_code}, "
            f"body={rollback_list_body}"
        )

        current_course_ids = [
            course["course_id"]
            for course in rollback_list_body
        ]

        rollback_course_ids = []

        # 기존 과목은 원래 순서대로 원복
        for course_id in original_course_ids:
            if course_id in current_course_ids:
                rollback_course_ids.append(course_id)

        # 병렬 실행 중 추가된 과목은 목록에서 제거하지 않고 뒤에 유지
        for course_id in current_course_ids:
            if course_id not in original_course_ids:
                rollback_course_ids.append(course_id)

        # 원래 과목 순서로 복원
        rollback_response = teacher_client.request(
            "POST",
            f"/classroom/{common_data.teacher_classroom_id}/course/reorder",
            json={
                "course_ids": rollback_course_ids,
            },
        )

        rollback_body = rollback_response.json()

        if rollback_response.status_code == 409:
            continue

        # 과목 순서 원복 HTTP 응답 성공 여부 검증
        assert rollback_response.status_code == 200, (
            f"과목 순서 원복 HTTP 응답 실패: "
            f"status_code={rollback_response.status_code}, "
            f"body={rollback_body}"
        )

        rollback_success = True
        break

    assert rollback_success is True, (
        f"과목 순서 원복 실패: "
        f"expected={original_course_ids}, "
        f"rollback_course_ids={rollback_course_ids}"
    )

    # 과목 순서 원복 응답 body 검증
    assert rollback_body == {}, (
        f"과목 순서 원복 응답 body가 예상 결과와 다름: {rollback_body}"
    )


### Negative Test

@pytest.mark.p1
def test_teacher_cannot_create_lecture_without_course_id(rest_teacher_client):
    # 우선순위 : P2
    # TC ID: TC-TEACHER_COURSE-015
    # course_id 누락 시 수업 생성 실패 응답 확인 API 테스트.

    # Given
    # course_id 누락 상태의 수업 생성 payload
    payload = {
        "title": "API_CREATE_TEST",
        "description": "API_CREATE_TEST",
        "lecture_type": 0,
        "teaching_datetime": 1779894000000,
        "is_opened": "false",
        "is_preview": "false",
    }

    # When
    # course_id 없이 수업 생성 API 호출
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture/edit/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 여부 검증
    assert response.status_code == 200, (
        f"course_id 누락 수업 생성 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 실패 여부 검증
    assert body["_result"]["status"] == "fail", (
        f"course_id 누락 요청이 실패하지 않음: {body}"
    )

@pytest.mark.p1
def test_teacher_cannot_create_lecture_with_invalid_course_id(rest_teacher_client):
    # 우선순위 : P2
    # TC ID: TC-TEACHER_COURSE-016
    # 존재하지 않는 course_id 입력 시 수업 생성 실패 응답 확인 API 테스트.

    # Given
    # 존재하지 않는 course_id 수업 생성 payload
    payload = {
        "course_id": 999999999,
        "title": "API_CREATE_TEST",
        "description": "API_CREATE_TEST",
        "lecture_type": 0,
        "teaching_datetime": 1779894000000,
        "is_opened": "false",
        "is_preview": "false",
    }

    # When
    # 잘못된 course_id로 수업 생성 API 호출
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture/edit/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 여부 검증
    assert response.status_code == 200, (
        f"잘못된 course_id 수업 생성 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 실패 여부 검증
    assert body["_result"]["status"] == "fail", (
        f"잘못된 course_id 요청이 실패하지 않음: {body}"
    )

@pytest.mark.p1
def test_teacher_cannot_change_lecture_page_visibility_without_lecture_page_ids(
    rest_teacher_client,
):
    # 우선순위 : P2
    # TC ID: TC-TEACHER_COURSE-017
    # lecture_page_ids 누락 시 공개 상태 변경 실패 응답 확인 API 테스트.

    # Given
    # lecture_page_ids 누락 공개 상태 변경 payload
    payload = {
        "is_opened": "true",
    }

    # When
    # lecture_page_ids 없이 공개 상태 변경 API 호출
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture_page/visibility/edit/bulk/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 여부 검증
    assert response.status_code == 200, (
        f"lecture_page_ids 누락 공개 상태 변경 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 실패 여부 검증
    assert body["_result"]["status"] == "fail", (
        f"lecture_page_ids 누락 요청이 실패하지 않음: {body}"
    )

@pytest.mark.p1
def test_teacher_cannot_move_lecture_page_without_new_order_no(rest_teacher_client):
    # 우선순위 : P2
    # TC ID: TC-TEACHER_COURSE-018
    # new_order_no 누락 시 수업자료 순서 변경 실패 응답 확인 API 테스트.

    # Given
    # new_order_no 누락 수업자료 순서 변경 payload
    payload = {
        "lecture_page_id": teacher_course_case[
            "lecture_page_id"
        ],
        "locator_type": 0,
    }

    # When
    # new_order_no 없이 수업자료 순서 변경 API 호출
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture_page/move/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 여부 검증
    assert response.status_code == 200, (
        f"new_order_no 누락 수업자료 순서 변경 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 실패 여부 검증
    assert body["_result"]["status"] == "fail", (
        f"new_order_no 누락 요청이 실패하지 않음: {body}"
    )

@pytest.mark.p1
def test_teacher_cannot_create_material_quiz_without_options_default(rest_teacher_client):
    # 우선순위 : P2
    # TC ID: TC-TEACHER_COURSE-019
    # options_default 누락 시 퀴즈 생성 실패 응답 확인 API 테스트.

    # Given
    # options_default 누락 퀴즈 학습자료 생성 payload
    payload = {
        "lecture_id": teacher_course_case["lecture_id"],
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
        "answer_info_default": "[0]",
        "answer_info": "[0]",
        "is_auto_grade": "true",
        "explanation_info": '{"is_enabled":false,"value":""}',
        "options_set_enabled": "false",
    }

    # When
    # options_default 없이 퀴즈 생성 API 호출
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/material_quiz/edit/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 여부 검증
    assert response.status_code == 200, (
        f"options_default 누락 퀴즈 생성 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 실패 여부 검증
    assert body["_result"]["status"] == "fail", (
        f"options_default 누락 요청이 실패하지 않음: {body}"
    )

@pytest.mark.p1
def test_teacher_cannot_add_invalid_course_to_classroom(teacher_client):
    # 우선순위 : P2
    # TC ID: TC-TEACHER_COURSE-020
    # 존재하지 않는 original_course_ids로 과목 추가 시 목록에 반영되지 않음 확인 API 테스트.

    invalid_original_course_id = 999999999

    payload = {
        "original_course_ids": [
            invalid_original_course_id,
        ],
    }

    # When
    # 존재하지 않는 course_id로 클래스룸 과목 추가 API 호출
    response = teacher_client.request(
        "POST",
        f"/v2/classroom/{common_data.teacher_classroom_id}/course/bulk",
        json=payload,
    )

    body = response.json()

    # 과목 추가 요청 HTTP 응답 여부 검증
    assert response.status_code == 200, (
        f"잘못된 course_id 과목 추가 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # Then
    # 클래스룸 과목 목록 재조회
    after_response = teacher_client.get(
        f"/classroom/{common_data.teacher_classroom_id}/course",
        params={
            "skip": 0,
            "count": 100,
        },
    )

    after_body = after_response.json()

    # 과목 목록 재조회 HTTP 응답 성공 여부 검증
    assert after_response.status_code == 200, (
        f"과목 목록 재조회 HTTP 응답 실패: "
        f"status_code={after_response.status_code}, body={after_body}"
    )

    invalid_added_courses = []

    # 잘못된 original_course_id가 목록에 반영되지 않았는지 확인
    for course in after_body:
        if course.get("original_course_id") == invalid_original_course_id:
            invalid_added_courses.append(course)

    assert invalid_added_courses == [], (
        f"잘못된 original_course_id 과목이 목록에 추가됨: "
        f"invalid_original_course_id={invalid_original_course_id}, "
        f"courses={invalid_added_courses}"
    )

@pytest.mark.p1
def test_teacher_cannot_clone_lecture_with_invalid_lecture_id(rest_teacher_client):
    # 우선순위 : P2
    # TC ID: TC-TEACHER_COURSE-021
    # 존재하지 않는 lecture_id 입력 시 수업 복제 실패 응답 확인 API 테스트.

    # Given
    # 존재하지 않는 lecture_id 수업 복제 payload
    payload = {
        "lecture_id": 999999999,
        "target_course_id": teacher_course_case[
            "course_id"
        ],
    }

    # When
    # 잘못된 lecture_id로 수업 복제 API 호출
    response = rest_teacher_client.request(
        "POST",
        f"/org/{common_data.org_teacher}/lecture/clone/",
        data=payload,
    )

    body = response.json()

    # Then
    # HTTP 응답 여부 검증
    assert response.status_code == 200, (
        f"잘못된 lecture_id 수업 복제 HTTP 응답 실패: "
        f"status_code={response.status_code}, body={body}"
    )

    # 실제 API 비즈니스 로직 실패 여부 검증
    assert body["_result"]["status"] == "fail", (
        f"잘못된 lecture_id 요청이 실패하지 않음: {body}"
    )
