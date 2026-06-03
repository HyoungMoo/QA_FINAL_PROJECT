"""
Part 2 load test analysis runner.

This script removes previously generated analysis outputs and then runs the
full Part 2 pipeline in order. Raw JMeter source files are not deleted.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent

GENERATED_DIRS = [
    BASE_DIR / "data" / "0_preparation_data" / "01_sanitized_data",
    BASE_DIR / "data" / "0_preparation_data" / "02_common_schema_data",
    BASE_DIR / "data" / "0_preparation_data" / "03_analysis_ready_data",
    BASE_DIR / "data" / "1_analysis_result_data" / "01_metric_summary",
    BASE_DIR / "data" / "1_analysis_result_data" / "02_visualization",
    BASE_DIR / "data" / "1_analysis_result_data" / "03_bottleneck_candidates",
    BASE_DIR / "data" / "1_analysis_result_data" / "06_bottleneck_threshold",
    BASE_DIR / "data" / "1_analysis_result_data" / "09_go_nogo_improvement",
    BASE_DIR / "reports" / "1_metric_analysis",
    BASE_DIR / "reports" / "2_result_analysis",
]

PIPELINE_SCRIPTS = [
    BASE_DIR / "analysis" / "0_preparation" / "00_preprocess_load_test_data.py",
    BASE_DIR / "analysis" / "1_metric_analysis" / "01_data_validation.py",
    BASE_DIR / "analysis" / "1_metric_analysis" / "02_metric_summary.py",
    BASE_DIR / "analysis" / "1_metric_analysis" / "04_cross_validation.py",
    BASE_DIR / "analysis" / "1_metric_analysis" / "05_visualization.py",
    BASE_DIR / "analysis" / "2_result_analysis" / "03_bottleneck_candidates.py",
    BASE_DIR / "analysis" / "2_result_analysis" / "06_bottleneck_threshold.py",
    BASE_DIR / "analysis" / "2_result_analysis" / "09_go_nogo_improvement.py",
]


def reset_generated_dirs() -> None:
    """Delete and recreate generated output directories."""
    print("[reset] Remove previous generated outputs")

    for directory in GENERATED_DIRS:
        if directory.exists():
            print(f"  - remove: {directory.relative_to(PROJECT_ROOT)}")
            shutil.rmtree(directory)

        directory.mkdir(parents=True, exist_ok=True)
        (directory / ".gitkeep").touch()


def run_pipeline() -> None:
    """Run every Part 2 analysis script in the required order."""
    total = len(PIPELINE_SCRIPTS)
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"

    for index, script_path in enumerate(PIPELINE_SCRIPTS, start=1):
        relative_script = script_path.relative_to(PROJECT_ROOT)
        print(f"[{index}/{total}] python {relative_script}")

        subprocess.run(
            [sys.executable, str(script_path)],
            cwd=PROJECT_ROOT,
            check=True,
            env=env,
        )


def main() -> None:
    reset_generated_dirs()
    run_pipeline()
    print("[done] Part 2 load analysis pipeline completed")


if __name__ == "__main__":
    main()
