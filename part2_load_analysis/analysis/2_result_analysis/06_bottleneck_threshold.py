"""병목 API 및 임계점 도출."""

from __future__ import annotations

import os
from pathlib import Path
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd


# ---------------------------------------------------------------------------
# 1. 경로 설정
# ---------------------------------------------------------------------------

# 이 파일은 analysis/2_result_analysis/ 아래에 있으므로 parents[2]가
# part2_load_analysis 폴더를 가리킨다.
BASE_DIR = Path(__file__).resolve().parents[2]

ANALYSIS_READY_DATA_DIR = BASE_DIR / "data" / "0_preparation_data" / "03_analysis_ready_data"
RESULT_DATA_DIR = BASE_DIR / "data" / "1_analysis_result_data"
REPORT_DIR = BASE_DIR / "reports" / "2_result_analysis" / "06_bottleneck_threshold"

METRICS_PATH = ANALYSIS_READY_DATA_DIR / "loadtest_analysis_ready_metrics_by_api.csv"
CANDIDATE_PATH = (
    RESULT_DATA_DIR
    / "03_bottleneck_candidates"
    / "03_bottleneck_candidates_focus.csv"
)

OUTPUT_DIR = RESULT_DATA_DIR / "06_bottleneck_threshold"
THRESHOLD_OUTPUT_PATH = OUTPUT_DIR / "06_bottleneck_threshold.csv"
SUMMARY_OUTPUT_PATH = OUTPUT_DIR / "06_bottleneck_api_summary.csv"


# ---------------------------------------------------------------------------
# 2. 판단 기준
# ---------------------------------------------------------------------------

# 프로젝트 pass 기준. 이 값을 넘으면 명확한 위험으로 본다.
PASS_AVG_MS = 1000
PASS_MAX_MS = 5000
PASS_ERROR_RATE = 0.01

# 03 후보 선정에서 사용한 관찰 기준. 06에서도 "주의 신호"로 재사용한다.
P95_CAUTION_MS = 500
MAX_CAUTION_MS = 800
ERROR_CAUTION_RATE = 0.001

# 부하 증가에 따라 평균/p95가 이 정도 이상 상승하면 악화 추세로 본다.
AVG_DEGRADATION_PCT = 20
P95_DEGRADATION_PCT = 20

# 100명 처리량이 10명 대비 5배 미만이면 선형 확장 관점에서 정체 가능성으로 본다.
# 10명 -> 100명은 부하가 10배이므로, 절반 미만 성장부터 보수적으로 관찰한다.
TPS_SCALE_MIN_RATIO = 5


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

REQUIRED_CANDIDATE_COLUMNS = {
    "team",
    "load_level",
    "api_label",
    "candidate_level",
    "bottleneck_score",
}


# ---------------------------------------------------------------------------
# 3. 공통 유틸
# ---------------------------------------------------------------------------

def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_csv(path, encoding="utf-8-sig")


def validate_columns(df: pd.DataFrame, required_columns: set[str], source_name: str) -> None:
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise ValueError(f"{source_name} missing columns: {missing_columns}")


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


def reset_output_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    # 이 환경에서는 새 파일 생성과 덮어쓰기는 가능하지만 삭제 권한이 막히는 경우가 있다.
    # 06 산출물은 고정 파일명을 사용하므로 실행할 때마다 같은 파일을 덮어써 오래된 값이 남지 않게 한다.


def setup_korean_font() -> None:
    # Windows 환경에서는 Malgun Gothic을 우선 사용한다.
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False


def write_text_safely(path: Path, text: str) -> None:
    # 일부 Windows ACL 환경에서는 기존 파일을 w 모드로 다시 여는 것은 막히지만,
    # r+ 모드로 내용을 교체하는 것은 가능하다. 반복 실행을 위해 두 경우를 나눈다.
    if path.exists():
        with path.open("r+", encoding="utf-8-sig", newline="") as file:
            file.seek(0)
            file.write(text)
            file.truncate()
    else:
        path.write_text(text, encoding="utf-8-sig")


def write_bytes_safely(path: Path, content: bytes) -> None:
    if path.exists():
        with path.open("r+b") as file:
            file.seek(0)
            file.write(content)
            file.truncate()
    else:
        path.write_bytes(content)


# ---------------------------------------------------------------------------
# 4. 후보 API 추세 분석
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


def classify_row(row: pd.Series) -> str:
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


def build_row_reason(row: pd.Series) -> str:
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


def analyze_candidate_trends(metrics: pd.DataFrame, candidate_apis: list[str]) -> pd.DataFrame:
    rows = []
    target_metrics = metrics[metrics["api_label"].isin(candidate_apis)].copy()

    for (team, api), sub in target_metrics.groupby(["team", "api_label"], dropna=False):
        sub = sub.sort_values("load_level").reset_index(drop=True)
        if sub.empty:
            continue

        first = sub.iloc[0]
        last = sub.iloc[-1]
        avg_delta_pct = (
            (last["avg_response_time_ms"] - first["avg_response_time_ms"])
            / first["avg_response_time_ms"]
            * 100
            if first["avg_response_time_ms"]
            else 0
        )
        p95_delta_pct = (
            (last["p95_response_time_ms"] - first["p95_response_time_ms"])
            / first["p95_response_time_ms"]
            * 100
            if first["p95_response_time_ms"]
            else 0
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
        elif has_p95_signal or has_max_signal or has_error_signal:
            final_level = "관찰 대상"
        else:
            final_level = "명확한 병목 아님"

        if has_degradation:
            reason = "부하 증가에 따른 응답시간 악화 신호"
        elif has_p95_signal or has_max_signal or has_error_signal:
            reason = "기본 응답시간 또는 순간 위험 신호는 있으나 부하 증가형 악화는 약함"
        else:
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


def build_threshold_rows(metrics: pd.DataFrame, candidate_apis: list[str]) -> pd.DataFrame:
    threshold_df = metrics[metrics["api_label"].isin(candidate_apis)].copy()
    threshold_df["risk_level"] = threshold_df.apply(classify_row, axis=1)
    threshold_df["risk_reason"] = threshold_df.apply(build_row_reason, axis=1)

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


# ---------------------------------------------------------------------------
# 5. 그래프 생성
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
            axis.set_xticks([10, 30, 50, 70, 100])

        fig.tight_layout()
        safe_api_name = str(api).replace("/", "_").replace(" ", "_")
        output_path = REPORT_DIR / f"06_{safe_api_name}_threshold_trend.png"
        image_buffer = BytesIO()
        fig.savefig(image_buffer, format="png", dpi=150)
        write_bytes_safely(output_path, image_buffer.getvalue())
        plt.close(fig)


# ---------------------------------------------------------------------------
# 6. 저장 및 출력
# ---------------------------------------------------------------------------

def save_outputs(threshold_df: pd.DataFrame, summary_df: pd.DataFrame) -> None:
    write_text_safely(THRESHOLD_OUTPUT_PATH, threshold_df.to_csv(index=False))
    write_text_safely(SUMMARY_OUTPUT_PATH, summary_df.to_csv(index=False))


def print_summary(summary_df: pd.DataFrame, threshold_df: pd.DataFrame) -> None:
    print(f"[SAVE] {THRESHOLD_OUTPUT_PATH}")
    print(f"[SAVE] {SUMMARY_OUTPUT_PATH}")
    print(f"[SAVE] {REPORT_DIR}")
    print()
    print("[06 병목/임계점 요약]")
    print(summary_df.to_string(index=False))
    print()
    print("[위험 구간 개수]")
    print(threshold_df["risk_level"].value_counts().to_string())


# ---------------------------------------------------------------------------
# 7. main
# ---------------------------------------------------------------------------

def main() -> None:
    # my_code 내부에서 상대 경로로 실행할 때 Windows 권한 오류가 나는 경우가 있어,
    # Codex 작업 루트로 cwd를 맞춘 뒤 절대 경로 기반으로 처리한다.
    os.chdir(BASE_DIR.parents[2])

    metrics_df = normalize_metric_columns(read_csv(METRICS_PATH))
    validate_columns(metrics_df, REQUIRED_METRIC_COLUMNS, "metrics data")

    candidates_df = read_csv(CANDIDATE_PATH)
    candidate_apis = get_candidate_api_labels(candidates_df)
    if not candidate_apis:
        raise ValueError("No candidate APIs found from 03 output.")

    reset_output_dirs()

    threshold_df = build_threshold_rows(metrics_df, candidate_apis)
    summary_df = analyze_candidate_trends(metrics_df, candidate_apis)

    save_outputs(threshold_df, summary_df)
    plot_candidate_trends(threshold_df, candidate_apis)
    print_summary(summary_df, threshold_df)


if __name__ == "__main__":
    main()
