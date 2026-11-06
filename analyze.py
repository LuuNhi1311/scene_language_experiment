"""Quét đầu ra của scripts/run.py, lập bảng và đẩy lên Weights and Biases.

    python analyze.py --repo ./scene-language
    python analyze.py --repo ./scene-language --wandb

Số lượng đối tượng không chấm tự động được: trong 24 mẫu, con số nằm ở bốn
dạng khác nhau (hằng trong loop(), biến truyền vào loop(), danh sách Python,
hai range() lồng nhau). Vì vậy script chỉ trích các con số bắt được vào cột
numbers_seen làm bằng chứng, còn đúng/sai lấy từ results/manual_grading.csv do
người đọc chương trình ghi.

Cấu trúc đầu ra của tác giả:
    <repo>/scripts/outputs/run_*/<scene>_*/<i>/{program.py, error.txt, renderings/}
"""
import argparse
import csv
import re
from pathlib import Path

import config

NUMBER = re.compile(r"\bloop\s*\(\s*(\d+)"
                    r"|\brange\s*\(\s*(\d+)\s*\)"
                    r"|\bnum_\w+\s*(?::\s*int)?\s*=\s*(\d+)")


def read_grading(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open(encoding="utf8") as f:
        return {(r["scene"], int(r["sample"])): r for r in csv.DictReader(f)}


def scan(sample: Path) -> dict:
    prog = sample / "program.py"
    text = prog.read_text(encoding="utf8", errors="replace") if prog.is_file() else ""
    numbers = [next(g for g in m if g) for m in NUMBER.findall(text)]
    rend = sample / "renderings"
    return {
        "program_generated": int(prog.is_file()),
        "has_error": int((sample / "error.txt").is_file()),
        "num_renders": len(list(rend.glob("*"))) if rend.is_dir() else 0,
        "program_lines": len(text.splitlines()),
        "numbers_seen": ";".join(numbers),
    }


def collect(repo: Path, grading: dict) -> list:
    rows = []
    for run_dir in sorted((repo / "scripts/outputs").glob("run_*")):
        for scene in sorted(p for p in run_dir.iterdir() if p.is_dir()):
            item = next((i for i in config.PROMPTS if i["key"].lower() in scene.name.lower()), None)
            if item is None:
                continue
            for s in sorted((p for p in scene.iterdir() if p.name.isdigit()), key=lambda p: int(p.name)):
                g = grading.get((item["key"], int(s.name)), {})
                rows.append({
                    "scene": item["key"], "sample": int(s.name), "expected_count": item["expect"],
                    **scan(s),
                    "count_correct": g.get("correct", ""),
                    "count_expression": g.get("count_expression", ""),
                    "sample_path": s.relative_to(repo).as_posix(),
                })
    return rows


def print_table(rows: list, graded: bool) -> None:
    print(f"\n{'scene':<12}{'expected':>9}{'generated':>11}{'correct':>9}")
    print("-" * 41)
    for item in config.PROMPTS:
        g = [r for r in rows if r["scene"] == item["key"]]
        if not g:
            continue
        gen = f"{sum(r['program_generated'] for r in g)}/{len(g)}"
        ok = f"{sum(int(r['count_correct'] or 0) for r in g)}/{len(g)}" if graded else "-"
        print(f"{item['key']:<12}{item['expect']:>9}{gen:>11}{ok:>9}")
    print("-" * 41)
    n = len(rows)
    print(f"Program generated: {sum(r['program_generated'] for r in rows)}/{n}")
    if graded:
        ok = sum(int(r["count_correct"] or 0) for r in rows)
        print(f"Count correct (manual): {ok}/{n} = {ok / n:.3f}   (paper: 1.000)")
    else:
        print("Chưa chấm. Tạo results/manual_grading.csv rồi chạy lại.")


def push_wandb(rows: list) -> None:
    import wandb
    for r in rows:
        run = wandb.init(project=config.WANDB_PROJECT, reinit=True,
                         name=f"{r['scene']}-{r['sample']}", group=r["scene"],
                         tags=[r["scene"], "manual" if r["count_correct"] != "" else "ungraded"],
                         config={**r, "model": config.MODEL, "temperature": config.TEMPERATURE})
        log = {k: r[k] for k in ("program_generated", "has_error", "num_renders", "program_lines")}
        if r["count_correct"] != "":
            log["count_correct"] = int(r["count_correct"])
        wandb.log(log)
        for gif in sorted((Path(r["sample_path"]) / "renderings").glob("*.gif"))[:2]:
            wandb.log({"render": wandb.Video(str(gif), format="gif")})
        run.finish()
    print(f"Đã đẩy {len(rows)} run lên project '{config.WANDB_PROJECT}'.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--grading", default="results/manual_grading.csv")
    p.add_argument("--csv", default="results/results.csv")
    p.add_argument("--wandb", action="store_true")
    a = p.parse_args()

    grading = read_grading(Path(a.grading))
    rows = collect(Path(a.repo).resolve(), grading)
    if not rows:
        raise SystemExit("Không thấy mẫu nào. Chạy run_experiments.py trước.")

    out = Path(a.csv)
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print_table(rows, graded=bool(grading))
    print(f"Đã ghi {out}")
    if a.wandb:
        push_wandb(rows)


if __name__ == "__main__":
    main()
