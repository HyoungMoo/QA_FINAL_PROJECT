# QA 4기 최종 프로젝트

엘리스 LXP 플랫폼의 주요 기능을 API 관점에서 검증하고, 제공된 부하 테스트 결과를 분석하기 위한 QA 프로젝트입니다.

본 프로젝트는 학습자와 교육자 권한에서 핵심 API를 검증하고, 응답 구조와 권한 경계를 확인하여 서비스 품질 이슈를 재현 가능한 형태로 정리하는 것을 목표로 합니다.

## 주요 범위

- API 기능 테스트 자동화
- 학습자/교육자 권한별 테스트 시나리오 검증(+권한 경계 테스트)
- 부하 테스트 결과 분석
- 발견 이슈 및 개선안 정리

## 테스트 대상

API 테스트는 아래 기능을 중심으로 진행합니다.

| 구분 | 테스트 대상 |
|---|---|
| 학습자 | 클래스 홈, 학습 과목, 수업 일정, 게시판 |
| 교육자 | 클래스 홈, 학습 과목, 수업 일정, 게시판 |

권한 경계 테스트는 토큰 이름이 아니라 `계정 + 조직 + 클래스룸 내 역할`을 기준으로 판단합니다.

## 기술 스택

| 구분 | 사용 도구 |
|---|---|
| Language | Python |
| Test Framework | pytest |
| HTTP Client | requests |
| Environment | python-dotenv |
| API Manual Test | Postman |

## 디렉토리 구조

```text
elice_lxp_test_team3/
├── README.md
├── part1_api_automation/
│   ├── tests/
│   │   ├── test_student/
│   │   │   ├── __init__.py             # 학습자 테스트 패키지 인식 파일
│   │   │   ├── test_board.py           # 학습자 게시판 API 테스트
│   │   │   ├── test_class_home.py      # 학습자 클래스 홈 API 테스트
│   │   │   ├── test_course.py          # 학습자 학습 과목 API 테스트
│   │   │   └── test_schedule.py        # 학습자 수업 일정 API 테스트
│   │   ├── test_teacher/
│   │   │   ├── __init__.py             # 교육자 테스트 패키지 인식 파일
│   │   │   ├── test_board.py           # 교육자 권한 게시판 API 테스트
│   │   │   ├── test_class_home.py      # 교육자 권한 클래스 홈 API 테스트
│   │   │   ├── test_course.py          # 교육자 권한 학습 과목 API 테스트
│   │   │   └── test_schedule.py        # 교육자 권한 수업 일정 API 테스트
│   │   ├── __init__.py                 # pytest 모듈 충돌 방지를 위한 패키지 인식 파일
│   │   ├── conftest.py                 # pytest 공통 fixture 및 API client 설정
│   │   └── test_auth.py                # 인증/권한 관련 테스트
│   ├── utils/
│   │   ├── test_data/
│   │   │   ├── common_data.py          # 공통 테스트 데이터
│   │   │   └── student_material_data.py # 학습 자료 테스트 데이터
│   │   ├── api_client.py               # API 요청 client wrapper
│   │   ├── config.py                   # .env 기반 환경 설정 로더
│   │   └── request_helper.py           # API 요청 helper
│   ├── reports/                        # 테스트 리포트 출력 경로
│   ├── .env.example                    # 로컬 환경 변수 샘플
│   ├── pytest.ini                      # pytest 실행 설정
│   └── requirements.txt                # Python 의존성 목록
└── part2_load_analysis/
    ├── analysis/
    │   └── load_test_analysis.ipynb    # 부하 테스트 결과 분석 노트북
    ├── data/
    │   ├── team2_results/              # 2팀 부하 테스트 결과 데이터
    │   └── team3_results/              # 3팀 부하 테스트 결과 데이터
    ├── jmeter_draft/
    │   └── load_test_scenario_v2.jmx   # JMeter 테스트 플랜 초안
    └── reports/                        # 부하 테스트 분석 리포트 출력 경로
```

## 실행 준비

```bash
cd part1_api_automation
pip install -r requirements.txt
```

`.env.example` 파일을 참고해 로컬에 `.env` 파일을 생성합니다.

```text
student_id=
token=
```

`.env`에는 인증 토큰 등 민감 정보가 포함되므로 Git에 업로드하지 않습니다.

## 테스트 실행

전체 테스트 실행:

```bash
cd part1_api_automation
pytest
```

학습자 테스트 실행:

```bash
pytest tests/test_student
```

교육자 테스트 실행:

```bash
pytest tests/test_teacher
```

출력 로그를 함께 확인:

```bash
pytest -s
```

HTML 리포트 생성:

```bash
pytest --html=reports/report.html --self-contained-html
```

### 테스트 마커
- smoke 테스트 등 스크립트 작성 진행에 맞춰 마커 추가 예정

우선순위별 테스트 실행:

```bash
pytest -m p0
pytest -m p1
pytest -m p2
```

## 테스트 우선순위

| Marker | 기준 |
|---|---|
| `p0` | 높은 우선순위, 핵심 기능, 기본 접근 가능 여부, 주요 사용자 흐름 |
| `p1` | 보통 우선순위, 주요 기능의 상세 응답 검증 |
| `p2` | 낮은 우선순위, 보조 기능, 부가 정보 |

## 테스트 작성 기준

테스트 코드는 `Given - When - Then` 흐름을 기준으로 작성합니다.

```python
@pytest.mark.p0
def test_example():
    # Given-When-Then
    # Given

    # When

    # Then
```

기본 검증 항목:

- HTTP status code
- Content-Type
- 응답 body 타입
- 필수 key 존재 여부
- 주요 필드 타입과 값 범위
- 실패 응답의 `_result`, `fail_code`, `fail_message`

일부 API는 HTTP status code가 `200`이어도 body 내부에서 실패 상태가 내려올 수 있으므로, 단순히 `status_code == 200`만으로 성공을 판단하지 않습니다.

## API 요청 정책

운영 서비스에 영향을 줄 수 있으므로 API 호출은 아래 기준을 따릅니다.

- 요청 간 최소 대기 시간 적용
- 요청 timeout 설정 적용
- 불필요한 반복 호출 지양
- `POST`, `PATCH`, `DELETE` API는 데이터 변경 가능성을 먼저 확인
- 500 에러, 접속 지연, 비정상 응답이 반복되면 즉시 중단하고 기록

## Git Workflow

기본 브랜치 전략:

```text
main
└── develop
    └── feature/*
```

작업 시작:

```bash
git switch develop
git pull origin develop
git switch -c feature/작업명
```

작업 반영:

```bash
git add -A
git commit -m "작업 내용"
git push -u origin feature/작업명
```

GitLab에서 Merge Request를 생성하고, 코드 리뷰 후 `develop` 브랜치로 병합합니다.

## 코드 리뷰 체크리스트

- 테스트 목적이 TC와 일치하는가?
- API base URL, path, params, headers가 명세와 일치하는가?
- 학습자/교육자 권한에 맞는 테스트 데이터가 사용되었는가?
- 응답 body 검증이 충분한가?
- 성공/실패 기준이 명확한가?
- 민감 정보가 코드에 포함되지 않았는가?

## Git 제외 대상

다음 파일과 디렉토리는 Git에 업로드하지 않습니다.

- `.env`
- Python cache
- pytest cache
- 로컬 가상환경
- 테스트 실행 결과 리포트
- 제공받은 부하 테스트 원본 로그