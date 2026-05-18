# 수강생 권한으로 접근 가능한 API 테스트를 작성하는 파일
#
# 예: 클래스 정보 조회, 과목 목록 조회, 일정 조회, 게시판 목록 조회 등
# Postman에서 먼저 호출이 성공한 API를 기준으로 pytest 테스트를 추가한다.
#
# 공통 client는 tests/conftest.py의 student_client fixture를 사용한다.

import pytest


class TestSchedule:

    def test_schedule_list(self, student_client, settings):
        """수업 일정 진입 시 학습자의 수업 일정 목록이 정상 조회되는가?"""
        response = student_client.get(
            "/schedule",
            params={
                "classroom_id": settings.classroom_id,
                "dt_start_ge": "2026-04-16T15:00:00.000Z",
                "dt_start_le": "2026-06-14T14:59:59.999Z",
                "count": 40,
            },
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_schedule_by_date(self, student_client, settings):
        """날짜를 지정하면 해당 날짜의 수업 일정 목록이 정상 조회되는가?"""
        response = student_client.get(
            "/schedule/by_date",
            params={
                "classroom_id": settings.classroom_id,
                "date": "2026-05-15",
            },
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_schedule_count(self, student_client, settings):
        """기간 내 수업 일정 개수가 정상 조회되는가?"""
        response = student_client.get(
            "/schedule/count",
            params={
                "classroom_id": settings.classroom_id,
                "dt_start_ge": "2026-04-16T15:00:00.000Z",
                "dt_start_le": "2026-06-14T14:59:59.999Z",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (int, dict))

    def test_schedule_summary(self, student_client, settings):
        """기간 내 수업 일정 요약 정보가 정상 조회되는가?"""
        response = student_client.get(
            "/schedule/summary",
            params={
                "classroom_id": settings.classroom_id,
                "dt_start_ge": "2026-04-16T15:00:00.000Z",
                "dt_start_le": "2026-06-14T14:59:59.999Z",
            },
        )
        assert response.status_code == 200
        assert isinstance(response.json(), (dict, list))

    def test_schedule_detail(self, student_client, settings):
        """특정 수업 일정의 상세 정보가 정상 조회되는가?"""
        list_response = student_client.get(
            "/schedule",
            params={
                "classroom_id": settings.classroom_id,
                "dt_start_ge": "2026-04-16T15:00:00.000Z",
                "dt_start_le": "2026-06-14T14:59:59.999Z",
            },
        )
        schedules = list_response.json()
        if not schedules:
            pytest.skip("조회된 일정이 없어 상세 테스트를 건너뜁니다.")

        schedule_id = schedules[0]["id"]
        response = student_client.get(f"/schedule/{schedule_id}")
        assert response.status_code == 200
        assert response.json()["id"] == schedule_id


class TestScheduleIcs:

    def test_schedule_ics(self, student_client, settings):
        """수업 일정을 ICS 캘린더 형식으로 정상 다운로드할 수 있는가?"""
        response = student_client.get(
            "/schedule/ics",
            params={
                "classroom_id": settings.classroom_id,
                "dt_start_ge": "2026-04-16T15:00:00.000Z",
                "dt_start_le": "2026-06-14T14:59:59.999Z",
                "offset": 0,
                "count": 40,
                "timezone": "Asia/Seoul",
            },
        )
        assert response.status_code == 200
        assert "text/calendar" in response.headers.get("content-type", "")
        assert "BEGIN:VCALENDAR" in response.text

    def test_schedule_ics_no_token(self, settings):
        """토큰 없이 ICS 요청 시 401을 반환하는가?"""
        from utils.api_client import APIClient
        no_auth_client = APIClient(
            base_url=settings.classroom_base_url,
            token=None,
            org_name=settings.org_name,
            timeout=settings.request_timeout_seconds,
            min_interval=settings.min_request_interval_seconds,
        )
        response = no_auth_client.get(
            "/schedule/ics",
            params={
                "classroom_id": settings.classroom_id,
                "dt_start_ge": "2026-04-16T15:00:00.000Z",
                "dt_start_le": "2026-06-14T14:59:59.999Z",
                "offset": 0,
                "count": 40,
                "timezone": "Asia/Seoul",
            },
        )
        assert response.status_code == 401

    def test_schedule_ics_invalid_classroom(self, student_client):
        """존재하지 않는 classroom_id로 ICS 요청 시 404를 반환하는가?"""
        response = student_client.get(
            "/schedule/ics",
            params={
                "classroom_id": "00000000-0000-0000-0000-000000000000",
                "dt_start_ge": "2026-04-16T15:00:00.000Z",
                "dt_start_le": "2026-06-14T14:59:59.999Z",
                "offset": 0,
                "count": 40,
                "timezone": "Asia/Seoul",
            },
        )
        assert response.status_code in (403, 404)
