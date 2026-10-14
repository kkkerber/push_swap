"""Stage 11: python3 tests/test_complex.py [--valgrind]. Run make first."""

import argparse
import itertools
from pathlib import Path
import random
import shutil
import subprocess
import tempfile

from test_medium import PROBE as STACK_PROBE, ROOT
from test_small import OPS, replay

# Reuse the common per-command ownership/link/counter probe for both strategies.
PROBE = STACK_PROBE.replace("sort_medium", "sort_complex").replace("MEDIUM", "COMPLEX")
PROBE = PROBE.replace("count, locked, live;", "count, locked, live, sparse;")
PROBE = PROBE.replace("rank = node->rank;", "rank = 2000 - node->value;")
PROBE = PROBE.replace("seen[rank] = 1;", """seen[rank] = 1;
            assert(node->rank == (sparse ?
                (rank == count - 1 ? 2147483647 : rank * 1024) : rank));""")
PROBE = PROBE.replace("count = size + guard;", """count = size + guard;
    sparse = strcmp(argv[1], "sparse") == 0;""")
PROBE = PROBE.replace("node->rank = rank;", """node->rank = sparse ?
            (rank == count - 1 ? 2147483647 : rank * 1024) : rank;""")


def radix_model(values):
    """Independent list model, including public ra's singleton no-op rule."""
    if values == sorted(values):
        return ""
    a, b, output = values[:], [], []
    for bit in range(max(values).bit_length()):
        for _ in range(len(a)):
            if a[0] & (1 << bit):
                if len(a) > 1:
                    a.append(a.pop(0))
                    output.append("ra")
            else:
                b.insert(0, a.pop(0))
                output.append("pb")
        while b:
            a.insert(0, b.pop(0))
            output.append("pa")
    assert a == sorted(values)
    return "\n".join(output) + "\n"


def validate(values, output):
    assert replay(values, output) == (sorted(values), []), values
    if values == sorted(values):
        assert not output
    if len(values) > 5:
        assert output == radix_model(values), values
        assert len(output.splitlines()) <= 2 * len(values) * max(values).bit_length()


def cli(values, flag="--complex"):
    args = [str(ROOT / "push_swap"), *([flag] if flag and values else []),
            *map(str, values)]
    result = subprocess.run(args, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0 and not result.stderr, result
    ranks = {value: rank for rank, value in enumerate(sorted(values))}
    validate([ranks[value] for value in values], result.stdout)
    return result.stdout


def check_probe(binary, values, memory, mode="normal"):
    command = [str(binary), mode, *map(str, values)]
    if memory:
        command = ["valgrind", "--quiet", "--leak-check=full",
                   "--show-leak-kinds=all", "--errors-for-leak-kinds=all",
                   "--error-exitcode=99", *command]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    ops = result.stdout.splitlines()
    counters = [len(ops), *[ops.count(op) for op in OPS]]
    assert result.stderr == "COUNTERS " + " ".join(map(str, counters)) + "\n", result
    if mode == "guard":
        assert not ops
    else:
        if mode == "sparse":
            values = [2147483647 if v == len(values) - 1 else v * 1024 for v in values]
        validate(values, result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--valgrind", action="store_true")
    options = parser.parse_args()
    if options.valgrind and not shutil.which("valgrind"):
        parser.error("Valgrind is not installed")
    for n in range(7):
        for values in itertools.permutations(range(n)):
            cli(list(values))
    patterns = []
    sizes = {6, 100, 500, 1000, 1500}
    sizes.update(2 ** bit + delta for bit in range(3, 11) for delta in (-1, 0, 1))
    for n in sorted(sizes):
        ordered = list(range(n))
        shuffled = ordered[:]
        random.Random(n).shuffle(shuffled)
        patterns += [ordered, ordered[::-1], [1, 0, *range(2, n)], shuffled]
    for values in patterns:
        cli(values)
    cli([2147483647, -2147483648, 0, 42, -42, 1])
    # Exactly 50% disorder at n=8 and above it select Complex.
    for values in ([7, 6, 1, 0, 2, 3, 4, 5], list(range(19, -1, -1))):
        assert cli(values) == cli(values, "--adaptive") == cli(values, "")
    counts = {}
    for n, target in ((100, 1500), (500, 8000)):
        counts[n] = []
        for seed in range(20):
            values = list(range(n))
            random.Random(seed).shuffle(values)
            count = len(cli(values).splitlines())
            assert count < target
            counts[n].append(count)
    flags = ["cc", "-Wall", "-Wextra", "-Werror", "-g",
             "-I", str(ROOT / "includes"), "-I", str(ROOT / "ft_printf")]
    if not options.valgrind:
        flags += ["-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
    sources = [p for p in (ROOT / "src").rglob("*.c") if p.name != "main.c"]
    sources += list((ROOT / "ft_printf").glob("*.c"))
    with tempfile.TemporaryDirectory(prefix="push-swap-complex-") as folder:
        tmp = Path(folder)
        objects = []
        for i, source in enumerate(sources):
            obj = tmp / f"source_{i}.o"
            defines = ["-Dmalloc=test_malloc", "-Dfree=test_free"]
            if source.parent.name == "operations":
                defines += [f"-D{name}=real_{name}" for name in OPS]
            subprocess.run([*flags, *defines, "-c", str(source), "-o", str(obj)], check=True)
            objects.append(str(obj))
        probe, binary = tmp / "probe.c", tmp / "probe"
        probe.write_text(PROBE)
        subprocess.run([*flags, str(probe), *objects, "-o", str(binary)], check=True)
        for values in [[], [0], [1, 0], [2, 0, 1], [3, 2, 1, 0],
                       [4, 3, 2, 1, 0], *patterns]:
            check_probe(binary, values, options.valgrind)
        check_probe(binary, [2, 1, 0], options.valgrind, "guard")
        check_probe(binary, [5, 2, 0, 4, 3, 1], options.valgrind, "sparse")
    print("PASS: permutations 0-6; powers-of-two boundaries; patterns through 1500;")
    print("exact radix model; sparse ranks through INT_MAX; per-command invariants;")
    print("counters; no malloc/free; selector routing;",
          "Valgrind" if options.valgrind else "ASan/UBSan (Valgrind not run)")
    for n, samples in counts.items():
        print(f"n={n}: min/max operations {min(samples)}/{max(samples)}")


if __name__ == "__main__":
    main()
