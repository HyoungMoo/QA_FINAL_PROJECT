import requests

# Authorization 인증 헤더 생성
def get_auth_headers(token):
    return {
        "Authorization": token,
    }

# GET API 요청
def get_request(url, headers, params, timeout):
    return requests.get(
        url=url,
        headers=headers,
        params=params,
        timeout=timeout,
    )