import pytest

from utils.test_data import common_data


@pytest.mark.p0
@pytest.mark.teacher
def test_get_course_list_as_educator(teacher_client):
    # 우선순위 : P0
    # TC ID: TC_TEACHER_CLASSHOME_001
    # Postman에서 성공 확인한 교육자 담당 과목 목록 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 토큰 보유), 교육자 조직 정보 보유
        # When : 교육자 과목 목록 조회 API를 호출 : GET https://api-classroom.elice.io/classroom/course/as_educator?skip=0&count=10
        # Then : response 결과 확인 : status_code가 200인지, body에 과목 목록 정보가 있는지 확인
    # 입력값 : 교육자 토큰, 교육자 조직명, skip, count 준비 : token, qaproject, 0, 10

    # Given : 로그인 상태(유효한 토큰 보유), 교육자 조직 정보 보유
    params = {
        "skip": 0,
        "count": 10,
    }

    # When : 교육자 과목 목록 조회 API를 호출
    response = teacher_client.get(
        "/classroom/course/as_educator",
        params=params,
    )

    # Then : response 결과 확인

    # assert 1. response의 status code가 200인지 확인
    assert response.status_code == 200, (
        f"응답 상태 코드가 200이 아닙니다. "
        f"status_code={response.status_code}, response={response.text}"
    )

    # assert 2. 응답 Content-Type이 JSON 형식인지 확인
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type, (
        f"응답 Content-Type이 JSON 형식이 아닙니다. "
        f"content_type={content_type}, response={response.text}"
    )

    body = response.json()

    # assert 3. 응답 body가 list 형식인지 확인
    assert isinstance(body, list), (
        f"응답 body가 list 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    # assert 4. 응답 과목 수가 요청 count 이하인지 확인
    assert len(body) <= params["count"], (
        f"응답 과목 수가 요청 count보다 많습니다. "
        f"actual={len(body)}, expected_max={params['count']}"
    )

    # assert 5. 교육자 과목 목록이 1개 이상 조회되는지 확인
    assert len(body) > 0, (
        "교육자 과목 목록이 비어 있습니다."
    )

    first_course = body[0]

    # assert 6. 첫 번째 과목 정보가 dict 형식인지 확인
    assert isinstance(first_course, dict), (
        f"첫 번째 과목 정보가 dict 형식이 아닙니다. "
        f"type={type(first_course).__name__}, value={first_course}"
    )

    # assert 7. 첫 번째 과목 정보에 필수 key가 모두 있는지 확인
    required_course_keys = [
        "classroom",
        "id",
        "course_id",
        "title",
        "course_type",
        "status",
        "created",
        "modified",
    ]

    missing_course_keys = [
        key for key in required_course_keys
        if key not in first_course
    ]

    assert not missing_course_keys, (
        f"첫 번째 과목 정보에 필수 항목이 없습니다. "
        f"missing_keys={missing_course_keys}, "
        f"course_keys={list(first_course.keys())}"
    )

    # assert 8. classroom이 dict 형식인지 확인
    assert isinstance(first_course["classroom"], dict), (
        f"classroom이 dict 형식이 아닙니다. "
        f"type={type(first_course['classroom']).__name__}, "
        f"value={first_course['classroom']}"
    )

    classroom = first_course["classroom"]

    # assert 9. classroom.id가 교육자 클래스룸 ID와 일치하는지 확인
    assert classroom.get("id") == common_data.teacher_classroom_id, (
        f"classroom.id가 교육자 클래스룸 ID와 일치하지 않습니다. "
        f"actual={classroom.get('id')}, "
        f"expected={common_data.teacher_classroom_id}"
    )

    # assert 10. title이 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(first_course["title"], str), (
        f"title이 str 형식이 아닙니다. "
        f"type={type(first_course['title']).__name__}, "
        f"value={first_course['title']}"
    )

    assert first_course["title"].strip() != "", (
        f"title 값이 비어 있습니다. title={first_course['title']!r}"
    )

    # assert 11. 응답 목록 전체의 기본 구조 확인
    for course in body:
        assert isinstance(course, dict), (
            f"과목 정보가 dict 형식이 아닙니다. "
            f"type={type(course).__name__}, value={course}"
        )

        missing_keys = [
            key for key in required_course_keys
            if key not in course
        ]

        assert not missing_keys, (
            f"과목 정보에 필수 key가 없습니다. "
            f"missing_keys={missing_keys}, "
            f"course_keys={list(course.keys())}"
        )

        assert isinstance(course["classroom"], dict), (
            f"classroom이 dict 형식이 아닙니다. "
            f"course_id={course.get('id')}, "
            f"value={course['classroom']}"
        )

        assert isinstance(course["title"], str), (
            f"과목 title이 str 형식이 아닙니다. "
            f"course_id={course.get('id')}, "
            f"type={type(course['title']).__name__}, "
            f"value={course['title']}"
        )

        assert course["title"].strip() != "", (
            f"과목 title 값이 비어 있습니다. "
            f"course_id={course.get('id')}, "
            f"title={course['title']!r}"
        )

    print("")
    print("")
    print("TC_NO:TC_TEACHER_CLASSHOME_001")
    print("status_code", response.status_code)
    print("(교육자 과목 목록 수)course_count:", len(body))
    print("(클래스룸 ID)classroom.id:", classroom.get("id"))
    print("(클래스룸 이름)classroom.name:", classroom.get("name"))
    print("(첫 번째 과목 ID)id:", first_course["id"])
    print("(첫 번째 과목 course_id)course_id:", first_course["course_id"])
    print("(첫 번째 과목 제목)title:", first_course["title"])
    print("(첫 번째 과목 상태)status:", first_course["status"])


@pytest.mark.p1
@pytest.mark.teacher
def test_update_classroom_name(teacher_client):
    # 우선순위 : P1
    # TC ID: TC_TEACHER_CLASSHOME_002
    # Postman에서 성공 확인한 교육자 클래스룸 이름 수정 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 토큰 보유), 교육자 조직 정보 보유, 수정 대상 클래스룸 ID 보유
        # When : 클래스룸 이름 수정 API를 호출 : PATCH https://api-classroom.elice.io/classroom/{classroom_id}
        # Then : response 결과 확인 : status_code가 200인지, body에 수정 대상 클래스룸 ID가 반환되는지 확인
    # 입력값 : 교육자 토큰, 교육자 조직명, 클래스룸 ID, name 준비 : token, qaproject, classroom_id, name

    # Given : 로그인 상태(유효한 토큰 보유), 교육자 조직 정보 보유, 수정 대상 클래스룸 ID 보유
    classroom_id = common_data.teacher_classroom_id

    # 운영 데이터 변경을 피하기 위해 현재 클래스룸 이름을 조회한 뒤 같은 이름으로 PATCH한다.
    get_response = teacher_client.get(f"/classroom/{classroom_id}")

    assert get_response.status_code == 200, (
        f"클래스룸 정보 조회 응답 상태 코드가 200이 아닙니다. "
        f"status_code={get_response.status_code}, response={get_response.text}"
    )

    classroom_body = get_response.json()

    assert isinstance(classroom_body, dict), (
        f"클래스룸 조회 응답 body가 dict 형식이 아닙니다. "
        f"type={type(classroom_body).__name__}, body={classroom_body}"
    )

    assert "name" in classroom_body, (
        f"클래스룸 조회 응답 body에 'name' 항목이 없습니다. "
        f"body_keys={list(classroom_body.keys())}"
    )

    classroom_name = classroom_body["name"]
    payload = {
        "name": classroom_name,
    }

    # When : 클래스룸 이름 수정 API를 호출
    response = teacher_client.request(
        "PATCH",
        f"/classroom/{classroom_id}",
        json=payload,
    )

    # Then : response 결과 확인

    # assert 1. response의 status code가 200인지 확인
    assert response.status_code == 200, (
        f"응답 상태 코드가 200이 아닙니다. "
        f"status_code={response.status_code}, response={response.text}"
    )

    # assert 2. 응답 Content-Type이 JSON 형식인지 확인
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type, (
        f"응답 Content-Type이 JSON 형식이 아닙니다. "
        f"content_type={content_type}, response={response.text}"
    )

    body = response.json()

    # assert 3. 응답 body가 dict 형식인지 확인
    assert isinstance(body, dict), (
        f"응답 body가 dict 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    # assert 4. id 항목이 있는지 확인
    assert "id" in body, (
        f"응답 body에 'id' 항목이 없습니다. "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. 응답 id가 수정 대상 클래스룸 ID와 일치하는지 확인
    assert body["id"] == classroom_id, (
        f"응답 id가 수정 대상 클래스룸 ID와 일치하지 않습니다. "
        f"actual={body.get('id')}, expected={classroom_id}"
    )

    # assert 6. id가 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(body["id"], str), (
        f"id가 str 형식이 아닙니다. "
        f"type={type(body['id']).__name__}, value={body['id']}"
    )

    assert body["id"].strip() != "", (
        f"id 값이 비어 있습니다. id={body['id']!r}"
    )

    print("")
    print("")
    print("TC_NO:TC_TEACHER_CLASSHOME_002")
    print("status_code", response.status_code)
    print("(클래스룸 ID)id:", body["id"])
    print("(요청 클래스룸 이름)name:", classroom_name)


@pytest.mark.p1
@pytest.mark.teacher
def test_get_classroom_member_count(teacher_client):
    # 우선순위 : P1
    # TC ID: TC_TEACHER_CLASSHOME_003
    # Postman에서 성공 확인한 교육자 클래스룸 멤버 수 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 토큰 보유), 교육자 조직 정보 보유, 조회 대상 클래스룸 ID 보유
        # When : 클래스룸 멤버 수 조회 API를 호출 : GET https://api-classroom.elice.io/member/count?classroom_id={classroom_id}
        # Then : response 결과 확인 : status_code가 200인지, body가 클래스룸 멤버 수를 나타내는 숫자인지 확인
    # 입력값 : 교육자 토큰, 교육자 조직명, 클래스룸 ID 준비 : token, qaproject, classroom_id

    # Given : 로그인 상태(유효한 토큰 보유), 교육자 조직 정보 보유, 조회 대상 클래스룸 ID 보유
    classroom_id = common_data.teacher_classroom_id
    params = {
        "classroom_id": classroom_id,
    }

    # When : 클래스룸 멤버 수 조회 API를 호출
    response = teacher_client.get(
        "/member/count",
        params=params,
    )

    # Then : response 결과 확인

    # assert 1. response의 status code가 200인지 확인
    assert response.status_code == 200, (
        f"응답 상태 코드가 200이 아닙니다. "
        f"status_code={response.status_code}, response={response.text}"
    )

    # assert 2. 응답 Content-Type이 JSON 형식인지 확인
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type, (
        f"응답 Content-Type이 JSON 형식이 아닙니다. "
        f"content_type={content_type}, response={response.text}"
    )

    body = response.json()

    # assert 3. 응답 body가 int 형식인지 확인
    assert isinstance(body, int), (
        f"응답 body가 int 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    # assert 4. 멤버 수가 0 이상인지 확인
    assert body >= 0, (
        f"멤버 수가 0보다 작습니다. member_count={body}"
    )

    print("")
    print("")
    print("TC_NO:TC_TEACHER_CLASSHOME_003")
    print("status_code", response.status_code)
    print("(클래스룸 ID)classroom_id:", classroom_id)
    print("(클래스룸 멤버 수)member_count:", body)
