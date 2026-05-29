# 성능 지표 집계
# 목적:
# - 분석용 요청 데이터를 기준으로 성능 지표를 계산한다.
# - 팀, 부하 단계, API별로 비교 가능한 표를 만든다.

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# 1. 경로 설정
# ---------------------------------------------------------------------------

# 현재 파일 기준 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parents[2]

# 전처리 완료된 성능 지표 CSV 경로
METRICS_PATH = (
    BASE_DIR
    / "data"
    / "0_preparation_data"
    / "03_analysis_ready_data"
    / "loadtest_analysis_ready_metrics_by_api.csv"
)

# 활성 사용자(active thread) 구간별 상세 분석에 사용하는 요청 단위 데이터
# (API별 집계 데이터가 아닌 raw request 기반 데이터)
REQUESTS_PATH = (
    BASE_DIR
    / "data"
    / "0_preparation_data"
    / "03_analysis_ready_data"
    / "loadtest_analysis_ready_requests.csv"
)


# 분석 결과 저장 폴더
OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "1_analysis_result_data"
    / "01_metric_summary"
)

# 폴더가 없으면 자동 생성
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 2. 공통 저장 함수
# ---------------------------------------------------------------------------

def save_csv(df: pd.DataFrame, file_name: str) -> None:
    """
    DataFrame을 CSV로 저장한다.

    Parameters
    ----------
    df : pd.DataFrame
        저장할 데이터프레임

    file_name : str
        저장 파일명
    """
    output_path = OUTPUT_DIR / file_name

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"[SAVE] {output_path}")


# ---------------------------------------------------------------------------
# 3. p95 기준 상위 API 추출
# ---------------------------------------------------------------------------

def create_p95_top_summary(df: pd.DataFrame) -> None:
    """
    p95 응답시간 기준으로 느린 API를 정렬한다.

    목적:
    - 병목 후보 API 확인
    - 고부하 환경에서 느린 요청 탐지
    """

    p95_top = df.sort_values(
        "p95_response_time_ms",
        ascending=False,
    )[
        [
            "team",
            "load_level",
            "api_label",
            "sample_count",
            "success_count",
            "error_count",
            "avg_response_time_ms",
            "max_response_time_ms",
            "p95_response_time_ms",
            "error_rate",
            "throughput_per_sec",
        ]
    ]

    save_csv(p95_top, "01_p95_top_api.csv")


# ---------------------------------------------------------------------------
# 4. API별 평균 응답시간 요약
# ---------------------------------------------------------------------------

def create_avg_response_summary(df: pd.DataFrame) -> None:
    """
    API별 평균 응답시간 요약 데이터를 생성한다.

    목적:
    - 어떤 API가 상대적으로 느린지 확인
    - Team2 / Team3 성능 비교
    """

    avg_summary = (
        df.groupby(
            ["team", "api_label"],
            as_index=False,
        )
        .agg(
            avg_response_time_ms=("avg_response_time_ms", "mean"),
            max_response_time_ms=("max_response_time_ms", "max"),
            p95_response_time_ms=("p95_response_time_ms", "mean"),
            error_rate=("error_rate", "mean"),
            throughput_per_sec=("throughput_per_sec", "mean"),
        )
        .sort_values(
            ["team", "avg_response_time_ms"],
            ascending=[True, False],
        )
        .round(3)
    )

    save_csv(avg_summary, "02_avg_response_by_api.csv")


# ---------------------------------------------------------------------------
# 5. 오류 발생 API 요약
# ---------------------------------------------------------------------------

def create_error_summary(df: pd.DataFrame) -> None:
    """
    error_rate가 0보다 큰 API만 추출한다.

    목적:
    - 실패 요청 발생 API 확인
    - 부하 환경에서 오류 발생 구간 탐색
    """

    error_summary = df[df["error_rate"] > 0][
        [
            "team",
            "load_level",
            "api_label",
            "sample_count",
            "success_count",
            "error_count",
            "error_rate",
            "avg_response_time_ms",
            "p95_response_time_ms",
        ]
    ].sort_values(
        "error_rate",
        ascending=False,
    )

    save_csv(error_summary, "03_error_api_summary.csv")


# ---------------------------------------------------------------------------
# 6. 팀별 / 부하단계별 성능 요약
# ---------------------------------------------------------------------------

def create_team_load_summary(df: pd.DataFrame) -> None:
    """
    팀별 / 부하단계별 성능 요약 데이터를 생성한다.

    목적:
    - load 증가에 따른 성능 변화 확인
    - Team2 / Team3 비교 분석
    """

    team_load_summary = (
        df.groupby(
            ["team", "load_level"],
            as_index=False,
        )
        .agg(
            avg_response_time_ms=("avg_response_time_ms", "mean"),
            max_response_time_ms=("max_response_time_ms", "max"),
            p95_response_time_ms=("p95_response_time_ms", "mean"),
            total_sample_count=("sample_count", "sum"),
            total_error_count=("error_count", "sum"),
            avg_error_rate=("error_rate", "mean"),
            total_throughput_per_sec=("throughput_per_sec", "sum"),
        )
        .sort_values(
            ["team", "load_level"],
        )
        .round(3)
    )

    save_csv(team_load_summary, "04_team_load_summary.csv")


# ---------------------------------------------------------------------------
# 7. 활성 사용자 구간별 성능 요약
# ---------------------------------------------------------------------------

def create_active_thread_bucket_summary(df: pd.DataFrame) -> None:
    """
    active_threads_group을 10명 단위 구간으로 묶어 성능 지표를 요약한다.

    목적:
    - 같은 부하 단계 안에서 활성 사용자 수 증가에 따른 p95 변화 확인
    - 특정 사용자 구간에서 오류율이 증가하는지 확인
    - 병목이 시작되는 active thread 구간 탐색
    """

    bucket_df = df.copy()

    bucket_df = bucket_df.dropna(
        subset=[
            "active_threads_group",
            "response_time_ms",
            "success",
        ]
    )

    bucket_df["active_threads_group"] = pd.to_numeric(
        bucket_df["active_threads_group"],
        errors="coerce",
    )

    bucket_df["response_time_ms"] = pd.to_numeric(
        bucket_df["response_time_ms"],
        errors="coerce",
    )

    bucket_df = bucket_df.dropna(
        subset=[
            "active_threads_group",
            "response_time_ms",
        ]
    )

    bucket_df["active_thread_bucket"] = (
        ((bucket_df["active_threads_group"] - 1) // 10) * 10 + 1
    ).astype(int).astype(str) + "~" + (
        ((bucket_df["active_threads_group"] - 1) // 10) * 10 + 10
    ).astype(int).astype(str) + "명"

    bucket_df["is_error"] = bucket_df["success"].map(
        lambda value: not value if pd.notna(value) else pd.NA
    )

    bucket_summary = (
        bucket_df.groupby(
            [
                "team",
                "load_level",
                "api_label",
                "active_thread_bucket",
            ],
            as_index=False,
        )
        .agg(
            sample_count=("response_time_ms", "size"),
            avg_response_time_ms=("response_time_ms", "mean"),
            max_response_time_ms=("response_time_ms", "max"),
            p95_response_time_ms=(
                "response_time_ms",
                lambda values: values.quantile(0.95),
            ),
            error_count=("is_error", "sum"),
        )
    )

    bucket_summary["error_rate"] = (
        bucket_summary["error_count"] / bucket_summary["sample_count"]
    )

    bucket_summary = bucket_summary.sort_values(
        [
            "team",
            "load_level",
            "api_label",
            "active_thread_bucket",
        ]
    ).round(3)

    save_csv(
        bucket_summary,
        "05_active_thread_bucket_summary.csv",
    )



# ---------------------------------------------------------------------------
# 8. 주요 관찰 대상 API 추출
# ---------------------------------------------------------------------------

def create_high_response_candidate_summary(df: pd.DataFrame) -> None:
    """
    병목 가능성이 있는 API를 추출한다.

    병목 기준:
    - p95 >= 300ms
    - 평균 응답시간 >= 300ms
    - error_rate > 0

    목적:
    - 발표용 병목 후보 선정
    - 개선 우선순위 도출
    """

    bottleneck_candidates = df[
        (df["p95_response_time_ms"] >= 300)
        | (df["avg_response_time_ms"] >= 300)
        | (df["error_rate"] > 0)
    ][
        [
            "team",
            "load_level",
            "api_label",
            "sample_count",
            "avg_response_time_ms",
            "max_response_time_ms",
            "p95_response_time_ms",
            "error_count",
            "error_rate",
            "throughput_per_sec",
        ]
    ].sort_values(
        ["p95_response_time_ms", "error_rate"],
        ascending=[False, False],
    )

    save_csv(
        bottleneck_candidates,
        "06_high_response_candidates.csv",
    )


# ---------------------------------------------------------------------------
# 9. 메인 실행
# ---------------------------------------------------------------------------

def main() -> None:
    """
    성능 지표 요약 분석 실행

    실행 내용:
    1. p95 기준 느린 API 추출
    2. 평균 응답시간 요약 생성
    3. 오류 발생 API 추출
    4. 팀별 / 부하단계별 성능 요약 생성
    5. 주요 관찰 대상 API 추출
    """

    # metrics CSV 로드
    df = pd.read_csv(
        METRICS_PATH,
        encoding="utf-8-sig",
    )

    # 활성 사용자 구간별(p95, 오류율, TPS) 상세 분석용 요청 데이터 로드
    request_df = pd.read_csv(
        REQUESTS_PATH,
        encoding="utf-8-sig",
    )

    # 분석 실행
    create_p95_top_summary(df)

    create_avg_response_summary(df)

    create_error_summary(df)

    create_team_load_summary(df)

    create_active_thread_bucket_summary(request_df)

    create_high_response_candidate_summary(df)

    print("[DONE] 성능 지표 요약 파일 생성 완료")


# ---------------------------------------------------------------------------
# 10. 프로그램 시작점
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()