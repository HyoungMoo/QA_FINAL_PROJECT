from utils.config import get_settings
from utils.request_helper import get_auth_headers, get_request


def test_get_week1_2lecture_material_pdf():
    # Given
    # 1주차 2번 강의자료 PDF 조회에 필요한 설정값 세팅
    settings = get_settings()

    url = (
        f"{settings.base_rest_url}"
        f"/org/{settings.org}"
        f"/material_pdf/get/"
    )

    headers = get_auth_headers(
        settings.student_token
    )

    params = {
        "material_pdf_id": settings.week1_2lecture_material_id,
    }

    # When
    # 강의자료 PDF 조회 API 요청
    response = get_request(
        url=url,
        headers=headers,
        params=params,
        timeout=settings.request_timeout_seconds,
    )


    # Then
    # 강의자료 PDF 조회 성공 여부 확인
    assert response.status_code == 200, (
        f"강의자료 PDF 조회 실패 "
        f"(status_code={response.status_code})"
    )

    data = response.json()

    # API 결과 상태가 ok 검증
    assert data["_result"]["status"] == "ok", (
        f"강의자료 PDF 응답 실패: {data}"
    )

    # 응답 데이터에 material_pdf 정보 포함 검증
    assert "material_pdf" in data, (
        "응답 데이터에 material_pdf 정보가 없습니다."
    )