
import re
import uuid

import pytest
from utils.test_data import common_data

pytestmark = pytest.mark.teacher

UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)

DT_START = "2026-04-16T15:00:00.000Z"
DT_END = "2026-06-14T14:59:59.999Z"

# 테스트 실행마다 고유한 summary로 이전 실행 잔여 데이터와 충돌 방지
SCHEDULE_SUMMARY = f"TC-TSCH 테스트 일정 {uuid.uuid4().hex[:8]}"
FIXTURE_DT_START = "2026-06-01T09:00:00.000Z"
FIXTURE_DT_END = "2026-06-01T10:00:00.000Z"
_FIXTURE_DATE = FIXTURE_DT_START[:10]  # "2026-06-01" — _find_schedule_id 날짜와 동기화


def _find_schedule_id(teacher_client, summary):
    """생성된 일정을 summary로 찾아 ID 반환"""
    response = teacher_client.get(
        "/schedule",
        params={
            "classroom_id": common_data.teacher_classroom_id,
            "dt_start_ge": f"{_FIXTURE_DATE}T00:00:00.000Z",
            "dt_start_le": f"{_FIXTURE_DATE}T23:59:59.999Z",
            "count": 40,
        },
    )
    schedules = response.json()
    schedule = next((s for s in schedules if s.get("summary") == summary), None)
    return schedule["id"] if schedule else None


@pytest.fixture(scope="module")
def created_schedule_id(teacher_client):
    """수정 테스트에 사용할 일정을 생성하고, 테스트 완료 후 삭제한다."""
    create_response = teacher_client.request(
        "POST",
        "/schedule",
        json={
            "classroom_id": common_data.teacher_classroom_id,
            "summary": SCHEDULE_SUMMARY,
            "dt_start": FIXTURE_DT_START,
            "dt_end": FIXTURE_DT_END,
            "classroom_time_zone": "KST",
        },
    )
    assert create_response.status_code == 200, (
        f"테스트용 일정 생성 실패: {create_response.text}"
    )

    schedule_id = _find_schedule_id(teacher_client, SCHEDULE_SUMMARY)
    assert schedule_id is not None, "생성한 테스트 일정을 찾을 수 없습니다."

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
        # Given: 유효한 교육자 토큰, 유효한 classroom_id, 유효한 날짜 범위
        # When: GET /schedule 호출
        # Then: 200 응답, 일정 목록 반환

        response = teacher_client.get(
            "/schedule",
            params={
                "classroom_id": common_data.teacher_classroom_id,
                "dt_start_ge": DT_START,
                "dt_start_le": DT_END,
                "count": 40,
            },
        )

        assert response.status_code == 200, (
            f"응답 상태 코드가 200이 아닙니다. "
            f"status_code={response.status_code}, response={response.text}"
        )

        data = response.json()
        assert isinstance(data, list), (
            f"응답 body가 list 형식이 아닙니다. type={type(data).__name__}"
        )

        assert len(data) > 0, (
            f"일정 목록이 비어 있습니다. 테스트 기간 내 데이터를 확인하세요. "
            f"dt_start_ge={DT_START}, dt_start_le={DT_END}"
        )

        first = data[0]

        # assert 3. 필수 필드가 존재하는지 확인
        required_keys = ["id", "uid", "summary", "dt_start", "dt_end", "tags"]
        missing_keys = [k for k in required_keys if k not in first]
        assert not missing_keys, (
            f"응답 항목에 필수 필드가 없습니다. missing={missing_keys}"
        )

        # assert 4. id가 UUID 형식인지 확인
        assert UUID_RE.match(first["id"]), (
            f"id가 UUID 형식이 아닙니다. id={first['id']}"
        )

        # assert 5. summary가 string 형식인지 확인
        assert isinstance(first["summary"], str), (
            f"summary가 string 형식이 아닙니다. type={type(first['summary']).__name__}"
        )

        # assert 6. tags.classroom_id가 요청한 classroom_id와 일치하는지 확인
        assert "classroom_id" in first["tags"], (
            f"tags에 classroom_id가 없습니다. tags={first['tags']}"
        )
        assert first["tags"]["classroom_id"] == common_data.teacher_classroom_id, (
            f"tags.classroom_id가 요청값과 다릅니다. "
            f"expected={common_data.teacher_classroom_id}, actual={first['tags']['classroom_id']}"
        )

        print(f"\nTC_NO: TC-TSCH-001 | status_code: {response.status_code} | 일정 개수: {len(data)}")

    @pytest.mark.p0
    def test_schedule_create(self, created_schedule_id):
        # 우선순위: P0
        # TC ID: TC-TSCH-002
        # Given: 유효한 교육자 토큰, 유효한 classroom_id
        # When: POST /schedule 호출 (fixture 내부에서 실행 및 상태코드 검증)
        # Then: 200 응답, 일정 ID 반환

        assert created_schedule_id is not None, "일정 생성에 실패했습니다."
        print(f"\nTC_NO: TC-TSCH-002 | created_schedule_id: {created_schedule_id}")

    @pytest.mark.p0
    def test_schedule_edit(self, teacher_client, created_schedule_id):
        # 우선순위: P0
        # TC ID: TC-TSCH-003
        # Given: 유효한 교육자 토큰, 존재하는 schedule_id
        # When: PATCH /schedule/{id} 호출
        # Then: 200 응답

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
        print(f"\nTC_NO: TC-TSCH-003 | status_code: {response.status_code}")

    @pytest.mark.p0
    def test_schedule_delete(self, teacher_client):
        # 우선순위: P0
        # TC ID: TC-TSCH-004
        # Given: 유효한 교육자 토큰, 새로 생성한 schedule_id
        # When: DELETE /schedule/{id} 호출
        # Then: 200 응답

        delete_summary = "TC-TSCH-004 삭제 테스트용"
        teacher_client.request(
            "POST",
            "/schedule",
            json={
                "classroom_id": common_data.teacher_classroom_id,
                "summary": delete_summary,
                "dt_start": FIXTURE_DT_START,
                "dt_end": FIXTURE_DT_END,
                "classroom_time_zone": "KST",
            },
        )
        schedule_id = _find_schedule_id(teacher_client, delete_summary)
        assert schedule_id is not None, "삭제 테스트용 일정 생성 실패"

        response = teacher_client.request(
            "DELETE",
            f"/schedule/{schedule_id}",
            json={"classroom_id": common_data.teacher_classroom_id},
        )

        assert response.status_code == 200, (
            f"응답 상태 코드가 200이 아닙니다. "
            f"status_code={response.status_code}, response={response.text}"
        )
        print(f"\nTC_NO: TC-TSCH-004 | status_code: {response.status_code}")

    @pytest.mark.p2
    def test_schedule_create_invalid_timezone(self, teacher_client):
        # 우선순위: P2
        # TC ID: TC-TSCH-005
        # Given: 유효한 교육자 토큰
        # When: POST /schedule에 IANA 형식 timezone 입력
        # Then: 422 응답

        response = teacher_client.request(
            "POST",
            "/schedule",
            json={
                "classroom_id": common_data.teacher_classroom_id,
                "summary": "timezone 오류 테스트",
                "dt_start": FIXTURE_DT_START,
                "dt_end": FIXTURE_DT_END,
                "classroom_time_zone": "Asia/Seoul",
            },
        )

        assert response.status_code == 422, (
            f"잘못된 timezone 요청 시 422가 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )
        print(f"\nTC_NO: TC-TSCH-005 | status_code: {response.status_code}")

    @pytest.mark.p0
    def test_unauthorized_create_schedule(self, student_client):
        # 우선순위: P0
        # TC ID: TC-TSCH-006
        # Given: 학습자 org, 학습자 classroom_id
        # When: POST /schedule 호출
        # Then: 403 응답

        response = student_client.request(
            "POST",
            "/schedule",
            json={
                "classroom_id": common_data.student_classroom_id,
                "summary": "권한 테스트",
                "dt_start": FIXTURE_DT_START,
                "dt_end": FIXTURE_DT_END,
            },
        )

        assert response.status_code == 403, (
            f"학습자 org로 일정 생성 시 403이 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )
        print(f"\nTC_NO: TC-TSCH-006 | status_code: {response.status_code}")

    @pytest.mark.p1
    def test_schedule_edit_not_found(self, teacher_client):
        # 우선순위: P1
        # TC ID: TC-TSCH-007
        # Given: 유효한 교육자 토큰
        # When: PATCH /schedule/{id}에 존재하지 않는 id 입력
        # Then: 409 응답

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
        print(f"\nTC_NO: TC-TSCH-007 | status_code: {response.status_code}")

    @pytest.mark.p1
    def test_schedule_create_invalid_date_format(self, teacher_client):
        # 우선순위: P1
        # TC ID: TC-TSCH-008
        # Given: 유효한 교육자 토큰
        # When: POST /schedule에 ISO 8601 형식이 아닌 날짜 값 입력
        # Then: 409 응답

        response = teacher_client.request(
            "POST",
            "/schedule",
            json={
                "classroom_id": common_data.teacher_classroom_id,
                "summary": "날짜 형식 오류 테스트",
                "dt_start": "2026/05/21",
                "dt_end": "2026/05/21",
                "classroom_time_zone": "KST",
            },
        )

        assert response.status_code == 409, (
            f"잘못된 날짜 형식 요청 시 409가 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )
        print(f"\nTC_NO: TC-TSCH-008 | status_code: {response.status_code}")

    @pytest.mark.p2
    def test_schedule_create_date_reversed(self, teacher_client):
        # 우선순위: P2
        # TC ID: TC-TSCH-009
        # Given: 유효한 교육자 토큰
        # When: POST /schedule에 dt_start가 dt_end보다 늦은 값 입력
        # Then: 409 응답

        response = teacher_client.request(
            "POST",
            "/schedule",
            json={
                "classroom_id": common_data.teacher_classroom_id,
                "summary": "날짜 역전 테스트",
                "dt_start": FIXTURE_DT_END,
                "dt_end": FIXTURE_DT_START,
                "classroom_time_zone": "KST",
            },
        )

        assert response.status_code == 409, (
            f"날짜 역전 요청 시 409가 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )
        print(f"\nTC_NO: TC-TSCH-009 | status_code: {response.status_code}")

    @pytest.mark.p1
    def test_schedule_create_missing_summary(self, teacher_client):
        # 우선순위: P1
        # TC ID: TC-TSCH-010
        # Given: 유효한 교육자 토큰
        # When: POST /schedule에 summary 파라미터 없이 요청
        # Then: 422 응답

        response = teacher_client.request(
            "POST",
            "/schedule",
            json={
                "classroom_id": common_data.teacher_classroom_id,
                "dt_start": FIXTURE_DT_START,
                "dt_end": FIXTURE_DT_END,
                "classroom_time_zone": "KST",
            },
        )

        assert response.status_code == 422, (
            f"summary 누락 요청 시 422가 아닌 응답이 반환되었습니다. "
            f"status_code={response.status_code}, response={response.text}"
        )
        print(f"\nTC_NO: TC-TSCH-010 | status_code: {response.status_code}")
