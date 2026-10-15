"""Stage 15: reproducible load tests; run make, then this script --valgrind.

Full defaults: 1000 seeds at n=100 and 500 at n=500 for each strategy.
Reports include worst seeds; --replay REPORT rechecks them after any change.
"""

import argparse
from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
STRATEGIES = ("simple", "medium", "complex", "adaptive")
OPS = ("sa", "sb", "ss", "pa", "pb", "ra", "rb", "rr", "rra", "rrb", "rrr")
SPLIT = {"ss": ("sa", "sb"), "rr": ("ra", "rb"), "rrr": ("rra", "rrb")}


def generated(size, seed):
    # A fresh generator for every case makes each saved seed self-contained.
    return random.Random(seed).sample(range(-1000000000, 1000000000), size)


def checked(values, operations):
    """Independent deque checker; reject invalid commands and require A sorted/B empty."""
    a, b = deque(values), deque()
    for op in operations:
        assert op in OPS, f"invalid command: {op!r}"
        if op in ("sa", "ss") and len(a) > 1:
            first, second = a.popleft(), a.popleft()
            a.appendleft(first)
            a.appendleft(second)
        if op in ("sb", "ss") and len(b) > 1:
            first, second = b.popleft(), b.popleft()
            b.appendleft(first)
            b.appendleft(second)
        if op == "pa" and b:
            a.appendleft(b.popleft())
        if op == "pb" and a:
            b.appendleft(a.popleft())
        if op in ("ra", "rr"):
            a.rotate(-1)
        if op in ("rb", "rr"):
            b.rotate(-1)
        if op in ("rra", "rrr"):
            a.rotate(1)
        if op in ("rrb", "rrr"):
            b.rotate(1)
    assert list(a) == sorted(values) and not b, "checker: unsorted A or nonempty B"


def execute(values, strategy, memory=False):
    args = [str(ROOT / "push_swap"), "--bench"]
    if strategy != "default":
        args.append("--" + strategy)
    args += list(map(str, values))
    if memory:
        args = ["valgrind", "--quiet", "--leak-check=full", "--show-leak-kinds=all",
                "--errors-for-leak-kinds=all", "--error-exitcode=99", *args]
    result = subprocess.run(args, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result
    assert not result.stdout or result.stdout.endswith("\n"), result
    operations = result.stdout.splitlines()
    # Correctness is checked before the command count is analyzed.
    checked(values, operations)
    fields = dict(row.split(": ", 1) for row in result.stderr.splitlines())
    assert len(fields) == 16, fields  # Also rejects Valgrind diagnostics.
    counts = Counter(operations)
    assert all(int(fields[op]) == counts[op] for op in OPS), fields
    assert int(fields["Total operations"]) == len(operations)
    if values == sorted(values):
        assert not operations, "sorted input emitted commands"
    digest = hashlib.sha256(result.stdout.encode()).hexdigest()
    return operations, fields, digest


def random_series(size, trials, strategy):
    counts, worst = [], []
    effective = Counter()
    saved_rotations = 0
    for seed in range(trials):
        values = generated(size, seed)
        try:
            operations, fields, digest = execute(values, strategy)
            # Expand simultaneous operations and check that the same input still sorts.
            expanded = [part for op in operations for part in SPLIT.get(op, (op,))]
            checked(values, expanded)
        except Exception as error:
            raise AssertionError(f"n={size}, seed={seed}, strategy={strategy}") from error
        count = len(operations)
        counts.append(count)
        saved_rotations += operations.count("rr") + operations.count("rrr")
        effective[fields["Effective strategy"]] += 1
        worst.append({"seed": seed, "operations": count, "sha256": digest})
        worst = sorted(worst, key=lambda row: (-row["operations"], row["seed"]))[:3]
    summary = {
        "size": size, "strategy": strategy, "trials": trials,
        "minimum": min(counts), "average": round(sum(counts) / trials, 2),
        "maximum": max(counts), "worst": worst, "effective": dict(effective),
        "rotations_saved_vs_expanded_stream": saved_rotations,
    }
    # Explicit Simple is intentionally quadratic; it is measured, not substituted.
    if strategy != "simple":
        target = 1500 if size == 100 else 8000
        assert max(counts) < target, summary
    print(f"n={size} {strategy}: min/avg/max "
          f"{summary['minimum']}/{summary['average']}/{summary['maximum']}", flush=True)
    return summary


def replay_worst(report, memory=False, exact=False):
    runs = 0
    for series in report["random"]:
        for worst in series["worst"]:
            values = generated(series["size"], worst["seed"])
            ops, _, digest = execute(values, series["strategy"], memory)
            if exact:
                assert len(ops) == worst["operations"] and digest == worst["sha256"]
            if series["strategy"] != "simple":
                assert len(ops) < (1500 if len(values) == 100 else 8000)
            runs += 1
    return runs


def stress(memory=False):
    results = []
    for size in (95, 501, 1000, 2048):
        ordered = list(range(size))
        patterns = {
            "sorted": ordered, "reverse": ordered[::-1],
            "rotated": ordered[size // 3:] + ordered[:size // 3],
            "nearly_sorted": [1, 0, *ordered[2:]],
            "random": generated(size, 150015),
            "alternating": ordered[::2] + ordered[1::2][::-1],
        }
        for pattern, values in patterns.items():
            for strategy in STRATEGIES:
                ops, _, digest = execute(values, strategy)
                if strategy == "adaptive":
                    _, _, default_digest = execute(values, "default")
                    assert digest == default_digest
                results.append({"size": size, "pattern": pattern,
                                "strategy": strategy, "operations": len(ops)})
        if memory:
            for strategy in STRATEGIES:
                execute(patterns["random"], strategy, memory=True)
        print(f"stress n={size}: all patterns/selectors passed", flush=True)
    # Check signed extremes without changing rank order assumptions.
    for strategy in STRATEGIES:
        execute([-2147483648, 2147483647, 0, -1, 1, 42, -42], strategy, memory)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials-100", type=int, default=1000)
    parser.add_argument("--trials-500", type=int, default=500)
    parser.add_argument("--valgrind", action="store_true")
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "docs/performance_stage15.json")
    options = parser.parse_args()
    if min(options.trials_100, options.trials_500) < 1:
        parser.error("trial counts must be positive")
    if options.valgrind and not shutil.which("valgrind"):
        parser.error("Valgrind is required for --valgrind")
    if options.replay:
        report = json.loads(options.replay.read_text())
        runs = replay_worst(report, options.valgrind)
        print(f"PASS: replayed {runs} saved worst cases")
        return
    report = {"generator": "random.Random(seed).sample(range(-1000000000, 1000000000), n)",
              "checker": "independent Python deque replay before counting",
              "valgrind": options.valgrind, "random": []}
    for size, trials in ((100, options.trials_100), (500, options.trials_500)):
        for strategy in STRATEGIES:
            report["random"].append(random_series(size, trials, strategy))
    report["stress"] = stress(options.valgrind)
    report["worst_replays"] = replay_worst(report, options.valgrind, exact=True)
    # The report is written only after the entire run succeeds.
    options.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: report saved to {options.output}", flush=True)


if __name__ == "__main__":
    main()
