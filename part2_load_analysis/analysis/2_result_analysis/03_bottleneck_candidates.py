# 분석표 구조 정리
# 목적:
# - 성능 지표를 기준으로 1차 병목 후보 API를 정리한다.
# - 병목 판단에 필요한 분석표 구조를 만든다.

from __future__ import annotations
from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------------
# 1. 경로 설정
# 2. 병목 후보 판단 기준
# 3. 입력 데이터 로드 및 검증
# 4. 요청 단위 보조 근거 생성
# 5. 병목 점수 계산
# 6. 결과 테이블 생성 및 저장
# ---------------------------------------------------------------------------

# 02_metric_summary.py는 발표/검토용 요약표를 넓게 생성한다.
# 이 파일은 02 산출물을 직접 입력으로 쓰지 않고, 전처리 완료 지표와 요청 단위
# 데이터를 다시 읽어 p99/느린 요청 수/실패 요청 수를 보강한 병목 후보표를 만든다.


# ---------------------------------------------------------------------------
# 1. 경로 설정
# ---------------------------------------------------------------------------

# 이 파일은 analysis/2_result_analysis/ 아래에 있으므로 parents[2]가
# part2_load_analysis 폴더를 가리킨다.
BASE_DIR = Path(__file__).resolve().parents[2]

# 00 전처리 스크립트가 만든 최종 분석용 CSV를 입력으로 사용한다.
ANALYSIS_READY_DATA_DIR = BASE_DIR / "data" / "0_preparation_data" / "03_analysis_ready_data"

# 03 단계의 결과는 전용 하위 폴더에 저장한다.
RESULT_DATA_DIR = BASE_DIR / "data" / "1_analysis_result_data"
OUTPUT_DIR = RESULT_DATA_DIR / "03_bottleneck_candidates"

# metrics 파일은 API/팀/부하 단계별로 이미 집계된 성능 지표다.
METRICS_PATH = ANALYSIS_READY_DATA_DIR / "loadtest_analysis_ready_metrics_by_api.csv"

# requests 파일은 개별 요청 단위 데이터다. p99, 실패 요청 수, 느린 요청 수를 보강할 때 사용한다.
REQUESTS_PATH = ANALYSIS_READY_DATA_DIR / "loadtest_analysis_ready_requests.csv"
OUTPUT_PATH = OUTPUT_DIR / "03_bottleneck_candidates.csv"
FOCUS_OUTPUT_PATH = OUTPUT_DIR / "03_bottleneck_candidates_focus.csv"


# ---------------------------------------------------------------------------
# 2. 병목 후보 판단 기준
# ---------------------------------------------------------------------------

# 이번 단계는 최종 확정이 아니라 1차 후보 선별이다.
# 절대 기준은 보수적으로 두고, 현재 데이터 안에서 상대적으로 나쁜 API도 함께 잡는다.

# 평균 응답시간이 300ms 이상이면 사용자가 전반적으로 느리다고 느낄 가능성이 있어 경고로 본다.
AVG_RESPONSE_WARN_MS = 300

# p95는 전체 요청 중 느린 쪽 5%의 경계값이다. 500ms 이상이면 일부 사용자가 지연을 겪는다고 본다.
P95_RESPONSE_WARN_MS = 500

# max는 순간 튐 현상을 보기 위한 값이다. 800ms 이상이면 이상값 후보로 본다.
MAX_RESPONSE_WARN_MS = 800

# 오류율은 0이 가장 좋다. 여기서는 0.1% 이상부터 위험 신호로 잡는다.
ERROR_RATE_WARN = 0.001

# 같은 팀/같은 부하 단계 안에서 상위 25%에 드는 API는 상대적으로 느린 API로 표시한다.
RELATIVE_TOP_RATE = 0.25


# metrics_by_api 파일에서 반드시 있어야 하는 컬럼이다.
# 이 컬럼들이 없으면 병목 점수를 계산할 수 없으므로 바로 중단한다.
REQUIRED_METRIC_COLUMNS = {
    "team",
    "load_level",
    "api_label",
    "sample_count",
    "error_count",
    "avg_response_time_ms",
    "max_response_time_ms",
    "p95_response_time_ms",
    "std_response_time_ms",
    "error_rate",
    "throughput_per_sec",
}

# requests 파일에서 반드시 있어야 하는 컬럼이다.
# 요청 단위 보조 근거를 만들기 위한 최소 컬럼만 요구한다.
REQUIRED_REQUEST_COLUMNS = {
    "team",
    "load_level",
    "api_label",
    "response_time_ms",
    "is_error",
}


# ---------------------------------------------------------------------------
# 3. 입력 데이터 로드 및 검증
# ---------------------------------------------------------------------------


def read_csv(path: Path) -> pd.DataFrame:
    # 입력 파일이 없으면 뒤에서 알 수 없는 KeyError가 나기 전에 명확하게 실패시킨다.
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_csv(path, encoding="utf-8-sig")


def validate_columns(df: pd.DataFrame, required_columns: set[str], source_name: str) -> None:
    # 전처리 산출물 구조가 바뀌었을 때 가장 먼저 확인할 수 있는 방어 코드다.
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise ValueError(f"{source_name} missing columns: {missing_columns}")


def normalize_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    # CSV는 숫자처럼 보여도 문자열로 읽힐 수 있다.
    # 비교/점수 계산 전에 숫자 컬럼을 명시적으로 변환한다.
    numeric_columns = [
        "load_level",
        "sample_count",
        "error_count",
        "avg_response_time_ms",
        "max_response_time_ms",
        "p95_response_time_ms",
        "std_response_time_ms",
        "error_rate",
        "throughput_per_sec",
    ]

    normalized = df.copy()
    for column in numeric_columns:
        # 변환할 수 없는 값은 NaN으로 두어 pandas 계산에서 자연스럽게 제외되도록 한다.
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    return normalized


def normalize_bool_series(series: pd.Series) -> pd.Series:
    # CSV 로드 방식에 따라 bool 값이 True/False, "true"/"false", 1/0 등으로
    # 들어올 수 있다. bool("False")가 True가 되는 문제를 피하기 위해 명시 변환한다.
    normalized = series.copy()

    if pd.api.types.is_bool_dtype(normalized):
        return normalized

    text = normalized.astype(str).str.strip().str.lower()
    return text.map(
        {
            "true": True,
            "1": True,
            "yes": True,
            "false": False,
            "0": False,
            "no": False,
            "nan": False,
            "none": False,
            "": False,
        }
    ).fillna(False)


# ---------------------------------------------------------------------------
# 4. 요청 단위 보조 근거 생성
# ---------------------------------------------------------------------------


def summarize_request_evidence(requests_df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(requests_df, REQUIRED_REQUEST_COLUMNS, "requests data")

    request_data = requests_df.copy()

    # 요청 단위 데이터는 병목 후보 판단의 보조 근거다.
    # metrics 파일에 없는 p99, 느린 요청 수, 실패 요청 수를 여기서 만든다.
    request_data["response_time_ms"] = pd.to_numeric(
        request_data["response_time_ms"], errors="coerce"
    )
    request_data["is_error"] = normalize_bool_series(request_data["is_error"])

    return (
        # 팀/부하/API 단위로 묶어 metrics_by_api와 같은 기준의 보조 지표를 만든다.
        request_data.groupby(["team", "load_level", "api_label"], dropna=False)
        .agg(
            request_count=("response_time_ms", "size"),
            failed_request_count=("is_error", "sum"),
            # p99는 극단적으로 느린 요청이 일부 있는지 확인하는 보조 지표다.
            request_p99_response_time_ms=("response_time_ms", lambda x: x.quantile(0.99)),
            # p95 경고 기준보다 느린 개별 요청이 몇 건인지 센다.
            slow_request_count=("response_time_ms", lambda x: (x >= P95_RESPONSE_WARN_MS).sum()),
        )
        .reset_index()
    )


# ---------------------------------------------------------------------------
# 5. 병목 점수 계산
# ---------------------------------------------------------------------------


def add_relative_flags(metrics_df: pd.DataFrame) -> pd.DataFrame:
    scored = metrics_df.copy()

    # 절대 기준만 쓰면 전체적으로 빠른 테스트에서는 후보가 하나도 안 나올 수 있다.
    # 그래서 같은 팀/같은 부하 단계 안에서 상대적으로 나쁜 API도 같이 표시한다.
    scored["relative_avg_rank_pct"] = scored.groupby(["team", "load_level"])[
        "avg_response_time_ms"
    ].rank(pct=True)
    scored["relative_p95_rank_pct"] = scored.groupby(["team", "load_level"])[
        "p95_response_time_ms"
    ].rank(pct=True)
    scored["relative_error_rank_pct"] = scored.groupby(["team", "load_level"])[
        "error_rate"
    ].rank(pct=True)

    scored["is_relative_avg_high"] = scored["relative_avg_rank_pct"] >= 1 - RELATIVE_TOP_RATE
    scored["is_relative_p95_high"] = scored["relative_p95_rank_pct"] >= 1 - RELATIVE_TOP_RATE
    scored["is_relative_error_high"] = (
        # 오류율은 모두 0인 경우가 많으므로, 실제 오류가 있는 경우에만 상대 오류율 플래그를 켠다.
        (scored["error_rate"] > 0)
        & (scored["relative_error_rank_pct"] >= 1 - RELATIVE_TOP_RATE)
    )
    return scored


def add_bottleneck_scores(metrics_df: pd.DataFrame) -> pd.DataFrame:
    scored = add_relative_flags(metrics_df)

    # 절대 기준 플래그: 이 값들은 그 자체로 위험 신호가 될 수 있다.
    scored["is_avg_slow"] = scored["avg_response_time_ms"] >= AVG_RESPONSE_WARN_MS
    scored["is_p95_slow"] = scored["p95_response_time_ms"] >= P95_RESPONSE_WARN_MS
    scored["is_max_slow"] = scored["max_response_time_ms"] >= MAX_RESPONSE_WARN_MS
    scored["has_error"] = scored["error_rate"] >= ERROR_RATE_WARN

    # 점수 가중치:
    # - 평균/p95/오류율은 사용자 체감과 안정성에 직접 연결되므로 2점
    # - max와 상대 순위는 보조 신호이므로 1점
    # 점수가 높을수록 06 단계에서 우선 검토할 후보가 된다.
    scored["bottleneck_score"] = (
        scored["is_avg_slow"].astype(int) * 2
        + scored["is_p95_slow"].astype(int) * 2
        + scored["is_max_slow"].astype(int) * 1
        + scored["has_error"].astype(int) * 2
        + scored["is_relative_avg_high"].astype(int) * 1
        + scored["is_relative_p95_high"].astype(int) * 1
        + scored["is_relative_error_high"].astype(int) * 1
    )

    return scored


def classify_candidate_level(score: int) -> str:
    # 이 등급은 최종 결론이 아니라 03 단계의 정렬 기준이다.
    # 06 단계에서 임계점과 그래프를 함께 보고 최종 병목 여부를 판단한다.
    if score >= 5:
        return "병목 후보"
    if score >= 3:
        return "관찰 필요"
    return "정상 범위"


def build_reason(row: pd.Series) -> str:
    reasons: list[str] = []

    # 결과 CSV를 사람이 바로 읽을 수 있도록, 점수가 올라간 이유를 문장으로 남긴다.
    if row["is_avg_slow"]:
        reasons.append(f"평균 응답시간 {row['avg_response_time_ms']:.1f}ms")
    if row["is_p95_slow"]:
        reasons.append(f"p95 응답시간 {row['p95_response_time_ms']:.1f}ms")
    if row["is_max_slow"]:
        reasons.append(f"최대 응답시간 {row['max_response_time_ms']:.1f}ms")
    if row["has_error"]:
        reasons.append(f"오류율 {row['error_rate']:.3%}")
    if row["is_relative_avg_high"]:
        reasons.append("같은 팀/부하 단계 내 평균 응답시간 상위권")
    if row["is_relative_p95_high"]:
        reasons.append("같은 팀/부하 단계 내 p95 응답시간 상위권")
    if row["is_relative_error_high"]:
        reasons.append("같은 팀/부하 단계 내 오류율 상위권")

    if not reasons:
        return "주요 위험 신호 없음"
    return " / ".join(reasons)


# ---------------------------------------------------------------------------
# 6. 결과 테이블 생성 및 저장
# ---------------------------------------------------------------------------


def create_bottleneck_candidates(metrics_df: pd.DataFrame, requests_df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(metrics_df, REQUIRED_METRIC_COLUMNS, "metrics data")

    # metrics: 후보 점수 계산의 주 데이터
    # request_evidence: 요청 단위에서만 확인 가능한 보조 근거
    metrics = normalize_numeric_columns(metrics_df)
    request_evidence = summarize_request_evidence(requests_df)
    scored = add_bottleneck_scores(metrics)

    # 두 데이터는 team/load_level/api_label 단위로 합친다.
    # requests에 일부 API가 없더라도 metrics 기준 행은 유지한다.
    result = scored.merge(
        request_evidence,
        on=["team", "load_level", "api_label"],
        how="left",
    )

    result["candidate_level"] = result["bottleneck_score"].apply(classify_candidate_level)
    result["reason"] = result.apply(build_reason, axis=1)

    # 이후 06 단계에서 바로 쓰기 쉽도록 판단에 필요한 컬럼만 남긴다.
    output_columns = [
        "team",
        "load_level",
        "api_label",
        "sample_count",
        "avg_response_time_ms",
        "p95_response_time_ms",
        "max_response_time_ms",
        "std_response_time_ms",
        "error_count",
        "error_rate",
        "throughput_per_sec",
        "request_p99_response_time_ms",
        "slow_request_count",
        "failed_request_count",
        "bottleneck_score",
        "candidate_level",
        "reason",
    ]

    # 병목 점수가 높은 행을 위로 올리고, 같은 점수라면 p95/max가 큰 API를 먼저 보이게 한다.
    return result[output_columns].sort_values(
        by=["bottleneck_score", "p95_response_time_ms", "max_response_time_ms"],
        ascending=[False, False, False],
    )


def save_result(df: pd.DataFrame) -> None:
    # 결과 폴더가 없으면 생성한다. 원본/전처리 데이터 폴더와는 분리해서 저장한다.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 같은 스크립트를 여러 번 실행해도 이전 03 결과가 섞이지 않도록 기존 CSV를 먼저 지운다.
    for old_csv in OUTPUT_DIR.glob("03_bottleneck_candidates*.csv"):
        try:
            old_csv.unlink()
        except PermissionError as exc:
            raise PermissionError(
                f"기존 결과 파일을 삭제할 수 없습니다. 열려 있는 파일을 닫고 다시 실행하세요: {old_csv}"
            ) from exc

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    focus_df = df[df["candidate_level"].isin(["병목 후보", "관찰 필요"])].copy()
    focus_df.to_csv(FOCUS_OUTPUT_PATH, index=False, encoding="utf-8-sig")


def print_focus_summary(df: pd.DataFrame) -> None:
    focus_df = df[df["candidate_level"].isin(["병목 후보", "관찰 필요"])].copy()

    if focus_df.empty:
        print("Focus candidates: 0")
        return

    print()
    print(f"Focus CSV: {FOCUS_OUTPUT_PATH}")

    for level in ("병목 후보", "관찰 필요"):
        level_df = focus_df[focus_df["candidate_level"] == level]
        print()
        print(f"{level}: {len(level_df)}")

        for row in level_df.itertuples(index=False):
            print(
                f"- {row.team} / {int(row.load_level)}명 / {row.api_label} "
                f"/ score {int(row.bottleneck_score)} "
                f"/ avg {row.avg_response_time_ms:.1f}ms "
                f"/ p95 {row.p95_response_time_ms:.1f}ms "
                f"/ max {row.max_response_time_ms:.1f}ms "
                f"/ error {row.error_rate:.3%}"
            )
            print(f"  reason: {row.reason}")


def main() -> None:
    # 실행 흐름:
    # 1. 전처리 완료 데이터 로드
    # 2. 병목 후보 점수 계산
    # 3. 결과 CSV 저장
    # 4. 콘솔에 등급별 개수 출력
    metrics_df = read_csv(METRICS_PATH)
    requests_df = read_csv(REQUESTS_PATH)

    candidates_df = create_bottleneck_candidates(metrics_df, requests_df)
    save_result(candidates_df)

    print(f"Created: {OUTPUT_PATH}")
    print(f"Rows: {len(candidates_df)}")
    print(candidates_df["candidate_level"].value_counts().to_string())
    print_focus_summary(candidates_df)


if __name__ == "__main__":
    main()
