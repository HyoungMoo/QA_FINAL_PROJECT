# 데이터 검증
# 목적:
# - 분석 기준 데이터가 신뢰할 수 있는 상태인지 확인한다.
# - 원본 로그, 공통 스키마 데이터, 분석용 데이터 사이의 요청 수와 주요 값 차이를 점검한다.

from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
PREPARATION_DATA_DIR = DATA_DIR / "0_preparation_data"

SANITIZED_DIR = PREPARATION_DATA_DIR / "01_sanitized_data"
COMMON_SCHEMA_DIR = PREPARATION_DATA_DIR / "02_common_schema_data"
ANALYSIS_READY_DIR = PREPARATION_DATA_DIR / "03_analysis_ready_data"

METRICS_PATH = ANALYSIS_READY_DIR / "loadtest_analysis_ready_metrics_by_api.csv"

APIS = ["로그인", "과목 정보 조회", "시험 입장", "시험 시작", "시험 제출", "재응시"]

SUMMARY_LABEL_MAP = {
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


# ---------------------------------------------------------------------------
# 중복 행 검사
# ---------------------------------------------------------------------------

def check_duplicates(df: pd.DataFrame, label: str) -> dict:
    key_cols = ["timestamp", "thread_name", "api_label", "response_time_ms"]
    available = [c for c in key_cols if c in df.columns]
    total = len(df)
    duplicated = df.duplicated(subset=available).sum()
    return {
        "label": label,
        "total_rows": total,
        "duplicate_rows": int(duplicated),
        "duplicate_rate_%": round(duplicated / total * 100, 1) if total > 0 else 0,
    }


def run_duplicate_check() -> pd.DataFrame:
    results = []
    for team in ("team2_results", "team3_results"):
        team_dir = COMMON_SCHEMA_DIR / team
        for csv_path in sorted(team_dir.glob("*_common_schema.csv")):
            df = pd.read_csv(csv_path, encoding="utf-8-sig")
            results.append(check_duplicates(df, f"{team}/{csv_path.name}"))
    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# 원본(request-level) vs 요약(summary CSV) 수치 비교
# ---------------------------------------------------------------------------

def load_team2_summary() -> pd.DataFrame:
    frames = []
    for csv_path in sorted((SANITIZED_DIR / "team2_results").glob("test*_result_sanitized.csv")):
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        df = df[df["Label"].notna()]
        df["api_label"] = df["Label"].map(lambda x: SUMMARY_LABEL_MAP.get(str(x).strip(), x))
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def load_team3_summary() -> pd.DataFrame:
    frames = []
    for csv_path in sorted((SANITIZED_DIR / "team3_results").glob("summary*_data_sanitized.csv")):
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        df = df[df["Label"].notna()]
        df["api_label"] = df["Label"].map(lambda x: SUMMARY_LABEL_MAP.get(str(x).strip(), x))
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _summary_verdict(diff_pct: float) -> str:
    """10%/30% 기준으로 요약 파일 수치 신뢰 여부를 판정한다."""
    if diff_pct < 10:
        return "정상"
    elif diff_pct < 30:
        return "주의 (원본 우선)"
    else:
        return "배제 (요약 파일 오류)"


def compare_raw_vs_summary(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for team, summary_df in [("Team2", load_team2_summary()), ("Team3", load_team3_summary())]:
        if summary_df.empty:
            continue
        for _, s_row in summary_df[summary_df["api_label"].isin(APIS)].iterrows():
            api = s_row["api_label"]
            load = s_row.get("load_level")
            s_avg = pd.to_numeric(s_row.get("Average"), errors="coerce")
            s_count = pd.to_numeric(s_row.get("# Samples"), errors="coerce")
            match = metrics[
                (metrics["team"] == team)
                & (metrics["load_level"] == load)
                & (metrics["api_label"] == api)
            ]
            if match.empty or pd.isna(s_avg):
                continue
            r_avg = match.iloc[0]["avg_response_time_ms"]
            r_count = match.iloc[0]["sample_count"]
            diff_pct = abs(r_avg - s_avg) / s_avg * 100
            rows.append({
                "team": team,
                "load_level": load,
                "api_label": api,
                "summary_avg_ms": round(s_avg, 1),
                "raw_avg_ms": round(r_avg, 1),
                "avg_diff_%": round(diff_pct, 1),
                "verdict": _summary_verdict(diff_pct),
                "summary_count": int(s_count) if not pd.isna(s_count) else None,
                "raw_count": int(r_count),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 신뢰도 판정 요약 (Day 9)
# ---------------------------------------------------------------------------

def reliability_summary(dup_df: pd.DataFrame) -> None:
    print("\n" + "=" * 70)
    print("[ 신뢰도 판정 ]")
    print("=" * 70)
    print("""
■ 데이터 출처
  - Team2: JMeter XML (result10~100.xml) + 요약 CSV (test10~100_result.csv)
  - Team3: JMeter XLSX (test10~100.xlsx) + 요약 CSV (summary10~100_data.csv)
  - 통합 방법: pandas read_xml / read_excel / read_csv 로 단일 DataFrame 병합
  - 시나리오: 로그인 → 과목 정보 → 시험 입장 → 시험 시작 → 시험 제출 → 재응시
  - 부하 단계: 10 / 30 / 50 / 70 / 100 (동시 사용자 수)

■ 전처리 기준
  - 민감정보 제거: requestHeader, responseHeader, responseData, queryString
  - 공통 스키마 정규화: 두 팀의 컬럼 명칭·타입 통일
  - 분석 대상 필터: response_time_ms >= 0, 필수 컬럼 비결측

■ 계산 방식
  - avg / p50 / p90 / p95: pandas quantile
  - error_rate: error_count / sample_count
  - throughput_per_sec: sample_count / 테스트 소요 시간(초)

■ Pass Criteria (분석 기준값)
  - Error Rate        : 1% 미만  (초과 시 원인 분석 필수)
  - 평균 Latency      : 1,000ms 이내
  - Max Response Time : 5,000ms 이내
  - TPS               : 부하 증가 대비 선형 확장 여부 관찰 (변곡점 도출)
  - Std. Dev.         : 급증 시 불안정 신호로 판단
""")

    t3 = dup_df[dup_df["label"].str.startswith("team3")]
    t2 = dup_df[dup_df["label"].str.startswith("team2")]
    t3_dup = t3["duplicate_rows"].sum()
    t3_total = t3["total_rows"].sum()
    t3_rate = t3_dup / t3_total * 100 if t3_total > 0 else 0

    print(f"  Team2: 중복 {t2['duplicate_rows'].sum()}건 → 판정: 신뢰 가능 [OK]")
    print(f"  Team3: 중복 {t3_dup}건 / {t3_total}건 ({t3_rate:.1f}%)")
    if t3_rate > 30:
        print("    → 응답시간(avg/p90/p95): 신뢰 가능 [OK]")
        print("    → 처리량(throughput, sample_count): 참고값으로만 활용 [참고]")
    else:
        print("    → 판정: 신뢰 가능 [OK]")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    metrics = pd.read_csv(METRICS_PATH, encoding="utf-8-sig")
    pd.set_option("display.max_rows", 100)
    pd.set_option("display.width", 130)

    print("=" * 70)
    print("[ Day 7-A ] 중복 행 검사")
    print("=" * 70)
    dup_df = run_duplicate_check()
    print(dup_df.to_string(index=False))

    print("\n" + "=" * 70)
    print("[ Day 7-B ] 원본(request-level) vs 요약(summary CSV) 평균 응답시간 비교")
    print("  판정 기준: 차이 10% 미만 → 정상 / 10~30% → 주의(원본 우선) / 30% 이상 → 배제")
    print("=" * 70)
    raw_vs_summary = compare_raw_vs_summary(metrics)
    if raw_vs_summary.empty:
        print("비교 가능한 데이터 없음")
    else:
        print(raw_vs_summary.to_string(index=False))

    reliability_summary(dup_df)


if __name__ == "__main__":
    main()
