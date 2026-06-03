# QA 4기 최종 프로젝트

엘리스 LXP 플랫폼의 주요 기능을 API 관점에서 검증하고, 제공된 부하 테스트 결과를 분석하기 위한 QA 프로젝트입니다.

본 프로젝트는 학습자와 교육자 권한에서 핵심 API를 검증하고, 응답 구조와 권한 경계를 확인하여 서비스 품질 이슈를 재현 가능한 형태로 정리하는 것을 목표로 합니다.

## 1. 프로젝트 소개

### 주요 범위

- API 기능 테스트 자동화
- 학습자/교육자 권한별 테스트 시나리오 검증
- 권한 경계 테스트
- 부하 테스트 결과 분석
- 발견 이슈 및 개선안 정리

### 테스트 대상

API 테스트는 아래 기능을 중심으로 진행합니다.

| 구분 | 테스트 대상 |
|---|---|
| 학습자 | 클래스 홈, 학습 과목, 수업 일정, 게시판 |
| 교육자 | 클래스 홈, 학습 과목, 수업 일정 |
| 권한 경계 | 학습자 권한으로 교육자 전용 API 접근 시 차단 여부 |

권한 경계 테스트는 토큰 이름이 아니라 `계정 + 조직 + 클래스룸 내 역할`을 기준으로 판단합니다.
현재 교육자 게시판 API는 학습자와 권한 차이가 명확한 별도 기능을 확인하지 못해 독립 테스트 대상으로 확정하지 않았습니다.

### 기술 스택

| 구분 | 사용 도구 |
|---|---|
| Language | Python |
| Test Framework | pytest |
| HTTP Client | requests |
| Environment | python-dotenv |
| Test Report | pytest-html, Allure |
| Test Utility | pytest-xdist, pytest-cov, coverage |
| Data Analysis | pandas |
| Excel Reader | openpyxl |
| Visualization | matplotlib, seaborn |
| API Manual Test | Postman |
| Spike Test Scenario | JMeter |
| CI | GitHub Actions |
| Code Management | GitLab, GitHub |

## 2. 프로젝트 구조

### 디렉토리 구조

```text
elice_lxp_test_team3/
├── .github/
│   └── workflows/
│       └── api-test.yml                    # GitHub Actions API 테스트 workflow
├── .gitignore
├── README.md
├── requirements.txt                        # Python 의존성 목록
├── part1_api_automation/
│   ├── tests/
│   │   ├── test_student/
│   │   │   ├── __init__.py                 # 학습자 테스트 패키지 인식 파일
│   │   │   ├── test_board.py               # 학습자 게시판 API 테스트
│   │   │   ├── test_class_home.py          # 학습자 클래스 홈 API 테스트
│   │   │   ├── test_course.py              # 학습자 학습 과목 API 테스트
│   │   │   └── test_schedule.py            # 학습자 수업 일정 API 테스트
│   │   ├── test_teacher/
│   │   │   ├── __init__.py                 # 교육자 테스트 패키지 인식 파일
│   │   │   ├── test_board.py               # 교육자 권한 게시판 API 테스트
│   │   │   ├── test_class_home.py          # 교육자 권한 클래스 홈 API 테스트
│   │   │   ├── test_course.py              # 교육자 권한 학습 과목 API 테스트
│   │   │   └── test_schedule.py            # 교육자 권한 수업 일정 API 테스트
│   │   ├── __init__.py                     # pytest 모듈 충돌 방지를 위한 패키지 인식 파일
│   │   ├── conftest.py                     # pytest 공통 fixture 및 API client 설정
│   │   └── test_permission_boundary.py     # 권한 경계 테스트
│   ├── utils/
│   │   ├── test_data/
│   │   │   ├── common_data.py              # 공통 테스트 데이터
│   │   │   └── student_material_data.py    # 학습 자료 테스트 데이터
│   │   ├── config.py                       # .env 기반 환경 설정 로더
│   │   ├── api_client.py                   # API 요청 client wrapper
│   │   └── request_helper.py               # API 요청 helper
│   ├── reports/                            # pytest-html, Allure 리포트 출력 경로
│   ├── .env.example                        # 로컬 환경 변수 샘플
│   └── pytest.ini                          # pytest 실행 설정
└── part2_load_analysis/
    ├── analysis/
    │   ├── 00_load_analysis.py             # 전처리/분석/결과 생성을 한 번에 실행하는 통합 스크립트
    │   ├── 0_preparation/
    │   │   └── 00_preprocess_load_test_data.py # 원본 로그를 분석 가능 데이터로 가공
    │   ├── 1_metric_analysis/
    │   │   ├── 01_data_validation.py           # 데이터 신뢰도와 품질 검증
    │   │   ├── 02_metric_summary.py            # 성능 지표 집계
    │   │   ├── 04_cross_validation.py          # Team2 / Team3 결과 교차 검증
    │   │   └── 05_visualization.py             # 성능 지표 시각화
    │   └── 2_result_analysis/
    │       ├── 03_bottleneck_candidates.py     # 1차 병목 후보 정리
    │       ├── 06_bottleneck_threshold.py      # 병목 API와 임계점 도출
    │       └── 09_go_nogo_improvement.py       # Go/No-Go 기준 및 개선안 정리
    ├── data/
    │   ├── 0_preparation_data/
    │   │   ├── 00_raw_data/                # 원본 부하 테스트 파일 보관
    │   │   ├── 01_sanitized_data/          # 민감정보 제거 후 1차 가공 결과
    │   │   ├── 02_common_schema_data/      # Team2 / Team3 공통 컬럼 변환 결과
    │   │   └── 03_analysis_ready_data/     # 실제 분석에 사용할 최종 전처리 데이터
    │   └── 1_analysis_result_data/         # 분석 단계별 결과 데이터
    ├── jmeter_draft/
    │   └── spike_test_scenario_1000_v1.jmx # 1,000명 Spike 테스트 시나리오 초안
    └── reports/
        ├── 1_metric_analysis/              # 지표 분석 리포트
        ├── 2_result_analysis/              # 병목/임계점 분석 리포트
        └── 3_final/                        # 최종 보고 산출물
```

### Git 제외 대상

다음 파일과 디렉토리는 Git에 업로드하지 않습니다.

- `.env`
- Python cache
- pytest cache
- 로컬 가상환경
- 테스트 실행 결과 리포트
- 제공받은 부하 테스트 원본 로그
- Part 2 전처리 과정에서 생성되는 CSV 결과

## 3. API 테스트 자동화

### 실행 준비

프로젝트 루트에서 의존성을 설치합니다.

```bash
pip install -r requirements.txt
```

`.env.example` 파일을 참고해 로컬에 `.env` 파일을 생성합니다.

```text
student_id=
token=
```

`.env`에는 인증 토큰 등 민감 정보가 포함되므로 Git에 업로드하지 않습니다.

### 테스트 실행

Part 1 전체 테스트 실행:

```bash
cd part1_api_automation
pytest
```

프로젝트 루트에서 실행할 경우:

```bash
pytest .\part1_api_automation\
```

학습자 테스트 실행:

```bash
pytest tests/test_student
```

교육자 테스트 실행:

```bash
pytest tests/test_teacher
```

권한 경계 테스트 실행:

```bash
pytest tests/test_permission_boundary.py
```

출력 로그를 함께 확인:

```bash
pytest -s
```

### 테스트 마커

등록된 pytest marker는 `part1_api_automation/pytest.ini`에서 관리합니다.

| Marker | 기준 |
|---|---|
| `p0` | 높은 우선순위, 핵심 기능, 기본 접근 가능 여부, 주요 사용자 흐름 |
| `p1` | 보통 우선순위, 주요 기능의 상세 응답 검증 |
| `p2` | 낮은 우선순위, 보조 기능, 부가 정보 |
| `smoke` | 빠른 핵심 동작 확인 |
| `student` | 학습자 권한 API 테스트 |
| `teacher` | 교육자 권한 API 테스트 |
| `auth` | 인증/권한 경계 테스트 |
| `safety` | 운영 서비스 보호 정책 관련 테스트 |

우선순위별 테스트 실행:

```bash
pytest -m p0
pytest -m p1
pytest -m p2
```

권한/범위별 테스트 실행:

```bash
pytest -m student
pytest -m teacher
pytest -m auth
```

smoke 테스트 실행:

```bash
pytest -m smoke
```

### 병렬 테스트 실행

`pytest-xdist`가 설치되어 있어 병렬 실행이 가능합니다.

```bash
pytest -n auto      # 자동 병렬 실행
pytest -n 8         # 8개 병렬 실행
```

다만 본 프로젝트의 API 테스트는 실제 API 서버를 호출합니다.
병렬 실행 시 worker 수만큼 요청량이 증가할 수 있으므로 기본 실행은 순차 실행을 권장합니다.

주의사항:

- 운영 서비스 보호를 위해 병렬 실행은 필요한 경우에만 제한적으로 사용합니다.
- `APIClient`의 요청 간 최소 대기 시간은 client 인스턴스 기준으로 적용됩니다.
- 병렬 worker가 여러 개로 늘어나면 전체 요청량은 순차 실행보다 커질 수 있습니다.
- 요청 지연, 500 응답, timeout이 반복되면 병렬 실행을 중단하고 순차 실행으로 재확인합니다.

### 테스트 작성 기준

테스트 코드는 `Given - When - Then` 흐름을 기준으로 작성합니다.

```python
@pytest.mark.p0
def test_example():
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

### API 요청 정책

운영 서비스에 영향을 줄 수 있으므로 API 호출은 아래 기준을 따릅니다.

- 요청 간 최소 대기 시간 적용
- 요청 timeout 설정 적용
- 기본 실행은 순차 실행 권장
- 불필요한 반복 호출 지양
- `POST`, `PATCH`, `DELETE` API는 데이터 변경 가능성을 먼저 확인
- 500 에러, 접속 지연, 비정상 응답이 반복되면 즉시 중단하고 기록

## 4. 테스트 리포팅 및 CI

### pytest HTML 리포트

HTML 리포트 생성:

```bash
cd part1_api_automation
pytest --html=reports/report.html --self-contained-html
```

### Allure 리포트

Allure 리포트 결과 생성:

```bash
cd part1_api_automation
pytest --alluredir=reports/allure-results
```

Allure HTML 리포트 생성 및 열기:

```bash
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

Allure CLI는 별도 설치가 필요하며 Java 실행 환경이 필요합니다. Windows에서는 `scoop install allure` 등으로 설치할 수 있습니다.

Allure 화면에서 `500 Failed to fetch`가 표시되면 기존 결과와 리포트의 충돌 가능성이 있습니다.
이 경우 `allure-results`와 `allure-report`를 모두 삭제한 뒤 다시 생성합니다.

```powershell
cd .\part1_api_automation

Remove-Item -Recurse -Force .\reports\allure-results, .\reports\allure-report

pytest --alluredir=reports/allure-results

allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

### GitHub Actions

GitHub Actions workflow는 `.github/workflows/api-test.yml`에서 관리합니다.

- `develop` 브랜치 push 시 전체 API 테스트 실행
- `feature/**`, `feat/**`, `fix/**` 브랜치 push 시 변경 범위에 따라 테스트 선택 실행
- GitHub Actions 화면에서 `workflow_dispatch`로 수동 실행 가능
- `TOKEN`, `STUDENT_ID`는 GitHub Actions Secrets로 관리
- pytest 실행 결과를 `reports/report.html`로 생성
- 테스트 실패 시에도 결과 확인이 가능하도록 artifact 업로드에 `if: always()` 적용
- 외부 API timeout 등 일시적 실패가 발생할 수 있으므로 실패한 단일 테스트는 로컬에서 재현 여부를 확인

변경 범위별 실행 기준:

| 변경 조건 | 실행 범위 |
|---|---|
| `develop` push | 전체 API 테스트 |
| `workflow_dispatch` 수동 실행 | 전체 API 테스트 |
| `feature/**`, `feat/**`, `fix/**` push에서 변경 파일이 `test_*.py`인 경우 | 변경된 테스트 파일만 실행 |
| `feature/**`, `feat/**`, `fix/**` push에서 `conftest.py`, `api_client.py`, `config.py`, `request_helper.py`, `pytest.ini`, `utils/test_data/*.py` 변경 | `p0 or p1` 테스트 실행 |
| `feature/**`, `feat/**`, `fix/**` push에서 Part 1 테스트/공통 파일 변경이 없는 경우 | `smoke` 테스트 실행 |

공통 fixture나 API client 계층이 변경되면 여러 테스트에 영향을 줄 수 있으므로 변경 파일만 실행하지 않고 `p0 or p1` 범위로 넓혀 확인합니다.
GitLab Merge Request는 GitHub Pull Request 이벤트로 미러링되지 않는 경우가 많으므로, 이 workflow는 branch push 기준으로 동작하도록 구성합니다.

## 5. 부하 테스트 데이터 분석

### Raw Data 배치

Part 2 부하 테스트 분석은 로컬에 배치한 원본 JMeter 결과 파일을 입력으로 사용합니다.
원본 로그와 생성 CSV는 Git에 업로드하지 않습니다.

원본 파일은 아래 경로에 배치합니다.

```text
part2_load_analysis/
└── data/
    └── 0_preparation_data/
        └── 00_raw_data/
            ├── team2_results/    # Team2 XML/CSV raw files
            └── team3_results/    # Team3 XLSX/CSV raw files
```

### 통합 분석 실행

프로젝트 루트에서 아래 명령어 하나만 실행하면 전처리, 지표 분석, 교차 검증, 시각화, 병목 후보, Go/No-Go 기준 파일이 순서대로 생성됩니다.

```bash
python .\part2_load_analysis\analysis\00_load_analysis.py
```

통합 스크립트는 실행 전에 기존 생성물을 삭제하고 다시 생성합니다.
단, 원본 부하 테스트 파일이 들어 있는 `00_raw_data`는 삭제하지 않습니다.

재생성 대상:

```text
part2_load_analysis/data/0_preparation_data/01_sanitized_data
part2_load_analysis/data/0_preparation_data/02_common_schema_data
part2_load_analysis/data/0_preparation_data/03_analysis_ready_data
part2_load_analysis/data/1_analysis_result_data 하위 분석 결과 폴더
part2_load_analysis/reports/1_metric_analysis
part2_load_analysis/reports/2_result_analysis
```

최종 분석 기준 파일은 아래 위치에 생성됩니다.

```text
part2_load_analysis/data/0_preparation_data/03_analysis_ready_data/
├── loadtest_analysis_ready_requests.csv        # 요청 단위 상세 분석 데이터
└── loadtest_analysis_ready_metrics_by_api.csv  # 팀/부하/API별 성능 지표 요약 데이터
```

### 실행 순서

`00_load_analysis.py`는 내부적으로 아래 스크립트를 순서대로 실행합니다.

```bash
python .\part2_load_analysis\analysis\0_preparation\00_preprocess_load_test_data.py
python .\part2_load_analysis\analysis\1_metric_analysis\01_data_validation.py
python .\part2_load_analysis\analysis\1_metric_analysis\02_metric_summary.py
python .\part2_load_analysis\analysis\1_metric_analysis\04_cross_validation.py
python .\part2_load_analysis\analysis\1_metric_analysis\05_visualization.py
python .\part2_load_analysis\analysis\2_result_analysis\03_bottleneck_candidates.py
python .\part2_load_analysis\analysis\2_result_analysis\06_bottleneck_threshold.py
python .\part2_load_analysis\analysis\2_result_analysis\09_go_nogo_improvement.py
```

### 1,000명 Spike 테스트 시나리오

`part2_load_analysis/jmeter_draft/`에는 1,000명 Spike Traffic 대비 JMeter 시나리오 초안이 포함되어 있습니다.

- `spike_test_scenario_1000_v1.jmx`: 1,000명 Spike Traffic 대비 테스트 시나리오 초안

## 6. 협업 방식

### Git Workflow

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
