"""
Part 2 부하 테스트 로그 분석 작업 파일.

현재 단계의 목표:
1. 00_raw_data 원본 파일을 읽는다.
2. Team3 원본 XLSX에서 Response Assertion 행을 제외한다.
3. request/response 전문, header, queryString 등 민감정보 가능성이 있는 컬럼을 제외한다.
4. 01_sanitized_data에 1차 가공 결과를 CSV로 저장한다.

다음 단계:
- 02_common_schema_data: Team2 / Team3가 동일한 컬럼 구조를 갖도록 정규화
- 03_analysis_ready_data: 성능 지표 집계와 시각화에 바로 사용할 데이터 생성
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from time import time_ns
from urllib.parse import urlparse

import pandas as pd


# ---------------------------------------------------------------------------
# 1. 경로 설정
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
PREPARATION_DATA_DIR = DATA_DIR / "0_preparation_data"

RAW_DATA_DIR = PREPARATION_DATA_DIR / "00_raw_data"
SANITIZED_DATA_DIR = PREPARATION_DATA_DIR / "01_sanitized_data"
COMMON_SCHEMA_DATA_DIR = PREPARATION_DATA_DIR / "02_common_schema_data"
ANALYSIS_READY_DATA_DIR = PREPARATION_DATA_DIR / "03_analysis_ready_data"

TEAM2_RAW_DIR = RAW_DATA_DIR / "team2_results"
TEAM3_RAW_DIR = RAW_DATA_DIR / "team3_results"

TEAM2_SANITIZED_DIR = SANITIZED_DATA_DIR / "team2_results"
TEAM3_SANITIZED_DIR = SANITIZED_DATA_DIR / "team3_results"

TEAM2_COMMON_SCHEMA_DIR = COMMON_SCHEMA_DATA_DIR / "team2_results"
TEAM3_COMMON_SCHEMA_DIR = COMMON_SCHEMA_DATA_DIR / "team3_results"

ANALYSIS_READY_REQUESTS_PATH = ANALYSIS_READY_DATA_DIR / "loadtest_analysis_ready_requests.csv"
ANALYSIS_READY_METRICS_PATH = ANALYSIS_READY_DATA_DIR / "loadtest_analysis_ready_metrics_by_api.csv"


# ---------------------------------------------------------------------------
# 2. Team3 Response Assertion 제외 기준
# ---------------------------------------------------------------------------

# Team3 XLSX에는 실제 API 응답 결과 행과 Response Assertion 결과 행이 함께 저장되어 있다.
# Response Assertion은 API 요청 자체가 아니라 JMeter의 검증 결과 행이므로,
# 성능 지표 계산에서는 제외한다.
ASSERTION_RESULT_COLUMN = "name"
ASSERTION_RESULT_VALUE = "Response Assertion"


# ---------------------------------------------------------------------------
# 3. 민감정보 제외 기준
# ---------------------------------------------------------------------------

# 요청/응답 전문, header, queryString에는 토큰, 계정, 비밀번호, 응답 전문이
# 포함될 수 있으므로 1차 가공 결과에서 제외한다.
SENSITIVE_COLUMNS = {
    "requestHeader",
    "responseHeader",
    "responseData",
    "queryString",
}

# Excel 변환 과정에서 생긴 class 계열 컬럼은 성능 분석 의미가 낮고,
# request/response 전문의 타입 정보에 해당하므로 함께 제외한다.
LOW_VALUE_COLUMNS = {
    "class",
    "class2",
    "class3",
    "class4",
    "class5",
    "class6",
}

DROP_COLUMNS = SENSITIVE_COLUMNS | LOW_VALUE_COLUMNS


# ---------------------------------------------------------------------------
# 4. 공통 유틸
# ---------------------------------------------------------------------------

def extract_load_level(file_name: str) -> int | None:
    """파일명에서 부하 단계(10, 30, 50, 70, 100)를 추출한다."""
    match = re.search(r"\d+", file_name)
    return int(match.group(0)) if match else None


def ensure_output_dirs() -> None:
    """1차 가공 결과 저장 폴더를 생성한다."""
    TEAM2_SANITIZED_DIR.mkdir(parents=True, exist_ok=True)
    TEAM3_SANITIZED_DIR.mkdir(parents=True, exist_ok=True)
    TEAM2_COMMON_SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    TEAM3_COMMON_SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    COMMON_SCHEMA_DATA_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_READY_DATA_DIR.mkdir(parents=True, exist_ok=True)


def output_path_for(source_path: Path, output_dir: Path) -> Path:
    """원본 파일명을 유지하되 CSV 확장자로 1차 가공 결과 경로를 만든다."""
    return output_dir / f"{source_path.stem}_sanitized.csv"


def save_csv_safely(df: pd.DataFrame, path: Path) -> Path:
    """
    CSV를 저장한다.

    Windows에서 파일이 Excel/편집기/미리보기 등에 열려 있으면 덮어쓰기나 삭제가
    실패할 수 있다. 이 경우 파이프라인 전체가 멈추지 않도록 pending 파일로 저장한다.
    """
    try:
        df.to_csv(path, index=False, encoding="utf-8-sig")
        return path
    except PermissionError:
        pending_path = path.with_name(f"{path.stem}_pending_{time_ns()}{path.suffix}")
        df.to_csv(pending_path, index=False, encoding="utf-8-sig")
        print(f"[WARN] Locked file skipped: {path}")
        print(f"[WARN] Wrote pending file instead: {pending_path}")
        return pending_path


# ---------------------------------------------------------------------------
# 5. Team2 XML 1차 가공
# ---------------------------------------------------------------------------

def sanitize_team2_xml(xml_path: Path) -> pd.DataFrame:
    """
    Team2 JMeter XML 파일에서 민감정보를 제외한 요청 단위 데이터를 추출한다.

    제외하는 것:
    - responseHeader
    - requestHeader
    - responseData
    - queryString

    남기는 것:
    - httpSample attribute: t, lt, ct, ts, s, lb, rc, rm, tn, ng, na 등
    - method
    - java.net.URL
    - team, load_level, source_file
    """
    rows: list[dict[str, object]] = []
    load_level = extract_load_level(xml_path.name)

    for _, elem in ET.iterparse(xml_path, events=("end",)):
        if elem.tag != "httpSample":
            continue

        row: dict[str, object] = {
            "team": "Team2",
            "load_level": load_level,
            "source_file": xml_path.name,
        }
        row.update(elem.attrib)

        for child in elem:
            if child.tag in SENSITIVE_COLUMNS:
                continue
            if child.tag == "method":
                row["method"] = child.text
            elif child.tag == "java.net.URL":
                row["url"] = child.text

        rows.append(row)
        elem.clear()

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 6. Team3 XLSX 사전 가공 및 1차 가공
# ---------------------------------------------------------------------------

def remove_team3_response_assertion_rows(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """
    Team3 XLSX에서 Response Assertion 행을 제외한다.

    Team3 원본에는 동일 요청에 대해 실제 API 응답 행과 Assertion 결과 행이
    함께 기록되어 있다. Assertion 행까지 요청으로 집계하면 sample_count,
    throughput, error_rate가 왜곡될 수 있으므로 전처리 초반에 제외한다.
    """
    if ASSERTION_RESULT_COLUMN not in df.columns:
        return df

    assertion_mask = (
        df[ASSERTION_RESULT_COLUMN]
        .astype(str)
        .str.strip()
        .eq(ASSERTION_RESULT_VALUE)
    )
    removed_count = int(assertion_mask.sum())

    if removed_count:
        print(f"[INFO] Removed Team3 Response Assertion rows: {source_name} ({removed_count})")

    return df.loc[~assertion_mask].copy()


def sanitize_team3_xlsx(xlsx_path: Path) -> pd.DataFrame:
    """
    Team3 Excel 파일에서 Assertion 결과 행과 민감정보 가능 컬럼을 제외한다.

    Team3 XLSX에는 requestHeader, responseHeader, responseData, queryString이
    컬럼으로 존재할 수 있으므로 해당 컬럼을 제거한 뒤 CSV로 저장한다.
    """
    df = pd.read_excel(xlsx_path)
    load_level = extract_load_level(xlsx_path.name)

    df = remove_team3_response_assertion_rows(df, xlsx_path.name)
    df = df.drop(columns=[col for col in DROP_COLUMNS if col in df.columns])
    df.insert(0, "source_file", xlsx_path.name)
    df.insert(0, "load_level", load_level)
    df.insert(0, "team", "Team3")

    if "java.net.URL" in df.columns and "url" not in df.columns:
        df = df.rename(columns={"java.net.URL": "url"})

    return df


# ---------------------------------------------------------------------------
# 7. 요약 CSV 1차 가공
# ---------------------------------------------------------------------------

def sanitize_summary_csv(csv_path: Path, team: str) -> pd.DataFrame:
    """
    요약 CSV는 요청/응답 전문이 없는 집계 파일이므로 그대로 읽되,
    추적을 위해 team, load_level, source_file 컬럼을 추가한다.
    """
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    load_level = extract_load_level(csv_path.name)

    df.insert(0, "source_file", csv_path.name)
    df.insert(0, "load_level", load_level)
    df.insert(0, "team", team)

    return df


# ---------------------------------------------------------------------------
# 8. 01_sanitized_data 생성
# ---------------------------------------------------------------------------

def create_sanitized_outputs() -> None:
    """00_raw_data의 파일들을 읽어 01_sanitized_data에 1차 가공 결과를 저장한다."""
    ensure_output_dirs()

    # Team2 XML: 요청 단위 원본 로그
    for xml_path in sorted(TEAM2_RAW_DIR.glob("*.xml")):
        df = sanitize_team2_xml(xml_path)
        save_csv_safely(df, output_path_for(xml_path, TEAM2_SANITIZED_DIR))

    # Team2 CSV: 요약 집계 파일
    for csv_path in sorted(TEAM2_RAW_DIR.glob("*.csv")):
        df = sanitize_summary_csv(csv_path, team="Team2")
        save_csv_safely(df, output_path_for(csv_path, TEAM2_SANITIZED_DIR))

    # Team3 XLSX: 요청 단위 원본 로그
    # summary*.xlsx는 요청 단위 분석 대상이 아니므로 test*.xlsx만 처리한다.
    for xlsx_path in sorted(TEAM3_RAW_DIR.glob("test*.xlsx")):
        df = sanitize_team3_xlsx(xlsx_path)
        save_csv_safely(df, output_path_for(xlsx_path, TEAM3_SANITIZED_DIR))

    # Team3 CSV: 요약 집계 파일
    for csv_path in sorted(TEAM3_RAW_DIR.glob("*.csv")):
        df = sanitize_summary_csv(csv_path, team="Team3")
        save_csv_safely(df, output_path_for(csv_path, TEAM3_SANITIZED_DIR))

    # 폴더 보존용 .gitkeep이 없는 경우 생성한다.
    for output_dir in (TEAM2_SANITIZED_DIR, TEAM3_SANITIZED_DIR):
        gitkeep = output_dir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()


def reset_sanitized_outputs() -> None:
    """1차 가공 결과를 다시 만들기 위해 기존 산출 CSV만 제거한다."""
    for output_dir in (TEAM2_SANITIZED_DIR, TEAM3_SANITIZED_DIR):
        if not output_dir.exists():
            continue
        for csv_path in output_dir.glob("*.csv"):
            try:
                csv_path.unlink()
            except PermissionError:
                print(f"[WARN] Could not delete locked sanitized file: {csv_path}")


def sanitized_outputs_exist() -> bool:
    """1차 가공 결과가 이미 생성되어 있는지 확인한다."""
    return any(TEAM2_SANITIZED_DIR.glob("*_sanitized.csv")) and any(
        TEAM3_SANITIZED_DIR.glob("*_sanitized.csv")
    )


# ---------------------------------------------------------------------------
# 9. 02_common_schema_data 생성
# ---------------------------------------------------------------------------

API_LABEL_MAP = {
    "Auth": "로그인",
    "Auth - Login": "로그인",
    "1. 과목 정보": "과목 정보 조회",
    "API 1 - 과목 정보": "과목 정보 조회",
    "2. 시험 입장": "시험 입장",
    "API 2 - 시험 입장": "시험 입장",
    "3. 시험 시작": "시험 시작",
    "API 3 - 시험 시작": "시험 시작",
    "4. 시험 제출": "시험 제출",
    "API 4 - 시험 제출": "시험 제출",
    "5. 재응시": "재응시",
    "API 5 - 재응시": "재응시",
}

COMMON_REQUEST_COLUMNS = [
    "team",
    "load_level",
    "source_file",
    "api_label_raw",
    "api_label",
    "method",
    "url",
    "response_time_ms",
    "latency_ms",
    "connect_time_ms",
    "success",
    "response_code",
    "response_message",
    "timestamp",
    "thread_name",
    "data_type",
    "sample_count",
    "error_count",
    "active_threads_group",
    "active_threads_all",
    "bytes_received",
    "bytes_sent",
    "failure",
    "error",
]

ANALYSIS_READY_COLUMNS = [
    "team",
    "load_level",
    "run_id",
    "source_file",
    "api_label",
    "api_label_raw",
    "endpoint_path",
    "response_time_ms",
    "latency_ms",
    "connect_time_ms",
    "success",
    "is_error",
    "response_code",
    "response_message",
    "timestamp",
    "request_datetime",
    "elapsed_from_start_sec",
    "active_threads_group",
    "active_threads_all",
    "bytes_received",
    "bytes_sent",
]


def normalize_api_label(label: object) -> object:
    """원본 API 라벨을 공통 API 라벨로 변환한다."""
    if pd.isna(label):
        return label
    label_text = str(label).strip()
    return API_LABEL_MAP.get(label_text, label_text)


def to_bool(value: object) -> bool | None:
    """JMeter 성공 여부 값을 bool로 변환한다."""
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def add_missing_common_columns(df: pd.DataFrame) -> pd.DataFrame:
    """공통 스키마에 없는 컬럼을 추가하고 컬럼 순서를 맞춘다."""
    for column in COMMON_REQUEST_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA
    return df[COMMON_REQUEST_COLUMNS]


def convert_team2_request_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Team2 sanitized XML 데이터를 공통 요청 단위 스키마로 변환한다."""
    converted = pd.DataFrame()
    converted["team"] = df["team"]
    converted["source_file"] = df["source_file"]
    converted["load_level"] = converted["source_file"].map(extract_load_level)
    converted["api_label_raw"] = df["lb"]
    converted["api_label"] = df["lb"].map(normalize_api_label)
    converted["method"] = df["method"] if "method" in df.columns else pd.NA
    converted["url"] = df["url"] if "url" in df.columns else pd.NA
    converted["response_time_ms"] = pd.to_numeric(df["t"], errors="coerce")
    converted["latency_ms"] = pd.to_numeric(df["lt"], errors="coerce")
    converted["connect_time_ms"] = pd.to_numeric(df["ct"], errors="coerce")
    converted["success"] = df["s"].map(to_bool)
    converted["response_code"] = df["rc"]
    converted["response_message"] = df["rm"]
    converted["timestamp"] = pd.to_numeric(df["ts"], errors="coerce")
    converted["thread_name"] = df["tn"]
    converted["data_type"] = df["dt"] if "dt" in df.columns else pd.NA
    converted["sample_count"] = pd.to_numeric(df["sc"], errors="coerce") if "sc" in df.columns else pd.NA
    converted["error_count"] = pd.to_numeric(df["ec"], errors="coerce") if "ec" in df.columns else pd.NA
    converted["active_threads_group"] = pd.to_numeric(df["ng"], errors="coerce")
    converted["active_threads_all"] = pd.to_numeric(df["na"], errors="coerce")

    return add_missing_common_columns(converted)


def convert_team3_request_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Team3 sanitized XLSX 데이터를 공통 요청 단위 스키마로 변환한다."""
    converted = pd.DataFrame()
    converted["team"] = df["team"]
    converted["source_file"] = df["source_file"]
    converted["load_level"] = converted["source_file"].map(extract_load_level)
    converted["api_label_raw"] = df["lb"]
    converted["api_label"] = df["lb"].map(normalize_api_label)
    converted["method"] = df["method"] if "method" in df.columns else pd.NA
    converted["url"] = df["url"] if "url" in df.columns else pd.NA
    converted["response_time_ms"] = pd.to_numeric(df["t"], errors="coerce")
    converted["latency_ms"] = pd.to_numeric(df["lt"], errors="coerce")
    converted["connect_time_ms"] = pd.to_numeric(df["ct"], errors="coerce")
    converted["success"] = df["s"].map(to_bool)
    converted["response_code"] = df["rc"]
    converted["response_message"] = df["rm"]
    converted["timestamp"] = pd.to_numeric(df["ts"], errors="coerce")
    converted["thread_name"] = df["tn"]
    converted["data_type"] = df["dt"] if "dt" in df.columns else pd.NA
    converted["active_threads_group"] = pd.to_numeric(df["ng"], errors="coerce")
    converted["active_threads_all"] = pd.to_numeric(df["na"], errors="coerce")
    converted["bytes_received"] = pd.to_numeric(df["by"], errors="coerce") if "by" in df.columns else pd.NA
    converted["bytes_sent"] = pd.to_numeric(df["sby"], errors="coerce") if "sby" in df.columns else pd.NA
    converted["failure"] = df["failure"] if "failure" in df.columns else pd.NA
    converted["error"] = df["error"] if "error" in df.columns else pd.NA

    return add_missing_common_columns(converted)


def create_common_schema_outputs() -> None:
    """01_sanitized_data의 요청 단위 원본 로그를 공통 컬럼 구조로 변환한다."""
    ensure_output_dirs()

    team2_frames = []
    for csv_path in sorted(TEAM2_SANITIZED_DIR.glob("result*_sanitized.csv")):
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        converted = convert_team2_request_schema(df)
        team2_frames.append(converted)
        save_csv_safely(
            converted,
            TEAM2_COMMON_SCHEMA_DIR / csv_path.name.replace("_sanitized", "_common_schema"),
        )

    team3_frames = []
    for csv_path in sorted(TEAM3_SANITIZED_DIR.glob("test*_sanitized.csv")):
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        converted = convert_team3_request_schema(df)
        team3_frames.append(converted)
        save_csv_safely(
            converted,
            TEAM3_COMMON_SCHEMA_DIR / csv_path.name.replace("_sanitized", "_common_schema"),
        )

    combined_frames = team2_frames + team3_frames
    if combined_frames:
        combined = pd.concat(combined_frames, ignore_index=True)
        save_csv_safely(
            combined,
            COMMON_SCHEMA_DATA_DIR / "loadtest_common_schema_requests.csv",
        )

    for output_dir in (TEAM2_COMMON_SCHEMA_DIR, TEAM3_COMMON_SCHEMA_DIR):
        gitkeep = output_dir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()


def reset_common_schema_outputs() -> None:
    """2차 공통 스키마 결과 CSV를 제거한다."""
    for output_dir in (TEAM2_COMMON_SCHEMA_DIR, TEAM3_COMMON_SCHEMA_DIR):
        if output_dir.exists():
            for csv_path in output_dir.glob("*.csv"):
                try:
                    csv_path.unlink()
                except PermissionError:
                    print(f"[WARN] Could not delete locked common schema file: {csv_path}")
    combined_path = COMMON_SCHEMA_DATA_DIR / "loadtest_common_schema_requests.csv"
    if combined_path.exists():
        try:
            combined_path.unlink()
        except PermissionError:
            print(f"[WARN] Could not delete locked combined file: {combined_path}")


def extract_endpoint_path(url: object) -> object:
    """Return only the path part of a URL for API-level analysis."""
    if pd.isna(url):
        return pd.NA
    parsed = urlparse(str(url))
    return parsed.path or str(url)


def create_analysis_ready_requests(df: pd.DataFrame) -> pd.DataFrame:
    """Filter common-schema rows down to the columns needed for analysis."""
    analysis_df = df.copy()

    for column in (
        "load_level",
        "response_time_ms",
        "latency_ms",
        "connect_time_ms",
        "timestamp",
        "active_threads_group",
        "active_threads_all",
        "bytes_received",
        "bytes_sent",
    ):
        if column in analysis_df.columns:
            analysis_df[column] = pd.to_numeric(analysis_df[column], errors="coerce")

    analysis_df["success"] = analysis_df["success"].map(to_bool)
    analysis_df["is_error"] = analysis_df["success"].map(
        lambda value: not value if value is not None else pd.NA
    )
    analysis_df["run_id"] = (
        analysis_df["team"].astype(str)
        + "_"
        + analysis_df["source_file"].astype(str).map(lambda value: Path(value).stem)
    )
    analysis_df["endpoint_path"] = analysis_df["url"].map(extract_endpoint_path)
    analysis_df["request_datetime"] = pd.to_datetime(
        analysis_df["timestamp"], unit="ms", utc=True, errors="coerce"
    )

    required_columns = [
        "team",
        "load_level",
        "api_label",
        "response_time_ms",
        "success",
        "timestamp",
    ]
    analysis_df = analysis_df.dropna(subset=required_columns)
    analysis_df = analysis_df[analysis_df["response_time_ms"] >= 0]

    analysis_df = analysis_df.sort_values(
        ["team", "load_level", "source_file", "timestamp", "api_label"],
        ignore_index=True,
    )
    first_timestamp_by_run = analysis_df.groupby("run_id")["timestamp"].transform("min")
    analysis_df["elapsed_from_start_sec"] = (
        analysis_df["timestamp"] - first_timestamp_by_run
    ) / 1000

    return analysis_df[ANALYSIS_READY_COLUMNS]


def create_analysis_ready_metrics(analysis_df: pd.DataFrame) -> pd.DataFrame:
    """Create basic API-level performance metrics from analysis-ready requests."""
    grouped = analysis_df.groupby(["team", "load_level", "api_label"], dropna=False)

    metrics = grouped.agg(
        sample_count=("response_time_ms", "size"),
        success_count=("success", "sum"),
        error_count=("is_error", "sum"),
        avg_response_time_ms=("response_time_ms", "mean"),
        min_response_time_ms=("response_time_ms", "min"),
        max_response_time_ms=("response_time_ms", "max"),
        p50_response_time_ms=("response_time_ms", lambda values: values.quantile(0.50)),
        p90_response_time_ms=("response_time_ms", lambda values: values.quantile(0.90)),
        p95_response_time_ms=("response_time_ms", lambda values: values.quantile(0.95)),
        std_response_time_ms=("response_time_ms", "std"),
        avg_latency_ms=("latency_ms", "mean"),
        avg_connect_time_ms=("connect_time_ms", "mean"),
        started_at=("timestamp", "min"),
        ended_at=("timestamp", "max"),
    ).reset_index()

    metrics["error_rate"] = metrics["error_count"] / metrics["sample_count"]
    duration_sec = (metrics["ended_at"] - metrics["started_at"]) / 1000
    metrics["throughput_per_sec"] = metrics["sample_count"] / duration_sec.where(
        duration_sec > 0
    )

    numeric_columns = [
        "avg_response_time_ms",
        "min_response_time_ms",
        "max_response_time_ms",
        "p50_response_time_ms",
        "p90_response_time_ms",
        "p95_response_time_ms",
        "std_response_time_ms",
        "avg_latency_ms",
        "avg_connect_time_ms",
        "error_rate",
        "throughput_per_sec",
    ]
    metrics[numeric_columns] = metrics[numeric_columns].round(3)

    return metrics.sort_values(["team", "load_level", "api_label"], ignore_index=True)


def reset_analysis_ready_outputs() -> None:
    """Remove generated analysis-ready CSV files before rebuilding them."""
    if not ANALYSIS_READY_DATA_DIR.exists():
        return
    for csv_path in ANALYSIS_READY_DATA_DIR.glob("*.csv"):
        try:
            csv_path.unlink()
        except PermissionError:
            print(f"[WARN] Could not delete locked analysis-ready file: {csv_path}")


def create_analysis_ready_outputs() -> None:
    """Create 03_analysis_ready_data from the combined common-schema request data."""
    ensure_output_dirs()
    combined_path = COMMON_SCHEMA_DATA_DIR / "loadtest_common_schema_requests.csv"
    if not combined_path.exists():
        print(f"[WARN] Common schema file not found: {combined_path}")
        return

    common_df = pd.read_csv(combined_path, encoding="utf-8-sig")
    analysis_df = create_analysis_ready_requests(common_df)
    metrics_df = create_analysis_ready_metrics(analysis_df)

    save_csv_safely(analysis_df, ANALYSIS_READY_REQUESTS_PATH)
    save_csv_safely(metrics_df, ANALYSIS_READY_METRICS_PATH)

    gitkeep = ANALYSIS_READY_DATA_DIR / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()


def main() -> None:
    """1차 가공 결과를 준비하고 2차 공통 스키마 결과를 생성한다."""
    reset_sanitized_outputs()
    create_sanitized_outputs()
    reset_common_schema_outputs()
    create_common_schema_outputs()
    reset_analysis_ready_outputs()
    create_analysis_ready_outputs()


if __name__ == "__main__":
    main()
