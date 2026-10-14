"""Stage 9: Simple at arbitrary sizes, preserving the shared small-sort checks."""

import itertools
from pathlib import Path
import random
import subprocess
import tempfile

from test_small import PROBE as SMALL_PROBE, replay

ROOT = Path(__file__).resolve().parents[1]
# Reuse the independent identity/link/allocation probe, extending its capacity.
# Full per-command invariants run on small cases; larger cases check ownership
# at every operation and full identity/links before and after sorting.
PROBE = SMALL_PROBE.replace("[8]", "[1001]").replace("size <= 7", "size <= 1000")
PROBE = PROBE.replace("sort_small", "sort_simple").replace("size <= 5 && !guarded", "!guarded")
PROBE = PROBE.replace("__real_##name(data); verify();",
                      "__real_##name(data); if (count <= 20) verify(); "
                      "else assert(context->a.size + context->b.size == count);")
PROBE = PROBE.replace("    verify();\n    forbid_memory = 1;", """    verify();
    assert(stack_min_rank_position(NULL) == -1);
    if (!size) assert(stack_min_rank_position(&data.a) == -1);
    forbid_memory = 1;""")


def check(binary, values, mode="normal", memory=False):
    command = [str(binary), mode, *map(str, values)]
    if memory:
        command = ["valgrind", "--quiet", "--leak-check=full",
                   "--show-leak-kinds=all", "--errors-for-leak-kinds=all",
                   "--error-exitcode=99", *command]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, (len(values), mode, result.stderr)
    ops = result.stdout.splitlines()
    counters = [len(ops), *[ops.count(op) for op in ("sa", "pa", "pb", "ra", "rra")]]
    assert result.stderr == "COUNTERS " + " ".join(map(str, counters)) + "\n", result
    if mode == "guard":
        assert not result.stdout, result
        return
    assert replay(values, result.stdout) == (sorted(values), []), (values, result)
    if values == sorted(values):
        assert not result.stdout, result
    if len(values) <= 5:
        assert len(ops) <= (0, 0, 1, 2, 6, 10)[len(values)], result
    else:
        bound = sum(size // 2 for size in range(1, len(values) + 1)) + 2 * len(values)
        assert len(ops) <= bound, (len(values), len(ops), bound)
    return result.stdout


def cli(values, flag="--simple"):
    args = [str(ROOT / "push_swap"), *([flag] if values else []), *map(str, values)]
    result = subprocess.run(args, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0 and not result.stderr, result
    assert replay(values, result.stdout) == (sorted(values), []), (values, result)
    if values == sorted(values): assert not result.stdout, result


def main():
    rng = random.Random(42)
    cases = [[], [0], *[list(p) for size in range(2, 6)
                       for p in itertools.permutations(range(size))]]
    for size in (6, 10, 20, 95, 100, 500, 1000):
        values = rng.sample(range(-1000000, 1000000), size)
        cases.extend([values, sorted(values), sorted(values, reverse=True)])
    for _ in range(25):
        cases.append(rng.sample(range(-10000, 10000), rng.randrange(6, 40)))
    cases.append([2147483647, -2147483648, 0, 100, -100, 1])
    sources = [p for p in sorted((ROOT / "src").rglob("*.c")) if p.name != "main.c"]
    with tempfile.TemporaryDirectory(prefix="push-swap-simple-") as temp:
        probe = Path(temp) / "probe.c"
        binary = Path(temp) / "probe"
        probe.write_text(PROBE)
        subprocess.run(["cc", "-Wall", "-Wextra", "-Werror", "-g",
                        "-fsanitize=undefined", "-fno-sanitize-recover=all",
                        "-I", str(ROOT / "includes"), "-I", str(ROOT / "ft_printf"),
                        str(probe), *map(str, sources), str(ROOT / "ft_printf/libftprintf.a"),
                        *[f"-Wl,--wrap={name}" for name in
                          ("malloc", "free", "sa", "pa", "pb", "ra", "rra")],
                        "-o", str(binary)], check=True)
        for values in cases:
            check(binary, values)
            cli(values)
        for size in (6, 20, 1000):
            values = list(range(size))
            rng.shuffle(values)
            check(binary, values, "ranks")
        check(binary, [2, 1, 0], "guard")
        # The minimum at the bottom must take one reverse rotation.
        output = check(binary, [1, 2, 3, 4, 5, 6, 0])
        assert output.startswith("rra\npb\n"), output
        # Default/explicit Adaptive chooses Simple on this low-disorder input.
        low_disorder = [1, 0, *range(2, 20)]
        cli(low_disorder, "--adaptive")
        result = subprocess.run([str(ROOT / "push_swap"), *map(str, low_disorder)],
                                capture_output=True, text=True)
        assert result.returncode == 0 and not result.stderr, result
        assert replay(low_disorder, result.stdout) == (sorted(low_disorder), []), result
        cli(low_disorder, "--medium")
        cli(low_disorder, "--complex")
        for values in ([], [0], [5, 4, 3, 2, 1, 0], cases[-1],
                       list(range(99, -1, -1)), list(range(999, -1, -1))):
            check(binary, values, memory=True)
    print(f"PASS: {len(cases)} Simple inputs, all small permutations, sizes through 1000,")
    print("explicit/Adaptive selectors, shortest rotation, rank-only decisions, command bound,")
    print("identity/links/counters/original metrics and no malloc/free; UBSan; 6 Valgrind paths")


if __name__ == "__main__":
    main()
