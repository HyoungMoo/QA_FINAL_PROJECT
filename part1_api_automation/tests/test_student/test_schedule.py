
import pytest
from utils.api_client import APIClient
from utils.test_data import common_data

DT_START = "2026-04-16T15:00:00.000Z"
DT_END = "2026-06-14T14:59:59.999Z"


class TestSchedule:

    def test_schedule_list(self, student_client):
        """TC-SCH-001: 유효한 조건으로 수업 일정 목록이 정상 조회되는가"""
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 40,
            },
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_schedule_count(self, student_client):
        """TC-SCH-002: 기간 내 수업 일정 개수가 정상 조회되는가"""
        response = student_client.get(
            "/schedule/count",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
            },
        )
        assert response.status_code == 200
        assert isinstance(response.json(), (int, dict))

    def test_schedule_no_token(self, settings):
        """TC-SCH-004: 토큰 없이 요청 시 403을 반환하는가"""
        no_auth_client = APIClient(
            base_url=common_data.base_classroom_url,
            token=None,
            org_name=common_data.org,
            timeout=settings.request_timeout_seconds,
            min_interval=0.3,
        )
        response = no_auth_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 40,
            },
        )
        assert response.status_code == 403

    def test_schedule_invalid_classroom_id(self, student_client):
        """TC-SCH-005: 존재하지 않는 classroom_id로 요청 시 오류를 반환하는가"""
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": "00000000-0000-0000-0000-000000000000",
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 40,
            },
        )
        assert response.status_code in (409, 422)

    def test_schedule_missing_classroom_id(self, student_client):
        """TC-SCH-006: classroom_id 누락 시 422를 반환하는가"""
        response = student_client.get(
            "/schedule",
            params={
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 40,
            },
        )
        assert response.status_code == 422

    def test_schedule_reversed_date_range(self, student_client):
        """TC-SCH-007: dt_start_ge가 dt_start_le보다 늦을 때 오류를 반환하는가"""
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": DT_END,
                "dt_start_le": DT_START,
                "count": 40,
            },
        )
        assert response.status_code in (400, 409, 422)

    def test_schedule_same_date_range(self, student_client):
        """TC-SCH-008: dt_start_ge와 dt_start_le가 동일할 때 처리되는가"""
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": "2026-05-15T00:00:00.000Z",
                "dt_start_le": "2026-05-15T00:00:00.000Z",
                "count": 40,
            },
        )
        assert response.status_code in (200, 409)

    def test_schedule_invalid_date_format(self, student_client):
        """TC-SCH-009: 잘못된 날짜 형식 입력 시 422를 반환하는가"""
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": "2026/04/16",
                "dt_start_le": "2026/06/14",
                "count": 40,
            },
        )
        assert response.status_code == 422

    def test_schedule_count_zero(self, student_client):
        """TC-SCH-010: count=0 입력 시 처리되는가"""
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 0,
            },
        )
        assert response.status_code in (200, 409, 422)

    def test_schedule_count_large(self, student_client):
        """TC-SCH-011: count에 매우 큰 값 입력 시 처리되는가"""
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 99999,
            },
        )
        assert response.status_code in (200, 400, 409)


class TestScheduleIcs:

    def test_schedule_ics(self, student_client):
        """TC-SCH-003: 수업 일정을 ICS 형식으로 정상 다운로드할 수 있는가"""
        response = student_client.get(
            "/schedule/ics",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "offset": 0,
                "count": 40,
                "timezone": "Asia/Seoul",
            },
        )
        assert response.status_code == 200
        assert "text/calendar" in response.headers.get("content-type", "")
        assert "BEGIN:VCALENDAR" in response.text

    def test_schedule_ics_no_token(self, settings):
        """TC-SCH-012: 토큰 없이 ICS 요청 시 403을 반환하는가"""
        no_auth_client = APIClient(
            base_url=common_data.base_classroom_url,
            token=None,
            org_name=common_data.org,
            timeout=settings.request_timeout_seconds,
            min_interval=0.3,
        )
        response = no_auth_client.get(
            "/schedule/ics",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "offset": 0,
                "count": 40,
                "timezone": "Asia/Seoul",
            },
        )
        assert response.status_code == 403

    def test_schedule_ics_invalid_classroom(self, student_client):
        """TC-SCH-013: 존재하지 않는 classroom_id로 ICS 요청 시 오류를 반환하는가"""
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
        assert response.status_code == 409

    def test_schedule_ics_invalid_timezone(self, student_client):
        """TC-SCH-014: 유효하지 않은 timezone 입력 시 422를 반환하는가"""
        response = student_client.get(
            "/schedule/ics",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "offset": 0,
                "count": 40,
                "timezone": "Invalid/Zone",
            },
        )
        assert response.status_code in (409, 422)

    def test_schedule_ics_no_schedules_in_range(self, student_client):
        """TC-SCH-015: 일정이 없는 기간 조회 시 처리되는가"""
        response = student_client.get(
            "/schedule/ics",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": "2020-01-01T00:00:00.000Z",
                "dt_start_le": "2020-01-31T00:00:00.000Z",
                "offset": 0,
                "count": 40,
                "timezone": "Asia/Seoul",
            },
        )
        assert response.status_code in (200, 409)


class TestSchedulePermission:

    def test_student_cannot_create_schedule(self, student_client):
        """TC-SCH-016: 학습자 토큰으로 일정 생성 시 403을 반환하는가"""
        response = student_client.request(
            "POST",
            "/schedule",
            json={
                "classroom_id": common_data.classroom_id,
                "summary": "test",
                "dt_start": "2026-05-20T09:00:00.000Z",
                "dt_end": "2026-05-20T10:00:00.000Z",
            },
        )
        assert response.status_code == 403

    def test_student_cannot_update_schedule(self, student_client):
        """TC-SCH-017: 학습자 토큰으로 일정 수정 시 403을 반환하는가"""
        list_response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 40,
            },
        )
        schedules = list_response.json()
        if not schedules:
            pytest.skip("조회된 일정이 없어 테스트를 건너뜁니다.")

        schedule_id = schedules[0]["id"]
        response = student_client.request(
            "PATCH",
            f"/schedule/{schedule_id}",
            json={
                "classroom_id": common_data.classroom_id,
                "summary": "hacked",
            },
        )
        assert response.status_code == 403

    def test_student_cannot_delete_schedule(self, student_client):
        """TC-SCH-018: 학습자 토큰으로 일정 삭제 시 403을 반환하는가"""
        list_response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 40,
            },
        )
        schedules = list_response.json()
        if not schedules:
            pytest.skip("조회된 일정이 없어 테스트를 건너뜁니다.")

        schedule_id = schedules[0]["id"]
        response = student_client.request(
            "DELETE",
            f"/schedule/{schedule_id}",
            json={"classroom_id": common_data.classroom_id},
        )
        assert response.status_code == 403
