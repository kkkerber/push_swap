"""Stage 13: python3 tests/test_benchmark.py. Run make first."""

from collections import Counter
from pathlib import Path
import random
import subprocess
import tempfile

from test_dispatch import selected, with_inversions
from test_small import OPS, replay

ROOT = Path(__file__).resolve().parents[1]
FLAGS = ("--simple", "--medium", "--complex", "--adaptive")
NAMES = ("Simple", "Medium", "Complex", "Adaptive")
COMPLEXITIES = ("O(n^2)", "O(n*sqrt(n))", "O(n log n)")


def check(values, requested, flag):
    args = [str(ROOT / "push_swap"), *([flag] if flag else []), *map(str, values)]
    plain = subprocess.run(args, capture_output=True, text=True, check=True)
    result = subprocess.run([*args, "--bench"], capture_output=True,
                            text=True, check=True)
    assert not plain.stderr and result.stdout == plain.stdout
    assert replay(values, result.stdout) == (sorted(values), [])
    rows = result.stderr.splitlines()
    assert len(rows) == 16 and len(set(rows)) == 16, rows
    fields = dict(row.split(": ", 1) for row in rows)
    pairs = len(values) * (len(values) - 1) // 2
    inversions = sum(a > b for i, a in enumerate(values) for b in values[i + 1:])
    # Round the original disorder to nearest hundredth, using integers.
    percent = (inversions * 20000 + pairs) // (2 * pairs) if pairs else 0
    assert fields["Disorder"] == f"{percent // 100}.{percent % 100:02d}%"
    effective = selected(values, requested)
    assert fields["Requested strategy"] == NAMES[requested]
    assert fields["Effective strategy"] == NAMES[effective]
    assert fields["Theoretical complexity"] == COMPLEXITIES[effective]
    counts = Counter(result.stdout.splitlines())
    assert set(counts) <= set(OPS)
    assert all(int(fields[op]) == counts[op] for op in OPS)
    assert int(fields["Total operations"]) == sum(counts.values())
    assert sum(int(fields[op]) for op in OPS) == sum(counts.values())
    # A shared descriptor confirms the report follows every operation.
    merged = subprocess.run([*args, "--bench"], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, check=True)
    assert merged.stdout == result.stdout + result.stderr


def check_api():
    # Exercise every counter, ULLONG_MAX, zero pairs, disabled and null calls.
    source = r'''
#include "push_swap.h"
#include <limits.h>
int main(void)
{
    t_data data;
    data_init(&data);
    print_benchmark(NULL);
    print_benchmark(&data);
    data.config.bench = 1;
    data.effective_strategy = SIMPLE;
    data.stats.total = ULLONG_MAX;
    data.stats.sa = ULLONG_MAX - 10;
    data.stats.sb = 1;
    data.stats.ss = 1;
    data.stats.pa = 1;
    data.stats.pb = 1;
    data.stats.ra = 1;
    data.stats.rb = 1;
    data.stats.rr = 1;
    data.stats.rra = 1;
    data.stats.rrb = 1;
    data.stats.rrr = 1;
    print_benchmark(&data);
    return (0);
}
'''
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)
        (path / "probe.c").write_text(source)
        sources = [str(p) for p in (ROOT / "src").rglob("*.c") if p.name != "main.c"]
        subprocess.run(["cc", "-Wall", "-Wextra", "-Werror", "-Iincludes",
                        "-Ift_printf", str(path / "probe.c"), *sources,
                        "ft_printf/libftprintf.a", "-o", str(path / "probe")],
                       cwd=ROOT, check=True)
        result = subprocess.run([str(path / "probe")], capture_output=True,
                                text=True, check=True)
        assert not result.stdout and len(result.stderr.splitlines()) == 16
        fields = dict(row.split(": ", 1) for row in result.stderr.splitlines())
        assert fields["Disorder"] == "0.00%"
        assert int(fields["Total operations"]) == 2**64 - 1
        assert sum(int(fields[op]) for op in OPS) == 2**64 - 1


def main():
    rng = random.Random(13)
    cases = [[0], [1, 2, 3], [3, 2, 1], [2, 0, 3, 1],
             [-2147483648, 2147483647], list(range(100)), list(range(99, -1, -1))]
    cases += [with_inversions(6, count) for count in (1, 2, 3, 7, 8, 14)]
    cases += [rng.sample(range(-10000, 10000), n) for n in (6, 17, 100, 500)]
    for values in cases:
        for requested, flag in [*enumerate(FLAGS), (3, None)]:
            check(values, requested, flag)
    for args in (["--bench"], ["--bench", "1", "--bench"],
                 ["--bench", "1", "01"], ["--bench", "oops"]):
        result = subprocess.run([str(ROOT / "push_swap"), *args],
                                capture_output=True, text=True)
        assert result.returncode == 1 and result.stderr == "Error\n"
        assert not result.stdout
    result = subprocess.run([str(ROOT / "push_swap")], capture_output=True)
    assert result.returncode == 0 and not result.stdout and not result.stderr
    check_api()
    print("PASS: benchmark fields, rounding, routing, all counters, stream isolation,")
    print("post-sort output, unchanged commands, errors, ULLONG_MAX and API guards")


if __name__ == "__main__":
    main()
