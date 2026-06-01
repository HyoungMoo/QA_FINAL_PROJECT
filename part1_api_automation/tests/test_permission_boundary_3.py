# 권한 경계 관련 테스트를 작성하는 파일
# 구형모

import pytest
from utils.test_data import common_data

DT_START = "2026-04-16T15:00:00.000Z"
DT_END = "2026-06-14T14:59:59.999Z"


class TestSchedulePermission:

    @pytest.mark.p0
    def test_student_cannot_create_schedule(self, student_client):
        # 우선순위: P0
        # TC ID: TC-SCH-016
        # Given: 학습자 토큰, 일정 생성 요청 데이터
        # When: POST /schedule 호출
        # Then: 403 응답 (학습자는 생성 권한 없음)

        response = student_client.request(
            "POST",
            "/schedule",
            json={
                "classroom_id": common_data.student_classroom_id,
                "summary": "test",
                "dt_start": "2026-05-20T09:00:00.000Z",
                "dt_end": "2026-05-20T10:00:00.000Z",
            },
        )

        assert response.status_code == 403, (
            f"학습자 토큰으로 일정 생성 시 403이 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

    @pytest.mark.p0
    @pytest.mark.parametrize("method,extra_body", [
        pytest.param("PATCH", {"summary": "hacked"}, id="TC-SCH-017-update"),
        pytest.param("DELETE", {}, id="TC-SCH-018-delete"),
    ])
    def test_student_cannot_modify_schedule(self, student_client, method, extra_body):
        # 우선순위: P0
        # TC ID: TC-SCH-017 (PATCH), TC-SCH-018 (DELETE)
        # Given: 학습자 토큰, 기존 일정 ID
        # When: PATCH 또는 DELETE /schedule/{id} 호출
        # Then: 403 응답 (학습자는 수정/삭제 권한 없음)

        list_response = student_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.student_classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 40,
            },
        )
        schedules = list_response.json()
        if not schedules:
            pytest.skip("조회된 일정이 없어 테스트를 건너뜁니다.")

        schedule_id = schedules[0]["id"]

        body = {"classroom_id": common_data.student_classroom_id, **extra_body}
        response = student_client.request(method, f"/schedule/{schedule_id}", json=body)

        assert response.status_code == 403, (
            f"학습자 토큰으로 {method} 요청 시 403이 아닌 응답이 반환되었습니다. "
            f"schedule_id={schedule_id}, "
            f"status_code={response.status_code}, response={response.text}"
        )
