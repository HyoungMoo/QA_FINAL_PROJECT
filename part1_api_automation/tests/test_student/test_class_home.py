# 수강생 권한으로 접근 가능한 API 테스트를 작성하는 파일
#
# 예: 클래스 정보 조회, 과목 목록 조회, 일정 조회, 게시판 목록 조회 등
# Postman에서 먼저 호출이 성공한 API를 기준으로 pytest 테스트를 추가한다.
#
# 공통 client는 tests/conftest.py의 student_client fixture를 사용한다.


def test_get_student_dashboard(dashboard_student_client, settings):
    # Postman에서 성공 확인한 수강생 학습 현황 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(토큰 발급 계정과 학습자 계정이 동일해야 함)
        # When : 수강생 학습 현황 조회 API를 호출 : GET https://api-dashboard.elice.io/student/{student_id}?classroom_id={classroom_id}
        # Then : response 결과 확인 : status_code가 200인지, body 확인
    # 입력값 : 수강생 ID와 클래스룸 ID 준비 : student_id, classroom_id
    

    # Given : 로그인 상태(토큰 발급 계정과 학습자 계정이 동일해야 함)
    student_id = settings.student_id
    classroom_id = settings.classroom_id

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

    # print(response.status_code)
    # print("(학습 진행률)learning_progress", body["learning_progress"])
    # print("(테스트 평균 점수)test_score:", body["test_score"])
    # print("(평균 실습 자료)practice_score:", body["practice_score"])
    # print("submit_cnt:", body["submit_cnt"])
    # print("test_completed_cnt:", body["test_completed_cnt"])
    # print("(학습 완료 여부)learning_completed:", body["learning_completed"])


