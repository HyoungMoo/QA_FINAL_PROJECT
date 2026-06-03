# 수강생 권한으로 접근 가능한 API 테스트를 작성하는 파일
#
# 예: 클래스 정보 조회, 과목 목록 조회, 일정 조회, 게시판 목록 조회 등
# Postman에서 먼저 호출이 성공한 API를 기준으로 pytest 테스트를 추가한다.
#
# 공통 client는 tests/conftest.py의 student_client fixture를 사용한다.

import pytest

from utils.test_data import common_data

pytestmark = pytest.mark.student


@pytest.mark.p1
@pytest.mark.smoke
def test_get_board_article_list(student_client):
    # 우선순위 : P1
    # TC ID: TC-STUDENT-BOARD-001
    # Postman에서 성공 확인한 게시글 목록 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 클래스룸 ID 보유
        # When : 게시글 목록 조회 API를 호출 : GET https://api-classroom.elice.io/classroom/{classroom_id}/article?sort_by=created_desc&skip=0&count=3
        # Then : response 결과 확인 : status_code가 200인지, body에 게시글 목록 정보가 있는지 확인
    # 입력값 : 클래스룸 ID, 정렬 기준, skip, count 준비 : classroom_id, created_desc, 0, 3

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 클래스룸 ID 보유
    classroom_id = common_data.student_classroom_id
    params = {
        "sort_by": "created_desc",
        "skip": 0,
        "count": 3,
    }

    # When : 게시글 목록 조회 API를 호출
    response = student_client.get(
        f"/classroom/{classroom_id}/article",
        params=params,
    )

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

    # assert 4. 게시글 목록이 1개 이상 조회되는지 확인
    assert len(body) > 0, (
        "게시글 목록이 비어 있습니다."
    )

    # assert 5. 응답 게시글 수가 요청 count 이하인지 확인
    assert len(body) <= params["count"], (
        f"응답 게시글 수가 요청 count보다 많습니다. "
        f"actual={len(body)}, expected_max={params['count']}"
    )

    first_article = body[0]

    # assert 6. 첫 번째 게시글에 필수 key가 모두 있는지 확인
    required_keys = ["id", "title", "classroom_id"]
    missing_keys = [
        key for key in required_keys
        if key not in first_article
    ]

    assert not missing_keys, (
        f"첫 번째 게시글에 필수 항목이 없습니다. "
        f"missing_keys={missing_keys}, "
        f"article_keys={list(first_article.keys())}"
    )

    # assert 7. 모든 게시글의 classroom_id가 요청한 classroom_id와 같은지 확인
    for article in body:
        assert article.get("classroom_id") == classroom_id, (
            f"게시글의 classroom_id가 요청한 classroom_id와 일치하지 않습니다. "
            f"article_id={article.get('id')}, "
            f"actual={article.get('classroom_id')}, "
            f"expected={classroom_id}"
        )

    # assert 8. id가 int 형식이고, 0보다 큰 값인지 확인
    assert isinstance(first_article["id"], int), (
        f"id가 int 형식이 아닙니다. "
        f"type={type(first_article['id']).__name__}, "
        f"value={first_article['id']}"
    )

    assert first_article["id"] > 0, (
        f"id 값이 0 이하입니다. "
        f"id={first_article['id']}"
    )

    # assert 9. title이 str 형식이고, 빈 문자열이 아닌지 확인
    assert isinstance(first_article["title"], str), (
        f"title이 str 형식이 아닙니다. "
        f"type={type(first_article['title']).__name__}, "
        f"value={first_article['title']}"
    )

    assert first_article["title"].strip() != "", (
        f"title 값이 비어 있습니다. "
        f"title={first_article['title']!r}"
    )

    # assert 10. created_datetime 값이 있는 경우, created_desc 정렬이 맞는지 확인
    # 실제 응답 필드명이 created_datetime이 아니라면 created_at, created_date 등으로 수정 필요
    created_field = "created_datetime"

    if created_field in first_article:
        created_values = [
            article[created_field]
            for article in body
            if article.get(created_field)
        ]

        assert created_values == sorted(created_values, reverse=True), (
            f"게시글 목록이 {created_field} 기준 내림차순으로 정렬되어 있지 않습니다. "
            f"created_values={created_values}"
        )

    print("")
    print("")
    print("TC_NO:TC-STUDENT-BOARD-001")
    print("status_code", response.status_code)
    print("(게시글 목록 수)article_count:", len(body))
    print("(첫 번째 게시글 ID)id:", first_article["id"])
    print("(첫 번째 게시글 제목)title:", first_article["title"])
    print("(첫 번째 게시글 클래스룸 ID)classroom_id:", first_article["classroom_id"])


@pytest.mark.p1
def test_get_board_article_comment_list(rest_student_client):
    # 우선순위 : P1
    # TC ID: TC-STUDENT-BOARD-002
    # Postman에서 성공 확인한 게시글 댓글 목록 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 게시글 ID 보유
        # When : 게시글 댓글 목록 조회 API를 호출 : GET https://api-rest.elice.io/org/qatrack/board/article/comment/list/?board_article_id={board_article_id}&count=5&offset=0&sort_by={"key":"created_datetime","order":"desc"}
        # Then : response 결과 확인 : status_code가 200인지, body에 게시글 댓글 목록 정보가 있는지 확인
    # 입력값 : 게시글 ID, count, offset, sort_by 준비 : board_article_id, 5, 0, created_datetime desc

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 게시글 ID 보유
    # TODO: board_article_id는 현재 TC 기준 임시 테스트 데이터다.
    # 추후 팀 기준에 따라 fixture 또는 별도 test data 파일로 이동할 수 있다.
    board_article_id = 74915
    params = {
        "board_article_id": board_article_id,
        "count": 5,
        "offset": 0,
        "sort_by": '{"key":"created_datetime","order":"desc"}',
    }

    # When : 게시글 댓글 목록 조회 API를 호출
    response = rest_student_client.get(
        f"/org/{common_data.org_student}/board/article/comment/list/",
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
    required_body_keys = ["_result", "article_comments", "article_comment_count"]
    missing_body_keys = [
        key for key in required_body_keys
        if key not in body
    ]

    assert not missing_body_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_body_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. article_comments가 list 형식인지 확인
    assert isinstance(body["article_comments"], list), (
        f"article_comments가 list 형식이 아닙니다. "
        f"type={type(body['article_comments']).__name__}, "
        f"article_comments={body['article_comments']}"
    )

    # assert 6. article_comment_count가 int 형식인지 확인
    assert isinstance(body["article_comment_count"], int), (
        f"article_comment_count가 int 형식이 아닙니다. "
        f"type={type(body['article_comment_count']).__name__}, "
        f"value={body['article_comment_count']}"
    )

    # assert 7. article_comment_count가 0 이상인지 확인
    assert body["article_comment_count"] >= 0, (
        f"article_comment_count가 0보다 작습니다. "
        f"article_comment_count={body['article_comment_count']}"
    )

    # assert 8. 응답 댓글 목록 수가 요청 count 이하인지 확인
    assert len(body["article_comments"]) <= params["count"], (
        f"응답 댓글 목록 수가 요청 count보다 많습니다. "
        f"actual={len(body['article_comments'])}, "
        f"expected_max={params['count']}"
    )

    # assert 9. 전체 댓글 수가 현재 응답 댓글 목록 수보다 작지 않은지 확인
    assert body["article_comment_count"] >= len(body["article_comments"]), (
        f"전체 댓글 수가 현재 응답 댓글 목록 수보다 작습니다. "
        f"article_comment_count={body['article_comment_count']}, "
        f"article_comments_count={len(body['article_comments'])}"
    )

    # assert 10. 댓글이 있는 경우, 첫 번째 댓글에 필수 key가 있는지 확인
    if body["article_comments"]:
        first_comment = body["article_comments"][0]

        required_comment_keys = ["id", "content", "created_datetime"]
        missing_comment_keys = [
            key for key in required_comment_keys
            if key not in first_comment
        ]

        assert not missing_comment_keys, (
            f"첫 번째 댓글에 필수 항목이 없습니다. "
            f"missing_keys={missing_comment_keys}, "
            f"comment_keys={list(first_comment.keys())}"
        )

        # assert 11. 첫 번째 댓글 id가 int 형식이고 0보다 큰지 확인
        assert isinstance(first_comment["id"], int), (
            f"댓글 id가 int 형식이 아닙니다. "
            f"type={type(first_comment['id']).__name__}, "
            f"value={first_comment['id']}"
        )

        assert first_comment["id"] > 0, (
            f"댓글 id 값이 0 이하입니다. "
            f"id={first_comment['id']}"
        )

        # assert 12. 댓글 content가 str 형식인지 확인
        assert isinstance(first_comment["content"], str), (
            f"댓글 content가 str 형식이 아닙니다. "
            f"type={type(first_comment['content']).__name__}, "
            f"value={first_comment['content']}"
        )

        # assert 13. 댓글 created_datetime이 int 형식이고 0보다 큰 timestamp 값인지 확인
        assert isinstance(first_comment["created_datetime"], int), (
            f"created_datetime이 int 형식이 아닙니다. "
            f"type={type(first_comment['created_datetime']).__name__}, "
            f"value={first_comment['created_datetime']}"
        )

        assert first_comment["created_datetime"] > 0, (
            f"created_datetime 값이 0 이하입니다. "
            f"created_datetime={first_comment['created_datetime']}"
        )

        # assert 14. created_datetime 기준 내림차순 정렬인지 확인
        created_values = [
            comment["created_datetime"]
            for comment in body["article_comments"]
            if comment.get("created_datetime")
        ]

        assert created_values == sorted(created_values, reverse=True), (
            f"댓글 목록이 created_datetime 기준 내림차순으로 정렬되어 있지 않습니다. "
            f"created_values={created_values}"
        )

    print("")
    print("")
    print("TC_NO:TC-STUDENT-BOARD-002")
    print("status_code", response.status_code)
    print("(댓글 수)article_comment_count:", body["article_comment_count"])
    print("(댓글 목록 수)article_comments_count:", len(body["article_comments"]))

    if body["article_comments"]:
        first_comment = body["article_comments"][0]
        print("(첫 번째 댓글 ID)id:", first_comment.get("id"))
        print("(첫 번째 댓글 내용)content:", first_comment.get("content"))
        print("(첫 번째 댓글 작성일)created_datetime:", first_comment.get("created_datetime"))


@pytest.mark.p2
def test_get_file_resource(file_student_client):
    # 우선순위 : P2
    # TC ID: TC-STUDENT-BOARD-003
    # Postman에서 성공 확인한 파일 리소스 정보 조회 API.
    # Given-When-Then
        # Given : 로그인 상태(유효한 학습자 토큰 보유), 파일 ID 보유
        # When : 파일 리소스 정보 조회 API를 호출 : GET https://api-file.elice.io/resource/{file_id}
        # Then : response 결과 확인 : status_code가 200인지, body에 파일 리소스 정보가 있는지 확인
    # 입력값 : 파일 ID 준비 : file_id_1

    # Given : 로그인 상태(유효한 학습자 토큰 보유), 파일 ID 보유
    # TODO: file_id_1은 현재 TC 기준 임시 테스트 데이터다.
    # 추후 팀 기준에 따라 fixture 또는 별도 test data 파일로 이동할 수 있다.
    file_id_1 = "7ac8225c-6ecd-4aa1-833e-ab139ca713aa"

    # When : 파일 리소스 정보 조회 API를 호출
    response = file_student_client.get(f"/resource/{file_id_1}")

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
    required_keys = ["id", "name", "url", "mime", "size"]
    missing_keys = [
        key for key in required_keys
        if key not in body
    ]

    assert not missing_keys, (
        f"응답 body에 필수 항목이 없습니다. "
        f"missing_keys={missing_keys}, "
        f"body_keys={list(body.keys())}"
    )

    # assert 5. id : 파일 리소스 ID가 요청한 file_id와 동일한지 확인
    assert body["id"] == file_id_1, (
        f"파일 리소스 ID가 요청값과 일치하지 않습니다. "
        f"actual={body.get('id')}, expected={file_id_1}"
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
        f"파일명이 비어 있습니다. name={body['name']!r}"
    )

    # assert 8. url이 str 형식이고 http로 시작하는지 확인
    assert isinstance(body["url"], str), (
        f"url이 str 형식이 아닙니다. "
        f"type={type(body['url']).__name__}, value={body['url']}"
    )

    assert body["url"].startswith(("http://", "https://")), (
        f"url 형식이 올바르지 않습니다. url={body['url']}"
    )

    # assert 9. mime이 str 형식이고 MIME 형식인지 확인
    assert isinstance(body["mime"], str), (
        f"mime이 str 형식이 아닙니다. "
        f"type={type(body['mime']).__name__}, value={body['mime']}"
    )

    assert "/" in body["mime"], (
        f"mime 형식이 올바르지 않습니다. mime={body['mime']}"
    )

    # assert 10. size가 int 형식이고 0보다 큰지 확인
    assert isinstance(body["size"], int), (
        f"size가 int 형식이 아닙니다. "
        f"type={type(body['size']).__name__}, value={body['size']}"
    )

    assert body["size"] > 0, (
        f"파일 size가 0 이하입니다. size={body['size']}"
    )

    # assert 11. status가 있는 경우, str 형식인지 확인
    if "status" in body:
        assert isinstance(body["status"], str), (
            f"status가 str 형식이 아닙니다. "
            f"type={type(body['status']).__name__}, value={body['status']}"
        )

        assert body["status"].strip() != "", (
            f"status 값이 비어 있습니다. status={body['status']!r}"
        )

    print("")
    print("")
    print("TC_NO:TC-STUDENT-BOARD-003")
    print("status_code", response.status_code)
    print("(파일 리소스 ID)id:", body["id"])
    print("(파일명)name:", body["name"])
    print("(파일 URL)url:", body["url"])
    print("(파일 MIME 타입)mime:", body["mime"])
    print("(파일 크기)size:", body["size"])
    print("(파일 상태)status:", body.get("status"))
