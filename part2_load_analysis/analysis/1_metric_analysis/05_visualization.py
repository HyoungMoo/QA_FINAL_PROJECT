# 시각화
# 목적:
# - 성능 지표 변화를 그래프로 표현한다.
# - 병목 후보와 성능 저하 구간을 눈으로 확인할 수 있게 만든다.

from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd


# ---------------------------------------------------------------------------
# 1. 경로 설정
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

METRICS_PATH = (
    BASE_DIR
    / "data"
    / "0_preparation_data"
    / "03_analysis_ready_data"
    / "loadtest_analysis_ready_metrics_by_api.csv"
)

CHART_DIR = (
    BASE_DIR
    / "data"
    / "1_analysis_result_data"
    / "02_visualization"
)

CHART_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 2. 한글 폰트 설정
# ---------------------------------------------------------------------------

def set_korean_font() -> None:
    """matplotlib 그래프에서 한글이 깨지지 않도록 폰트를 설정한다."""
    font_candidates = ["Malgun Gothic", "맑은 고딕", "AppleGothic", "NanumGothic"]
    installed_fonts = {font.name for font in fm.fontManager.ttflist}

    for font_name in font_candidates:
        if font_name in installed_fonts:
            plt.rcParams["font.family"] = font_name
            break

    plt.rcParams["axes.unicode_minus"] = False


# ---------------------------------------------------------------------------
# 3. 공통 저장 함수
# ---------------------------------------------------------------------------

def save_chart(file_name: str) -> None:
    """현재 그래프를 PNG 파일로 저장한다."""
    output_path = CHART_DIR / file_name

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")

    print(f"[SAVE] {output_path}")


# ---------------------------------------------------------------------------
# 4. 로그인 API p95 응답시간 비교
# ---------------------------------------------------------------------------

def plot_login_p95(df: pd.DataFrame) -> None:
    login_df = df[df["api_label"] == "로그인"].sort_values(["team", "load_level"])

    plt.figure(figsize=(8, 5))

    for team in sorted(login_df["team"].unique()):
        team_df = login_df[login_df["team"] == team]

        plt.plot(
            team_df["load_level"],
            team_df["p95_response_time_ms"],
            marker="o",
            label=team,
        )

    plt.title("로그인 API P95 응답시간")
    plt.xlabel("부하 단계")
    plt.ylabel("P95 응답시간(ms)")
    plt.xticks([10, 30, 50, 70, 100])
    plt.legend()
    plt.grid(True)

    save_chart("01_login_api_p95_response_time.png")
    plt.show()
    plt.close()

# ---------------------------------------------------------------------------
# 5. API별 평균 응답시간 비교
# ---------------------------------------------------------------------------

def plot_avg_response_by_api(df: pd.DataFrame) -> None:
    avg_df = (
        df.groupby(["api_label", "team"], as_index=False)["avg_response_time_ms"]
        .mean()
    )

    pivot_df = avg_df.pivot(
        index="api_label",
        columns="team",
        values="avg_response_time_ms",
    )

    pivot_df = pivot_df.sort_values(by="Team3", ascending=False)

    plt.figure(figsize=(12, 6))

    x = range(len(pivot_df.index))
    width = 0.35

    plt.bar(
        [i - width / 2 for i in x],
        pivot_df["Team2"],
        width=width,
        label="Team2",
    )

    plt.bar(
        [i + width / 2 for i in x],
        pivot_df["Team3"],
        width=width,
        label="Team3",
    )

    plt.title("API별 평균 응답시간 비교")
    plt.xlabel("API")
    plt.ylabel("평균 응답시간(ms)")
    plt.xticks(
        ticks=x,
        labels=pivot_df.index,
        rotation=0,
    )
    plt.legend()
    plt.grid(axis="y")

    save_chart("02_avg_response_time_by_api_comparison.png")
    plt.show()
    plt.close()

# ---------------------------------------------------------------------------
# 6. API별 p95 응답시간 비교
# ---------------------------------------------------------------------------

def plot_p95_by_api(df: pd.DataFrame) -> None:
    p95_df = (
        df.groupby(["api_label", "team"], as_index=False)["p95_response_time_ms"]
        .mean()
    )

    pivot_df = p95_df.pivot(
        index="api_label",
        columns="team",
        values="p95_response_time_ms",
    )

    pivot_df = pivot_df.sort_values(by="Team3", ascending=False)

    plt.figure(figsize=(12, 6))

    x = range(len(pivot_df.index))
    width = 0.35

    plt.bar(
        [i - width / 2 for i in x],
        pivot_df["Team2"],
        width=width,
        label="Team2",
    )

    plt.bar(
        [i + width / 2 for i in x],
        pivot_df["Team3"],
        width=width,
        label="Team3",
    )

    plt.title("API별 P95 응답시간 비교")
    plt.xlabel("API")
    plt.ylabel("P95 응답시간(ms)")
    plt.xticks(
        ticks=x,
        labels=pivot_df.index,
        rotation=0,
    )
    plt.legend()
    plt.grid(axis="y")

    save_chart("03_p95_response_time_by_api_comparison.png")
    plt.show()
    plt.close()


# ---------------------------------------------------------------------------
# 7. 오류율 비교
# ---------------------------------------------------------------------------

def plot_error_rate(df: pd.DataFrame) -> None:
    error_df = (
        df.groupby(["api_label", "team"], as_index=False)
        .agg(error_rate=("error_rate", "max"))
    )

    pivot_df = error_df.pivot(
        index="api_label",
        columns="team",
        values="error_rate",
    ).fillna(0)

    pivot_df = pivot_df.sort_values(
        by="Team2",
        ascending=False,
    )

    plt.figure(figsize=(12, 5))

    x = range(len(pivot_df.index))
    width = 0.35

    plt.bar(
        [i - width / 2 for i in x],
        pivot_df["Team2"],
        width=width,
        label="Team2",
    )

    plt.bar(
        [i + width / 2 for i in x],
        pivot_df["Team3"],
        width=width,
        label="Team3",
    )

    plt.title("API별 오류율 비교")
    plt.xlabel("API")
    plt.ylabel("Error Rate")
    plt.xticks(
        ticks=x,
        labels=pivot_df.index,
        rotation=0,
    )
    plt.legend()
    plt.grid(axis="y")

    save_chart("04_error_rate_by_api.png")
    plt.show()
    plt.close()

# ---------------------------------------------------------------------------
# 8. 부하 단계별 처리량 비교
# ---------------------------------------------------------------------------

def plot_throughput_by_load(df: pd.DataFrame) -> None:
    throughput_df = (
        df.groupby(["team", "load_level"], as_index=False)["throughput_per_sec"]
        .sum()
        .sort_values(["team", "load_level"])
    )

    plt.figure(figsize=(8, 5))

    for team in sorted(throughput_df["team"].unique()):
        team_df = throughput_df[throughput_df["team"] == team]

        plt.plot(
            team_df["load_level"],
            team_df["throughput_per_sec"],
            marker="o",
            label=team,
        )

    plt.title("부하 단계별 처리량 비교")
    plt.xlabel("부하 단계")
    plt.ylabel("초당 처리량")
    plt.xticks([10, 30, 50, 70, 100])
    plt.legend()
    plt.grid(True)

    save_chart("05_throughput_by_load_level.png")
    plt.show()
    plt.close()

# ---------------------------------------------------------------------------
# 9. 부하 단계별 평균 응답시간 비교
# ---------------------------------------------------------------------------

def plot_avg_response_by_load(df: pd.DataFrame) -> None:
    load_df = (
        df.groupby(["team", "load_level"], as_index=False)["avg_response_time_ms"]
        .mean()
        .sort_values(["team", "load_level"])
    )

    plt.figure(figsize=(8, 5))

    for team in sorted(load_df["team"].unique()):
        team_df = load_df[load_df["team"] == team]

        plt.plot(
            team_df["load_level"],
            team_df["avg_response_time_ms"],
            marker="o",
            label=team,
        )

    plt.title("부하 단계별 평균 응답시간 비교")
    plt.xlabel("부하 단계")
    plt.ylabel("평균 응답시간(ms)")
    plt.xticks([10, 30, 50, 70, 100])
    plt.legend()
    plt.grid(True)

    save_chart("06_avg_response_time_by_load_level.png")
    plt.show()
    plt.close()

# ---------------------------------------------------------------------------
# 10. 메인 실행
# ---------------------------------------------------------------------------

def main() -> None:
    set_korean_font()

    df = pd.read_csv(METRICS_PATH, encoding="utf-8-sig")

    plot_login_p95(df)
    plot_avg_response_by_api(df)
    plot_p95_by_api(df)
    plot_error_rate(df)
    plot_throughput_by_load(df)
    plot_avg_response_by_load(df)

    print("[DONE] 시각화 그래프 생성 완료")


if __name__ == "__main__":
    main()