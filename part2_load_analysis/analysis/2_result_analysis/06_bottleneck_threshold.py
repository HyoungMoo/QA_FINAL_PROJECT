"""병목 API 및 임계점 도출.

03 단계에서 추린 후보 API를 대상으로 부하 단계별 지표와 활성 사용자 수 구간별
지표를 함께 확인해, 실제 병목인지 단순 관찰 대상인지 재판단한다.
"""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ---------------------------------------------------------------------------
# 1. 경로 설정
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

ANALYSIS_READY_DATA_DIR = BASE_DIR / "data" / "0_preparation_data" / "03_analysis_ready_data"
RESULT_DATA_DIR = BASE_DIR / "data" / "1_analysis_result_data"

METRICS_PATH = ANALYSIS_READY_DATA_DIR / "loadtest_analysis_ready_metrics_by_api.csv"
REQUESTS_PATH = ANALYSIS_READY_DATA_DIR / "loadtest_analysis_ready_requests.csv"
CANDIDATE_PATH = (
    RESULT_DATA_DIR
    / "03_bottleneck_candidates"
    / "03_bottleneck_candidates_focus.csv"
)

OUTPUT_DIR = RESULT_DATA_DIR / "06_bottleneck_threshold"
REPORT_DIR = BASE_DIR / "reports" / "2_result_analysis" / "06_bottleneck_threshold"

THRESHOLD_OUTPUT_PATH = OUTPUT_DIR / "06_bottleneck_threshold.csv"
SUMMARY_OUTPUT_PATH = OUTPUT_DIR / "06_bottleneck_api_summary.csv"
ACTIVE_BUCKET_OUTPUT_PATH = OUTPUT_DIR / "06_active_thread_bucket_metrics.csv"
ACTIVE_TREND_OUTPUT_PATH = OUTPUT_DIR / "06_active_thread_trend_check.csv"
ACTIVE_FOCUS_OUTPUT_PATH = OUTPUT_DIR / "06_active_thread_trend_check_focus.csv"


# ---------------------------------------------------------------------------
# 2. 판단 기준
# ---------------------------------------------------------------------------

PASS_AVG_MS = 1000
PASS_MAX_MS = 5000
PASS_ERROR_RATE = 0.01

P95_CAUTION_MS = 500
MAX_CAUTION_MS = 800
ERROR_CAUTION_RATE = 0.001

AVG_DEGRADATION_PCT = 20
P95_DEGRADATION_PCT = 20
TPS_SCALE_MIN_RATIO = 5

ACTIVE_BUCKET_SIZE = 10
MIN_RELIABLE_BUCKET_SAMPLES = 10
ACTIVE_P95_INCREASE_RATE = 0.20

LOAD_LEVELS = [10, 30, 50, 70, 100]

REQUIRED_METRIC_COLUMNS = {
    "team",
    "load_level",
    "api_label",
    "sample_count",
    "avg_response_time_ms",
    "max_response_time_ms",
    "p90_response_time_ms",
    "p95_response_time_ms",
    "std_response_time_ms",
    "error_rate",
    "throughput_per_sec",
}

REQUIRED_REQUEST_COLUMNS = {
    "team",
    "load_level",
    "api_label",
    "response_time_ms",
    "is_error",
    "elapsed_from_start_sec",
    "active_threads_group",
}

REQUIRED_CANDIDATE_COLUMNS = {
    "team",
    "load_level",
    "api_label",
    "candidate_level",
    "bottleneck_score",
}


# ---------------------------------------------------------------------------
# 3. 공통 유틸리티
# ---------------------------------------------------------------------------

def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_csv(path, encoding="utf-8-sig")


def validate_columns(df: pd.DataFrame, required_columns: set[str], source_name: str) -> None:
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise ValueError(f"{source_name} missing columns: {missing_columns}")


def normalize_bool_series(series: pd.Series) -> pd.Series:
    """문자열 False가 True로 해석되는 문제를 막기 위해 명시적으로 bool 변환한다."""

    if series.dtype == bool:
        return series

    normalized = series.astype(str).str.strip().str.lower()
    return normalized.isin({"true", "1", "yes", "y", "error", "fail", "failed"})


def normalize_metric_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    numeric_columns = [
        "load_level",
        "sample_count",
        "avg_response_time_ms",
        "max_response_time_ms",
        "p90_response_time_ms",
        "p95_response_time_ms",
        "std_response_time_ms",
        "error_rate",
        "throughput_per_sec",
    ]
    for column in numeric_columns:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    return normalized


def normalize_request_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    numeric_columns = [
        "load_level",
        "response_time_ms",
        "elapsed_from_start_sec",
        "active_threads_group",
    ]
    for column in numeric_columns:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    normalized["is_error"] = normalize_bool_series(normalized["is_error"])
    return normalized


def reset_output_dirs() -> None:
    """06 산출물 폴더 안의 기존 파일만 정리한다."""

    for directory in [OUTPUT_DIR, REPORT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        for path in directory.iterdir():
            if path.is_file():
                try:
                    path.unlink()
                except PermissionError:
                    print(f"[WARN] Output file is locked, skip delete: {path}")


def setup_korean_font() -> None:
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False


def save_csv(df: pd.DataFrame, path: Path) -> Path:
    """CSV를 저장한다. 열려 있는 파일이면 timestamp가 붙은 대체 파일로 저장한다."""

    try:
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"[SAVE] {path}")
        return path
    except PermissionError:
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        fallback_path = path.with_name(f"{path.stem}_{timestamp}{path.suffix}")
        df.to_csv(fallback_path, index=False, encoding="utf-8-sig")
        print(f"[WARN] Output file is locked: {path}")
        print(f"[SAVE] {fallback_path}")
        return fallback_path


def save_png(fig: plt.Figure, path: Path) -> Path:
    """PNG를 저장한다. 열려 있는 파일이면 timestamp가 붙은 대체 파일로 저장한다."""

    image_buffer = BytesIO()
    fig.savefig(image_buffer, format="png", dpi=150)

    try:
        path.write_bytes(image_buffer.getvalue())
        print(f"[SAVE] {path}")
        return path
    except PermissionError:
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        fallback_path = path.with_name(f"{path.stem}_{timestamp}{path.suffix}")
        fallback_path.write_bytes(image_buffer.getvalue())
        print(f"[WARN] Output file is locked: {path}")
        print(f"[SAVE] {fallback_path}")
        return fallback_path


# ---------------------------------------------------------------------------
# 4. 03 후보 API 재검토
# ---------------------------------------------------------------------------

def get_candidate_api_labels(candidates: pd.DataFrame) -> list[str]:
    validate_columns(candidates, REQUIRED_CANDIDATE_COLUMNS, "candidate data")
    return sorted(candidates["api_label"].dropna().unique().tolist())


def first_load_over_threshold(sub: pd.DataFrame) -> int | None:
    caution_rows = sub[
        (sub["avg_response_time_ms"] >= PASS_AVG_MS)
        | (sub["p95_response_time_ms"] >= P95_CAUTION_MS)
        | (sub["max_response_time_ms"] >= MAX_CAUTION_MS)
        | (sub["error_rate"] >= ERROR_CAUTION_RATE)
    ]
    if caution_rows.empty:
        return None
    return int(caution_rows.sort_values("load_level").iloc[0]["load_level"])


def classify_threshold_row(row: pd.Series) -> str:
    if (
        row["avg_response_time_ms"] >= PASS_AVG_MS
        or row["max_response_time_ms"] >= PASS_MAX_MS
        or row["error_rate"] >= PASS_ERROR_RATE
    ):
        return "위험"
    if (
        row["p95_response_time_ms"] >= P95_CAUTION_MS
        or row["max_response_time_ms"] >= MAX_CAUTION_MS
        or row["error_rate"] >= ERROR_CAUTION_RATE
    ):
        return "주의"
    return "안정"


def build_threshold_reason(row: pd.Series) -> str:
    reasons: list[str] = []
    if row["avg_response_time_ms"] >= PASS_AVG_MS:
        reasons.append(f"평균 응답시간 {row['avg_response_time_ms']:.1f}ms")
    if row["p95_response_time_ms"] >= P95_CAUTION_MS:
        reasons.append(f"p95 {row['p95_response_time_ms']:.1f}ms")
    if row["max_response_time_ms"] >= MAX_CAUTION_MS:
        reasons.append(f"max {row['max_response_time_ms']:.1f}ms")
    if row["error_rate"] >= ERROR_CAUTION_RATE:
        reasons.append(f"오류율 {row['error_rate']:.3%}")
    if not reasons:
        return "기준 내"
    return " / ".join(reasons)


def build_threshold_rows(metrics: pd.DataFrame, candidate_apis: list[str]) -> pd.DataFrame:
    threshold_df = metrics[metrics["api_label"].isin(candidate_apis)].copy()
    threshold_df["risk_level"] = threshold_df.apply(classify_threshold_row, axis=1)
    threshold_df["risk_reason"] = threshold_df.apply(build_threshold_reason, axis=1)

    output_columns = [
        "team",
        "load_level",
        "api_label",
        "sample_count",
        "avg_response_time_ms",
        "p90_response_time_ms",
        "p95_response_time_ms",
        "max_response_time_ms",
        "std_response_time_ms",
        "error_rate",
        "throughput_per_sec",
        "risk_level",
        "risk_reason",
    ]
    return threshold_df[output_columns].sort_values(
        ["api_label", "team", "load_level"],
        ignore_index=True,
    )


def analyze_candidate_trends(metrics: pd.DataFrame, candidate_apis: list[str]) -> pd.DataFrame:
    rows = []
    target_metrics = metrics[metrics["api_label"].isin(candidate_apis)].copy()

    for (team, api), sub in target_metrics.groupby(["team", "api_label"], dropna=False):
        sub = sub.sort_values("load_level").reset_index(drop=True)
        if sub.empty:
            continue

        first = sub.iloc[0]
        last = sub.iloc[-1]
        avg_delta_pct = safe_delta_pct(
            last["avg_response_time_ms"], first["avg_response_time_ms"]
        )
        p95_delta_pct = safe_delta_pct(
            last["p95_response_time_ms"], first["p95_response_time_ms"]
        )
        tps_ratio = (
            last["throughput_per_sec"] / first["throughput_per_sec"]
            if first["throughput_per_sec"]
            else pd.NA
        )

        avg_values = sub["avg_response_time_ms"].tolist()
        p95_values = sub["p95_response_time_ms"].tolist()
        avg_monotone = all(avg_values[i] <= avg_values[i + 1] for i in range(len(avg_values) - 1))
        p95_monotone = all(p95_values[i] <= p95_values[i + 1] for i in range(len(p95_values) - 1))

        has_degradation = (
            avg_delta_pct >= AVG_DEGRADATION_PCT
            or p95_delta_pct >= P95_DEGRADATION_PCT
            or avg_monotone
            or p95_monotone
        )
        has_error_signal = bool((sub["error_rate"] >= ERROR_CAUTION_RATE).any())
        has_tps_stall = bool(pd.notna(tps_ratio) and tps_ratio < TPS_SCALE_MIN_RATIO)
        has_p95_signal = bool((sub["p95_response_time_ms"] >= P95_CAUTION_MS).any())
        has_max_signal = bool((sub["max_response_time_ms"] >= MAX_CAUTION_MS).any())

        if has_degradation and (has_error_signal or has_tps_stall or has_p95_signal):
            final_level = "병목 가능성 높음"
            reason = "부하 증가에 따른 응답시간 악화 신호"
        elif has_p95_signal or has_max_signal or has_error_signal:
            final_level = "관찰 대상"
            reason = "기본 응답시간 또는 순간 위험 신호는 있으나 부하 증가형 악화는 약함"
        else:
            final_level = "명확한 병목 아님"
            reason = "주요 위험 신호 없음"

        rows.append(
            {
                "team": team,
                "api_label": api,
                "avg_10_ms": round(first["avg_response_time_ms"], 3),
                "avg_100_ms": round(last["avg_response_time_ms"], 3),
                "avg_delta_pct": round(avg_delta_pct, 3),
                "p95_10_ms": round(first["p95_response_time_ms"], 3),
                "p95_100_ms": round(last["p95_response_time_ms"], 3),
                "p95_delta_pct": round(p95_delta_pct, 3),
                "max_response_time_ms": round(sub["max_response_time_ms"].max(), 3),
                "max_error_rate": round(sub["error_rate"].max(), 5),
                "tps_10": round(first["throughput_per_sec"], 3),
                "tps_100": round(last["throughput_per_sec"], 3),
                "tps_ratio_100_vs_10": round(tps_ratio, 3) if pd.notna(tps_ratio) else pd.NA,
                "avg_monotone_increase": avg_monotone,
                "p95_monotone_increase": p95_monotone,
                "threshold_load_level": first_load_over_threshold(sub),
                "final_bottleneck_level": final_level,
                "final_reason": reason,
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["final_bottleneck_level", "api_label", "team"],
        ignore_index=True,
    )


def safe_delta_pct(end_value: float, start_value: float) -> float:
    if pd.isna(start_value) or start_value == 0:
        return 0.0
    return (end_value - start_value) / start_value * 100


# ---------------------------------------------------------------------------
# 5. 활성 사용자 수 구간별 추가 검증
# ---------------------------------------------------------------------------

def build_active_thread_bucket_label(value: float | int | None) -> str | None:
    if pd.isna(value) or value <= 0:
        return None

    bucket_end = int(((int(value) - 1) // ACTIVE_BUCKET_SIZE + 1) * ACTIVE_BUCKET_SIZE)
    bucket_start = bucket_end - ACTIVE_BUCKET_SIZE + 1
    return f"{bucket_start}~{bucket_end}"


def build_active_thread_bucket_sort_key(label: str | None) -> int:
    if not label or "~" not in str(label):
        return 9999
    return int(str(label).split("~")[0])


def build_active_thread_bucket_metrics(
    requests: pd.DataFrame,
    candidate_apis: list[str],
) -> pd.DataFrame:
    """후보 API에 대해 active_threads_group 10명 단위 구간별 지표를 만든다."""

    target_requests = requests[requests["api_label"].isin(candidate_apis)].copy()
    target_requests = target_requests.dropna(
        subset=["team", "load_level", "api_label", "response_time_ms", "active_threads_group"]
    )
    target_requests["active_thread_bucket"] = target_requests["active_threads_group"].apply(
        build_active_thread_bucket_label
    )
    target_requests = target_requests.dropna(subset=["active_thread_bucket"])

    grouped = (
        target_requests.groupby(
            ["team", "load_level", "api_label", "active_thread_bucket"],
            dropna=False,
        )
        .agg(
            sample_count=("response_time_ms", "size"),
            avg_response_time_ms=("response_time_ms", "mean"),
            p90_response_time_ms=("response_time_ms", lambda x: x.quantile(0.90)),
            p95_response_time_ms=("response_time_ms", lambda x: x.quantile(0.95)),
            max_response_time_ms=("response_time_ms", "max"),
            error_count=("is_error", "sum"),
            duration_sec=("elapsed_from_start_sec", lambda x: max(x.max() - x.min(), 0)),
        )
        .reset_index()
    )

    grouped["error_rate"] = grouped["error_count"] / grouped["sample_count"]
    grouped["throughput_per_sec"] = grouped.apply(
        lambda row: row["sample_count"] / row["duration_sec"]
        if row["duration_sec"] > 0
        else pd.NA,
        axis=1,
    )
    grouped["sample_reliability"] = grouped["sample_count"].apply(
        lambda value: "신뢰 가능" if value >= MIN_RELIABLE_BUCKET_SAMPLES else "낮은 표본"
    )
    grouped["active_thread_bucket_start"] = grouped["active_thread_bucket"].apply(
        build_active_thread_bucket_sort_key
    )

    return grouped.sort_values(
        ["api_label", "team", "load_level", "active_thread_bucket_start"],
        ignore_index=True,
    )


def classify_active_bucket_row(row: pd.Series) -> str:
    if (
        row["max_response_time_ms"] >= PASS_MAX_MS
        or row["error_rate"] >= PASS_ERROR_RATE
    ):
        return "위험"
    if (
        row["p95_response_time_ms"] >= P95_CAUTION_MS
        or row["max_response_time_ms"] >= MAX_CAUTION_MS
        or row["error_rate"] >= ERROR_CAUTION_RATE
    ):
        return "주의"
    return "안정"


def analyze_active_thread_trends(active_bucket_df: pd.DataFrame) -> pd.DataFrame:
    """구간별 지표가 부하 증가에 따라 악화되는지 요약한다."""

    rows = []
    working = active_bucket_df.copy()
    working["bucket_risk_level"] = working.apply(classify_active_bucket_row, axis=1)

    for (team, load_level, api), sub in working.groupby(
        ["team", "load_level", "api_label"], dropna=False
    ):
        sub = sub.sort_values("active_thread_bucket_start").reset_index(drop=True)
        reliable = sub[sub["sample_reliability"] == "신뢰 가능"].copy()
        trend_source = reliable if not reliable.empty else sub

        first = trend_source.iloc[0]
        last = trend_source.iloc[-1]
        p95_delta_pct = safe_delta_ratio(
            last["p95_response_time_ms"], first["p95_response_time_ms"]
        )
        tps_delta_pct = safe_delta_ratio(
            last["throughput_per_sec"], first["throughput_per_sec"]
        )
        p95_values = trend_source["p95_response_time_ms"].tolist()
        p95_positive_steps = sum(
            p95_values[i] < p95_values[i + 1] for i in range(len(p95_values) - 1)
        )
        p95_positive_step_rate = (
            p95_positive_steps / (len(p95_values) - 1)
            if len(p95_values) > 1
            else 0
        )

        reliable_warning_count = int((reliable["bucket_risk_level"] == "주의").sum())
        reliable_risk_count = int((reliable["bucket_risk_level"] == "위험").sum())
        reliable_error_count = int((reliable["error_count"] > 0).sum())

        judgement, reason = classify_active_thread_trend(
            reliable_warning_count=reliable_warning_count,
            reliable_risk_count=reliable_risk_count,
            reliable_error_count=reliable_error_count,
            p95_delta_pct=p95_delta_pct,
            p95_positive_step_rate=p95_positive_step_rate,
            p95_max=trend_source["p95_response_time_ms"].max(),
            max_error_rate=trend_source["error_rate"].max(),
        )

        rows.append(
            {
                "team": team,
                "load_level": load_level,
                "api_label": api,
                "bucket_count": len(sub),
                "reliable_bucket_count": len(reliable),
                "total_sample_count": int(sub["sample_count"].sum()),
                "first_bucket": first["active_thread_bucket"],
                "last_bucket": last["active_thread_bucket"],
                "p95_start_ms": round(first["p95_response_time_ms"], 3),
                "p95_end_ms": round(last["p95_response_time_ms"], 3),
                "p95_delta_pct": round(p95_delta_pct, 5),
                "p95_positive_steps": p95_positive_steps,
                "p95_positive_step_rate": round(p95_positive_step_rate, 5),
                "p95_max_ms": round(trend_source["p95_response_time_ms"].max(), 3),
                "max_response_time_ms": round(trend_source["max_response_time_ms"].max(), 3),
                "tps_start": round(first["throughput_per_sec"], 5)
                if pd.notna(first["throughput_per_sec"])
                else pd.NA,
                "tps_end": round(last["throughput_per_sec"], 5)
                if pd.notna(last["throughput_per_sec"])
                else pd.NA,
                "tps_delta_pct": round(tps_delta_pct, 5),
                "total_error_count": int(sub["error_count"].sum()),
                "max_error_rate": round(trend_source["error_rate"].max(), 5),
                "reliable_warning_bucket_count": reliable_warning_count,
                "reliable_risk_bucket_count": reliable_risk_count,
                "reliable_error_bucket_count": reliable_error_count,
                "bottleneck_judgement": judgement,
                "reason": reason,
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["api_label", "bottleneck_judgement", "load_level", "team"],
        ignore_index=True,
    )


def safe_delta_ratio(end_value: float, start_value: float) -> float:
    if pd.isna(start_value) or start_value == 0 or pd.isna(end_value):
        return 0.0
    return (end_value - start_value) / start_value


def classify_active_thread_trend(
    reliable_warning_count: int,
    reliable_risk_count: int,
    reliable_error_count: int,
    p95_delta_pct: float,
    p95_positive_step_rate: float,
    p95_max: float,
    max_error_rate: float,
) -> tuple[str, str]:
    """활성 사용자 구간별 추세를 병목 판단 문구로 분류한다."""

    # 단일 구간의 순간 오류만으로 병목을 강하게 의심하면 과대 해석이 된다.
    # 위험/오류가 반복되고, 동시에 p95가 활성 사용자 증가에 따라 악화될 때만 강한 병목 신호로 본다.
    if (
        reliable_risk_count >= 2
        and reliable_error_count >= 2
        and p95_delta_pct >= ACTIVE_P95_INCREASE_RATE
        and p95_positive_step_rate >= 0.5
    ):
        return "병목 의심 강함", "위험/오류 구간이 반복되고 p95 증가 추세가 함께 확인됨"

    if reliable_warning_count >= 3 and p95_max >= P95_CAUTION_MS:
        return "기준 초과 반복", f"주의 이상 구간 {reliable_warning_count}개"

    if p95_delta_pct >= ACTIVE_P95_INCREASE_RATE and p95_positive_step_rate >= 0.5:
        if p95_max >= P95_CAUTION_MS or max_error_rate >= ERROR_CAUTION_RATE:
            return "부하 증가형 관찰 필요", "활성 사용자 증가에 따라 p95가 상승하고 기준 신호가 있음"
        return "기준 내 상대 증가", "p95는 증가하지만 절대 기준은 낮음"

    if reliable_warning_count > 0 or reliable_error_count > 0:
        return "단일 구간 관찰", "일부 구간에서만 주의 또는 오류가 확인됨"

    return "명확한 병목 신호 없음", "구간별 p95, 오류율 기준에서 주요 신호 없음"


def build_active_thread_focus(active_trend_df: pd.DataFrame) -> pd.DataFrame:
    focus_levels = {
        "병목 의심 강함",
        "기준 초과 반복",
        "부하 증가형 관찰 필요",
        "단일 구간 관찰",
        "기준 내 상대 증가",
    }
    return active_trend_df[
        active_trend_df["bottleneck_judgement"].isin(focus_levels)
    ].reset_index(drop=True)


# ---------------------------------------------------------------------------
# 6. 그래프 생성
# ---------------------------------------------------------------------------

def plot_candidate_trends(threshold_df: pd.DataFrame, candidate_apis: list[str]) -> None:
    setup_korean_font()

    for api in candidate_apis:
        api_df = threshold_df[threshold_df["api_label"] == api]
        if api_df.empty:
            continue

        fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

        for team in sorted(api_df["team"].unique()):
            team_df = api_df[api_df["team"] == team].sort_values("load_level")
            axes[0].plot(
                team_df["load_level"],
                team_df["avg_response_time_ms"],
                marker="o",
                label=f"{team} avg",
            )
            axes[0].plot(
                team_df["load_level"],
                team_df["p95_response_time_ms"],
                marker="s",
                linestyle="--",
                label=f"{team} p95",
            )
            axes[1].plot(
                team_df["load_level"],
                team_df["error_rate"] * 100,
                marker="o",
                label=f"{team} error %",
            )

        axes[0].axhline(P95_CAUTION_MS, color="orange", linestyle=":", label="p95 caution")
        axes[0].axhline(PASS_AVG_MS, color="red", linestyle=":", label="avg pass limit")
        axes[0].set_title(f"{api} 응답시간 추세")
        axes[0].set_ylabel("ms")
        axes[0].legend(loc="best")
        axes[0].grid(True, alpha=0.3)

        axes[1].axhline(PASS_ERROR_RATE * 100, color="red", linestyle=":", label="error pass limit")
        axes[1].set_title(f"{api} 오류율 추세")
        axes[1].set_xlabel("load level")
        axes[1].set_ylabel("error rate (%)")
        axes[1].legend(loc="best")
        axes[1].grid(True, alpha=0.3)

        for axis in axes:
            axis.set_xticks(LOAD_LEVELS)

        fig.tight_layout()
        safe_api_name = str(api).replace("/", "_").replace(" ", "_")
        save_png(fig, REPORT_DIR / f"06_{safe_api_name}_threshold_trend.png")
        plt.close(fig)


# ---------------------------------------------------------------------------
# 7. 저장 및 출력
# ---------------------------------------------------------------------------

def save_outputs(
    threshold_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    active_bucket_df: pd.DataFrame,
    active_trend_df: pd.DataFrame,
    active_focus_df: pd.DataFrame,
) -> None:
    save_csv(threshold_df, THRESHOLD_OUTPUT_PATH)
    save_csv(summary_df, SUMMARY_OUTPUT_PATH)
    save_csv(active_bucket_df, ACTIVE_BUCKET_OUTPUT_PATH)
    save_csv(active_trend_df, ACTIVE_TREND_OUTPUT_PATH)
    save_csv(active_focus_df, ACTIVE_FOCUS_OUTPUT_PATH)


def print_summary(
    summary_df: pd.DataFrame,
    threshold_df: pd.DataFrame,
    active_focus_df: pd.DataFrame,
) -> None:
    print()
    print("[06 병목/임계점 요약]")
    print(summary_df.to_string(index=False))
    print()
    print("[위험 구간 개수]")
    print(threshold_df["risk_level"].value_counts().to_string())
    print()
    print("[활성 사용자 구간 추가 검토]")
    if active_focus_df.empty:
        print("추가 관찰 대상 없음")
    else:
        print(active_focus_df["bottleneck_judgement"].value_counts().to_string())


# ---------------------------------------------------------------------------
# 8. main
# ---------------------------------------------------------------------------

def main() -> None:
    metrics_df = normalize_metric_columns(read_csv(METRICS_PATH))
    validate_columns(metrics_df, REQUIRED_METRIC_COLUMNS, "metrics data")

    requests_df = normalize_request_columns(read_csv(REQUESTS_PATH))
    validate_columns(requests_df, REQUIRED_REQUEST_COLUMNS, "requests data")

    candidates_df = read_csv(CANDIDATE_PATH)
    candidate_apis = get_candidate_api_labels(candidates_df)
    if not candidate_apis:
        raise ValueError("No candidate APIs found from 03 output.")

    reset_output_dirs()

    threshold_df = build_threshold_rows(metrics_df, candidate_apis)
    summary_df = analyze_candidate_trends(metrics_df, candidate_apis)
    active_bucket_df = build_active_thread_bucket_metrics(requests_df, candidate_apis)
    active_trend_df = analyze_active_thread_trends(active_bucket_df)
    active_focus_df = build_active_thread_focus(active_trend_df)

    save_outputs(
        threshold_df=threshold_df,
        summary_df=summary_df,
        active_bucket_df=active_bucket_df,
        active_trend_df=active_trend_df,
        active_focus_df=active_focus_df,
    )
    plot_candidate_trends(threshold_df, candidate_apis)
    print_summary(summary_df, threshold_df, active_focus_df)


if __name__ == "__main__":
    main()
