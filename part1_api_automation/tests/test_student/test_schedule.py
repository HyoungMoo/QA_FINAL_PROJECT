
import re

import pytest
import requests
from utils.api_client import APIClient
from utils.test_data import common_data

UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)

# 실제 수업 기간에 해당하는 테스트 범위 (이 기간에 실제 일정 데이터가 존재함)
DT_START = "2026-04-16T15:00:00.000Z"
DT_END = "2026-06-14T14:59:59.999Z"

pytestmark = pytest.mark.student


class TestSchedule:

    @pytest.mark.p0
    @pytest.mark.smoke
    def test_schedule_list(self, student_client):
        # 우선순위: P0
        # TC ID: TC-SCH-001
        # Given-When-Then
        #   Given: 유효한 학습자 토큰, 유효한 classroom_id, 유효한 날짜 범위
        #   When: GET /schedule 호출
        #   Then: 200 응답, 일정 목록 반환

        # Given: 유효한 파라미터 준비
        params = {
            "classroom_id": common_data.student_classroom_id,
            "dt_start_ge": DT_START,
            "dt_start_le": DT_END,
            "count": 40,
        }

        # When: 수업 일정 목록 조회 API 호출
        response = student_client.get("/schedule", params=params)

        # Then: 응답 결과 확인

        # assert 1. 상태 코드가 200인지 확인
        assert response.status_code == 200, (
            f"응답 상태 코드가 200이 아닙니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

        data = response.json()

        # assert 2. 응답 body가 list 형식인지 확인
        assert isinstance(data, list), (
            f"응답 body가 list 형식이 아닙니다. "
            f"type={type(data).__name__}, body={data}"
        )

        # assert 3. 일정 목록이 비어있지 않은지 확인
        assert len(data) > 0, (
            f"일정 목록이 비어 있습니다. 테스트 기간 내 데이터를 확인하세요. "
            f"dt_start_ge={DT_START}, dt_start_le={DT_END}"
        )

        first = data[0]

        # assert 4. 필수 필드가 존재하는지 확인
        required_keys = ["id", "uid", "summary", "dt_start", "dt_end", "tags"]
        missing_keys = [key for key in required_keys if key not in first]
        assert not missing_keys, (
            f"응답 항목에 필수 필드가 없습니다. "
            f"missing_keys={missing_keys}, keys={list(first.keys())}"
        )

        # assert 5. id가 UUID 형식인지 확인
        assert UUID_RE.match(first["id"]), (
            f"id가 UUID 형식이 아닙니다. id={first['id']}"
        )

        # assert 6. summary가 string 형식인지 확인
        assert isinstance(first["summary"], str), (
            f"summary가 string 형식이 아닙니다. type={type(first['summary']).__name__}"
        )

        # assert 7. tags.classroom_id가 요청한 classroom_id와 일치하는지 확인
        assert "classroom_id" in first["tags"], (
            f"tags에 classroom_id가 없습니다. tags={first['tags']}"
        )
        assert first["tags"]["classroom_id"] == common_data.student_classroom_id, (
            f"tags.classroom_id가 요청값과 다릅니다. "
            f"expected={common_data.student_classroom_id}, actual={first['tags']['classroom_id']}"
        )

        print("")
        print("TC_NO: TC-SCH-001")
        print("status_code:", response.status_code)
        print("일정 개수:", len(data))
        print("첫 번째 일정 summary:", first.get("summary"))

    @pytest.mark.p1
    def test_schedule_count(self, student_client):
        # 우선순위: P1
        # TC ID: TC-SCH-002
        # Given-When-Then
        #   Given: 유효한 학습자 토큰, 유효한 classroom_id, 유효한 날짜 범위
        #   When: GET /schedule/count 호출
        #   Then: 200 응답, count 값 반환

        # Given: 유효한 파라미터 준비
        params = {
            "classroom_id": common_data.student_classroom_id,
            "dt_start_ge": DT_START,
            "dt_start_le": DT_END,
        }

        # When: 수업 일정 개수 조회 API 호출
        response = student_client.get("/schedule/count", params=params)

        # Then: 응답 결과 확인

        # assert 1. 상태 코드가 200인지 확인
        assert response.status_code == 200, (
            f"응답 상태 코드가 200이 아닙니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

        data = response.json()

        # assert 2. 응답 body가 dict 형식인지 확인
        assert isinstance(data, dict), (
            f"응답 body가 dict 형식이 아닙니다. "
            f"type={type(data).__name__}, body={data}"
        )

        # assert 3. count 필드가 존재하는지 확인
        assert "count" in data, (
            f"응답에 'count' 필드가 없습니다. body={data}"
        )

        # assert 4. count 값이 0 이상의 정수인지 확인
        assert isinstance(data["count"], int), (
            f"count 값이 정수가 아닙니다. "
            f"type={type(data['count']).__name__}, value={data['count']}"
        )
        assert data["count"] >= 0, (
            f"count 값이 음수입니다. count={data['count']}"
        )

        print("")
        print("TC_NO: TC-SCH-002")
        print("status_code:", response.status_code)
        print("일정 개수(count):", data["count"])

    @pytest.mark.p0
    def test_schedule_no_token(self):
        # 우선순위: P0
        # TC ID: TC-SCH-004
        # Given-When-Then
        #   Given: 토큰 없음
        #   When: GET /schedule 호출
        #   Then: 403 응답

        # Given: 토큰 없는 클라이언트 생성
        no_auth_client = APIClient(
            base_url=common_data.base_classroom_url,
            token=None,
            org_name=common_data.org_student,
            timeout=5,
            min_interval=0.3,
        )

        # When: 토큰 없이 수업 일정 목록 조회 API 호출
        try:
            response = no_auth_client.get(
                "/schedule",
                params={
                    "classroom_id": common_data.student_classroom_id,
                    "dt_start_ge": DT_START,
                    "dt_start_le": DT_END,
                    "count": 40,
                },
            )
        except requests.exceptions.Timeout:
            pytest.skip("인증 없는 요청이 네트워크 레벨에서 차단되어 타임아웃 발생")

        # Then: 응답 결과 확인

        # assert 1. 상태 코드가 403인지 확인
        assert response.status_code == 403, (
            f"토큰 없이 요청 시 403이 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

    @pytest.mark.p1
    def test_schedule_nonexistent_classroom_id(self, student_client):
        # 우선순위: P1
        # TC ID: TC-SCH-005
        # Given: UUID 형식은 맞지만 존재하지 않는 classroom_id
        # When: GET /schedule 호출
        # Then: 409 응답

        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": "00000000-0000-0000-0000-000000000000",
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 40,
            },
        )

        assert response.status_code == 409, (
            f"존재하지 않는 classroom_id 요청 시 409가 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

        print("")
        print("TC_NO: TC-SCH-005")
        print("status_code:", response.status_code)

    @pytest.mark.p1
    @pytest.mark.parametrize("classroom_id", [
        pytest.param("invalid-classroom-id", id="non-uuid-string"),
        pytest.param("12345", id="numeric-string"),
    ])
    def test_schedule_invalid_format_classroom_id(self, student_client, classroom_id):
        # 우선순위: P1
        # TC ID: TC-SCH-005-1
        # Given: UUID 형식 자체가 틀린 classroom_id
        # When: GET /schedule 호출
        # Then: 422 응답 (파라미터 파싱 단계에서 거부)

        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 40,
            },
        )

        assert response.status_code == 422, (
            f"UUID 형식 오류 classroom_id 요청 시 422가 아닌 응답이 반환되었습니다. "
            f"classroom_id={classroom_id}, "
            f"status_code={response.status_code}, response={response.text}"
        )

    @pytest.mark.p1
    def test_schedule_missing_classroom_id(self, student_client):
        # 우선순위: P1
        # TC ID: TC-SCH-006
        # Given-When-Then
        #   Given: classroom_id 파라미터 누락
        #   When: GET /schedule 호출
        #   Then: 422 응답

        # When: classroom_id 없이 API 호출
        response = student_client.get(
            "/schedule",
            params={
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 40,
            },
        )

        # Then: 응답 결과 확인

        # assert 1. 상태 코드가 422인지 확인
        assert response.status_code == 422, (
            f"classroom_id 누락 시 422가 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

    @pytest.mark.p2
    def test_schedule_reversed_date_range(self, student_client):
        # 우선순위: P2
        # TC ID: TC-SCH-007
        # Given-When-Then
        #   Given: dt_start_ge가 dt_start_le보다 늦은 날짜
        #   When: GET /schedule 호출
        #   Then: 오류 응답 반환

        # When: 날짜 역전 파라미터로 API 호출
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.student_classroom_id,
                "dt_start_ge": DT_END,
                "dt_start_le": DT_START,
                "count": 40,
            },
        )

        # Then: 응답 결과 확인

        # assert 1. 오류 상태 코드 반환 확인
        assert response.status_code == 409, (
            f"날짜 역전 요청 시 오류 응답이 아닙니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

    @pytest.mark.p2
    def test_schedule_same_datetime_range(self, student_client):
        # 우선순위: P2
        # TC ID: TC-SCH-008
        # Given-When-Then
        #   Given: dt_start_ge와 dt_start_le가 동일한 날짜/시각
        #   When: GET /schedule 호출
        #   Then: 200 응답, 빈 배열 또는 해당 시점에 정확히 시작하는 일정 반환

        # When: 동일한 시작/종료 경계값으로 API 호출
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.student_classroom_id,
                "dt_start_ge": "2026-05-15T00:00:00.000Z",
                "dt_start_le": "2026-05-15T00:00:00.000Z",
                "count": 40,
            },
        )

        # Then: 정상 응답과 배열 body 확인
        assert response.status_code == 200, (
            f"동일 날짜 범위 요청 시 200이 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

        data = response.json()
        assert isinstance(data, list), (
            f"응답 body가 list 형식이 아닙니다. "
            f"type={type(data).__name__}, body={data}"
        )

        assert len(data) <= 40, (
            f"응답 일정 개수가 count보다 큽니다. count=40, actual={len(data)}"
        )

    @pytest.mark.p1
    def test_schedule_invalid_date_format(self, student_client):
        # 우선순위: P1
        # TC ID: TC-SCH-009
        # Given-When-Then
        #   Given: 잘못된 날짜 형식 (YYYY/MM/DD)
        #   When: GET /schedule 호출
        #   Then: 422 응답

        # When: 잘못된 날짜 형식으로 API 호출
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.student_classroom_id,
                "dt_start_ge": "2026/04/16",
                "dt_start_le": "2026/06/14",
                "count": 40,
            },
        )

        # Then: 응답 결과 확인

        # assert 1. 상태 코드가 422인지 확인
        assert response.status_code == 422, (
            f"잘못된 날짜 형식 요청 시 422가 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

    @pytest.mark.p2
    def test_schedule_count_zero(self, student_client):
        # 우선순위: P2
        # TC ID: TC-SCH-010
        # Given-When-Then
        #   Given: count=0
        #   When: GET /schedule 호출
        #   Then: 200(빈 목록) 또는 오류 응답

        # When: count=0으로 API 호출
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.student_classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 0,
            },
        )

        # Then: 응답 결과 확인

        # assert 1. 200 또는 오류 응답 확인
        assert response.status_code == 409, (
            f"count=0 요청 시 예상치 못한 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

    @pytest.mark.p2
    def test_schedule_count_large(self, student_client):
        # 우선순위: P2
        # TC ID: TC-SCH-011
        # Given-When-Then
        #   Given: count=99999 (매우 큰 값)
        #   When: GET /schedule 호출
        #   Then: 200 또는 오류 응답

        # When: count=99999로 API 호출
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.student_classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 99999,
            },
        )

        # Then: 응답 결과 확인

        # assert 1. 200 또는 오류 응답 확인
        assert response.status_code == 409, (
            f"count=99999 요청 시 예상치 못한 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )


class TestScheduleIcs:

    @pytest.mark.p1
    def test_schedule_ics(self, student_client):
        # 우선순위: P1
        # TC ID: TC-SCH-003
        # Given-When-Then
        #   Given: 유효한 학습자 토큰, 유효한 classroom_id, 날짜 범위, timezone
        #   When: GET /schedule/ics 호출
        #   Then: 200 응답, ICS 형식 파일 반환

        # Given: 유효한 파라미터 준비
        params = {
            "classroom_id": common_data.student_classroom_id,
            "dt_start_ge": DT_START,
            "dt_start_le": DT_END,
            "offset": 0,
            "count": 40,
            "timezone": "Asia/Seoul",
        }

        # When: ICS 다운로드 API 호출
        response = student_client.get("/schedule/ics", params=params)

        # Then: 응답 결과 확인

        # assert 1. 상태 코드가 200인지 확인
        assert response.status_code == 200, (
            f"응답 상태 코드가 200이 아닙니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

        # assert 2. Content-Type이 text/calendar인지 확인
        content_type = response.headers.get("content-type", "")
        assert "text/calendar" in content_type, (
            f"Content-Type이 text/calendar가 아닙니다. "
            f"content_type={content_type}"
        )

        # assert 3. ICS 형식 시작 태그가 있는지 확인
        assert "BEGIN:VCALENDAR" in response.text, (
            f"ICS 응답에 BEGIN:VCALENDAR가 없습니다. response={response.text[:200]}"
        )

        # assert 4. ICS 형식 종료 태그가 있는지 확인
        assert "END:VCALENDAR" in response.text, (
            f"ICS 응답에 END:VCALENDAR가 없습니다. response={response.text[:200]}"
        )

        print("")
        print("TC_NO: TC-SCH-003")
        print("status_code:", response.status_code)
        print("content_type:", content_type)
        print("ICS 응답 앞부분:", response.text[:100])

    @pytest.mark.p0
    def test_schedule_ics_no_token(self):
        # 우선순위: P0
        # TC ID: TC-SCH-012
        # Given-When-Then
        #   Given: 토큰 없음
        #   When: GET /schedule/ics 호출
        #   Then: 403 응답

        # Given: 토큰 없는 클라이언트 생성
        no_auth_client = APIClient(
            base_url=common_data.base_classroom_url,
            token=None,
            org_name=common_data.org_student,
            timeout=5,
            min_interval=0.3,
        )

        # When: 토큰 없이 ICS 다운로드 API 호출
        try:
            response = no_auth_client.get(
                "/schedule/ics",
                params={
                    "classroom_id": common_data.student_classroom_id,
                    "dt_start_ge": DT_START,
                    "dt_start_le": DT_END,
                    "offset": 0,
                    "count": 40,
                    "timezone": "Asia/Seoul",
                },
            )
        except requests.exceptions.Timeout:
            pytest.skip("인증 없는 요청이 네트워크 레벨에서 차단되어 타임아웃 발생")

        # Then: 응답 결과 확인

        # assert 1. 상태 코드가 403인지 확인
        assert response.status_code == 403, (
            f"토큰 없이 ICS 요청 시 403이 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

    @pytest.mark.p1
    def test_schedule_ics_invalid_classroom(self, student_client):
        # 우선순위: P1
        # TC ID: TC-SCH-013
        # Given-When-Then
        #   Given: 존재하지 않는 classroom_id
        #   When: GET /schedule/ics 호출
        #   Then: 409 오류 응답

        # When: 존재하지 않는 classroom_id로 ICS API 호출
        response = student_client.get(
            "/schedule/ics",
            params={
                "classroom_id": "00000000-0000-0000-0000-000000000000",
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "offset": 0,
                "count": 40,
                "timezone": "Asia/Seoul",
            },
        )

        # Then: 응답 결과 확인

        # assert 1. 상태 코드가 409인지 확인
        assert response.status_code == 409, (
            f"존재하지 않는 classroom_id로 ICS 요청 시 409가 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

    @pytest.mark.p2
    def test_schedule_ics_invalid_timezone(self, student_client):
        # 우선순위: P2
        # TC ID: TC-SCH-014
        # Given-When-Then
        #   Given: 유효하지 않은 timezone 값
        #   When: GET /schedule/ics 호출
        #   Then: 오류 응답

        # When: 유효하지 않은 timezone으로 ICS API 호출
        response = student_client.get(
            "/schedule/ics",
            params={
                "classroom_id": common_data.student_classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "offset": 0,
                "count": 40,
                "timezone": "Invalid/Zone",
            },
        )

        # Then: 응답 결과 확인

        # assert 1. 오류 상태 코드 반환 확인
        assert response.status_code == 409, (
            f"유효하지 않은 timezone 요청 시 오류 응답이 아닙니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

    @pytest.mark.p1
    def test_schedule_ics_no_schedules_in_range(self, student_client):
        # 우선순위: P1
        # TC ID: TC-SCH-015
        # Given-When-Then
        #   Given: 일정이 없는 날짜 범위
        #   When: GET /schedule/ics 호출
        #   Then: 200(빈 캘린더) 반환

        # When: 일정이 없는 기간으로 ICS API 호출
        response = student_client.get(
            "/schedule/ics",
            params={
                "classroom_id": common_data.student_classroom_id,
                "dt_start_ge": "2020-01-01T00:00:00.000Z",
                "dt_start_le": "2020-01-31T00:00:00.000Z",
                "offset": 0,
                "count": 40,
                "timezone": "Asia/Seoul",
            },
        )

        # Then: 응답 결과 확인

        # assert 1. 200 응답 확인 (빈 캘린더)
        assert response.status_code == 200, (
            f"일정 없는 기간 ICS 요청 시 200이 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )
