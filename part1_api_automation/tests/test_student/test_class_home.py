# 수강생 권한으로 접근 가능한 API 테스트를 작성하는 파일
#
# 예: 클래스 정보 조회, 과목 목록 조회, 일정 조회, 게시판 목록 조회 등
# Postman에서 먼저 호출이 성공한 API를 기준으로 pytest 테스트를 추가한다.
#
# 공통 client는 tests/conftest.py의 student_client fixture를 사용한다.

import pytest

from utils.test_data import common_data


@pytest.mark.p0
def test_get_account_me(account_student_client):
    # 우선순위 : P0
    # TC ID: TC_CLASSHOME_001
    # Postman에서 성공 확인한 현재 로그인 사용자 정보 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유)
        # When : 현재 로그인 사용자 정보 조회 API를 호출 : GET https://api-account.elice.io/account/me
        # Then : response 결과 확인 : status_code가 200인지, body에 계정 정보가 있는지 확인
    # 입력값 : 학습자 토큰

    # Given : 로그인 상태(유효한 학습자 토큰 보유)

    # When : 현재 로그인 사용자 정보 조회 API를 호출 : GET https://api-account.elice.io/account/me
    response = account_student_client.get("/account/me")

    # Then : response 결과 확인 : status_code가 200인지, body에 계정 정보가 있는지 확인
    # assert 1. response의 status code가 200인지 확인
    assert response.status_code == 200, (
        f"응답 상태 코드가 200이 아닙니다. "
        f"status_code={response.status_code}, response={response.text}"
    )

    body = response.json()

    # assert 2. id : 현재 로그인한 계정의 id가 있는지 확인
    assert "id" in body, (
        f"응답 body에 'id' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 3. fullname : 현재 로그인한 계정의 이름이 있는지 확인
    assert "fullname" in body, (
        f"응답 body에 'fullname' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 4. account_type : 현재 로그인한 계정 유형이 있는지 확인
    assert "account_type" in body, (
        f"응답 body에 'account_type' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 5. auth_email : 현재 로그인한 계정의 인증 이메일 정보가 있는지 확인
    assert "auth_email" in body, (
        f"응답 body에 'auth_email' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_001")
    print("status_code",response.status_code)
    print("(계정 ID)id:", body["id"])
    print("(이름)fullname:", body["fullname"])
    print("(계정 유형)account_type:", body["account_type"])
    print("(인증 이메일)auth_email:", body["auth_email"])


@pytest.mark.p1
def test_get_activation_info(billing2_student_client):
    # 우선순위 : P1
    # TC ID: TC_CLASSHOME_002
    # Postman에서 성공 확인한 LXP 구독/활성화 정보 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 조직 ID와 서비스 유형 보유
        # When : 구독/활성화 정보 조회 API를 호출 : GET https://api-billing2.elice.io/activation?filter_statuses=activated&filter_organization_id={org_no_1}&filter_service_type=lxp&skip=0&count=1
        # Then : response 결과 확인 : status_code가 200인지, body에 활성화 정보가 있는지 확인
    # 입력값 : 조직 ID, 활성화 상태, 서비스 유형, skip, count 준비 : org_no_1, activated, lxp, 0, 1

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 조직 ID와 서비스 유형 보유
    # TODO: org_no_1은 현재 임시 테스트 데이터다.
    # 추후 팀 기준에 따라 fixture 또는 별도 test data 파일로 이동할 수 있다.
    org_no_1 = 4653
    params = {
        "filter_statuses": "activated",
        "filter_organization_id": org_no_1,
        "filter_service_type": "lxp",
        "skip": 0,
        "count": 1,
    }

    # When : 구독/활성화 정보 조회 API를 호출 : GET https://api-billing2.elice.io/activation?filter_statuses=activated&filter_organization_id={org_no_1}&filter_service_type=lxp&skip=0&count=1
    response = billing2_student_client.get(
        "/activation",
        params=params,
    )

    # Then : response 결과 확인 : status_code가 200인지, body에 활성화 정보가 있는지 확인
    # assert 1. response의 status code가 200인지 확인
    assert response.status_code == 200, (
        f"응답 상태 코드가 200이 아닙니다. "
        f"status_code={response.status_code}, response={response.text}"
    )

    body = response.json()

    # assert 2. 응답 body가 list 형식인지 확인
    assert isinstance(body, list), (
        f"응답 body가 list 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    # assert 3. 활성화 정보가 1개 이상 조회되는지 확인
    assert len(body) > 0, (
        "활성화 정보 목록이 비어 있습니다."
    )

    activation = body[0]

    # assert 4. id : 활성화 정보 ID가 있는지 확인
    assert "id" in activation, (
        f"첫 번째 활성화 정보에 'id' 항목이 없습니다. "
        f"activation keys={list(activation.keys())}"
    )

    # assert 5. organization_id : 조직 ID가 있는지 확인
    assert "organization_id" in activation, (
        f"첫 번째 활성화 정보에 'organization_id' 항목이 없습니다. "
        f"activation keys={list(activation.keys())}"
    )

    # assert 6. status : 활성화 상태가 activated인지 확인
    assert activation["status"] == "activated", (
        f"활성화 상태가 activated가 아닙니다. "
        f"actual={activation.get('status')}"
    )

    # assert 7. service_type : 서비스 유형이 lxp인지 확인
    assert activation["service_type"] == "lxp", (
        f"서비스 유형이 lxp가 아닙니다. "
        f"actual={activation.get('service_type')}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_002")
    print("status_code", response.status_code)
    print("(활성화 정보 ID)id:", activation["id"])
    print("(조직 ID)organization_id:", activation["organization_id"])
    print("(조직명)organization_name:", activation.get("organization_name"))
    print("(상태)status:", activation["status"])
    print("(서비스 유형)service_type:", activation["service_type"])


@pytest.mark.p0
def test_get_classroom_detail(student_client):
    # 우선순위 : P0
    # TC ID: TC_CLASSHOME_004
    # Postman에서 성공 확인한 클래스룸 기본 정보 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 클래스룸 ID 보유
        # When : 클래스룸 정보 조회 API를 호출 : GET https://api-classroom.elice.io/classroom/{classroom_id}
        # Then : response 결과 확인 : status_code가 200인지, body에 클래스룸 기본 정보가 있는지 확인
    # 입력값 : 클래스룸 ID 준비 : classroom_id

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 클래스룸 ID 보유
    classroom_id = common_data.student_classroom_id

    # When : 클래스룸 정보 조회 API를 호출 : GET https://api-classroom.elice.io/classroom/{classroom_id}
    response = student_client.get(f"/classroom/{classroom_id}")

    # Then : response 결과 확인 : status_code가 200인지, body에 클래스룸 기본 정보가 있는지 확인
    # assert 1. response의 status code가 200인지 확인
    assert response.status_code == 200, (
        f"응답 상태 코드가 200이 아닙니다. "
        f"status_code={response.status_code}, response={response.text}"
    )

    body = response.json()

    # assert 2. id : 응답 클래스룸 id가 입력한 classroom_id와 동일한지 확인
    assert body["id"] == classroom_id, (
        f"classroom id가 입력값과 일치하지 않습니다. "
        f"actual={body.get('id')}, expected={classroom_id}"
    )

    # assert 3. name : 클래스룸 이름이 있는지 확인
    assert "name" in body, (
        f"응답 body에 'name' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 4. course_count : 클래스룸 과목 수 정보가 있는지 확인
    assert "course_count" in body, (
        f"응답 body에 'course_count' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 5. member_count : 클래스룸 멤버 수 정보가 있는지 확인
    assert "member_count" in body, (
        f"응답 body에 'member_count' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 6. member_role : 로그인 계정의 클래스룸 역할 정보가 있는지 확인
    assert "member_role" in body, (
        f"응답 body에 'member_role' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_004")
    print("status_code",response.status_code)
    print("(클래스룸 ID)id:", body["id"])
    print("(클래스룸 이름)name:", body["name"])
    print("(과목 수)course_count:", body["course_count"])
    print("(멤버 수)member_count:", body["member_count"])
    print("(사용자 역할)member_role:", body["member_role"])


@pytest.mark.p0
def test_get_classroom_course_list(student_client):
    # 우선순위 : P0
    # TC ID: TC_CLASSHOME_006
    # Postman에서 성공 확인한 클래스룸 과목 목록 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 클래스룸 ID 보유
        # When : 과목 목록 조회 API를 호출 : GET https://api-classroom.elice.io/classroom/{classroom_id}/course?filter_title=%%&skip=0&count=40
        # Then : response 결과 확인 : status_code가 200인지, body에 과목 목록 정보가 있는지 확인
    # 입력값 : 클래스룸 ID, filter_title, skip, count 준비 : classroom_id, %%, 0, 40

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 클래스룸 ID 보유
    classroom_id = common_data.student_classroom_id
    params = {
        "filter_title": "%%",
        "skip": 0,
        "count": 40,
    }

    # When : 과목 목록 조회 API를 호출 : GET https://api-classroom.elice.io/classroom/{classroom_id}/course?filter_title=%%&skip=0&count=40
    response = student_client.get(
        f"/classroom/{classroom_id}/course",
        params=params,
    )

    # Then : response 결과 확인 : status_code가 200인지, body에 과목 목록 정보가 있는지 확인
    # assert 1. response의 status code가 200인지 확인
    assert response.status_code == 200, (
        f"응답 상태 코드가 200이 아닙니다. "
        f"status_code={response.status_code}, response={response.text}"
    )

    body = response.json()

    # assert 2. 응답 body가 list 형식인지 확인
    assert isinstance(body, list), (
        f"응답 body가 list 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    # assert 3. 과목 목록이 1개 이상 조회되는지 확인
    assert len(body) > 0, (
        "과목 목록이 비어 있습니다."
    )

    first_course = body[0]

    # assert 4. id : 과목 항목에 id가 있는지 확인
    assert "id" in first_course, (
        f"첫 번째 과목에 'id' 항목이 없습니다. "
        f"course keys={list(first_course.keys())}"
    )

    # assert 5. title : 과목 항목에 title이 있는지 확인
    assert "title" in first_course, (
        f"첫 번째 과목에 'title' 항목이 없습니다. "
        f"course keys={list(first_course.keys())}"
    )

    # assert 6. classroom_course_status : 과목 항목에 클래스룸 과목 상태가 있는지 확인
    assert "classroom_course_status" in first_course, (
        f"첫 번째 과목에 'classroom_course_status' 항목이 없습니다. "
        f"course keys={list(first_course.keys())}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_006")
    print("status_code",response.status_code)
    print("(과목 목록 수)course_count:", len(body))
    print("(첫 번째 과목 ID)id:", first_course["id"])
    print("(첫 번째 과목 제목)title:", first_course["title"])
    print(
        "(첫 번째 과목 상태)classroom_course_status:",
        first_course["classroom_course_status"],
    )


@pytest.mark.p0
def test_get_classroom_next_lecture_page(dashboard_student_client):
    # 우선순위 : P0
    # TC ID: TC_CLASSHOME_016
    # Postman에서 성공 확인한 클래스룸 다음 학습 강의 페이지 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 클래스룸 ID 보유
        # When : 다음 학습 강의 페이지 조회 API를 호출 : GET https://api-dashboard.elice.io/classroom/{classroom_id}/next_lecture_page
        # Then : response 결과 확인 : status_code가 200인지, body에 다음 학습 강의 페이지 정보가 있는지 확인
    # 입력값 : 클래스룸 ID 준비 : classroom_id

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 클래스룸 ID 보유
    classroom_id = common_data.student_classroom_id

    # When : 다음 학습 강의 페이지 조회 API를 호출 : GET https://api-dashboard.elice.io/classroom/{classroom_id}/next_lecture_page
    response = dashboard_student_client.get(
        f"/classroom/{classroom_id}/next_lecture_page"
    )

    # Then : response 결과 확인 : status_code가 200인지, body에 다음 학습 강의 페이지 정보가 있는지 확인
    # assert 1. response의 status code가 200인지 확인
    assert response.status_code == 200, (
        f"응답 상태 코드가 200이 아닙니다. "
        f"status_code={response.status_code}, response={response.text}"
    )

    body = response.json()

    # assert 2. course_id : 다음 학습 대상 과목 ID가 있는지 확인
    assert "course_id" in body, (
        f"응답 body에 'course_id' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 3. lecture_id : 다음 학습 대상 강의 ID가 있는지 확인
    assert "lecture_id" in body, (
        f"응답 body에 'lecture_id' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 4. lecture_page_id : 다음 학습 대상 강의 페이지 ID가 있는지 확인
    assert "lecture_page_id" in body, (
        f"응답 body에 'lecture_page_id' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 5. course_title : 다음 학습 대상 과목명이 있는지 확인
    assert "course_title" in body, (
        f"응답 body에 'course_title' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 6. lecture_page_title : 다음 학습 대상 강의 페이지명이 있는지 확인
    assert "lecture_page_title" in body, (
        f"응답 body에 'lecture_page_title' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 7. completed : 다음 학습 대상 완료 여부가 있는지 확인
    assert "completed" in body, (
        f"응답 body에 'completed' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_016")
    print("status_code",response.status_code)
    print("(과목 ID)course_id:", body["course_id"])
    print("(강의 ID)lecture_id:", body["lecture_id"])
    print("(강의 페이지 ID)lecture_page_id:", body["lecture_page_id"])
    print("(과목명)course_title:", body["course_title"])
    print("(강의 페이지명)lecture_page_title:", body["lecture_page_title"])
    print("(완료 여부)completed:", body["completed"])


@pytest.mark.p0
def test_get_student_dashboard(dashboard_student_client, settings):
    # 우선순위 : P0
    # TC ID: TC_CLASSHOME_017
    # Postman에서 성공 확인한 수강생 학습 현황 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(토큰 발급 계정과 학습자 계정이 동일해야 함)
        # When : 수강생 학습 현황 조회 API를 호출 : GET https://api-dashboard.elice.io/student/{student_id}?classroom_id={classroom_id}
        # Then : response 결과 확인 : status_code가 200인지, body 확인
    # 입력값 : 수강생 ID와 클래스룸 ID 준비 : student_id, classroom_id
    

    # Given : 로그인 상태(토큰 발급 계정과 학습자 계정이 동일해야 함)
    student_id = settings.student_id
    classroom_id = common_data.student_classroom_id

    # When : 수강생 학습 현황 조회 API를 호출 : GET https://api-dashboard.elice.io/student/{student_id}?classroom_id={classroom_id}
    response = dashboard_student_client.get(
        f"/student/{student_id}",
        params={"classroom_id": classroom_id},
    )

    # Then : response 결과 확인 : status_code가 200인지, body 확인
    # assert 1. response의 status code가 200인지 확인
    assert response.status_code == 200, (
        f"응답 상태 코드가 200이 아닙니다. "
        f"status_code={response.status_code}, response={response.text}"
    )

    body = response.json()

    # assert 2. account : 계정 있는지 확인
    assert "account" in body, (
        f"응답 body에 'account' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 3. account 내 id와 .env의 학습자 아이디가 동일한지 확인
    assert body["account"]["id"] == int(settings.student_id), (
        f"account.id가 .env의 student_id와 일치하지 않습니다. "
        f"actual={body['account']['id']}, expected={settings.student_id}"
    )

    # assert 4. learning_progress : 학습 진행률
    assert "learning_progress" in body, (
        f"응답 body에 'learning_progress' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 5. test_score : 테스트 평균 점수
    assert "test_score" in body, (
        f"응답 body에 'test_score' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 6. practice_score : 평균 실습 자료 점수
    assert "practice_score" in body, (
        f"응답 body에 'practice_score' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 7. submit_cnt : ? : response body에는 있지만, 어떤 항목인지 미상
    assert "submit_cnt" in body, (
        f"응답 body에 'submit_cnt' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 8. test_completed_cnt : ? : response body에는 있지만, 어떤 항목인지 미상
    assert "test_completed_cnt" in body, (
        f"응답 body에 'test_completed_cnt' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 9. learning_completed : 학습 완료 여부--classroom_id에 해당하는 수업
    assert "learning_completed" in body, (
        f"응답 body에 'learning_completed' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_017")
    print("status_code",response.status_code)
    print("(학습 진행률)learning_progress", body["learning_progress"])
    print("(테스트 평균 점수)test_score:", body["test_score"])
    print("(평균 실습 자료)practice_score:", body["practice_score"])
    print("submit_cnt:", body["submit_cnt"])
    print("test_completed_cnt:", body["test_completed_cnt"])
    print("(학습 완료 여부)learning_completed:", body["learning_completed"])


@pytest.mark.p0
def test_get_student_course_progress_list(dashboard_student_client, settings):
    # 우선순위 : P0
    # TC ID: TC_CLASSHOME_018
    # Postman에서 성공 확인한 학습자 과목별 진행 현황 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 학습자 ID와 클래스룸 ID 보유
        # When : 학습자 과목별 진행 현황 조회 API를 호출 : GET https://api-dashboard.elice.io/student/{student_id}/course?classroom_id={classroom_id}&sort_by=stats_updated_desc&offset=0&count=3
        # Then : response 결과 확인 : status_code가 200인지, body에 과목별 학습 진행 현황 정보가 있는지 확인
    # 입력값 : 학습자 ID, 클래스룸 ID, 정렬 기준, offset, count 준비 : student_id, classroom_id, stats_updated_desc, 0, 3

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 학습자 ID와 클래스룸 ID 보유
    student_id = settings.student_id
    classroom_id = common_data.student_classroom_id
    params = {
        "classroom_id": classroom_id,
        "sort_by": "stats_updated_desc",
        "offset": 0,
        "count": 3,
    }

    # When : 학습자 과목별 진행 현황 조회 API를 호출 : GET https://api-dashboard.elice.io/student/{student_id}/course?classroom_id={classroom_id}&sort_by=stats_updated_desc&offset=0&count=3
    response = dashboard_student_client.get(
        f"/student/{student_id}/course",
        params=params,
    )

    # Then : response 결과 확인 : status_code가 200인지, body에 과목별 학습 진행 현황 정보가 있는지 확인
    # assert 1. response의 status code가 200인지 확인
    assert response.status_code == 200, (
        f"응답 상태 코드가 200이 아닙니다. "
        f"status_code={response.status_code}, response={response.text}"
    )

    body = response.json()

    # assert 2. 응답 body가 list 형식인지 확인
    assert isinstance(body, list), (
        f"응답 body가 list 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    # assert 3. 과목별 진행 현황 목록이 1개 이상 조회되는지 확인
    assert len(body) > 0, (
        "과목별 진행 현황 목록이 비어 있습니다."
    )

    first_course_progress = body[0]

    # assert 4. course : 과목 정보가 있는지 확인
    assert "course" in first_course_progress, (
        f"첫 번째 과목 진행 현황에 'course' 항목이 없습니다. "
        f"keys={list(first_course_progress.keys())}"
    )

    course = first_course_progress["course"]

    # assert 5. course.id : 과목 ID가 있는지 확인
    assert "id" in course, (
        f"course 항목에 'id'가 없습니다. "
        f"course keys={list(course.keys())}"
    )

    # assert 6. course.title : 과목명이 있는지 확인
    assert "title" in course, (
        f"course 항목에 'title'이 없습니다. "
        f"course keys={list(course.keys())}"
    )

    # assert 7. learning_progress : 과목별 학습 진행률이 있는지 확인
    assert "learning_progress" in first_course_progress, (
        f"첫 번째 과목 진행 현황에 'learning_progress' 항목이 없습니다. "
        f"keys={list(first_course_progress.keys())}"
    )

    # assert 8. test_score : 과목별 테스트 평균 점수가 있는지 확인
    assert "test_score" in first_course_progress, (
        f"첫 번째 과목 진행 현황에 'test_score' 항목이 없습니다. "
        f"keys={list(first_course_progress.keys())}"
    )

    # assert 9. practice_score : 과목별 평균 실습 자료 점수가 있는지 확인
    assert "practice_score" in first_course_progress, (
        f"첫 번째 과목 진행 현황에 'practice_score' 항목이 없습니다. "
        f"keys={list(first_course_progress.keys())}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_018")
    print("status_code",response.status_code)
    print("(과목별 진행 현황 수)course_progress_count:", len(body))
    print("(첫 번째 과목 ID)course.id:", course["id"])
    print("(첫 번째 과목명)course.title:", course["title"])
    print("(학습 진행률)learning_progress:", first_course_progress["learning_progress"])
    print("(테스트 평균 점수)test_score:", first_course_progress["test_score"])
    print("(평균 실습 자료)practice_score:", first_course_progress["practice_score"])


@pytest.mark.p0
def test_get_global_account_detail(rest_student_client):
    # 우선순위 : P0
    # TC ID: TC_CLASSHOME_023
    # Postman에서 성공 확인한 현재 로그인 사용자 계정 상세 정보 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유)
        # When : 계정 상세 정보 조회 API를 호출 : GET https://api-rest.elice.io/global/account/get/
        # Then : response 결과 확인 : status_code가 200인지, body에 계정 상세 정보가 있는지 확인
    # 입력값 : 없음

    # Given : 로그인 상태(유효한 학습자 토큰 보유)

    # When : 계정 상세 정보 조회 API를 호출 : GET https://api-rest.elice.io/global/account/get/
    response = rest_student_client.get("/global/account/get/")

    # Then : response 결과 확인 : status_code가 200인지, body에 계정 상세 정보가 있는지 확인
    # assert 1. response의 status code가 200인지 확인
    assert response.status_code == 200, (
        f"응답 상태 코드가 200이 아닙니다. "
        f"status_code={response.status_code}, response={response.text}"
    )

    body = response.json()

    # assert 2. _result : API 처리 결과 정보가 있는지 확인
    assert "_result" in body, (
        f"응답 body에 '_result' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 3. account : 계정 상세 정보가 있는지 확인
    assert "account" in body, (
        f"응답 body에 'account' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    account = body["account"]

    # assert 4. account.id : 계정 ID가 있는지 확인
    assert "id" in account, (
        f"account 항목에 'id'가 없습니다. "
        f"account keys={list(account.keys())}"
    )

    # assert 5. account.fullname : 계정 이름이 있는지 확인
    assert "fullname" in account, (
        f"account 항목에 'fullname'이 없습니다. "
        f"account keys={list(account.keys())}"
    )

    # assert 6. account.email : 계정 이메일이 있는지 확인
    assert "email" in account, (
        f"account 항목에 'email'이 없습니다. "
        f"account keys={list(account.keys())}"
    )

    # assert 7. account_login_info : 계정 로그인 정보가 있는지 확인
    assert "account_login_info" in body, (
        f"응답 body에 'account_login_info' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 8. account_users : 조직별 사용자 정보가 있는지 확인
    assert "account_users" in body, (
        f"응답 body에 'account_users' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_023")
    print("status_code", response.status_code)
    print("(계정 ID)account.id:", account["id"])
    print("(이름)account.fullname:", account["fullname"])
    print("(이메일)account.email:", account["email"])
    print("(로그인 정보)account_login_info:", body["account_login_info"])
    print("(조직 사용자 수)account_users_count:", len(body["account_users"]))
