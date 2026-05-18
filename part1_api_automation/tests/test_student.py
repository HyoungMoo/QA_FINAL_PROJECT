# 수강생 권한으로 접근 가능한 API 테스트를 작성하는 파일
#
# 예: 클래스 정보 조회, 과목 목록 조회, 일정 조회, 게시판 목록 조회 등
# Postman에서 먼저 호출이 성공한 API를 기준으로 pytest 테스트를 추가한다.
#
# 공통 client는 tests/conftest.py의 student_client fixture를 사용한다.


def test_get_student_dashboard(dashboard_student_client, settings):
    # Postman에서 성공 확인한 수강생 학습 현황 조회 API.
    # Given-When-Then
        # Given : 수강생 ID와 클래스룸 ID 준비 : student_id, classroom_id
        # When : 수강생 학습 현황 조회 API를 호출 : GET https://api-dashboard.elice.io/student/{student_id}?classroom_id={classroom_id}
        # Then : response의 status code가 200인지 확인 / response body에 항목들이 들어있는지 확인

    
    # Given
    student_id = settings.student_id
    classroom_id = settings.classroom_id

    # When
    response = dashboard_student_client.get(
        f"/student/{student_id}",
        params={"classroom_id": classroom_id},
    )

    # Then
    assert response.status_code == 200
    body = response.json()

    # 1. account : 계정 있는지 확인
    # 2. account 내 id와 .env의 학습자 아이디가 동일한지 확인
    # 3. learning_progress : 학습 진행률
    # 4. test_score : 테스트 평균 점수
    # 5. practice_score : 평균 실습 자료 점수
    # 6. submit_cnt : ? : response body에는 있지만, 어떤 항목인지 미상
    # 7. test_completed_cnt : ? : response body에는 있지만, 어떤 항목인지 미상
    # 8. learning_completed : 학습 완료 여부--classroom_id에 해당하는 수업
    assert "account" in body
    assert body["account"]["id"] == int(settings.student_id)
    assert "learning_progress" in body
    assert "test_score" in body
    assert "practice_score" in body
    assert "submit_cnt" in body
    assert "test_completed_cnt" in body
    assert "learning_completed" in body
