"""Chạy bộ prompt trong config.py bằng scripts/run.py của tác giả.

    python run_experiments.py --repo ./scene-language --dry-run
    python run_experiments.py --repo ./scene-language
"""
import argparse
import csv
import subprocess
import sys
import time
from pathlib import Path

import config

MARK = "  # set by run_experiments.py"


def set_model(repo: Path, model: str) -> None:
    """Ghi đè CLAUDE_MODEL_NAME trong claude_client.py của tác giả.

    File gốc có ba dòng gán liên tiếp, dòng cuối thắng. Dòng do script này
    thêm được đánh dấu để lần sau gỡ ra trước khi chèn lại.
    """
    f = repo / "engine/utils/claude_client.py"
    lines = [l for l in f.read_text(encoding="utf8").splitlines() if MARK not in l]
    i = max(i for i, l in enumerate(lines) if l.startswith("CLAUDE_MODEL_NAME"))
    lines.insert(i + 1, f"CLAUDE_MODEL_NAME = {model!r}{MARK}")
    f.write_text("\n".join(lines) + "\n", encoding="utf8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, help="thư mục clone scene-language")
    p.add_argument("--model", default=config.MODEL)
    p.add_argument("--dry-run", action="store_true", help="chỉ in lệnh, không gọi API")
    a = p.parse_args()

    repo = Path(a.repo).resolve()
    if not (repo / "scripts/run.py").is_file():
        sys.exit(f"Không thấy scripts/run.py trong {repo}")
    if not a.dry_run and not (repo / "engine/key.py").is_file():
        sys.exit(f"Thiếu {repo}/engine/key.py chứa ANTHROPIC_API_KEY")
    if not a.dry_run:
        set_model(repo, a.model)
    print(f"model = {a.model}\n")

    log = Path("results/run_log.csv")
    log.parent.mkdir(exist_ok=True)
    new = not log.exists()
    with log.open("a", newline="", encoding="utf8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["model", "scene", "seconds", "exit_code", "prompt"])
        for item in config.PROMPTS:
            cmd = [sys.executable, "scripts/run.py", "--tasks", item["text"],
                   "--num-completions", str(config.NUM_COMPLETIONS),
                   "--temperature", str(config.TEMPERATURE)]
            print(subprocess.list2cmdline(cmd))
            if a.dry_run:
                continue
            t0 = time.time()
            rc = subprocess.run(cmd, cwd=repo).returncode
            dt = round(time.time() - t0, 1)
            print(f"  -> {dt}s, exit code {rc}\n")
            w.writerow([a.model, item["key"], dt, rc, item["text"]])
            fh.flush()

    if not a.dry_run:
        print(f"Nhật ký: {log}\nBước tiếp: python analyze.py --repo {a.repo}")


if __name__ == "__main__":
    main()
