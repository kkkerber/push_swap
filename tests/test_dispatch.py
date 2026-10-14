"""Stage 12: python3 tests/test_dispatch.py [--valgrind]. Run make first."""

import argparse
import itertools
import os
from pathlib import Path
import random
import shutil
import subprocess
import tempfile

from test_medium import PROBE as STACK_PROBE, ROOT
from test_small import OPS, replay

FLAGS = ("--simple", "--medium", "--complex", "--adaptive")
# Reuse the per-operation node identity, rank, link and allocation guards.
# Start with stale effective_strategy so the entry point must select it itself.
PROBE = STACK_PROBE.replace("sort_medium", "route_sort")
PROBE = PROBE.replace("data.config.requested_strategy = MEDIUM;",
                      'data.config.requested_strategy = (t_strategy)atoi(getenv("REQUESTED"));')
PROBE = PROBE.replace("strategy_select(&data);", "data.effective_strategy = ADAPTIVE;")
PROBE = PROBE.replace("effective = data.effective_strategy;",
                      'effective = (t_strategy)atoi(getenv("EXPECTED"));')
PROBE = PROBE.replace("data.config.requested_strategy == MEDIUM",
                      'data.config.requested_strategy == (t_strategy)atoi(getenv("REQUESTED"))')


def selected(values, requested=3):
    if requested != 3:
        return requested
    pairs = len(values) * (len(values) - 1) // 2
    inversions = sum(a > b for i, a in enumerate(values) for b in values[i + 1:])
    if not pairs or inversions * 5 < pairs:
        return 0
    return 1 if inversions * 2 < pairs else 2


def cli(values, flag=None):
    args = [str(ROOT / "push_swap"), *([flag] if flag and values else []),
            *map(str, values)]
    result = subprocess.run(args, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0 and not result.stderr, result
    assert replay(values, result.stdout) == (sorted(values), []), values
    if values == sorted(values):
        assert not result.stdout
    return result.stdout


def check_cli(values):
    outputs = [cli(values, flag) for flag in FLAGS]
    assert outputs[3] == cli(values) == outputs[selected(values)], values
    if len(values) <= 5:
        assert len(set(outputs)) == 1, values


def with_inversions(n, inversions):
    remaining = list(range(n))
    result = []
    while remaining:
        index = min(inversions, len(remaining) - 1)
        result.append(remaining.pop(index))
        inversions -= index
    assert inversions == 0
    return result


def check_probe(binary, values, requested, memory, guard=False):
    # Probe values are reversed relative to ranks to catch value-based sorting.
    effective = 3 if guard else selected([2000 - v for v in values], requested)
    env = dict(os.environ, REQUESTED=str(requested), EXPECTED=str(effective))
    args = [str(binary), "guard" if guard else "normal", *map(str, values)]
    if memory:
        args = ["valgrind", "--quiet", "--leak-check=full",
                "--show-leak-kinds=all", "--errors-for-leak-kinds=all",
                "--error-exitcode=99", *args]
    result = subprocess.run(args, capture_output=True, text=True, env=env, timeout=60)
    assert result.returncode == 0, (values, requested, result.stderr)
    ops = result.stdout.splitlines()
    assert result.stderr == "COUNTERS " + " ".join(map(str,
        [len(ops), *[ops.count(op) for op in OPS]])) + "\n", result
    if guard:
        assert not ops
    else:
        assert result.stdout == cli(values, FLAGS[effective]), (values, requested)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--valgrind", action="store_true")
    options = parser.parse_args()
    if options.valgrind and not shutil.which("valgrind"):
        parser.error("Valgrind is not installed")
    for n in range(6):
        for permutation in itertools.permutations(range(n)):
            check_cli(list(permutation))
    # Immediately below, exactly at, and immediately above both boundaries.
    boundaries = [with_inversions(6, k) for k in (2, 3, 4)]
    boundaries += [with_inversions(8, k) for k in (13, 14, 15)]
    assert [selected(v) for v in boundaries] == [0, 1, 1, 1, 2, 2]
    patterns = []
    for n in (6, 8, 100, 500, 1000):
        values = list(range(n))
        shuffled = values[:]
        random.Random(n).shuffle(shuffled)
        patterns += [values, values[::-1], [1, 0, *range(2, n)], shuffled]
    for values in boundaries + patterns:
        check_cli(values)
    check_cli([2147483647, -2147483648, 0, -42, 42, 1])
    flags = ["cc", "-Wall", "-Wextra", "-Werror", "-g",
             "-I", str(ROOT / "includes"), "-I", str(ROOT / "ft_printf")]
    if not options.valgrind:
        flags += ["-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
    sources = [p for p in (ROOT / "src").rglob("*.c") if p.name != "main.c"]
    sources += list((ROOT / "ft_printf").glob("*.c"))
    with tempfile.TemporaryDirectory(prefix="push-swap-dispatch-") as folder:
        tmp = Path(folder)
        objects = []
        for i, source in enumerate(sources):
            obj = tmp / f"source_{i}.o"
            defines = ["-Dmalloc=test_malloc", "-Dfree=test_free"]
            if source.parent.name == "operations":
                defines += [f"-D{name}=real_{name}" for name in OPS]
            subprocess.run([*flags, *defines, "-c", str(source), "-o", str(obj)], check=True)
            objects.append(str(obj))
        probe = tmp / "probe.c"
        probe.write_text(PROBE)
        for entry in ("sort_dispatch", "sort_adaptive"):
            binary = tmp / entry
            subprocess.run([*flags, f"-Droute_sort={entry}", str(probe), *objects,
                            "-o", str(binary)], check=True)
            cases = [[], [0], [1, 0], [2, 1, 0], [3, 2, 1, 0], [4, 3, 2, 1, 0]]
            for requested in range(4):
                for values in cases + boundaries + patterns:
                    check_probe(binary, values, requested, options.valgrind)
                check_probe(binary, [2, 1, 0], requested, options.valgrind, guard=True)
    print("PASS: all selectors; default equals Adaptive; exact 20%/50% boundaries;")
    print("all permutations 0-5; sorted and random inputs through 1000;")
    print("direct Adaptive/dispatcher APIs; requested/effective strategies; original metrics;")
    print("per-operation invariants, counters, no malloc/free, repeated sorting and B guard;")
    print("Valgrind" if options.valgrind else "ASan/UBSan (Valgrind not run)")


if __name__ == "__main__":
    main()
