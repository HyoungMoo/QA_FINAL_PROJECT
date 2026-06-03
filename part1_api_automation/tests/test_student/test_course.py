import pytest

from utils.api_client import APIClient
from utils.test_data import common_data
from utils.test_data.student_material_data import lecture_case

pytestmark = pytest.mark.student


### Positive Test


@pytest.mark.p0
def test_get_week1_2lecture_material_pdf(rest_student_client):
    # 우선순위 : P0
    # TC ID: TC-STUDENT-COURSE-001
    # 1주차 2번 강의자료 PDF 조회 API 테스트.

    # Given
    # 1주차 2번 강의자료 PDF 조회에 필요한 설정값 세팅
    params = {
        "material_pdf_id":
            lecture_case["week1_2lecture_material_id"],
    }

    # When
    # 강의자료 PDF 조회 API 요청
    response = rest_student_client.get(
        f"/org/{common_data.org_student}/material_pdf/get/",
        params=params,
    )

    # Then
    # 강의자료 PDF 조회 성공 여부 확인
    assert response.status_code == 200, (
        f"강의자료 PDF 조회 실패 "
        f"(status_code={response.status_code})"
    )

    data = response.json()

    # API 결과 상태가 ok 검증
    assert data["_result"]["status"] == "ok", (
        f"강의자료 PDF 응답 실패: {data}"
    )

    # 응답 데이터에 material_pdf 정보 포함 검증
    assert "material_pdf" in data, (
        "응답 데이터에 material_pdf 정보가 없습니다."
    )

    material_pdf = data["material_pdf"]

    # material_pdf 내부 핵심 정보 존재 여부 검증
    assert "id" in material_pdf, (
        "material_pdf 데이터에 id 정보가 없습니다."
    )

    assert "attachment" in material_pdf, (
        "material_pdf 데이터에 첨부파일 정보가 없습니다."
    )

    assert "url" in material_pdf["attachment"], (
        "material_pdf 첨부파일 데이터에 url 정보가 없습니다."
    )


@pytest.mark.p0
def test_get_week1_2lecture_quiz_material(rest_student_client):
    # 우선순위 : P0
    # TC ID: TC-STUDENT-COURSE-002
    # 1주차 2번 강의 퀴즈 자료 진입 API 테스트.

    # Given
    # 1주차 2번 강의 퀴즈 자료 조회에 필요한 설정값 세팅
    params = {
        "material_id":
            lecture_case["week1_2lecture_1quiz_material_id"],
        "material_type":
            lecture_case["lecture_quiz_material_type"],
    }

    # When
    # 퀴즈 자료 조회 API 요청
    response = rest_student_client.get(
        f"/org/{common_data.org_student}/lecture_page/resolve/",
        params=params,
    )

    # Then
    # 퀴즈 자료 조회 성공 여부 확인
    assert response.status_code == 200, (
        f"퀴즈 자료 조회 실패 "
        f"(status_code={response.status_code})"
    )

    data = response.json()

    assert data["_result"]["status"] == "ok", (
        f"퀴즈 자료 응답 실패: {data}"
    )

    assert "lecture_page_id" in data, (
        "응답 데이터에 lecture_page_id 정보가 없습니다."
    )


@pytest.mark.p0
def test_submit_week1_2lecture_quiz_correct_answer(rest_student_client):
    # 우선순위 : P0
    # TC ID: TC-STUDENT-COURSE-003
    # 퀴즈 정답 제출 및 채점 결과 조회 API 테스트.

    # Given
    # 1주차 2번 강의 퀴즈 정답 제출에 필요한 설정값 세팅
    submit_files = {
        "material_quiz_id": (
            None,
            lecture_case["week1_2lecture_1quiz_material_id"],
        ),
        "answer": (
            None,
            "[2]",
        ),
    }

    # When
    # 퀴즈 정답 제출 API 요청
    submit_response = rest_student_client.request(
        "POST",
        f"/org/{common_data.org_student}/material_quiz/response/add/",
        files=submit_files,
    )

    # Then
    # 퀴즈 정답 제출 성공 여부 확인
    assert submit_response.status_code == 200, (
        f"퀴즈 정답 제출 실패 "
        f"(status_code={submit_response.status_code})"
    )

    submit_data = submit_response.json()

    assert submit_data["_result"]["status"] == "ok", (
        f"퀴즈 정답 제출 응답 실패: {submit_data}"
    )

    assert "quiz_response_id" in submit_data, (
        "응답 데이터에 quiz_response_id 정보가 없습니다."
    )

    quiz_response_id = submit_data["quiz_response_id"]

    get_params = {
        "quiz_response_id": quiz_response_id,
    }

    # When
    # 퀴즈 정답 제출 결과 조회 API 요청
    get_response = rest_student_client.get(
        f"/org/{common_data.org_student}/material_quiz/response/get/",
        params=get_params,
    )

    # Then
    # 퀴즈 정답 채점 결과 검증
    assert get_response.status_code == 200, (
        f"퀴즈 정답 결과 조회 실패 "
        f"(status_code={get_response.status_code})"
    )

    get_data = get_response.json()

    assert get_data["_result"]["status"] == "ok", (
        f"퀴즈 정답 결과 조회 응답 실패: {get_data}"
    )

    quiz_response = get_data["quiz_response"]

    assert quiz_response["score"] == 100, (
        "정답 처리가 되지 않았습니다."
    )

    assert quiz_response["is_completed"] is True, (
        "정답 제출이 완료 처리되지 않았습니다."
    )


@pytest.mark.p1
def test_submit_week1_2lecture_quiz_wrong_answer(rest_student_client):
    # 우선순위 : P1
    # TC ID: TC-STUDENT-COURSE-004
    # 퀴즈 오답 제출 및 채점 결과 조회 API 테스트.

    # Given
    # 1주차 2번 강의 퀴즈 오답 제출에 필요한 설정값 세팅
    submit_files = {
        "material_quiz_id": (
            None,
            lecture_case["week1_2lecture_1quiz_material_id"],
        ),
        "answer": (
            None,
            "[1]",
        ),
    }

    # When
    # 퀴즈 오답 제출 API 요청
    submit_response = rest_student_client.request(
        "POST",
        f"/org/{common_data.org_student}/material_quiz/response/add/",
        files=submit_files,
    )

    # Then
    # 퀴즈 오답 제출 성공 여부 확인
    assert submit_response.status_code == 200, (
        f"퀴즈 오답 제출 실패 "
        f"(status_code={submit_response.status_code})"
    )

    submit_data = submit_response.json()

    assert submit_data["_result"]["status"] == "ok", (
        f"퀴즈 오답 제출 응답 실패: {submit_data}"
    )

    assert "quiz_response_id" in submit_data, (
        "응답 데이터에 quiz_response_id 정보가 없습니다."
    )

    quiz_response_id = submit_data["quiz_response_id"]

    get_params = {
        "quiz_response_id": quiz_response_id,
    }

    # When
    # 퀴즈 오답 제출 결과 조회 API 요청
    get_response = rest_student_client.get(
        f"/org/{common_data.org_student}/material_quiz/response/get/",
        params=get_params,
    )

    # Then
    # 퀴즈 오답 채점 결과 검증
    assert get_response.status_code == 200, (
        f"퀴즈 오답 결과 조회 실패 "
        f"(status_code={get_response.status_code})"
    )

    get_data = get_response.json()

    assert get_data["_result"]["status"] == "ok", (
        f"퀴즈 오답 결과 조회 응답 실패: {get_data}"
    )

    quiz_response = get_data["quiz_response"]

    assert quiz_response["score"] == 0, (
        "오답 제출 score 값이 예상값과 다릅니다."
    )

    assert quiz_response["is_completed"] is False, (
        "오답 제출이 완료 처리되었습니다."
    )


@pytest.mark.p0
def test_get_week1_2lecture_exercise_material(rest_student_client):
    # 우선순위 : P0
    # TC ID: TC-STUDENT-COURSE-005
    # 1주차 2번 강의 코딩 실습 자료 조회 API 테스트.

    # Given
    # 1주차 2번 강의 코딩 실습 자료 조회에 필요한 설정값 세팅
    params = {
        "material_id":
            lecture_case["week1_2lecture_1exercise_material_id"],
        "material_type":
            lecture_case["lecture_exercise_material_type"],
    }

    # When
    # 코딩 실습 자료 조회 API 요청
    response = rest_student_client.get(
        f"/org/{common_data.org_student}/lecture_page/resolve/",
        params=params,
    )

    # Then
    # 코딩 실습 자료 조회 성공 여부 확인
    assert response.status_code == 200, (
        f"코딩 실습 자료 조회 실패 "
        f"(status_code={response.status_code})"
    )

    data = response.json()

    assert data["_result"]["status"] == "ok", (
        f"코딩 실습 자료 응답 실패: {data}"
    )

    assert "lecture_page_id" in data, (
        "응답 데이터에 lecture_page_id 정보가 없습니다."
    )


@pytest.mark.p0
def test_run_week1_2lecture_exercise(rest_student_client):
    # 우선순위 : P0
    # TC ID: TC-STUDENT-COURSE-006
    # 코딩 실습 실행 화면 진입 API 테스트.

    # Given
    # 기본 실습방 조회
    room_response = rest_student_client.get(
        f"/org/{common_data.org_student}/material_exercise/default_room/get/",
        params={
            "material_exercise_id": lecture_case[
                "week1_2lecture_1exercise_material_id"
            ],
        },
    )

    room_body = room_response.json()

    # 기본 실습방 조회 성공 여부 검증
    assert room_response.status_code == 200, (
        f"기본 실습방 조회 실패 "
        f"(status_code={room_response.status_code}, body={room_body})"
    )

    assert room_body["_result"]["status"] == "ok", (
        f"기본 실습방 조회 응답 실패: {room_body}"
    )

    assert "exercise_room_id" in room_body, (
        f"exercise_room_id가 응답에 없습니다: {room_body}"
    )

    # 코딩 실습 실행 화면 진입 payload
    # 1주차 2번 강의 코딩 실습 실행에 필요한 설정값 세팅
    join_files = {
        "exercise_room_id": (
            None,
            str(room_body["exercise_room_id"]),
        ),
    }

    # When
    # 코딩 실습 실행 화면 진입 API 요청
    join_response = rest_student_client.request(
        "POST",
        f"/org/{common_data.org_student}/runner_room/exercise_room/join/",
        files=join_files,
    )

    join_data = join_response.json()

    # Then
    # 코딩 실습 실행 화면 진입 성공 여부 확인
    assert join_response.status_code == 200, (
        f"코딩 실습 실행 화면 진입 실패 "
        f"(status_code={join_response.status_code}, body={join_data})"
    )

    assert join_data["_result"]["status"] == "ok", (
        f"코딩 실습 실행 화면 진입 응답 실패: {join_data}"
    )

    assert "room_token" in join_data, (
        "코딩 실습 실행에 필요한 인증 정보가 반환되지 않았습니다."
    )

    assert "exercise_image_id" in join_data, (
        "코딩 실습 실행 환경 정보가 정상적으로 반환되지 않았습니다."
    )


@pytest.mark.p0
def test_submit_available_exercise(rest_student_client):
    # 우선순위 : P0
    # TC ID: TC-STUDENT-COURSE-007
    # 제출 가능한 코딩 실습 화면 진입 API 테스트.

    # Given
    # 기본 실습방 조회
    room_response = rest_student_client.get(
        f"/org/{common_data.org_student}/material_exercise/default_room/get/",
        params={
            "material_exercise_id": lecture_case[
                "submit_exercise_material_id"
            ],
        },
    )

    room_body = room_response.json()

    # 기본 실습방 조회 성공 여부 검증
    assert room_response.status_code == 200, (
        f"기본 실습방 조회 실패 "
        f"(status_code={room_response.status_code}, body={room_body})"
    )

    assert room_body["_result"]["status"] == "ok", (
        f"기본 실습방 조회 응답 실패: {room_body}"
    )

    assert "exercise_room_id" in room_body, (
        f"exercise_room_id가 응답에 없습니다: {room_body}"
    )

    # 코딩 실습 제출 화면 진입 payload
    # 제출 가능한 코딩 실습 제출에 필요한 설정값 세팅
    join_files = {
        "exercise_room_id": (
            None,
            str(room_body["exercise_room_id"]),
        ),
    }

    # When
    # 코딩 실습 제출 화면 진입 API 요청
    join_response = rest_student_client.request(
        "POST",
        f"/org/{common_data.org_student}/runner_room/exercise_room/join/",
        files=join_files,
    )

    join_data = join_response.json()

    # Then
    # 코딩 실습 제출 화면 진입 성공 여부 확인
    assert join_response.status_code == 200, (
        f"코딩 실습 제출 화면 진입 실패 "
        f"(status_code={join_response.status_code}, body={join_data})"
    )

    assert join_data["_result"]["status"] == "ok", (
        f"코딩 실습 제출 화면 진입 응답 실패: {join_data}"
    )

    assert "room_token" in join_data, (
        "코딩 실습 제출에 필요한 인증 정보가 반환되지 않았습니다."
    )

    assert "exercise_image_id" in join_data, (
        "코딩 실습 제출 환경 정보가 정상적으로 반환되지 않았습니다."
    )


@pytest.mark.p1
def test_move_next_lesson_from_material_pdf(rest_student_client):
    # 우선순위 : P1
    # TC ID: TC-STUDENT-COURSE-008
    # 강의자료 화면에서 다음 수업 이동 API 테스트.

    # Given
    # 강의자료에서 다음 수업 이동에 필요한 설정값 세팅
    params = {
        "material_id":
            lecture_case["week1_2lecture_1quiz_material_id"],
        "material_type":
            lecture_case["lecture_quiz_material_type"],
    }

    # When
    # 강의자료에서 다음 수업 이동 API 요청
    response = rest_student_client.get(
        f"/org/{common_data.org_student}/lecture_page/resolve/",
        params=params,
    )

    # Then
    # 다음 학습 항목 이동 성공 여부 확인
    assert response.status_code == 200, (
        f"다음 수업 이동 실패 "
        f"(status_code={response.status_code})"
    )

    data = response.json()

    assert data["_result"]["status"] == "ok", (
        f"다음 수업 이동 응답 실패: {data}"
    )

    assert "lecture_page_id" in data, (
        "다음 학습 항목 정보가 응답 데이터에 없습니다."
    )


@pytest.mark.p1
def test_move_previous_lesson_from_quiz(rest_student_client):
    # 우선순위 : P1
    # TC ID: TC-STUDENT-COURSE-009
    # 강의자료 화면에서 이전 수업 이동 API 테스트.

    # Given
    # 퀴즈 화면에서 이전 수업 이동에 필요한 설정값 세팅
    params = {
        "material_id":
            lecture_case["week1_2lecture_material_id"],
        "material_type":
            lecture_case["lecture_material_type"],
    }

    # When
    # 퀴즈 화면에서 이전 수업 이동 API 요청
    response = rest_student_client.get(
        f"/org/{common_data.org_student}/lecture_page/resolve/",
        params=params,
    )

    # Then
    # 이전 학습 항목 이동 성공 여부 확인
    assert response.status_code == 200, (
        f"이전 수업 이동 실패 "
        f"(status_code={response.status_code})"
    )

    data = response.json()

    assert data["_result"]["status"] == "ok", (
        f"이전 수업 이동 응답 실패: {data}"
    )

    assert "lecture_page_id" in data, (
        "이전 학습 항목 정보가 응답 데이터에 없습니다."
    )




### Negative Test


@pytest.mark.p0
def test_get_material_pdf_without_token(settings):
    # 우선순위 : P0
    # TC ID: TC-STUDENT-COURSE-011
    # Authorization Token 없이 강의자료 PDF 조회 시 인증 실패 응답 확인 API 테스트.

    # Given
    # Authorization Token 없이 강의자료 PDF 조회에 필요한 설정값 세팅
    no_auth_client = APIClient(
        base_url=common_data.base_rest_url,
        token=None,
        org_name=common_data.org_student,
        timeout=settings.request_timeout_seconds,
        min_interval=common_data.min_request_interval_seconds,
    )

    params = {
        "material_pdf_id":
            lecture_case["week1_2lecture_material_id"],
    }

    # When
    # Authorization Token 없이 강의자료 PDF 조회 API 요청
    response = no_auth_client.get(
        f"/org/{common_data.org_student}/material_pdf/get/",
        params=params,
    )

    # Then
    # 인증 오류 응답 여부 확인
    assert response.status_code == 200, (
        f"강의자료 PDF 조회 응답 실패 "
        f"(status_code={response.status_code})"
    )

    data = response.json()

    assert data["_result"]["status"] == "fail", (
        f"token 없이 인증 성공: {data}"
    )

    assert (
        "auth" in str(data).lower()
        or "token" in str(data).lower()
        or "session" in str(data).lower()
        or "permission" in str(data).lower()
    ), (
        "응답 데이터에 인증 실패 관련 정보가 없습니다."
    )


@pytest.mark.p2
def test_get_material_pdf_without_material_pdf_id(rest_student_client):
    # 우선순위 : P2
    # TC ID: TC-STUDENT-COURSE-010
    # material_pdf_id 누락 시 강의자료 PDF 조회 실패 응답 확인 API 테스트.

    # Given
    # material_pdf_id 없이 강의자료 PDF 조회에 필요한 설정값 세팅
    params = {}

    # When
    # material_pdf_id 없이 강의자료 PDF 조회 API 요청
    response = rest_student_client.get(
        f"/org/{common_data.org_student}/material_pdf/get/",
        params=params,
    )

    # Then
    # 필수 파라미터 누락 오류 응답 여부 확인
    assert response.status_code == 200, (
        f"강의자료 PDF 조회 응답 실패 "
        f"(status_code={response.status_code})"
    )

    data = response.json()

    assert data["_result"]["status"] == "fail", (
        f"필수 파라미터 누락 실패 응답 아님: {data}"
    )

    assert (
        "material_pdf_id" in str(data)
    ), (
        "응답 데이터에 material_pdf_id 관련 오류 정보가 없습니다."
    )

    assert "material_pdf" not in data, (
        "강의자료 PDF 데이터가 반환되었습니다."
    )


@pytest.mark.p2
def test_get_quiz_with_invalid_material_id(rest_student_client):
    # 우선순위 : P2
    # TC ID: TC-STUDENT-COURSE-012
    # 존재하지 않는 퀴즈 material_id 조회 실패 응답 확인 API 테스트.

    # Given
    # 존재하지 않는 퀴즈 material_id 조회에 필요한 설정값 세팅
    params = {
        "material_type":
            lecture_case["lecture_quiz_material_type"],
        "page_id":
            lecture_case["week1_2lecture_1quiz_page_id"],
        "material_id":
            "999999999",
    }

    # When
    # 존재하지 않는 퀴즈 material_id 조회 API 요청
    response = rest_student_client.get(
        f"/org/{common_data.org_student}/lecture_page/resolve/",
        params=params,
    )

    # Then
    # 존재하지 않는 퀴즈 material_id 오류 응답 여부 확인
    assert response.status_code == 200, (
        f"퀴즈 조회 응답 실패 "
        f"(status_code={response.status_code})"
    )

    data = response.json()

    assert data["_result"]["status"] == "fail", (
        f"존재하지 않는 퀴즈 material_id 오류 응답 아님: {data}"
    )

    assert (
        "not_found" in str(data).lower()
        or "not exist" in str(data).lower()
        or "invalid" in str(data).lower()
    ), (
        "응답 데이터에 존재하지 않는 퀴즈 관련 오류 정보가 없습니다."
    )

    assert "lecture_page_id" not in data, (
        "존재하지 않는 퀴즈 데이터가 반환되었습니다."
    )


@pytest.mark.p2
def test_get_exercise_with_invalid_room_id(rest_student_client):
    # 우선순위 : P2
    # TC ID: TC-STUDENT-COURSE-013
    # 존재하지 않는 실습 room_id로 실습방 진입 실패 응답 확인 API 테스트.

    # Given
    # 존재하지 않는 실습 room_id 조회에 필요한 설정값 세팅
    files = {
        "exercise_room_id": (
            None,
            "999999999",
        ),
    }

    # When
    # 존재하지 않는 실습 room_id 조회 API 요청
    response = rest_student_client.request(
        "POST",
        f"/org/{common_data.org_student}/runner_room/exercise_room/join/",
        files=files,
    )

    # Then
    # 존재하지 않는 실습 room_id 오류 응답 여부 확인
    assert response.status_code == 200, (
        f"코딩 실습 조회 응답 실패 "
        f"(status_code={response.status_code})"
    )

    data = response.json()

    assert data["_result"]["status"] == "fail", (
        f"존재하지 않는 실습 room_id 오류 응답 아님: {data}"
    )

    assert data["fail_code"] == "not_found_exercise_room", (
        "존재하지 않는 실습 room_id 오류가 정상적으로 반환되지 않았습니다."
    )

    assert "room_token" not in data, (
        "존재하지 않는 실습 room 정보가 반환되었습니다."
    )
