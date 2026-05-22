
import pytest
from utils.test_data import common_data

DT_START = "2026-04-16T15:00:00.000Z"
DT_END = "2026-06-14T14:59:59.999Z"

SCHEDULE_SUMMARY = "TC-TSCH 테스트 일정"


@pytest.fixture(scope="module")
def created_schedule_id(teacher_client):
    # 테스트용 일정 생성 후 id 반환, 테스트 완료 후 삭제
    teacher_client.request(
        "POST",
        "/schedule",
        json={
            "classroom_id": common_data.teacher_classroom_id,
            "summary": SCHEDULE_SUMMARY,
            "dt_start": "2026-05-21T09:00:00.000Z",
            "dt_end": "2026-05-21T10:00:00.000Z",
            "classroom_time_zone": "KST",
        },
    )

    list_response = teacher_client.get(
        "/schedule",
        params={
            "classroom_id": common_data.teacher_classroom_id,
            "dt_start_ge": "2026-05-21T00:00:00.000Z",
            "dt_start_le": "2026-05-21T23:59:59.999Z",
            "count": 40,
        },
    )
    schedules = list_response.json()
    schedule = next((s for s in schedules if s.get("summary") == SCHEDULE_SUMMARY), None)
    assert schedule is not None, "생성한 테스트 일정을 찾을 수 없습니다."

    schedule_id = schedule["id"]
    yield schedule_id

    teacher_client.request(
        "DELETE",
        f"/schedule/{schedule_id}",
        json={"classroom_id": common_data.teacher_classroom_id},
    )


class TestTeacherSchedule:

    @pytest.mark.p0
    def test_schedule_list(self, teacher_client):
        # 우선순위: P0
        # TC ID: TC-TSCH-001
        # Given-When-Then
        #   Given: 유효한 교육자 토큰, 유효한 classroom_id, 유효한 날짜 범위
        #   When: GET /schedule 호출
        #   Then: 200 응답, 일정 목록 반환

        params = {
            "classroom_id": common_data.teacher_classroom_id,
            "dt_start_ge": DT_START,
            "dt_start_le": DT_END,
            "count": 40,
        }

        response = teacher_client.get("/schedule", params=params)

        assert response.status_code == 200, (
            f"응답 상태 코드가 200이 아닙니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

        data = response.json()

        assert isinstance(data, list), (
            f"응답 body가 list 형식이 아닙니다. type={type(data).__name__}"
        )

        if data:
            required_keys = ["id", "summary", "dt_start", "dt_end", "tags"]
            missing_keys = [k for k in required_keys if k not in data[0]]
            assert not missing_keys, (
                f"응답 항목에 필수 필드가 없습니다. missing_keys={missing_keys}"
            )

        print("")
        print("TC_NO: TC-TSCH-001")
        print("status_code:", response.status_code)
        print("일정 개수:", len(data))

    @pytest.mark.p0
    def test_schedule_create(self, created_schedule_id):
        # 우선순위: P0
        # TC ID: TC-TSCH-002
        # Given-When-Then
        #   Given: 유효한 교육자 토큰, 유효한 classroom_id
        #   When: POST /schedule 호출
        #   Then: 200 응답, 일정 생성 확인

        assert created_schedule_id is not None, "일정 생성에 실패했습니다."

        print("")
        print("TC_NO: TC-TSCH-002")
        print("created_schedule_id:", created_schedule_id)

    @pytest.mark.p1
    def test_schedule_edit(self, teacher_client, created_schedule_id):
        # 우선순위: P1
        # TC ID: TC-TSCH-003
        # Given-When-Then
        #   Given: 유효한 교육자 토큰, 존재하는 schedule_id
        #   When: PATCH /schedule/{id} 호출
        #   Then: 200 응답

        response = teacher_client.request(
            "PATCH",
            f"/schedule/{created_schedule_id}",
            json={
                "classroom_id": common_data.teacher_classroom_id,
                "summary": "TC-TSCH 테스트 일정 수정",
            },
        )

        assert response.status_code == 200, (
            f"응답 상태 코드가 200이 아닙니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

        print("")
        print("TC_NO: TC-TSCH-003")
        print("status_code:", response.status_code)

    @pytest.mark.p1
    def test_schedule_delete(self, teacher_client, created_schedule_id):
        # 우선순위: P1
        # TC ID: TC-TSCH-004
        # Given-When-Then
        #   Given: 유효한 교육자 토큰, 존재하는 schedule_id
        #   When: DELETE /schedule/{id} 호출
        #   Then: 200 응답

        response = teacher_client.request(
            "DELETE",
            f"/schedule/{created_schedule_id}",
            json={"classroom_id": common_data.teacher_classroom_id},
        )

        assert response.status_code == 200, (
            f"응답 상태 코드가 200이 아닙니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

        print("")
        print("TC_NO: TC-TSCH-004")
        print("status_code:", response.status_code)

    @pytest.mark.p1
    def test_schedule_create_invalid_timezone(self, teacher_client):
        # 우선순위: P1
        # TC ID: TC-TSCH-005
        # Given-When-Then
        #   Given: 유효한 교육자 토큰
        #   When: POST /schedule에 잘못된 timezone 입력
        #   Then: 422 응답

        response = teacher_client.request(
            "POST",
            "/schedule",
            json={
                "classroom_id": common_data.teacher_classroom_id,
                "summary": "timezone 오류 테스트",
                "dt_start": "2026-05-21T09:00:00.000Z",
                "dt_end": "2026-05-21T10:00:00.000Z",
                "classroom_time_zone": "Asia/Seoul",
            },
        )

        assert response.status_code == 422, (
            f"잘못된 timezone 요청 시 422가 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

        print("")
        print("TC_NO: TC-TSCH-005")
        print("status_code:", response.status_code)

    @pytest.mark.p1
    def test_schedule_edit_not_found(self, teacher_client):
        # 우선순위: P1
        # TC ID: TC-TSCH-007
        # Given-When-Then
        #   Given: 유효한 교육자 토큰
        #   When: PATCH /schedule/{id}에 존재하지 않는 id 입력
        #   Then: 409 응답

        response = teacher_client.request(
            "PATCH",
            "/schedule/00000000-0000-0000-0000-000000000000",
            json={
                "classroom_id": common_data.teacher_classroom_id,
                "summary": "없는 일정 수정 시도",
            },
        )

        assert response.status_code == 409, (
            f"존재하지 않는 id 요청 시 409가 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

        print("")
        print("TC_NO: TC-TSCH-007")
        print("status_code:", response.status_code)

    @pytest.mark.p1
    def test_unauthorized_create_schedule(self, student_client):
        # 우선순위: P1
        # TC ID: TC-TSCH-006
        # Given-When-Then
        #   Given: 학습자 org, 학습자 classroom_id
        #   When: POST /schedule 호출
        #   Then: 403 응답

        response = student_client.request(
            "POST",
            "/schedule",
            json={
                "classroom_id": common_data.student_classroom_id,
                "summary": "권한 테스트",
                "dt_start": "2026-05-21T09:00:00.000Z",
                "dt_end": "2026-05-21T10:00:00.000Z",
            },
        )

        assert response.status_code == 403, (
            f"학습자 org로 일정 생성 시 403이 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

        print("")
        print("TC_NO: TC-TSCH-006")
        print("status_code:", response.status_code)
