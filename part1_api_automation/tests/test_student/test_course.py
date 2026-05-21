import requests
from utils.request_helper import get_auth_headers, get_request
from utils.test_data import common_data
from utils.test_data.student_material_data import lecture_case


def test_get_week1_2lecture_material_pdf(rest_student_client):
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


def test_get_week1_2lecture_quiz_material(rest_student_client):
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


def test_get_week1_2lecture_exercise_material(rest_student_client):
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


def test_get_material_pdf_without_token(settings):
    # Given
    # Authorization Token 없이 강의자료 PDF 조회에 필요한 설정값 세팅
    url = (
        f"{common_data.base_rest_url}"
        f"/org/{common_data.org_student}"
        f"/material_pdf/get/"
    )

    headers = {}

    params = {
        "material_pdf_id":
            lecture_case["week1_2lecture_material_id"],
    }

    # When
    # Authorization Token 없이 강의자료 PDF 조회 API 요청
    response = get_request(
        url=url,
        headers=headers,
        params=params,
        timeout=settings.request_timeout_seconds,
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


def test_submit_week1_2lecture_quiz_correct_answer(settings, rest_student_client):
    # Given
    # 1주차 2번 강의 퀴즈 정답 제출에 필요한 설정값 세팅
    submit_url = (
        f"{common_data.base_rest_url}"
        f"/org/{common_data.org_student}"
        f"/material_quiz/response/add/"
    )

    headers = get_auth_headers(
        settings.token
    )

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
    submit_response = requests.post(
        url=submit_url,
        headers=headers,
        files=submit_files,
        timeout=settings.request_timeout_seconds,
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


def test_submit_week1_2lecture_quiz_wrong_answer(settings, rest_student_client):
    # Given
    # 1주차 2번 강의 퀴즈 오답 제출에 필요한 설정값 세팅
    submit_url = (
        f"{common_data.base_rest_url}"
        f"/org/{common_data.org_student}"
        f"/material_quiz/response/add/"
    )

    headers = get_auth_headers(
        settings.token
    )

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
    submit_response = requests.post(
        url=submit_url,
        headers=headers,
        files=submit_files,
        timeout=settings.request_timeout_seconds,
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


def test_run_week1_2lecture_exercise(settings):
    # Given
    # 1주차 2번 강의 코딩 실습 실행에 필요한 설정값 세팅
    headers = get_auth_headers(
        settings.token
    )

    join_url = (
        f"{common_data.base_rest_url}"
        f"/org/{common_data.org_student}"
        f"/runner_room/exercise_room/join/"
    )

    join_files = {
        "exercise_room_id": (
            None,
            lecture_case["week1_2lecture_1exercise_room_id"],
        ),
    }

    # When
    # 코딩 실습 실행 화면 진입 API 요청
    join_response = requests.post(
        url=join_url,
        headers=headers,
        files=join_files,
        timeout=settings.request_timeout_seconds,
    )

    # Then
    # 코딩 실습 실행 화면 진입 성공 여부 확인
    assert join_response.status_code == 200, (
        f"코딩 실습 실행 화면 진입 실패 "
        f"(status_code={join_response.status_code})"
    )

    join_data = join_response.json()

    assert join_data["_result"]["status"] == "ok", (
        f"코딩 실습 실행 화면 진입 응답 실패: {join_data}"
    )

    assert "room_token" in join_data, (
        "코딩 실습 실행에 필요한 인증 정보가 반환되지 않았습니다."
    )

    assert "exercise_image_id" in join_data, (
        "코딩 실습 실행 환경 정보가 정상적으로 반환되지 않았습니다."
    )


def test_move_next_lesson_from_material_pdf(rest_student_client):
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


def test_move_previous_lesson_from_quiz(rest_student_client):
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


def test_get_material_pdf_without_material_pdf_id(rest_student_client):
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


def test_get_quiz_with_invalid_material_id(rest_student_client):
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


def test_get_exercise_with_invalid_room_id(settings):
    # Given
    # 존재하지 않는 실습 room_id 조회에 필요한 설정값 세팅
    headers = get_auth_headers(
        settings.token
    )

    url = (
        f"{common_data.base_rest_url}"
        f"/org/{common_data.org_student}"
        f"/runner_room/exercise_room/join/"
    )

    files = {
        "exercise_room_id": (
            None,
            "999999999",
        ),
    }

    # When
    # 존재하지 않는 실습 room_id 조회 API 요청
    response = requests.post(
        url=url,
        headers=headers,
        files=files,
        timeout=settings.request_timeout_seconds,
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


def test_submit_available_exercise(settings):
    # Given
    # 제출 가능한 코딩 실습 제출에 필요한 설정값 세팅
    headers = get_auth_headers(
        settings.token
    )

    join_url = (
        f"{common_data.base_rest_url}"
        f"/org/{common_data.org_student}"
        f"/runner_room/exercise_room/join/"
    )

    join_files = {
        "exercise_room_id": (
            None,
            lecture_case["submit_exercise_room_id"],
        ),
    }

    # When
    # 코딩 실습 제출 화면 진입 API 요청
    join_response = requests.post(
        url=join_url,
        headers=headers,
        files=join_files,
        timeout=settings.request_timeout_seconds,
    )

    # Then
    # 코딩 실습 제출 화면 진입 성공 여부 확인
    assert join_response.status_code == 200, (
        f"코딩 실습 제출 화면 진입 실패 "
        f"(status_code={join_response.status_code})"
    )

    join_data = join_response.json()

    assert join_data["_result"]["status"] == "ok", (
        f"코딩 실습 제출 화면 진입 응답 실패: {join_data}"
    )

    assert "room_token" in join_data, (
        "코딩 실습 제출에 필요한 인증 정보가 반환되지 않았습니다."
    )

    assert "exercise_image_id" in join_data, (
        "코딩 실습 제출 환경 정보가 정상적으로 반환되지 않았습니다."
    )

    room_token = join_data["room_token"]
    exercise_image_id = join_data["exercise_image_id"]

    submit_url = (
        f"{common_data.base_rest_url}"
        f"/org/{common_data.org_student}"
        f"/material_exercise/exercise_running/submit/"
    )

    submit_files = {
        "room_token": (
            None,
            room_token,
        ),
        "run_type": (
            None,
            "10",
        ),
        "exercise_image_id": (
            None,
            str(exercise_image_id),
        ),
    }

    # When
    # 코딩 실습 제출 API 요청
    submit_response = requests.post(
        url=submit_url,
        headers=headers,
        files=submit_files,
        timeout=settings.request_timeout_seconds,
    )

    # Then
    # 코딩 실습 제출 성공 여부 확인
    assert submit_response.status_code == 200, (
        f"코딩 실습 제출 실패 "
        f"(status_code={submit_response.status_code})"
    )

    submit_data = submit_response.json()

    assert submit_data["_result"]["status"] == "ok", (
        f"코딩 실습 제출 응답 실패: {submit_data}"
    )

    assert "exercise_running_id" in submit_data, (
        "코딩 실습 제출 결과 정보가 반환되지 않았습니다."
    )

    assert submit_data["run_type"] == 10, (
        "코딩 실습 제출 타입이 예상값과 다릅니다."
    )