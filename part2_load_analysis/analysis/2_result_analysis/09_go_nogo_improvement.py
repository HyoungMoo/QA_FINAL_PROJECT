"""Go / No-Go 기준 및 개선안.

03 후보 선정 결과와 06 병목/임계점 도출 결과를 종합해 최종 진행 판단을 만든다.
09는 지표를 새로 계산하는 단계가 아니라, 앞 단계 산출물을 보고서용 결론으로
정리하는 단계다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# 1. 경로 및 판단 기준 설정
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

RESULT_DATA_DIR = BASE_DIR / "data" / "1_analysis_result_data"
REPORT_DIR = BASE_DIR / "reports" / "2_result_analysis"

CANDIDATE_PATH = (
    RESULT_DATA_DIR
    / "03_bottleneck_candidates"
    / "03_bottleneck_candidates_focus.csv"
)
THRESHOLD_PATH = (
    RESULT_DATA_DIR
    / "06_bottleneck_threshold"
    / "06_bottleneck_threshold.csv"
)
API_SUMMARY_PATH = (
    RESULT_DATA_DIR
    / "06_bottleneck_threshold"
    / "06_bottleneck_api_summary.csv"
)
ACTIVE_THREAD_FOCUS_PATH = (
    RESULT_DATA_DIR
    / "06_bottleneck_threshold"
    / "06_active_thread_trend_check_focus.csv"
)

OUTPUT_DATA_DIR = RESULT_DATA_DIR / "09_go_nogo_improvement"
OUTPUT_REPORT_DIR = REPORT_DIR / "09_go_nogo_improvement"

DECISION_OUTPUT_PATH = OUTPUT_DATA_DIR / "09_go_nogo_decision.csv"
ACTION_OUTPUT_PATH = OUTPUT_DATA_DIR / "09_go_nogo_api_actions.csv"
EVIDENCE_OUTPUT_PATH = OUTPUT_DATA_DIR / "09_go_nogo_evidence.csv"
REPORT_OUTPUT_PATH = OUTPUT_REPORT_DIR / "09_go_nogo_improvement.md"

NO_GO_ERROR_RATE = 0.01
NO_GO_MAX_RESPONSE_MS = 5000
NO_GO_AVG_RESPONSE_MS = 1000

CAUTION_ERROR_RATE = 0.001
CAUTION_P95_RESPONSE_MS = 500
CAUTION_MAX_RESPONSE_MS = 800


@dataclass
class DecisionContext:
    """최종 판단에 필요한 사유를 모아두는 컨테이너."""

    no_go_reasons: list[str]
    caution_reasons: list[str]
    improvement_items: list[str]


# ---------------------------------------------------------------------------
# 2. 공통 유틸리티
# ---------------------------------------------------------------------------

def reset_output_dirs() -> None:
    """09 산출물 폴더 안의 기존 파일만 정리한다."""

    for directory in [OUTPUT_DATA_DIR, OUTPUT_REPORT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        for path in directory.iterdir():
            if path.is_file():
                try:
                    path.unlink()
                except PermissionError:
                    print(f"[WARN] Output file is locked, skip delete: {path}")


def read_csv(path: Path, required: bool = True) -> pd.DataFrame:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Input file not found: {path}")
        print(f"[WARN] Optional input file not found: {path}")
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


def percent(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.3f}%"


def ms(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.1f}ms"


def unique_join(values: pd.Series) -> str:
    cleaned = [str(value) for value in values.dropna().unique() if str(value).strip()]
    return ", ".join(cleaned)


def save_csv(df: pd.DataFrame, path: Path) -> Path:
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


# ---------------------------------------------------------------------------
# 3. 최종 판단 근거 수집
# ---------------------------------------------------------------------------

def collect_decision_context(
    threshold_df: pd.DataFrame,
    api_summary_df: pd.DataFrame,
    active_thread_focus_df: pd.DataFrame,
) -> DecisionContext:
    """06 결과에서 No-Go 사유와 Caution 사유를 수집한다."""

    no_go_reasons: list[str] = []
    caution_reasons: list[str] = []
    improvement_items: list[str] = []

    if not threshold_df.empty:
        risk_rows = threshold_df[threshold_df["risk_level"].astype(str) == "위험"]
        if not risk_rows.empty:
            no_go_reasons.append(f"06 위험 구간 {len(risk_rows)}건 존재")

        high_error_rows = threshold_df[threshold_df["error_rate"] >= NO_GO_ERROR_RATE]
        if not high_error_rows.empty:
            no_go_reasons.append(f"오류율 {NO_GO_ERROR_RATE:.1%} 이상 구간 {len(high_error_rows)}건 존재")

        high_max_rows = threshold_df[
            threshold_df["max_response_time_ms"] >= NO_GO_MAX_RESPONSE_MS
        ]
        if not high_max_rows.empty:
            no_go_reasons.append(
                f"최대 응답시간 {NO_GO_MAX_RESPONSE_MS:,}ms 이상 구간 {len(high_max_rows)}건 존재"
            )

        high_avg_rows = threshold_df[
            threshold_df["avg_response_time_ms"] >= NO_GO_AVG_RESPONSE_MS
        ]
        if not high_avg_rows.empty:
            no_go_reasons.append(
                f"평균 응답시간 {NO_GO_AVG_RESPONSE_MS:,}ms 이상 구간 {len(high_avg_rows)}건 존재"
            )

        caution_rows = threshold_df[threshold_df["risk_level"].astype(str) == "주의"]
        if not caution_rows.empty:
            caution_reasons.append(f"06 주의 구간 {len(caution_rows)}건 존재")

        p95_caution_rows = threshold_df[
            threshold_df["p95_response_time_ms"] >= CAUTION_P95_RESPONSE_MS
        ]
        if not p95_caution_rows.empty:
            caution_reasons.append(
                f"p95 {CAUTION_P95_RESPONSE_MS}ms 이상 구간 {len(p95_caution_rows)}건 존재"
            )

        error_caution_rows = threshold_df[
            threshold_df["error_rate"] >= CAUTION_ERROR_RATE
        ]
        if not error_caution_rows.empty:
            caution_reasons.append(
                f"오류율 {CAUTION_ERROR_RATE:.1%} 이상 구간 {len(error_caution_rows)}건 존재"
            )

    if not api_summary_df.empty:
        confirmed_rows = api_summary_df[
            api_summary_df["final_bottleneck_level"].astype(str).str.contains(
                "확정|위험|높음", na=False
            )
        ]
        if not confirmed_rows.empty:
            no_go_reasons.append(f"06 API 요약에서 병목 가능성 높은 API {len(confirmed_rows)}건 존재")

        observation_rows = api_summary_df[
            api_summary_df["final_bottleneck_level"].astype(str).str.contains(
                "관찰|주의", na=False
            )
        ]
        if not observation_rows.empty:
            caution_reasons.append(
                "관찰 대상 API: "
                + unique_join(observation_rows["api_label"])
            )

    if not active_thread_focus_df.empty:
        strong_rows = active_thread_focus_df[
            active_thread_focus_df["bottleneck_judgement"].astype(str).str.contains(
                "병목 의심 강함", na=False
            )
        ]
        if not strong_rows.empty:
            no_go_reasons.append(f"활성 사용자 구간 분석에서 병목 의심 강함 {len(strong_rows)}건 존재")

        repeated_rows = active_thread_focus_df[
            active_thread_focus_df["bottleneck_judgement"].astype(str).str.contains(
                "기준 초과 반복", na=False
            )
        ]
        if not repeated_rows.empty:
            caution_reasons.append(
                "활성 사용자 구간 기준 초과 반복: "
                + unique_join(repeated_rows["api_label"])
            )

    improvement_items = build_improvement_items(api_summary_df, active_thread_focus_df)
    if not improvement_items and caution_reasons:
        improvement_items.append("주의 구간 API의 p95, max, 오류율을 추가 모니터링")

    return DecisionContext(
        no_go_reasons=sorted(set(no_go_reasons)),
        caution_reasons=sorted(set(caution_reasons)),
        improvement_items=sorted(set(improvement_items)),
    )


def build_improvement_items(
    api_summary_df: pd.DataFrame,
    active_thread_focus_df: pd.DataFrame,
) -> list[str]:
    items: list[str] = []

    observed_apis: set[str] = set()
    if not api_summary_df.empty:
        observed_apis.update(
            api_summary_df[
                api_summary_df["final_bottleneck_level"].astype(str).str.contains(
                    "관찰|주의|높음", na=False
                )
            ]["api_label"].dropna().astype(str).tolist()
        )

    if not active_thread_focus_df.empty:
        observed_apis.update(active_thread_focus_df["api_label"].dropna().astype(str).tolist())

    for api_label in sorted(observed_apis):
        if api_label == "로그인":
            items.append("로그인 API: 인증 처리 시간, 토큰 검증, DB 조회 구간 모니터링")
        elif api_label == "시험 시작":
            items.append("시험 시작 API: Team2 100명 구간 오류 원인 확인")
        else:
            items.append(f"{api_label} API: p95, max, 오류율 추세 추가 확인")

    return items


def decide_go_nogo(context: DecisionContext) -> str:
    if context.no_go_reasons:
        return "No-Go"
    if context.caution_reasons:
        return "Conditional Go"
    return "Go"


# ---------------------------------------------------------------------------
# 4. 산출물 생성
# ---------------------------------------------------------------------------

def build_decision_output(context: DecisionContext, final_decision: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "final_decision": final_decision,
                "decision_summary": build_decision_summary(final_decision),
                "no_go_reason_count": len(context.no_go_reasons),
                "caution_reason_count": len(context.caution_reasons),
                "no_go_reasons": " / ".join(context.no_go_reasons) or "없음",
                "caution_reasons": " / ".join(context.caution_reasons) or "없음",
                "improvement_items": " / ".join(context.improvement_items) or "없음",
            }
        ]
    )


def build_decision_summary(final_decision: str) -> str:
    if final_decision == "No-Go":
        return "현재 기준으로는 추가 부하 테스트 또는 운영 반영 전 원인 분석이 필요하다."
    if final_decision == "Conditional Go":
        return "명확한 병목은 없지만 관찰 대상 API가 있어 모니터링 조건부 진행이 적절하다."
    return "현재 분석 기준에서는 주요 위험 신호가 없어 진행 가능하다."


def build_api_action_output(
    threshold_df: pd.DataFrame,
    api_summary_df: pd.DataFrame,
    active_thread_focus_df: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    if api_summary_df.empty:
        return pd.DataFrame()

    for _, api_row in api_summary_df.iterrows():
        team = api_row.get("team")
        api_label = api_row.get("api_label")

        related_threshold = threshold_df[
            (threshold_df["team"] == team)
            & (threshold_df["api_label"] == api_label)
        ] if not threshold_df.empty else pd.DataFrame()

        related_active = active_thread_focus_df[
            (active_thread_focus_df["team"] == team)
            & (active_thread_focus_df["api_label"] == api_label)
        ] if not active_thread_focus_df.empty else pd.DataFrame()

        max_p95 = related_threshold["p95_response_time_ms"].max() if not related_threshold.empty else None
        max_error_rate = related_threshold["error_rate"].max() if not related_threshold.empty else None
        max_response = api_row.get("max_response_time_ms")
        level = str(api_row.get("final_bottleneck_level", ""))

        action_level, action = classify_action(
            api_label=str(api_label),
            final_level=level,
            max_p95=max_p95,
            max_error_rate=max_error_rate,
            max_response=max_response,
            active_focus_count=len(related_active),
        )

        rows.append(
            {
                "team": team,
                "api_label": api_label,
                "final_bottleneck_level": level,
                "max_p95_response_time_ms": round(float(max_p95), 3) if pd.notna(max_p95) else None,
                "max_response_time_ms": round(float(max_response), 3) if pd.notna(max_response) else None,
                "max_error_rate": round(float(max_error_rate), 5) if pd.notna(max_error_rate) else None,
                "active_thread_focus_count": len(related_active),
                "action_level": action_level,
                "recommended_action": action,
            }
        )

    action_df = pd.DataFrame(rows)
    action_priority = {
        "No-Go": 0,
        "Caution": 1,
        "Go": 2,
    }
    action_df["action_priority"] = action_df["action_level"].map(action_priority).fillna(9)
    return (
        action_df.sort_values(["action_priority", "api_label", "team"])
        .drop(columns=["action_priority"])
        .reset_index(drop=True)
    )


def classify_action(
    api_label: str,
    final_level: str,
    max_p95: float | None,
    max_error_rate: float | None,
    max_response: float | None,
    active_focus_count: int,
) -> tuple[str, str]:
    has_no_go_signal = (
        "확정" in final_level
        or "위험" in final_level
        or "높음" in final_level
        or (pd.notna(max_response) and float(max_response) >= NO_GO_MAX_RESPONSE_MS)
        or (pd.notna(max_error_rate) and float(max_error_rate) >= NO_GO_ERROR_RATE)
    )
    if has_no_go_signal:
        return "No-Go", "원인 분석 후 재측정이 필요하다."

    has_caution_signal = (
        "관찰" in final_level
        or "주의" in final_level
        or active_focus_count > 0
        or (pd.notna(max_p95) and float(max_p95) >= CAUTION_P95_RESPONSE_MS)
        or (pd.notna(max_response) and float(max_response) >= CAUTION_MAX_RESPONSE_MS)
        or (pd.notna(max_error_rate) and float(max_error_rate) >= CAUTION_ERROR_RATE)
    )
    if has_caution_signal:
        if api_label == "로그인":
            return "Caution", "응답시간이 반복적으로 높아 인증/토큰/DB 조회 구간을 모니터링한다."
        if api_label == "시험 시작":
            return "Caution", "Team2 100명 구간 오류 발생 원인을 확인하고 재측정한다."
        return "Caution", "p95, max, 오류율 추세를 추가 모니터링한다."

    return "Go", "현재 기준에서는 별도 조치 없이 관찰한다."


def build_evidence_output(
    threshold_df: pd.DataFrame,
    active_thread_focus_df: pd.DataFrame,
) -> pd.DataFrame:
    evidence_frames: list[pd.DataFrame] = []

    if not threshold_df.empty:
        threshold_evidence = threshold_df[
            threshold_df["risk_level"].astype(str).isin(["주의", "위험"])
        ].copy()
        threshold_evidence["source"] = "06_bottleneck_threshold"
        threshold_evidence["evidence_type"] = threshold_evidence["risk_level"]
        evidence_frames.append(
            threshold_evidence[
                [
                    "source",
                    "evidence_type",
                    "team",
                    "load_level",
                    "api_label",
                    "avg_response_time_ms",
                    "p95_response_time_ms",
                    "max_response_time_ms",
                    "error_rate",
                    "risk_reason",
                ]
            ].rename(columns={"risk_reason": "reason"})
        )

    if not active_thread_focus_df.empty:
        active_evidence = active_thread_focus_df.copy()
        active_evidence["source"] = "06_active_thread_analysis"
        active_evidence["evidence_type"] = active_evidence["bottleneck_judgement"]
        evidence_frames.append(
            active_evidence[
                [
                    "source",
                    "evidence_type",
                    "team",
                    "load_level",
                    "api_label",
                    "p95_start_ms",
                    "p95_end_ms",
                    "p95_max_ms",
                    "max_response_time_ms",
                    "max_error_rate",
                    "reason",
                ]
            ].rename(
                columns={
                    "p95_start_ms": "avg_response_time_ms",
                    "p95_end_ms": "p95_response_time_ms",
                    "max_error_rate": "error_rate",
                }
            )
        )

    if not evidence_frames:
        return pd.DataFrame()

    return pd.concat(evidence_frames, ignore_index=True)


def write_markdown_report(
    final_decision: str,
    context: DecisionContext,
    decision_df: pd.DataFrame,
    action_df: pd.DataFrame,
    evidence_df: pd.DataFrame,
) -> None:
    lines: list[str] = [
        "# Go / No-Go 기준 및 개선안",
        "",
        "## 1. 최종 판단",
        "",
        f"- 최종 판단: **{final_decision}**",
        f"- 판단 요약: {decision_df.loc[0, 'decision_summary']}",
        "",
        "## 2. 판단 근거",
        "",
        "### No-Go 사유",
    ]

    lines.extend(format_bullets(context.no_go_reasons))
    lines.append("")
    lines.append("### Caution 사유")
    lines.extend(format_bullets(context.caution_reasons))

    lines.extend(
        [
            "",
            "## 3. API별 조치 방향",
            "",
            "| Team | API | 판단 | max p95 | max 응답시간 | max 오류율 | 조치 |",
            "|---|---|---|---:|---:|---:|---|",
        ]
    )

    if action_df.empty:
        lines.append("| - | - | - | - | - | - | 조치 대상 없음 |")
    else:
        for _, row in action_df.iterrows():
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(row.get("team", "-")),
                        str(row.get("api_label", "-")),
                        str(row.get("action_level", "-")),
                        ms(row.get("max_p95_response_time_ms")),
                        ms(row.get("max_response_time_ms")),
                        percent(row.get("max_error_rate")),
                        str(row.get("recommended_action", "-")),
                    ]
                )
                + " |"
            )

    lines.append("")
    lines.append("## 4. 개선안")
    lines.extend(format_bullets(context.improvement_items))

    lines.extend(
        [
            "",
            "## 5. 산출 파일",
            "",
            f"- 판단 요약 CSV: `{DECISION_OUTPUT_PATH}`",
            f"- API별 조치 CSV: `{ACTION_OUTPUT_PATH}`",
            f"- 판단 근거 CSV: `{EVIDENCE_OUTPUT_PATH}`",
            "",
            "## 6. 참고",
            "",
            "- 09 단계는 03 후보 선정 결과와 06 병목/임계점 분석 결과를 종합한다.",
            "- 평균 1,000ms 이상, max 5,000ms 이상, 오류율 1% 이상은 No-Go 신호로 본다.",
            "- p95 500ms 이상, max 800ms 이상, 오류율 0.1% 이상은 Caution 신호로 본다.",
        ]
    )

    REPORT_OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def format_bullets(items: list[str]) -> list[str]:
    if not items:
        return ["- 없음"]
    return [f"- {item}" for item in items]


# ---------------------------------------------------------------------------
# 5. main
# ---------------------------------------------------------------------------

def main() -> None:
    reset_output_dirs()

    candidates_df = read_csv(CANDIDATE_PATH)
    threshold_df = read_csv(THRESHOLD_PATH)
    api_summary_df = read_csv(API_SUMMARY_PATH)
    active_thread_focus_df = read_csv(ACTIVE_THREAD_FOCUS_PATH, required=False)

    context = collect_decision_context(
        threshold_df=threshold_df,
        api_summary_df=api_summary_df,
        active_thread_focus_df=active_thread_focus_df,
    )
    final_decision = decide_go_nogo(context)

    decision_df = build_decision_output(context, final_decision)
    action_df = build_api_action_output(
        threshold_df=threshold_df,
        api_summary_df=api_summary_df,
        active_thread_focus_df=active_thread_focus_df,
    )
    evidence_df = build_evidence_output(
        threshold_df=threshold_df,
        active_thread_focus_df=active_thread_focus_df,
    )

    print(f"[INPUT] candidates focus rows: {len(candidates_df)}")
    print(f"[INPUT] threshold rows: {len(threshold_df)}")
    print(f"[INPUT] api summary rows: {len(api_summary_df)}")
    print(f"[INPUT] active thread focus rows from 06: {len(active_thread_focus_df)}")

    save_csv(decision_df, DECISION_OUTPUT_PATH)
    save_csv(action_df, ACTION_OUTPUT_PATH)
    save_csv(evidence_df, EVIDENCE_OUTPUT_PATH)
    write_markdown_report(
        final_decision=final_decision,
        context=context,
        decision_df=decision_df,
        action_df=action_df,
        evidence_df=evidence_df,
    )
    print(f"[SAVE] {REPORT_OUTPUT_PATH}")

    print("\n[FINAL DECISION]")
    print(f"- {final_decision}: {decision_df.loc[0, 'decision_summary']}")
    print(f"- No-Go reasons: {len(context.no_go_reasons)}")
    print(f"- Caution reasons: {len(context.caution_reasons)}")
    print("[DONE] Go / No-Go 기준 및 개선안 생성 완료")


if __name__ == "__main__":
    main()
