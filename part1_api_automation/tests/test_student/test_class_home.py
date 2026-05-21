# 수강생 권한으로 접근 가능한 API 테스트를 작성하는 파일
#
# 예: 클래스 정보 조회, 과목 목록 조회, 일정 조회, 게시판 목록 조회 등
# Postman에서 먼저 호출이 성공한 API를 기준으로 pytest 테스트를 추가한다.
#
# 공통 client는 tests/conftest.py의 student_client fixture를 사용한다.

import pytest

from utils.test_data import common_data
from datetime import datetime, timezone

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

    # When : 현재 로그인 사용자 정보 조회 API를 호출
    response = account_student_client.get("/account/me")

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

    # assert 4. 응답 body에 필수 key가 모두 있는지 확인
    required_keys = ["id", "fullname", "account_type", "auth_email"]
    missing_keys = [
        key for key in required_keys
        if key not in body
    ]

    assert not missing_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. id가 int 형식이고 0보다 큰지 확인
    assert isinstance(body["id"], int), (
        f"id가 int 형식이 아닙니다. "
        f"type={type(body['id']).__name__}, value={body['id']}"
    )

    assert body["id"] > 0, (
        f"id 값이 0 이하입니다. id={body['id']}"
    )

    # assert 6. fullname이 str 형식인지 확인
    assert isinstance(body["fullname"], str), (
        f"fullname이 str 형식이 아닙니다. "
        f"type={type(body['fullname']).__name__}, value={body['fullname']}"
    )

    # fullname은 빈 값일 수도 있는 정책이 있을 수 있으므로,
    # 실제 서비스에서 이름이 반드시 있어야 한다면 아래 검증 유지
    assert body["fullname"].strip() != "", (
        f"fullname 값이 비어 있습니다. fullname={body['fullname']!r}"
    )

    # assert 7. account_type이 int 또는 str 형식인지 확인
    assert isinstance(body["account_type"], (int, str)), (
        f"account_type이 int 또는 str 형식이 아닙니다. "
        f"type={type(body['account_type']).__name__}, "
        f"value={body['account_type']}"
    )

    # assert 8. auth_email이 dict 형식인지 확인
    assert isinstance(body["auth_email"], dict), (
        f"auth_email이 dict 형식이 아닙니다. "
        f"type={type(body['auth_email']).__name__}, value={body['auth_email']}"
    )

    # assert 9. auth_email 내부에 필수 key가 있는지 확인
    required_auth_email_keys = ["email", "verified"]
    missing_auth_email_keys = [
        key for key in required_auth_email_keys
        if key not in body["auth_email"]
    ]

    assert not missing_auth_email_keys, (
        f"auth_email에 필수 항목이 없습니다. "
        f"missing_keys={missing_auth_email_keys}, "
        f"auth_email_keys={list(body['auth_email'].keys())}"
    )

    # assert 10. auth_email.email이 str 형식인지 확인
    assert isinstance(body["auth_email"]["email"], str), (
        f"auth_email.email이 str 형식이 아닙니다. "
        f"type={type(body['auth_email']['email']).__name__}, "
        f"value={body['auth_email']['email']}"
    )

    # assert 11. auth_email.email이 빈 문자열이 아닌지 확인
    assert body["auth_email"]["email"].strip() != "", (
        f"auth_email.email 값이 비어 있습니다. "
        f"email={body['auth_email']['email']!r}"
    )

    # assert 12. auth_email.email이 이메일 형식인지 확인
    assert "@" in body["auth_email"]["email"], (
        f"auth_email.email에 @가 없습니다. "
        f"email={body['auth_email']['email']}"
    )

    assert "." in body["auth_email"]["email"].split("@")[-1], (
        f"auth_email.email의 도메인 형식이 올바르지 않습니다. "
        f"email={body['auth_email']['email']}"
    )

    # assert 13. auth_email.verified는 None 또는 bool 형식인지 확인
    assert body["auth_email"]["verified"] is None or isinstance(body["auth_email"]["verified"], bool), (
        f"auth_email.verified가 None 또는 bool 형식이 아닙니다. "
        f"type={type(body['auth_email']['verified']).__name__}, "
        f"value={body['auth_email']['verified']}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_001")
    print("status_code", response.status_code)
    print("(계정 ID)id:", body["id"])
    print("(이름)fullname:", body["fullname"])
    print("(계정 유형)account_type:", body["account_type"])
    print("(인증 이메일)auth_email:", body["auth_email"]["email"])
    print("(이메일 인증 여부)verified:", body["auth_email"]["verified"])


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

    # When : 구독/활성화 정보 조회 API를 호출
    response = billing2_student_client.get(
        "/activation",
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

    # assert 4. 활성화 정보가 1개 이상 조회되는지 확인
    assert len(body) > 0, (
        "활성화 정보 목록이 비어 있습니다."
    )

    # assert 5. 응답 활성화 정보 수가 요청 count 이하인지 확인
    assert len(body) <= params["count"], (
        f"응답 활성화 정보 수가 요청 count보다 많습니다. "
        f"actual={len(body)}, expected_max={params['count']}"
    )

    activation = body[0]

    # assert 6. 첫 번째 활성화 정보에 필수 key가 모두 있는지 확인
    required_keys = [
        "id",
        "organization_id",
        "status",
        "service_type",
    ]

    missing_keys = [
        key for key in required_keys
        if key not in activation
    ]

    assert not missing_keys, (
        f"첫 번째 활성화 정보에 필수 항목이 없습니다. "
        f"missing_keys={missing_keys}, "
        f"activation_keys={list(activation.keys())}"
    )

    # assert 7. id가 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(activation["id"], str), (
        f"id가 str 형식이 아닙니다. "
        f"type={type(activation['id']).__name__}, "
        f"value={activation['id']}"
    )

    assert activation["id"].strip() != "", (
        f"id 값이 비어 있습니다. id={activation['id']!r}"
    )

    # assert 8. id가 UUID 형식인지 확인
    id_parts = activation["id"].split("-")

    assert len(id_parts) == 5, (
        f"id가 UUID 형식이 아닙니다. "
        f"id={activation['id']}"
    )

    assert all(id_parts), (
        f"id UUID 형식에 빈 구간이 있습니다. "
        f"id={activation['id']}"
    )

    # assert 9. organization_id가 요청한 조직 ID와 일치하는지 확인
    assert activation["organization_id"] == org_no_1, (
        f"organization_id가 요청한 조직 ID와 일치하지 않습니다. "
        f"actual={activation.get('organization_id')}, expected={org_no_1}"
    )

    # assert 10. organization_id가 int 형식인지 확인
    assert isinstance(activation["organization_id"], int), (
        f"organization_id가 int 형식이 아닙니다. "
        f"type={type(activation['organization_id']).__name__}, "
        f"value={activation['organization_id']}"
    )

    # assert 11. status가 요청한 활성화 상태와 일치하는지 확인
    assert activation["status"] == params["filter_statuses"], (
        f"활성화 상태가 요청값과 일치하지 않습니다. "
        f"actual={activation.get('status')}, "
        f"expected={params['filter_statuses']}"
    )

    # assert 12. status가 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(activation["status"], str), (
        f"status가 str 형식이 아닙니다. "
        f"type={type(activation['status']).__name__}, "
        f"value={activation['status']}"
    )

    assert activation["status"].strip() != "", (
        f"status 값이 비어 있습니다. status={activation['status']!r}"
    )

    # assert 13. service_type이 요청한 서비스 유형과 일치하는지 확인
    assert activation["service_type"] == params["filter_service_type"], (
        f"서비스 유형이 요청값과 일치하지 않습니다. "
        f"actual={activation.get('service_type')}, "
        f"expected={params['filter_service_type']}"
    )

    # assert 14. service_type이 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(activation["service_type"], str), (
        f"service_type이 str 형식이 아닙니다. "
        f"type={type(activation['service_type']).__name__}, "
        f"value={activation['service_type']}"
    )

    assert activation["service_type"].strip() != "", (
        f"service_type 값이 비어 있습니다. "
        f"service_type={activation['service_type']!r}"
    )

    # assert 15. organization_name이 있는 경우 str 형식인지 확인
    if "organization_name" in activation:
        assert isinstance(activation["organization_name"], str), (
            f"organization_name이 str 형식이 아닙니다. "
            f"type={type(activation['organization_name']).__name__}, "
            f"value={activation['organization_name']}"
        )

    # assert 16. 응답 목록 전체가 요청 조건과 일치하는지 확인
    for item in body:
        assert item.get("organization_id") == org_no_1, (
            f"활성화 정보의 organization_id가 요청값과 일치하지 않습니다. "
            f"activation_id={item.get('id')}, "
            f"actual={item.get('organization_id')}, expected={org_no_1}"
        )

        assert item.get("status") == params["filter_statuses"], (
            f"활성화 정보의 status가 요청값과 일치하지 않습니다. "
            f"activation_id={item.get('id')}, "
            f"actual={item.get('status')}, expected={params['filter_statuses']}"
        )

        assert item.get("service_type") == params["filter_service_type"], (
            f"활성화 정보의 service_type이 요청값과 일치하지 않습니다. "
            f"activation_id={item.get('id')}, "
            f"actual={item.get('service_type')}, expected={params['filter_service_type']}"
        )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_002")
    print("status_code", response.status_code)
    print("(활성화 정보 수)activation_count:", len(body))
    print("(활성화 정보 ID)id:", activation["id"])
    print("(조직 ID)organization_id:", activation["organization_id"])
    print("(조직명)organization_name:", activation.get("organization_name"))
    print("(상태)status:", activation["status"])
    print("(서비스 유형)service_type:", activation["service_type"])


@pytest.mark.p2
def test_get_channel_stat(channel_student_client):
    # 우선순위 : P2
    # TC ID: TC_CLASSHOME_003
    # Postman에서 성공 확인한 현재 사용자 기준 읽지 않은 H2H 메시지 존재 여부 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유)
        # When : 채널 메시지 상태 조회 API를 호출 : GET https://api-channel.elice.io/channel/stat
        # Then : response 결과 확인 : status_code가 200인지, body에 읽지 않은 H2H 메시지 존재 여부가 있는지 확인
    # 입력값 : 없음

    # Given : 로그인 상태(유효한 학습자 토큰 보유)

    # When : 채널 메시지 상태 조회 API를 호출
    response = channel_student_client.get("/channel/stat")

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

    # assert 4. 응답 body에 필수 key가 모두 있는지 확인
    required_keys = ["exist_unread_h2h_message"]
    missing_keys = [
        key for key in required_keys
        if key not in body
    ]

    assert not missing_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. exist_unread_h2h_message 값이 bool 형식인지 확인
    assert isinstance(body["exist_unread_h2h_message"], bool), (
        f"exist_unread_h2h_message 값이 bool 형식이 아닙니다. "
        f"type={type(body['exist_unread_h2h_message']).__name__}, "
        f"value={body['exist_unread_h2h_message']}"
    )

    # assert 6. exist_unread_h2h_message 값이 True 또는 False 중 하나인지 확인
    # bool 타입이면 사실상 항상 True/False지만, 테스트 의도를 명확히 하기 위해 작성
    assert body["exist_unread_h2h_message"] in [True, False], (
        f"exist_unread_h2h_message 값이 True/False가 아닙니다. "
        f"value={body['exist_unread_h2h_message']}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_003")
    print("status_code", response.status_code)
    print(
        "(읽지 않은 H2H 메시지 존재 여부)exist_unread_h2h_message:",
        body["exist_unread_h2h_message"],
    )


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

    # When : 클래스룸 정보 조회 API를 호출
    response = student_client.get(f"/classroom/{classroom_id}")

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

    # assert 4. 응답 body에 필수 key가 모두 있는지 확인
    required_keys = [
        "id",
        "name",
        "course_count",
        "member_count",
        "member_role",
    ]

    missing_keys = [
        key for key in required_keys
        if key not in body
    ]

    assert not missing_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. id : 응답 클래스룸 id가 입력한 classroom_id와 동일한지 확인
    assert body["id"] == classroom_id, (
        f"classroom id가 입력값과 일치하지 않습니다. "
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

    # assert 7. name이 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(body["name"], str), (
        f"name이 str 형식이 아닙니다. "
        f"type={type(body['name']).__name__}, value={body['name']}"
    )

    assert body["name"].strip() != "", (
        f"클래스룸 이름이 비어 있습니다. name={body['name']!r}"
    )

    # assert 8. course_count가 int 형식이고 0 이상인지 확인
    assert isinstance(body["course_count"], int), (
        f"course_count가 int 형식이 아닙니다. "
        f"type={type(body['course_count']).__name__}, "
        f"value={body['course_count']}"
    )

    assert body["course_count"] >= 0, (
        f"course_count가 0보다 작습니다. "
        f"course_count={body['course_count']}"
    )

    # assert 9. member_count가 int 형식이고 0보다 큰지 확인
    assert isinstance(body["member_count"], int), (
        f"member_count가 int 형식이 아닙니다. "
        f"type={type(body['member_count']).__name__}, "
        f"value={body['member_count']}"
    )

    assert body["member_count"] > 0, (
        f"member_count가 0 이하입니다. "
        f"member_count={body['member_count']}"
    )

    # assert 10. member_role이 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(body["member_role"], str), (
        f"member_role이 str 형식이 아닙니다. "
        f"type={type(body['member_role']).__name__}, "
        f"value={body['member_role']}"
    )

    assert body["member_role"].strip() != "", (
        f"member_role 값이 비어 있습니다. "
        f"member_role={body['member_role']!r}"
    )

    # assert 11. member_role이 허용된 역할 값 중 하나인지 확인
    allowed_member_roles = [
        "student",
        "educator",
        "teaching_assistant",
        "admin",
        "owner",
    ]

    assert body["member_role"] in allowed_member_roles, (
        f"member_role이 허용된 역할 값이 아닙니다. "
        f"actual={body['member_role']}, "
        f"allowed={allowed_member_roles}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_004")
    print("status_code", response.status_code)
    print("(클래스룸 ID)id:", body["id"])
    print("(클래스룸 이름)name:", body["name"])
    print("(과목 수)course_count:", body["course_count"])
    print("(멤버 수)member_count:", body["member_count"])
    print("(사용자 역할)member_role:", body["member_role"])


@pytest.mark.p1
def test_student_cannot_get_classroom_ticket_info(student_client):
    # 우선순위 : P1
    # TC ID: TC_CLASSHOME_005
    # Postman에서 성공 확인한 학습자 권한의 클래스룸 티켓 정보 조회 권한 경계 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 클래스룸 ID 보유, 학습자 권한 계정
        # When : 클래스룸 티켓 정보 조회 API를 호출 : GET https://api-classroom.elice.io/classroom/{classroom_id}/classroom_ticket/info
        # Then : response 결과 확인 : status_code가 403인지, body에 권한 없음 정보가 있는지 확인
    # 입력값 : 클래스룸 ID 준비 : classroom_id

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 클래스룸 ID 보유, 학습자 권한 계정
    classroom_id = common_data.student_classroom_id

    # When : 클래스룸 티켓 정보 조회 API를 호출
    response = student_client.get(
        f"/classroom/{classroom_id}/classroom_ticket/info"
    )

    # Then : response 결과 확인

    # assert 1. response의 status code가 403인지 확인
    assert response.status_code == 403, (
        f"응답 상태 코드가 403이 아닙니다. "
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

    # assert 4. 응답 body에 필수 key가 모두 있는지 확인
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
        f"응답 body에 필수 에러 항목이 없습니다. "
        f"missing_keys={missing_error_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. code가 str 형식인지 확인
    assert isinstance(body["code"], str), (
        f"code가 str 형식이 아닙니다. "
        f"type={type(body['code']).__name__}, "
        f"value={body['code']}"
    )

    # assert 6. code가 권한 없음 에러 코드인지 확인
    assert body["code"] == "has_no_permission", (
        f"권한 없음 에러 코드가 기대값과 다릅니다. "
        f"actual={body.get('code')}, expected=has_no_permission"
    )

    # assert 7. message가 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(body["message"], str), (
        f"message가 str 형식이 아닙니다. "
        f"type={type(body['message']).__name__}, "
        f"value={body['message']}"
    )

    assert body["message"].strip() != "", (
        f"message 값이 비어 있습니다. "
        f"message={body['message']!r}"
    )

    # assert 8. detail이 None, str, dict 또는 list 형식인지 확인
    # API에 따라 detail은 문자열, 객체, 배열, null로 내려올 수 있으므로 허용 범위를 넓게 둠
    assert body["detail"] is None or isinstance(body["detail"], (str, dict, list)), (
        f"detail이 None, str, dict 또는 list 형식이 아닙니다. "
        f"type={type(body['detail']).__name__}, "
        f"value={body['detail']}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_005")
    print("status_code", response.status_code)
    print("(클래스룸 ID)classroom_id:", classroom_id)
    print("(에러 코드)code:", body["code"])
    print("(에러 메시지)message:", body["message"])
    print("(에러 상세)detail:", body["detail"])


@pytest.mark.p2
def test_get_ai_model_list(community_student_client):
    # 우선순위 : P2
    # TC ID: TC_CLASSHOME_006
    # Postman에서 성공 확인한 AI 모델 목록 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 활성화 필터 보유
        # When : AI 모델 목록 조회 API를 호출 : GET https://api-community.elice.io/model?filter_is_active=true&skip=0&count=1
        # Then : response 결과 확인 : status_code가 200인지, body에 AI 모델 목록이 있는지 확인
    # 입력값 : 활성화 여부, skip, count 준비 : true, 0, 1

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 활성화 필터 보유
    params = {
        "filter_is_active": "true",
        "skip": 0,
        "count": 1,
    }

    # When : AI 모델 목록 조회 API를 호출
    response = community_student_client.get("/model", params=params)

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

    # assert 4. 응답 모델 수가 요청 count 이하인지 확인
    assert len(body) <= params["count"], (
        f"응답 모델 수가 요청 count보다 많습니다. "
        f"actual={len(body)}, expected_max={params['count']}"
    )

    # 모델 목록이 비어 있을 수도 있는 API라면 len(body) > 0은 필수로 두지 않는 것이 안전함
    if body:
        first_model = body[0]

        # assert 5. 첫 번째 모델 항목이 dict 형식인지 확인
        assert isinstance(first_model, dict), (
            f"첫 번째 AI 모델 항목이 dict 형식이 아닙니다. "
            f"type={type(first_model).__name__}, value={first_model}"
        )

        # assert 6. 첫 번째 모델에 필수 key가 모두 있는지 확인
        required_model_keys = [
            "id",
            "name",
            "is_active",
        ]

        missing_model_keys = [
            key for key in required_model_keys
            if key not in first_model
        ]

        assert not missing_model_keys, (
            f"첫 번째 AI 모델 항목에 필수 key가 없습니다. "
            f"missing_keys={missing_model_keys}, "
            f"model_keys={list(first_model.keys())}"
        )

        # assert 7. id가 int 또는 str 형식이고 빈 값이 아닌지 확인
        assert isinstance(first_model["id"], (int, str)), (
            f"모델 id가 int 또는 str 형식이 아닙니다. "
            f"type={type(first_model['id']).__name__}, "
            f"value={first_model['id']}"
        )

        assert str(first_model["id"]).strip() != "", (
            f"모델 id 값이 비어 있습니다. "
            f"id={first_model['id']!r}"
        )

        # assert 8. name이 str 형식이고 빈 문자열이 아닌지 확인
        assert isinstance(first_model["name"], str), (
            f"모델 name이 str 형식이 아닙니다. "
            f"type={type(first_model['name']).__name__}, "
            f"value={first_model['name']}"
        )

        assert first_model["name"].strip() != "", (
            f"모델 name 값이 비어 있습니다. "
            f"name={first_model['name']!r}"
        )

        # assert 9. is_active가 bool 형식인지 확인
        assert isinstance(first_model["is_active"], bool), (
            f"is_active가 bool 형식이 아닙니다. "
            f"type={type(first_model['is_active']).__name__}, "
            f"value={first_model['is_active']}"
        )

        # assert 10. 활성화 필터가 true이므로 is_active가 True인지 확인
        assert first_model["is_active"] is True, (
            f"활성화 모델 필터가 적용되지 않았습니다. "
            f"actual={first_model['is_active']}, expected=True"
        )

        # assert 11. 응답 목록 전체의 기본 구조와 활성화 여부 확인
        for model in body:
            assert isinstance(model, dict), (
                f"AI 모델 항목이 dict 형식이 아닙니다. "
                f"type={type(model).__name__}, value={model}"
            )

            missing_keys = [
                key for key in required_model_keys
                if key not in model
            ]

            assert not missing_keys, (
                f"AI 모델 항목에 필수 key가 없습니다. "
                f"missing_keys={missing_keys}, "
                f"model_keys={list(model.keys())}"
            )

            assert isinstance(model["name"], str), (
                f"모델 name이 str 형식이 아닙니다. "
                f"model_id={model.get('id')}, "
                f"type={type(model['name']).__name__}, "
                f"value={model['name']}"
            )

            assert model["name"].strip() != "", (
                f"모델 name 값이 비어 있습니다. "
                f"model_id={model.get('id')}, "
                f"name={model['name']!r}"
            )

            assert isinstance(model["is_active"], bool), (
                f"is_active가 bool 형식이 아닙니다. "
                f"model_id={model.get('id')}, "
                f"type={type(model['is_active']).__name__}, "
                f"value={model['is_active']}"
            )

            assert model["is_active"] is True, (
                f"활성화 모델 필터가 적용되지 않았습니다. "
                f"model_id={model.get('id')}, "
                f"actual={model['is_active']}, expected=True"
            )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_006")
    print("status_code", response.status_code)
    print("(AI 모델 목록 수)model_count:", len(body))

    if body:
        first_model = body[0]
        print("(첫 번째 모델 ID)id:", first_model.get("id"))
        print("(첫 번째 모델명)name:", first_model.get("name"))
        print("(활성화 여부)is_active:", first_model.get("is_active"))


@pytest.mark.p2
def test_get_token_grant_list(community_student_client):
    # 우선순위 : P2
    # TC ID: TC_CLASSHOME_007
    # Postman에서 성공 확인한 토큰 부여 정보 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 조회 시작일 필터 보유
        # When : 토큰 부여 정보 조회 API를 호출 : GET https://api-community.elice.io/token_grant
        # Then : response 결과 확인 : status_code가 200인지, body에 토큰 부여 정보가 있는지 확인
    # 입력값 : filter_period_start_at_le, offset, count 준비 : 2026-05-19, 0, 1

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 조회 시작일 필터 보유
    params = {
        "filter_period_start_at_le": "2026-05-19",
        "offset": 0,
        "count": 1,
    }

    # When : 토큰 부여 정보 조회 API를 호출
    response = community_student_client.get("/token_grant", params=params)

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

    # assert 4. 응답 토큰 부여 정보 수가 요청 count 이하인지 확인
    assert len(body) <= params["count"], (
        f"응답 토큰 부여 정보 수가 요청 count보다 많습니다. "
        f"actual={len(body)}, expected_max={params['count']}"
    )

    # 토큰 부여 정보가 없는 경우도 가능하므로 body가 있을 때만 상세 검증
    if body:
        first_grant = body[0]

        # assert 5. 첫 번째 토큰 부여 항목이 dict 형식인지 확인
        assert isinstance(first_grant, dict), (
            f"첫 번째 토큰 부여 항목이 dict 형식이 아닙니다. "
            f"type={type(first_grant).__name__}, value={first_grant}"
        )

        # assert 6. 첫 번째 토큰 부여 항목에 필수 key가 모두 있는지 확인
        required_grant_keys = [
            "id",
            "status",
            "granted_token",
            "used_token",
        ]

        missing_grant_keys = [
            key for key in required_grant_keys
            if key not in first_grant
        ]

        assert not missing_grant_keys, (
            f"첫 번째 토큰 부여 항목에 필수 key가 없습니다. "
            f"missing_keys={missing_grant_keys}, "
            f"grant_keys={list(first_grant.keys())}"
        )

        # assert 7. id가 int 또는 str 형식이고 빈 값이 아닌지 확인
        assert isinstance(first_grant["id"], (int, str)), (
            f"토큰 부여 id가 int 또는 str 형식이 아닙니다. "
            f"type={type(first_grant['id']).__name__}, "
            f"value={first_grant['id']}"
        )

        assert str(first_grant["id"]).strip() != "", (
            f"토큰 부여 id 값이 비어 있습니다. "
            f"id={first_grant['id']!r}"
        )

        # assert 8. status가 str 형식이고 빈 문자열이 아닌지 확인
        assert isinstance(first_grant["status"], str), (
            f"status가 str 형식이 아닙니다. "
            f"type={type(first_grant['status']).__name__}, "
            f"value={first_grant['status']}"
        )

        assert first_grant["status"].strip() != "", (
            f"status 값이 비어 있습니다. "
            f"status={first_grant['status']!r}"
        )

        # assert 9. granted_token이 int 또는 float 형식이고 0 이상인지 확인
        assert isinstance(first_grant["granted_token"], (int, float)), (
            f"granted_token이 int 또는 float 형식이 아닙니다. "
            f"type={type(first_grant['granted_token']).__name__}, "
            f"value={first_grant['granted_token']}"
        )

        assert first_grant["granted_token"] >= 0, (
            f"granted_token이 0보다 작습니다. "
            f"granted_token={first_grant['granted_token']}"
        )

        # assert 10. used_token이 int 또는 float 형식이고 0 이상인지 확인
        assert isinstance(first_grant["used_token"], (int, float)), (
            f"used_token이 int 또는 float 형식이 아닙니다. "
            f"type={type(first_grant['used_token']).__name__}, "
            f"value={first_grant['used_token']}"
        )

        assert first_grant["used_token"] >= 0, (
            f"used_token이 0보다 작습니다. "
            f"used_token={first_grant['used_token']}"
        )

        # assert 11. 사용 토큰이 부여 토큰보다 크지 않은지 확인
        assert first_grant["used_token"] <= first_grant["granted_token"], (
            f"used_token이 granted_token보다 큽니다. "
            f"used_token={first_grant['used_token']}, "
            f"granted_token={first_grant['granted_token']}"
        )

        # assert 12. 응답 목록 전체의 기본 구조 확인
        for grant in body:
            assert isinstance(grant, dict), (
                f"토큰 부여 항목이 dict 형식이 아닙니다. "
                f"type={type(grant).__name__}, value={grant}"
            )

            missing_keys = [
                key for key in required_grant_keys
                if key not in grant
            ]

            assert not missing_keys, (
                f"토큰 부여 항목에 필수 key가 없습니다. "
                f"missing_keys={missing_keys}, "
                f"grant_keys={list(grant.keys())}"
            )

            assert isinstance(grant["status"], str), (
                f"status가 str 형식이 아닙니다. "
                f"grant_id={grant.get('id')}, "
                f"type={type(grant['status']).__name__}, "
                f"value={grant['status']}"
            )

            assert grant["status"].strip() != "", (
                f"status 값이 비어 있습니다. "
                f"grant_id={grant.get('id')}, "
                f"status={grant['status']!r}"
            )

            assert isinstance(grant["granted_token"], (int, float)), (
                f"granted_token이 int 또는 float 형식이 아닙니다. "
                f"grant_id={grant.get('id')}, "
                f"type={type(grant['granted_token']).__name__}, "
                f"value={grant['granted_token']}"
            )

            assert grant["granted_token"] >= 0, (
                f"granted_token이 0보다 작습니다. "
                f"grant_id={grant.get('id')}, "
                f"granted_token={grant['granted_token']}"
            )

            assert isinstance(grant["used_token"], (int, float)), (
                f"used_token이 int 또는 float 형식이 아닙니다. "
                f"grant_id={grant.get('id')}, "
                f"type={type(grant['used_token']).__name__}, "
                f"value={grant['used_token']}"
            )

            assert grant["used_token"] >= 0, (
                f"used_token이 0보다 작습니다. "
                f"grant_id={grant.get('id')}, "
                f"used_token={grant['used_token']}"
            )

            assert grant["used_token"] <= grant["granted_token"], (
                f"used_token이 granted_token보다 큽니다. "
                f"grant_id={grant.get('id')}, "
                f"used_token={grant['used_token']}, "
                f"granted_token={grant['granted_token']}"
            )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_007")
    print("status_code", response.status_code)
    print("(토큰 부여 정보 수)token_grant_count:", len(body))

    if body:
        first_grant = body[0]
        print("(첫 번째 토큰 부여 ID)id:", first_grant.get("id"))
        print("(상태)status:", first_grant.get("status"))
        print("(부여 토큰)granted_token:", first_grant.get("granted_token"))
        print("(사용 토큰)used_token:", first_grant.get("used_token"))


@pytest.mark.p2
def test_get_token_quota_by_account(community_student_client, settings):
    # 우선순위 : P2
    # TC ID: TC_CLASSHOME_008
    # Postman에서 성공 확인한 토큰 쿼터 정보 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 학습자 ID 보유
        # When : 토큰 쿼터 정보 조회 API를 호출 : GET https://api-community.elice.io/token_quota/by_account
        # Then : response 결과 확인 : status_code가 200인지, body에 토큰 쿼터 정보가 있는지 확인
    # 입력값 : 학습자 ID 준비 : student_id

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 학습자 ID 보유
    params = {
        "account_id": settings.student_id,
    }

    # When : 토큰 쿼터 정보 조회 API를 호출
    response = community_student_client.get(
        "/token_quota/by_account",
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

    # assert 3. 응답 body가 dict 형식인지 확인
    assert isinstance(body, dict), (
        f"응답 body가 dict 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    # assert 4. 응답 body에 필수 key가 모두 있는지 확인
    required_keys = [
        "is_quota_enabled",
        "quota_info",
    ]

    missing_keys = [
        key for key in required_keys
        if key not in body
    ]

    assert not missing_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. is_quota_enabled가 bool 형식인지 확인
    assert isinstance(body["is_quota_enabled"], bool), (
        f"is_quota_enabled가 bool 형식이 아닙니다. "
        f"type={type(body['is_quota_enabled']).__name__}, "
        f"value={body['is_quota_enabled']}"
    )

    # assert 6. quota_info가 None 또는 dict 형식인지 확인
    assert body["quota_info"] is None or isinstance(body["quota_info"], dict), (
        f"quota_info가 None 또는 dict 형식이 아닙니다. "
        f"type={type(body['quota_info']).__name__}, "
        f"value={body['quota_info']}"
    )

    # assert 7. 쿼터가 활성화된 경우 quota_info가 dict 형식이고 비어 있지 않은지 확인
    if body["is_quota_enabled"]:
        assert isinstance(body["quota_info"], dict), (
            f"is_quota_enabled가 True인데 quota_info가 dict 형식이 아닙니다. "
            f"type={type(body['quota_info']).__name__}, "
            f"value={body['quota_info']}"
        )

        assert len(body["quota_info"].keys()) > 0, (
            f"is_quota_enabled가 True인데 quota_info가 비어 있습니다. "
            f"quota_info={body['quota_info']}"
        )

    # assert 8. status가 있는 경우 None, str 또는 int 형식인지 확인
    if "status" in body:
        assert body["status"] is None or isinstance(body["status"], (str, int)), (
            f"status가 None, str 또는 int 형식이 아닙니다. "
            f"type={type(body['status']).__name__}, "
            f"value={body['status']}"
        )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_008")
    print("status_code", response.status_code)
    print("(학습자 ID)account_id:", params["account_id"])
    print("(쿼터 사용 여부)is_quota_enabled:", body["is_quota_enabled"])
    print("(상태)status:", body.get("status"))
    print("(쿼터 정보)quota_info:", body["quota_info"])

    if isinstance(body["quota_info"], dict):
        print("(쿼터 정보 key 목록)quota_info_keys:", list(body["quota_info"].keys()))


@pytest.mark.p0
def test_get_classroom_next_lecture_page(dashboard_student_client):
    # 우선순위 : P0
    # TC ID: TC_CLASSHOME_009
    # Postman에서 성공 확인한 클래스룸 다음 학습 강의 페이지 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 클래스룸 ID 보유
        # When : 다음 학습 강의 페이지 조회 API를 호출 : GET https://api-dashboard.elice.io/classroom/{classroom_id}/next_lecture_page
        # Then : response 결과 확인 : status_code가 200인지, body에 다음 학습 강의 페이지 정보가 있는지 확인
    # 입력값 : 클래스룸 ID 준비 : classroom_id

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 클래스룸 ID 보유
    classroom_id = common_data.student_classroom_id

    # When : 다음 학습 강의 페이지 조회 API를 호출
    response = dashboard_student_client.get(
        f"/classroom/{classroom_id}/next_lecture_page"
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

    # assert 4. 응답 body에 필수 key가 모두 있는지 확인
    required_keys = [
        "course_id",
        "lecture_id",
        "lecture_page_id",
        "course_title",
        "lecture_page_title",
        "completed",
    ]

    missing_keys = [
        key for key in required_keys
        if key not in body
    ]

    assert not missing_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. course_id가 int 형식이고 0보다 큰지 확인
    assert isinstance(body["course_id"], int), (
        f"course_id가 int 형식이 아닙니다. "
        f"type={type(body['course_id']).__name__}, "
        f"value={body['course_id']}"
    )

    assert body["course_id"] > 0, (
        f"course_id 값이 0 이하입니다. "
        f"course_id={body['course_id']}"
    )

    # assert 6. lecture_id가 int 형식이고 0보다 큰지 확인
    assert isinstance(body["lecture_id"], int), (
        f"lecture_id가 int 형식이 아닙니다. "
        f"type={type(body['lecture_id']).__name__}, "
        f"value={body['lecture_id']}"
    )

    assert body["lecture_id"] > 0, (
        f"lecture_id 값이 0 이하입니다. "
        f"lecture_id={body['lecture_id']}"
    )

    # assert 7. lecture_page_id가 int 형식이고 0보다 큰지 확인
    assert isinstance(body["lecture_page_id"], int), (
        f"lecture_page_id가 int 형식이 아닙니다. "
        f"type={type(body['lecture_page_id']).__name__}, "
        f"value={body['lecture_page_id']}"
    )

    assert body["lecture_page_id"] > 0, (
        f"lecture_page_id 값이 0 이하입니다. "
        f"lecture_page_id={body['lecture_page_id']}"
    )

    # assert 8. course_title이 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(body["course_title"], str), (
        f"course_title이 str 형식이 아닙니다. "
        f"type={type(body['course_title']).__name__}, "
        f"value={body['course_title']}"
    )

    assert body["course_title"].strip() != "", (
        f"course_title 값이 비어 있습니다. "
        f"course_title={body['course_title']!r}"
    )

    # assert 9. lecture_page_title이 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(body["lecture_page_title"], str), (
        f"lecture_page_title이 str 형식이 아닙니다. "
        f"type={type(body['lecture_page_title']).__name__}, "
        f"value={body['lecture_page_title']}"
    )

    assert body["lecture_page_title"].strip() != "", (
        f"lecture_page_title 값이 비어 있습니다. "
        f"lecture_page_title={body['lecture_page_title']!r}"
    )

    # assert 10. completed가 bool 형식인지 확인
    assert isinstance(body["completed"], bool), (
        f"completed가 bool 형식이 아닙니다. "
        f"type={type(body['completed']).__name__}, "
        f"value={body['completed']}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_009")
    print("status_code", response.status_code)
    print("(과목 ID)course_id:", body["course_id"])
    print("(강의 ID)lecture_id:", body["lecture_id"])
    print("(강의 페이지 ID)lecture_page_id:", body["lecture_page_id"])
    print("(과목명)course_title:", body["course_title"])
    print("(강의 페이지명)lecture_page_title:", body["lecture_page_title"])
    print("(완료 여부)completed:", body["completed"])


@pytest.mark.p0
def test_get_student_dashboard(dashboard_student_client, settings):
    # 우선순위 : P0
    # TC ID: TC_CLASSHOME_010
    # Postman에서 성공 확인한 수강생 학습 현황 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(토큰 발급 계정과 학습자 계정이 동일해야 함)
        # When : 수강생 학습 현황 조회 API를 호출 : GET https://api-dashboard.elice.io/student/{student_id}?classroom_id={classroom_id}
        # Then : response 결과 확인 : status_code가 200인지, body 확인
    # 입력값 : 수강생 ID와 클래스룸 ID 준비 : student_id, classroom_id

    # 숫자 또는 숫자 문자열을 float으로 변환하는 helper
    def to_number(value, field_name):
        if value is None:
            return None

        assert isinstance(value, (int, float, str)), (
            f"{field_name}이 None, int, float 또는 str 형식이 아닙니다. "
            f"type={type(value).__name__}, value={value}"
        )

        try:
            return float(value)
        except ValueError:
            pytest.fail(
                f"{field_name}을 숫자로 변환할 수 없습니다. "
                f"value={value}"
            )

    # Given : 로그인 상태(토큰 발급 계정과 학습자 계정이 동일해야 함)
    student_id = settings.student_id
    classroom_id = common_data.student_classroom_id
    params = {
        "classroom_id": classroom_id,
    }

    # When : 수강생 학습 현황 조회 API를 호출
    response = dashboard_student_client.get(
        f"/student/{student_id}",
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

    # assert 3. 응답 body가 dict 형식인지 확인
    assert isinstance(body, dict), (
        f"응답 body가 dict 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    # assert 4. 응답 body에 필수 key가 모두 있는지 확인
    required_keys = [
        "account",
        "learning_progress",
        "test_score",
        "practice_score",
        "submit_cnt",
        "test_completed_cnt",
        "learning_completed",
    ]

    missing_keys = [
        key for key in required_keys
        if key not in body
    ]

    assert not missing_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. account가 dict 형식인지 확인
    assert isinstance(body["account"], dict), (
        f"account가 dict 형식이 아닙니다. "
        f"type={type(body['account']).__name__}, "
        f"value={body['account']}"
    )

    # assert 6. account 내부에 id가 있는지 확인
    assert "id" in body["account"], (
        f"account에 'id' 항목이 없습니다. "
        f"account_keys={list(body['account'].keys())}"
    )

    # assert 7. account.id와 .env의 학습자 ID가 동일한지 확인
    assert body["account"]["id"] == int(settings.student_id), (
        f"account.id가 .env의 student_id와 일치하지 않습니다. "
        f"actual={body['account']['id']}, expected={settings.student_id}"
    )

    # assert 8. learning_progress가 숫자로 변환 가능하고 0~100 범위인지 확인
    learning_progress = to_number(
        body["learning_progress"],
        "learning_progress",
    )

    assert learning_progress is not None, (
        "learning_progress 값이 None입니다."
    )

    assert 0 <= learning_progress <= 100, (
        f"learning_progress가 0~100 범위를 벗어났습니다. "
        f"learning_progress={body['learning_progress']}"
    )

    # assert 9. test_score가 None 또는 숫자로 변환 가능한 값인지 확인
    test_score = to_number(
        body["test_score"],
        "test_score",
    )

    if test_score is not None:
        assert 0 <= test_score <= 100, (
            f"test_score가 0~100 범위를 벗어났습니다. "
            f"test_score={body['test_score']}"
        )

    # assert 10. practice_score가 None 또는 숫자로 변환 가능한 값인지 확인
    practice_score = to_number(
        body["practice_score"],
        "practice_score",
    )

    if practice_score is not None:
        assert 0 <= practice_score <= 100, (
            f"practice_score가 0~100 범위를 벗어났습니다. "
            f"practice_score={body['practice_score']}"
        )

    # assert 11. submit_cnt가 int 형식이고 0 이상인지 확인
    assert isinstance(body["submit_cnt"], int), (
        f"submit_cnt가 int 형식이 아닙니다. "
        f"type={type(body['submit_cnt']).__name__}, "
        f"value={body['submit_cnt']}"
    )

    assert body["submit_cnt"] >= 0, (
        f"submit_cnt가 0보다 작습니다. "
        f"submit_cnt={body['submit_cnt']}"
    )

    # assert 12. test_completed_cnt가 int 형식이고 0 이상인지 확인
    assert isinstance(body["test_completed_cnt"], int), (
        f"test_completed_cnt가 int 형식이 아닙니다. "
        f"type={type(body['test_completed_cnt']).__name__}, "
        f"value={body['test_completed_cnt']}"
    )

    assert body["test_completed_cnt"] >= 0, (
        f"test_completed_cnt가 0보다 작습니다. "
        f"test_completed_cnt={body['test_completed_cnt']}"
    )

    # assert 13. learning_completed가 bool 형식인지 확인
    assert isinstance(body["learning_completed"], bool), (
        f"learning_completed가 bool 형식이 아닙니다. "
        f"type={type(body['learning_completed']).__name__}, "
        f"value={body['learning_completed']}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_010")
    print("status_code", response.status_code)
    print("(계정 ID)account.id:", body["account"]["id"])
    print("(학습 진행률)learning_progress:", body["learning_progress"])
    print("(테스트 평균 점수)test_score:", body["test_score"])
    print("(평균 실습 자료)practice_score:", body["practice_score"])
    print("submit_cnt:", body["submit_cnt"])
    print("test_completed_cnt:", body["test_completed_cnt"])
    print("(학습 완료 여부)learning_completed:", body["learning_completed"])


@pytest.mark.p2
def test_get_notification_stat(notification_student_client):
    # 우선순위 : P2
    # TC ID: TC_CLASSHOME_011
    # Postman에서 성공 확인한 알림 상태 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유)
        # When : 알림 상태 조회 API를 호출 : GET https://api-notification.elice.io/notification_stat
        # Then : response 결과 확인 : status_code가 200인지, body에 미확인 알림 개수가 있는지 확인
    # 입력값 : 없음

    # Given : 로그인 상태(유효한 학습자 토큰 보유)

    # When : 알림 상태 조회 API를 호출
    response = notification_student_client.get("/notification_stat")

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

    # assert 4. unchecked_count 항목이 있는지 확인
    assert "unchecked_count" in body, (
        f"응답 body에 'unchecked_count' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 5. unchecked_count가 int 형식인지 확인
    assert isinstance(body["unchecked_count"], int), (
        f"unchecked_count가 int 형식이 아닙니다. "
        f"type={type(body['unchecked_count']).__name__}, "
        f"value={body['unchecked_count']}"
    )

    # assert 6. unchecked_count가 0 이상인지 확인
    assert body["unchecked_count"] >= 0, (
        f"unchecked_count가 0보다 작습니다. "
        f"unchecked_count={body['unchecked_count']}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_011")
    print("status_code", response.status_code)
    print("(미확인 알림 개수)unchecked_count:", body["unchecked_count"])


@pytest.mark.p0
def test_get_session_count(org_student_client):
    # 우선순위 : P2
    # TC ID: TC_CLASSHOME_012
    # Postman에서 성공 확인한 세션 개수 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유)
        # When : 세션 개수 조회 API를 호출 : GET https://api-org.elice.io/session/count
        # Then : response 결과 확인 : status_code가 200인지, body가 세션 개수인지 확인
    # 입력값 : 없음

    # Given : 로그인 상태(유효한 학습자 토큰 보유)

    # When : 세션 개수 조회 API를 호출
    response = org_student_client.get("/session/count")

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

    # assert 4. 세션 개수가 0 이상인지 확인
    assert body >= 0, (
        f"세션 개수가 0보다 작습니다. "
        f"session_count={body}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_012")
    print("status_code", response.status_code)
    print("(세션 개수)session_count:", body)


@pytest.mark.p2
def test_get_account_cert_list(rest_student_client, settings):
    # 우선순위 : P2
    # TC ID: TC_CLASSHOME_013
    # Postman에서 성공 확인한 본인인증 정보 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 학습자 ID 보유
        # When : 본인인증 정보 조회 API를 호출 : GET https://api-rest.elice.io/global/account/cert/list/
        # Then : response 결과 확인 : status_code가 200인지, body에 본인인증 정보 목록이 있는지 확인
    # 입력값 : 학습자 ID, offset, count 준비 : student_id, 0, 1

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 학습자 ID 보유
    params = {
        "account_id": settings.student_id,
        "offset": 0,
        "count": 1,
    }

    # When : 본인인증 정보 조회 API를 호출
    response = rest_student_client.get(
        "/global/account/cert/list/",
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

    # assert 3. 응답 body가 dict 형식인지 확인
    assert isinstance(body, dict), (
        f"응답 body가 dict 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    # assert 4. 응답 body에 필수 key가 모두 있는지 확인
    required_keys = [
        "account_cert_info_count",
        "account_cert_info_list",
    ]

    missing_keys = [
        key for key in required_keys
        if key not in body
    ]

    assert not missing_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. account_cert_info_count가 int 형식이고 0 이상인지 확인
    assert isinstance(body["account_cert_info_count"], int), (
        f"account_cert_info_count가 int 형식이 아닙니다. "
        f"type={type(body['account_cert_info_count']).__name__}, "
        f"value={body['account_cert_info_count']}"
    )

    assert body["account_cert_info_count"] >= 0, (
        f"account_cert_info_count가 0보다 작습니다. "
        f"account_cert_info_count={body['account_cert_info_count']}"
    )

    # assert 6. account_cert_info_list가 list 형식인지 확인
    assert isinstance(body["account_cert_info_list"], list), (
        f"account_cert_info_list가 list 형식이 아닙니다. "
        f"type={type(body['account_cert_info_list']).__name__}, "
        f"value={body['account_cert_info_list']}"
    )

    # assert 7. 응답 목록 수가 요청 count 이하인지 확인
    assert len(body["account_cert_info_list"]) <= params["count"], (
        f"본인인증 정보 목록 수가 요청 count보다 많습니다. "
        f"actual={len(body['account_cert_info_list'])}, "
        f"expected_max={params['count']}"
    )

    # assert 8. 전체 본인인증 정보 개수가 현재 응답 목록 수보다 작지 않은지 확인
    assert body["account_cert_info_count"] >= len(body["account_cert_info_list"]), (
        f"전체 본인인증 정보 개수가 현재 응답 목록 수보다 작습니다. "
        f"account_cert_info_count={body['account_cert_info_count']}, "
        f"list_count={len(body['account_cert_info_list'])}"
    )

    # assert 9. 본인인증 정보가 있는 경우, 첫 번째 항목이 dict 형식인지 확인
    if body["account_cert_info_list"]:
        first_cert_info = body["account_cert_info_list"][0]

        assert isinstance(first_cert_info, dict), (
            f"첫 번째 본인인증 정보 항목이 dict 형식이 아닙니다. "
            f"type={type(first_cert_info).__name__}, "
            f"value={first_cert_info}"
        )

        assert len(first_cert_info.keys()) > 0, (
            f"첫 번째 본인인증 정보 항목에 key가 없습니다. "
            f"first_cert_info={first_cert_info}"
        )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_013")
    print("status_code", response.status_code)
    print("(본인인증 정보 개수)account_cert_info_count:", body["account_cert_info_count"])
    print("(본인인증 정보 목록 수)account_cert_info_list_count:", len(body["account_cert_info_list"]))

    if body["account_cert_info_list"]:
        print(
            "(첫 번째 본인인증 정보 key 목록)cert_info_keys:",
            list(body["account_cert_info_list"][0].keys()),
        )


@pytest.mark.p1
def test_get_global_account_detail(rest_student_client):
    # 우선순위 : P0
    # TC ID: TC_CLASSHOME_014
    # Postman에서 성공 확인한 현재 로그인 사용자 계정 상세 정보 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유)
        # When : 계정 상세 정보 조회 API를 호출 : GET https://api-rest.elice.io/global/account/get/
        # Then : response 결과 확인 : status_code가 200인지, body에 계정 상세 정보가 있는지 확인
    # 입력값 : 없음

    # Given : 로그인 상태(유효한 학습자 토큰 보유)

    # When : 계정 상세 정보 조회 API를 호출
    response = rest_student_client.get("/global/account/get/")

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

    # assert 4. 응답 body에 필수 key가 모두 있는지 확인
    required_body_keys = [
        "_result",
        "account",
        "account_login_info",
        "account_users",
    ]

    missing_body_keys = [
        key for key in required_body_keys
        if key not in body
    ]

    assert not missing_body_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_body_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. _result가 dict 형식인지 확인
    assert isinstance(body["_result"], dict), (
        f"_result가 dict 형식이 아닙니다. "
        f"type={type(body['_result']).__name__}, value={body['_result']}"
    )

    # assert 6. account가 dict 형식인지 확인
    assert isinstance(body["account"], dict), (
        f"account가 dict 형식이 아닙니다. "
        f"type={type(body['account']).__name__}, value={body['account']}"
    )

    account = body["account"]

    # assert 7. account에 필수 key가 모두 있는지 확인
    required_account_keys = [
        "id",
        "fullname",
        "email",
    ]

    missing_account_keys = [
        key for key in required_account_keys
        if key not in account
    ]

    assert not missing_account_keys, (
        f"account 항목에 필수 key가 없습니다. "
        f"missing_keys={missing_account_keys}, "
        f"account_keys={list(account.keys())}"
    )

    # assert 8. account.id가 int 또는 str 형식이고 빈 값이 아닌지 확인
    assert isinstance(account["id"], (int, str)), (
        f"account.id가 int 또는 str 형식이 아닙니다. "
        f"type={type(account['id']).__name__}, value={account['id']}"
    )

    assert str(account["id"]).strip() != "", (
        f"account.id 값이 비어 있습니다. "
        f"account.id={account['id']!r}"
    )

    # assert 9. account.fullname이 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(account["fullname"], str), (
        f"account.fullname이 str 형식이 아닙니다. "
        f"type={type(account['fullname']).__name__}, "
        f"value={account['fullname']}"
    )

    assert account["fullname"].strip() != "", (
        f"account.fullname 값이 비어 있습니다. "
        f"account.fullname={account['fullname']!r}"
    )

    # assert 10. account.email이 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(account["email"], str), (
        f"account.email이 str 형식이 아닙니다. "
        f"type={type(account['email']).__name__}, "
        f"value={account['email']}"
    )

    assert account["email"].strip() != "", (
        f"account.email 값이 비어 있습니다. "
        f"account.email={account['email']!r}"
    )

    # assert 11. account.email이 이메일 형식인지 확인
    assert "@" in account["email"], (
        f"account.email에 @가 없습니다. "
        f"account.email={account['email']}"
    )

    assert "." in account["email"].split("@")[-1], (
        f"account.email의 도메인 형식이 올바르지 않습니다. "
        f"account.email={account['email']}"
    )

    # assert 12. account_login_info가 dict 형식인지 확인
    assert isinstance(body["account_login_info"], dict), (
        f"account_login_info가 dict 형식이 아닙니다. "
        f"type={type(body['account_login_info']).__name__}, "
        f"value={body['account_login_info']}"
    )

    # assert 13. account_users가 list 형식인지 확인
    assert isinstance(body["account_users"], list), (
        f"account_users가 list 형식이 아닙니다. "
        f"type={type(body['account_users']).__name__}, "
        f"value={body['account_users']}"
    )

    # assert 14. account_users가 비어 있지 않은 경우, 첫 번째 항목이 dict 형식인지 확인
    if body["account_users"]:
        first_account_user = body["account_users"][0]

        assert isinstance(first_account_user, dict), (
            f"첫 번째 account_users 항목이 dict 형식이 아닙니다. "
            f"type={type(first_account_user).__name__}, "
            f"value={first_account_user}"
        )

        assert len(first_account_user.keys()) > 0, (
            f"첫 번째 account_users 항목에 key가 없습니다. "
            f"first_account_user={first_account_user}"
        )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_014")
    print("status_code", response.status_code)
    print("(계정 ID)account.id:", account["id"])
    print("(이름)account.fullname:", account["fullname"])
    print("(이메일)account.email:", account["email"])
    print("(로그인 정보)account_login_info:", body["account_login_info"])
    print("(조직 사용자 수)account_users_count:", len(body["account_users"]))

    if body["account_users"]:
        print(
            "(첫 번째 조직 사용자 key 목록)account_user_keys:",
            list(body["account_users"][0].keys()),
        )


@pytest.mark.p2
def test_get_global_organization_detail(rest_student_client):
    # 우선순위 : P1
    # TC ID: TC_CLASSHOME_015
    # Postman에서 성공 확인한 조직 상세 정보 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 조직 도메인 보유
        # When : 조직 정보 조회 API를 호출 : GET https://api-rest.elice.io/global/organization/get/?organization_domain=qatrack.elice.io
        # Then : response 결과 확인 : status_code가 200인지, body에 조직 상세 정보가 있는지 확인
    # 입력값 : 조직 도메인 준비 : qatrack.elice.io

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 조직 도메인 보유
    # TODO: organization_domain은 현재 TC 기준 임시 테스트 데이터다.
    # 추후 팀 기준에 따라 fixture 또는 별도 test data 파일로 이동할 수 있다.
    organization_domain = "qatrack.elice.io"
    params = {
        "organization_domain": organization_domain,
    }

    # When : 조직 정보 조회 API를 호출
    response = rest_student_client.get(
        "/global/organization/get/",
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

    # assert 3. 응답 body가 dict 형식인지 확인
    assert isinstance(body, dict), (
        f"응답 body가 dict 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    # assert 4. 응답 body에 필수 key가 모두 있는지 확인
    required_body_keys = [
        "_result",
        "organization",
    ]

    missing_body_keys = [
        key for key in required_body_keys
        if key not in body
    ]

    assert not missing_body_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_body_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. _result가 dict 형식인지 확인
    assert isinstance(body["_result"], dict), (
        f"_result가 dict 형식이 아닙니다. "
        f"type={type(body['_result']).__name__}, value={body['_result']}"
    )

    # assert 6. organization이 dict 형식인지 확인
    assert isinstance(body["organization"], dict), (
        f"organization이 dict 형식이 아닙니다. "
        f"type={type(body['organization']).__name__}, "
        f"value={body['organization']}"
    )

    organization = body["organization"]

    # assert 7. organization에 필수 key가 모두 있는지 확인
    required_organization_keys = [
        "id",
        "name",
        "name_short",
    ]

    missing_organization_keys = [
        key for key in required_organization_keys
        if key not in organization
    ]

    assert not missing_organization_keys, (
        f"organization 항목에 필수 key가 없습니다. "
        f"missing_keys={missing_organization_keys}, "
        f"organization_keys={list(organization.keys())}"
    )

    # assert 8. organization.id가 int 또는 str 형식이고 빈 값이 아닌지 확인
    assert isinstance(organization["id"], (int, str)), (
        f"organization.id가 int 또는 str 형식이 아닙니다. "
        f"type={type(organization['id']).__name__}, "
        f"value={organization['id']}"
    )

    assert str(organization["id"]).strip() != "", (
        f"organization.id 값이 비어 있습니다. "
        f"organization.id={organization['id']!r}"
    )

    # assert 9. organization.name이 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(organization["name"], str), (
        f"organization.name이 str 형식이 아닙니다. "
        f"type={type(organization['name']).__name__}, "
        f"value={organization['name']}"
    )

    assert organization["name"].strip() != "", (
        f"organization.name 값이 비어 있습니다. "
        f"organization.name={organization['name']!r}"
    )

    # assert 10. organization.name_short가 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(organization["name_short"], str), (
        f"organization.name_short가 str 형식이 아닙니다. "
        f"type={type(organization['name_short']).__name__}, "
        f"value={organization['name_short']}"
    )

    assert organization["name_short"].strip() != "", (
        f"organization.name_short 값이 비어 있습니다. "
        f"organization.name_short={organization['name_short']!r}"
    )

    # assert 11. organization.name_short가 기대 조직 short name과 일치하는지 확인
    # organization.domain은 현재 응답에서 None으로 내려오므로 식별 검증에는 name_short를 사용한다.
    assert organization["name_short"] == common_data.org_student, (
        f"조직 short name이 기대값과 일치하지 않습니다. "
        f"actual={organization.get('name_short')}, "
        f"expected={common_data.org_student}"
    )

    # assert 12. organization.domain이 있는 경우 None 또는 str 형식인지 확인
    if "domain" in organization:
        assert organization["domain"] is None or isinstance(organization["domain"], str), (
            f"organization.domain이 None 또는 str 형식이 아닙니다. "
            f"type={type(organization['domain']).__name__}, "
            f"value={organization['domain']}"
        )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_015")
    print("status_code", response.status_code)
    print("(조직 ID)organization.id:", organization["id"])
    print("(조직명)organization.name:", organization["name"])
    print("(조직 short name)organization.name_short:", organization.get("name_short"))
    print("(조직 도메인)organization.domain:", organization.get("domain"))


@pytest.mark.p2
def test_get_global_organization_unread_message_count(rest_student_client):
    # 우선순위 : P2
    # TC ID: TC_CLASSHOME_016
    # Postman에서 성공 확인한 조직 미확인 메시지 개수 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 조직 ID 보유
        # When : 조직 미확인 메시지 개수 조회 API를 호출 : GET https://api-rest.elice.io/global/organization/unread_message_count/get/
        # Then : response 결과 확인 : status_code가 200인지, body에 미확인 메시지 개수가 있는지 확인
    # 입력값 : 조직 ID 준비 : org_no_1

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 조직 ID 보유
    # TODO: org_no_1은 현재 TC 기준 임시 테스트 데이터다.
    org_no_1 = 4653
    params = {
        "organization_id": org_no_1,
    }

    # When : 조직 미확인 메시지 개수 조회 API를 호출
    response = rest_student_client.get(
        "/global/organization/unread_message_count/get/",
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

    # assert 3. 응답 body가 dict 형식인지 확인
    assert isinstance(body, dict), (
        f"응답 body가 dict 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    # assert 4. unread_message_count 항목이 있는지 확인
    assert "unread_message_count" in body, (
        f"응답 body에 'unread_message_count' 항목이 없습니다. "
        f"body keys={list(body.keys())}"
    )

    # assert 5. unread_message_count가 int 또는 숫자 문자열 형식인지 확인
    assert isinstance(body["unread_message_count"], (int, str)), (
        f"unread_message_count가 int 또는 str 형식이 아닙니다. "
        f"type={type(body['unread_message_count']).__name__}, "
        f"value={body['unread_message_count']}"
    )

    try:
        unread_message_count = int(body["unread_message_count"])
    except ValueError:
        pytest.fail(
            f"unread_message_count를 int로 변환할 수 없습니다. "
            f"value={body['unread_message_count']}"
        )

    # assert 6. unread_message_count가 0 이상인지 확인
    assert unread_message_count >= 0, (
        f"unread_message_count가 0보다 작습니다. "
        f"unread_message_count={body['unread_message_count']}"
    )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_016")
    print("status_code", response.status_code)
    print("(조직 ID)organization_id:", org_no_1)
    print("(미확인 메시지 개수)unread_message_count:", body["unread_message_count"])


@pytest.mark.p1
def test_get_org_user(rest_student_client):
    # 우선순위 : P1
    # TC ID: TC_CLASSHOME_017
    # Postman에서 성공 확인한 현재 로그인 사용자의 조직 내 사용자 정보 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 조직 정보 보유
        # When : 조직 사용자 정보 조회 API를 호출 : GET https://api-rest.elice.io/org/qatrack/user/get/
        # Then : response 결과 확인 : status_code가 200인지, body에 조직 사용자 정보가 있는지 확인
    # 입력값 : 조직명 준비 : qatrack

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 조직 정보 보유
    org = common_data.org_student

    # When : 조직 사용자 정보 조회 API를 호출
    response = rest_student_client.get(f"/org/{org}/user/get/")

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

    # assert 4. 응답 body에 필수 key가 모두 있는지 확인
    required_body_keys = [
        "_result",
        "user",
    ]

    missing_body_keys = [
        key for key in required_body_keys
        if key not in body
    ]

    assert not missing_body_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_body_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. _result가 dict 형식인지 확인
    assert isinstance(body["_result"], dict), (
        f"_result가 dict 형식이 아닙니다. "
        f"type={type(body['_result']).__name__}, "
        f"value={body['_result']}"
    )

    # assert 6. user가 dict 형식인지 확인
    assert isinstance(body["user"], dict), (
        f"user가 dict 형식이 아닙니다. "
        f"type={type(body['user']).__name__}, "
        f"value={body['user']}"
    )

    user = body["user"]

    # assert 7. user에 필수 key가 모두 있는지 확인
    required_user_keys = [
        "id",
        "fullname",
        "organization_id",
        "email",
    ]

    missing_user_keys = [
        key for key in required_user_keys
        if key not in user
    ]

    assert not missing_user_keys, (
        f"user 항목에 필수 key가 없습니다. "
        f"missing_keys={missing_user_keys}, "
        f"user_keys={list(user.keys())}"
    )

    # assert 8. user.id가 int 또는 str 형식이고 빈 값이 아닌지 확인
    assert isinstance(user["id"], (int, str)), (
        f"user.id가 int 또는 str 형식이 아닙니다. "
        f"type={type(user['id']).__name__}, "
        f"value={user['id']}"
    )

    assert str(user["id"]).strip() != "", (
        f"user.id 값이 비어 있습니다. "
        f"user.id={user['id']!r}"
    )

    # assert 9. user.fullname이 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(user["fullname"], str), (
        f"user.fullname이 str 형식이 아닙니다. "
        f"type={type(user['fullname']).__name__}, "
        f"value={user['fullname']}"
    )

    assert user["fullname"].strip() != "", (
        f"user.fullname 값이 비어 있습니다. "
        f"user.fullname={user['fullname']!r}"
    )

    # assert 10. user.organization_id가 int 또는 str 형식이고 빈 값이 아닌지 확인
    assert isinstance(user["organization_id"], (int, str)), (
        f"user.organization_id가 int 또는 str 형식이 아닙니다. "
        f"type={type(user['organization_id']).__name__}, "
        f"value={user['organization_id']}"
    )

    assert str(user["organization_id"]).strip() != "", (
        f"user.organization_id 값이 비어 있습니다. "
        f"user.organization_id={user['organization_id']!r}"
    )

    # assert 11. user.email이 str 형식이고 빈 문자열이 아닌지 확인
    assert isinstance(user["email"], str), (
        f"user.email이 str 형식이 아닙니다. "
        f"type={type(user['email']).__name__}, "
        f"value={user['email']}"
    )

    assert user["email"].strip() != "", (
        f"user.email 값이 비어 있습니다. "
        f"user.email={user['email']!r}"
    )

    # assert 12. user.email이 이메일 형식인지 확인
    assert "@" in user["email"], (
        f"user.email에 @가 없습니다. "
        f"user.email={user['email']}"
    )

    assert "." in user["email"].split("@")[-1], (
        f"user.email의 도메인 형식이 올바르지 않습니다. "
        f"user.email={user['email']}"
    )

    # assert 13. user.role이 있는 경우 None, int 또는 str 형식인지 확인
    if "role" in user:
        assert user["role"] is None or isinstance(user["role"], (int, str)), (
            f"user.role이 None, int 또는 str 형식이 아닙니다. "
            f"type={type(user['role']).__name__}, "
            f"value={user['role']}"
        )

        if isinstance(user["role"], int):
            assert user["role"] >= 0, (
                f"user.role 값이 0보다 작습니다. "
                f"role={user['role']}"
            )

        if isinstance(user["role"], str):
            assert user["role"].strip() != "", (
                f"user.role 문자열 값이 비어 있습니다. "
                f"role={user['role']!r}"
            )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_017")
    print("status_code", response.status_code)
    print("(조직 사용자 ID)user.id:", user["id"])
    print("(이름)user.fullname:", user["fullname"])
    print("(이메일)user.email:", user["email"])
    print("(조직 ID)user.organization_id:", user["organization_id"])
    print("(역할)user.role:", user.get("role"))


@pytest.mark.p2
def test_get_chat_room_list(rest_student_client):
    # 우선순위 : P2
    # TC ID: TC_CLASSHOME_018
    # Postman에서 성공 확인한 채팅방 목록 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 조직 정보 보유
        # When : 채팅방 목록 조회 API를 호출 : GET https://api-rest.elice.io/org/qatrack/chat/room/list/
        # Then : response 결과 확인 : status_code가 200인지, body에 채팅방 목록 정보가 있는지 확인
    # 입력값 : last_datetime, count 준비 : 1778843057656, 1

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 조직 정보 보유
    params = {
        "last_datetime": 1778843057656,
        "count": 1,
    }

    # When : 채팅방 목록 조회 API를 호출
    response = rest_student_client.get(
        f"/org/{common_data.org_student}/chat/room/list/",
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

    # assert 3. 응답 body가 dict 형식인지 확인
    assert isinstance(body, dict), (
        f"응답 body가 dict 형식이 아닙니다. "
        f"type={type(body).__name__}, body={body}"
    )

    # assert 4. 응답 body에 필수 key가 모두 있는지 확인
    required_body_keys = [
        "rooms",
        "room_count",
    ]

    missing_body_keys = [
        key for key in required_body_keys
        if key not in body
    ]

    assert not missing_body_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_body_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. rooms가 list 형식인지 확인
    assert isinstance(body["rooms"], list), (
        f"rooms가 list 형식이 아닙니다. "
        f"type={type(body['rooms']).__name__}, "
        f"value={body['rooms']}"
    )

    # assert 6. room_count가 int 또는 숫자 문자열 형식인지 확인
    assert isinstance(body["room_count"], (int, str)), (
        f"room_count가 int 또는 str 형식이 아닙니다. "
        f"type={type(body['room_count']).__name__}, "
        f"value={body['room_count']}"
    )

    try:
        room_count = int(body["room_count"])
    except ValueError:
        pytest.fail(
            f"room_count를 int로 변환할 수 없습니다. "
            f"value={body['room_count']}"
        )

    # assert 7. room_count가 0 이상인지 확인
    assert room_count >= 0, (
        f"room_count가 0보다 작습니다. "
        f"room_count={body['room_count']}"
    )

    # assert 8. 응답 채팅방 목록 수가 요청 count 이하인지 확인
    assert len(body["rooms"]) <= params["count"], (
        f"응답 채팅방 목록 수가 요청 count보다 많습니다. "
        f"actual={len(body['rooms'])}, expected_max={params['count']}"
    )

    # assert 9. 전체 채팅방 개수가 현재 응답 목록 수보다 작지 않은지 확인
    assert room_count >= len(body["rooms"]), (
        f"전체 채팅방 개수가 현재 응답 목록 수보다 작습니다. "
        f"room_count={room_count}, rooms_count={len(body['rooms'])}"
    )

    # 채팅방 목록이 없는 경우도 가능하므로 rooms가 있을 때만 상세 검증
    if body["rooms"]:
        first_room = body["rooms"][0]

        # assert 10. 첫 번째 채팅방 항목이 dict 형식인지 확인
        assert isinstance(first_room, dict), (
            f"첫 번째 채팅방 항목이 dict 형식이 아닙니다. "
            f"type={type(first_room).__name__}, value={first_room}"
        )

        # assert 11. 첫 번째 채팅방 항목에 필수 key가 모두 있는지 확인
        required_room_keys = [
            "title",
            "type",
        ]

        missing_room_keys = [
            key for key in required_room_keys
            if key not in first_room
        ]

        assert not missing_room_keys, (
            f"첫 번째 채팅방 항목에 필수 key가 없습니다. "
            f"missing_keys={missing_room_keys}, "
            f"room_keys={list(first_room.keys())}"
        )

        # assert 12. title이 None 또는 str 형식인지 확인
        # 1:1 채팅방 또는 시스템 채팅방에서는 title이 None일 가능성이 있어 허용
        assert first_room["title"] is None or isinstance(first_room["title"], str), (
            f"채팅방 title이 None 또는 str 형식이 아닙니다. "
            f"type={type(first_room['title']).__name__}, "
            f"value={first_room['title']}"
        )

        if isinstance(first_room["title"], str):
            assert first_room["title"].strip() != "", (
                f"채팅방 title 문자열이 비어 있습니다. "
                f"title={first_room['title']!r}"
            )

        # assert 13. type이 int 또는 str 형식이고 빈 값이 아닌지 확인
        assert isinstance(first_room["type"], (int, str)), (
            f"채팅방 type이 int 또는 str 형식이 아닙니다. "
            f"type={type(first_room['type']).__name__}, "
            f"value={first_room['type']}"
        )

        assert str(first_room["type"]).strip() != "", (
            f"채팅방 type 값이 비어 있습니다. "
            f"type={first_room['type']!r}"
        )

        # assert 14. 응답 목록 전체의 기본 구조 확인
        for room in body["rooms"]:
            assert isinstance(room, dict), (
                f"채팅방 항목이 dict 형식이 아닙니다. "
                f"type={type(room).__name__}, value={room}"
            )

            missing_keys = [
                key for key in required_room_keys
                if key not in room
            ]

            assert not missing_keys, (
                f"채팅방 항목에 필수 key가 없습니다. "
                f"missing_keys={missing_keys}, "
                f"room_keys={list(room.keys())}"
            )

            assert room["title"] is None or isinstance(room["title"], str), (
                f"채팅방 title이 None 또는 str 형식이 아닙니다. "
                f"room={room}, "
                f"type={type(room['title']).__name__}, "
                f"value={room['title']}"
            )

            if isinstance(room["title"], str):
                assert room["title"].strip() != "", (
                    f"채팅방 title 문자열이 비어 있습니다. "
                    f"title={room['title']!r}"
                )

            assert isinstance(room["type"], (int, str)), (
                f"채팅방 type이 int 또는 str 형식이 아닙니다. "
                f"room={room}, "
                f"type={type(room['type']).__name__}, "
                f"value={room['type']}"
            )

            assert str(room["type"]).strip() != "", (
                f"채팅방 type 값이 비어 있습니다. "
                f"type={room['type']!r}"
            )

    print("")
    print("")
    print("TC_NO:TC_CLASSHOME_018")
    print("status_code", response.status_code)
    print("(채팅방 개수)room_count:", body["room_count"])
    print("(채팅방 목록 수)rooms_count:", len(body["rooms"]))

    if body["rooms"]:
        first_room = body["rooms"][0]
        print("(첫 번째 채팅방 key 목록)room_keys:", list(first_room.keys()))
        print("(첫 번째 채팅방 제목)title:", first_room.get("title"))
        print("(첫 번째 채팅방 타입)type:", first_room.get("type"))

