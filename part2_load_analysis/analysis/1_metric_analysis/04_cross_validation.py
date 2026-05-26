# Team2/ Team3 교차 검증
# 목적:
# - 서로 다른 테스트 결과가 같은 경향을 보이는지 확인한다.
# - 비교 가능한 구간과 비교에 주의해야 하는 구간을 구분한다.
# - 두 팀 데이터를 교차 검증해 병목 API와 임계점을 예측한다.

from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
PREPARATION_DATA_DIR = DATA_DIR / "0_preparation_data"
ANALYSIS_READY_DIR = PREPARATION_DATA_DIR / "03_analysis_ready_data"

METRICS_PATH = ANALYSIS_READY_DIR / "loadtest_analysis_ready_metrics_by_api.csv"

APIS = ["로그인", "과목 정보 조회", "시험 입장", "시험 시작", "시험 제출", "재응시"]
LOAD_LEVELS = [10, 30, 50, 70, 100]

# Pass Criteria (프로젝트 기준)
PASS_AVG_MS = 1000
PASS_MAX_MS = 5000
PASS_ERROR_RATE = 0.01


# ---------------------------------------------------------------------------
# Team2 vs Team3 응답시간 교차 검증
# ---------------------------------------------------------------------------

def crosscheck_teams(metrics: pd.DataFrame) -> pd.DataFrame:
    t2 = metrics[metrics["team"] == "Team2"].set_index(["load_level", "api_label"])
    t3 = metrics[metrics["team"] == "Team3"].set_index(["load_level", "api_label"])
    common_idx = t2.index.intersection(t3.index)

    rows = []
    for load, api in common_idx:
        r2, r3 = t2.loc[(load, api)], t3.loc[(load, api)]
        avg2, avg3 = r2["avg_response_time_ms"], r3["avg_response_time_ms"]
        diff_pct = (avg2 - avg3) / avg3 * 100 if avg3 else None
        rows.append({
            "load_level": load,
            "api_label": api,
            "team2_avg_ms": round(avg2, 1),
            "team3_avg_ms": round(avg3, 1),
            "avg_diff_%": round(diff_pct, 1) if diff_pct is not None else None,
            "team2_p90_ms": round(r2["p90_response_time_ms"], 1),
            "team3_p90_ms": round(r3["p90_response_time_ms"], 1),
            "team2_error_rate": r2["error_rate"],
            "team3_error_rate": r3["error_rate"],
            "team2_throughput": round(r2["throughput_per_sec"], 3),
            "team3_throughput": round(r3["throughput_per_sec"], 3),
        })
    return pd.DataFrame(rows).sort_values(["load_level", "api_label"], ignore_index=True)


# ---------------------------------------------------------------------------
# 부하 증가에 따른 응답시간 트렌드 검증
# ---------------------------------------------------------------------------

def check_load_trend(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for team in ("Team2", "Team3"):
        for api in APIS:
            sub = metrics[(metrics["team"] == team) & (metrics["api_label"] == api)]
            sub = sub.sort_values("load_level")
            if len(sub) < 2:
                continue
            avgs = sub["avg_response_time_ms"].tolist()
            loads = sub["load_level"].tolist()
            is_monotone = all(avgs[i] <= avgs[i + 1] for i in range(len(avgs) - 1))
            rows.append({
                "team": team,
                "api_label": api,
                "load_avg_ms": {l: round(a, 1) for l, a in zip(loads, avgs)},
                "monotone_increase": is_monotone,
                "note": "" if is_monotone else "부하 증가에도 응답시간 감소 구간 있음",
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 병목 API 식별: 두 팀 모두에서 avg 응답시간이 높은 API
# ---------------------------------------------------------------------------

def identify_bottleneck_apis(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for api in APIS:
        for load in LOAD_LEVELS:
            sub = metrics[(metrics["api_label"] == api) & (metrics["load_level"] == load)]
            if sub.empty:
                continue
            avg_both = sub["avg_response_time_ms"].mean()
            p90_both = sub["p90_response_time_ms"].mean()
            std_both = sub["std_response_time_ms"].mean()
            err_both = sub["error_rate"].mean()
            rows.append({
                "api_label": api,
                "load_level": load,
                "avg_ms (양팀 평균)": round(avg_both, 1),
                "p90_ms (양팀 평균)": round(p90_both, 1),
                "std_ms (양팀 평균)": round(std_both, 1),
                "error_rate (양팀 평균)": round(err_both, 4),
            })

    df = pd.DataFrame(rows).sort_values(
        ["avg_ms (양팀 평균)"], ascending=False, ignore_index=True
    )
    return df


# ---------------------------------------------------------------------------
# 임계점 예측: TPS 선형 확장 이탈 구간 도출
# ---------------------------------------------------------------------------

def predict_threshold(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for team in ("Team2", "Team3"):
        for api in APIS:
            sub = (
                metrics[(metrics["team"] == team) & (metrics["api_label"] == api)]
                .sort_values("load_level")
                .reset_index(drop=True)
            )
            if len(sub) < 3:
                continue

            # 10VU 기준 TPS 대비 각 구간의 실제 TPS 비율 계산
            base_tps = sub.iloc[0]["throughput_per_sec"]
            base_load = sub.iloc[0]["load_level"]
            breakpoint_load = None

            for _, r in sub.iloc[1:].iterrows():
                expected_ratio = r["load_level"] / base_load
                actual_ratio = r["throughput_per_sec"] / base_tps if base_tps else 1
                # 실제 TPS 증가가 부하 증가의 50% 미만이면 선형 확장 이탈로 판단
                if actual_ratio < expected_ratio * 0.5:
                    breakpoint_load = int(r["load_level"])
                    break

            rows.append({
                "team": team,
                "api_label": api,
                "base_tps (10VU)": round(base_tps, 3),
                "max_tps (100VU)": round(sub.iloc[-1]["throughput_per_sec"], 3),
                "tps_breakpoint_VU": breakpoint_load if breakpoint_load else "선형 확장 유지",
                "max_avg_ms": round(sub["avg_response_time_ms"].max(), 1),
                "pass_criteria_ok": "OK" if sub["avg_response_time_ms"].max() <= PASS_AVG_MS else "NG",
            })
    return pd.DataFrame(rows).sort_values(["team", "api_label"], ignore_index=True)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    metrics = pd.read_csv(METRICS_PATH, encoding="utf-8-sig")
    pd.set_option("display.max_rows", 100)
    pd.set_option("display.width", 160)

    print("=" * 70)
    print("[ Day 8-A ] Team2 vs Team3 교차 검증 (부하 단계별 응답시간·에러율·처리량)")
    print("=" * 70)
    cross_df = crosscheck_teams(metrics)
    print(cross_df.to_string(index=False))

    print("\n" + "=" * 70)
    print("[ Day 8-B ] 부하 증가에 따른 응답시간 단조 증가 여부")
    print("=" * 70)
    trend_df = check_load_trend(metrics)
    for _, row in trend_df.iterrows():
        status = "OK" if row["monotone_increase"] else "!!"
        print(f"  [{status}] {row['team']} | {row['api_label']}: {row['load_avg_ms']}  {row['note']}")

    print("\n" + "=" * 70)
    print("[ Day 8-C ] 병목 API 식별 (양팀 평균 응답시간 기준)")
    print("=" * 70)
    bottleneck_df = identify_bottleneck_apis(metrics)
    print(bottleneck_df.to_string(index=False))

    print("\n" + "=" * 70)
    print("[ Day 8-D ] TPS 선형 확장 이탈 구간 (임계점 예측)")
    print(f"  기준: 실제 TPS 증가율이 부하 증가율의 50% 미만이면 이탈 판정")
    print(f"  Pass Criteria: avg <= {PASS_AVG_MS}ms, max <= {PASS_MAX_MS}ms, err < {PASS_ERROR_RATE*100}%")
    print("=" * 70)
    threshold_df = predict_threshold(metrics)
    print(threshold_df.to_string(index=False))


if __name__ == "__main__":
    main()
