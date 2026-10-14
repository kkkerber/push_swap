"""Stage 10: python3 tests/test_medium.py [--valgrind]. Run make first."""

import argparse
import itertools
import math
from pathlib import Path
import random
import shutil
import subprocess
import tempfile

from test_small import OPS, replay

ROOT = Path(__file__).resolve().parents[1]
PROBE = r'''
#include "push_swap.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static t_data *context;
static t_node *original[2001];
static int count, locked, live;

void *test_malloc(size_t size)
{
    void *ptr;
    assert(!locked);
    ptr = malloc(size);
    if (ptr) live++;
    return ptr;
}
void test_free(void *ptr)
{
    assert(!locked);
    if (ptr) { assert(live > 0); live--; }
    free(ptr);
}
static void verify(void)
{
    t_stack *stacks[2] = {&context->a, &context->b};
    t_node *node;
    int seen[2001] = {0};
    int k, i, rank;

    assert(context->a.size + context->b.size == count);
    assert(live == count);
    for (k = 0; k < 2; k++)
    {
        assert(stacks[k]->size >= 0 && stacks[k]->size <= count);
        if (!stacks[k]->size)
        {
            assert(!stacks[k]->top && !stacks[k]->bottom);
            continue;
        }
        assert(stacks[k]->top->prev == stacks[k]->bottom);
        assert(stacks[k]->bottom->next == stacks[k]->top);
        node = stacks[k]->top;
        for (i = 0; i < stacks[k]->size; i++)
        {
            rank = node->rank;
            assert(rank >= 0 && rank < count && !seen[rank]);
            seen[rank] = 1;
            assert(node == original[rank] && node->value == 2000 - rank);
            assert(node->next->prev == node && node->prev->next == node);
            if (i == stacks[k]->size - 1) assert(node == stacks[k]->bottom);
            node = node->next;
        }
        assert(node == stacks[k]->top);
    }
    for (i = 0; i < count; i++) assert(seen[i]);
}
#define WRAP(name) \
void real_##name(t_data *data); \
void name(t_data *data) { real_##name(data); verify(); }
WRAP(sa)
WRAP(sb)
WRAP(ss)
WRAP(pa)
WRAP(pb)
WRAP(ra)
WRAP(rb)
WRAP(rr)
WRAP(rra)
WRAP(rrb)
WRAP(rrr)

int main(int argc, char **argv)
{
    t_data data;
    t_node *node;
    int i, rank, size = argc - 2;
    int guard = strcmp(argv[1], "guard") == 0;
    unsigned long long total, inversions, pairs;
    t_strategy effective;

    assert(size >= 0 && size <= 2000);
    data_init(&data);
    context = &data;
    count = size + guard;
    for (i = 0; i < count; i++)
    {
        rank = i == size ? size : atoi(argv[i + 2]);
        assert(rank >= 0 && rank < count && !original[rank]);
        node = node_new(2000 - rank);
        assert(node);
        node->rank = rank;
        original[rank] = node;
        stack_add_bottom(i == size ? &data.b : &data.a, node);
    }
    data.config.requested_strategy = MEDIUM;
    data.config.strategy_set = 1;
    data.config.bench = 1;
    compute_disorder(&data);
    strategy_select(&data);
    inversions = data.inversions;
    pairs = data.pairs;
    effective = data.effective_strategy;
    verify();
    locked = 1;
    sort_medium(NULL);
    sort_medium(&data);
    verify();
    if (!guard)
    {
        assert(data.b.size == 0);
        node = data.a.top;
        for (i = 0; i < size; i++)
        {
            assert(node == original[i]);
            node = node->next;
        }
    }
    else
    {
        assert(data.stats.total == 0 && data.b.top == original[size]);
        node = data.a.top;
        for (i = 0; i < size; i++)
        {
            assert(node == original[atoi(argv[i + 2])]);
            node = node->next;
        }
    }
    total = data.stats.total;
    sort_medium(&data);
    assert(data.stats.total == total);
    assert(data.inversions == inversions && data.pairs == pairs);
    assert(data.effective_strategy == effective);
    assert(data.config.requested_strategy == MEDIUM);
    assert(data.config.strategy_set == 1 && data.config.bench == 1);
    fprintf(stderr, "COUNTERS %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu\n",
        data.stats.total, data.stats.sa, data.stats.sb, data.stats.ss,
        data.stats.pa, data.stats.pb, data.stats.ra, data.stats.rb,
        data.stats.rr, data.stats.rra, data.stats.rrb, data.stats.rrr);
    locked = 0;
    data_clear(&data);
    data_clear(&data);
    assert(live == 0);
    return 0;
}
'''


def validate(values, output):
    assert replay(values, output) == (sorted(values), []), values
    if values == sorted(values):
        assert not output, values
    n = len(values)
    width = max(1, math.isqrt(n))
    # At most one forward sweep per chunk; <= 2*width per return; pushes/buries.
    bound = n * ((n + width - 1) // width) + 2 * n * width + 3 * n
    assert len(output.splitlines()) <= bound, (n, bound)


def cli(values, flag="--medium"):
    command = [str(ROOT / "push_swap")]
    if flag and values:
        command.append(flag)
    result = subprocess.run([*command, *map(str, values)], capture_output=True,
                            text=True, timeout=60)
    assert result.returncode == 0 and not result.stderr, result
    validate(values, result.stdout)
    return result.stdout


def check_probe(binary, values, memory=False, guard=False):
    command = [str(binary), "guard" if guard else "normal", *map(str, values)]
    if memory:
        command = ["valgrind", "--quiet", "--leak-check=full",
                   "--show-leak-kinds=all", "--errors-for-leak-kinds=all",
                   "--error-exitcode=99", *command]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, (len(values), result.stderr)
    ops = result.stdout.splitlines()
    counters = [len(ops), *[ops.count(op) for op in OPS]]
    assert result.stderr == "COUNTERS " + " ".join(map(str, counters)) + "\n", result
    if guard:
        assert not result.stdout
    else:
        validate(values, result.stdout)
    return set(ops)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--valgrind", action="store_true")
    options = parser.parse_args()
    if options.valgrind and not shutil.which("valgrind"):
        parser.error("Valgrind is not installed")
    # Exhaustive small-sort delegation and all six-element permutations.
    cli_cases = [[], [0]]
    cli_cases += [list(p) for n in range(2, 7) for p in itertools.permutations(range(n))]
    for values in cli_cases:
        cli(values)
    rng = random.Random(42)
    patterns = []
    for n in (6, 7, 9, 10, 15, 16, 17, 31, 95, 100, 101, 499, 500, 501, 1000, 1500):
        ordered = list(range(n))
        shuffled = ordered[:]
        rng.shuffle(shuffled)
        patterns += [ordered, ordered[::-1], ordered[1:] + [0],
                     ordered[::2] + ordered[1::2], shuffled]
    for values in patterns:
        cli(values)
    cli([2147483647, -2147483648, 0, 42, -42, 1])
    # Exactly 20% and between boundaries for n=6; exactly 50% for n=4.
    for values in ([3, 0, 1, 2, 4, 5], [5, 0, 1, 2, 3, 4], [2, 1, 0, 3]):
        assert cli(values, "--adaptive") == cli(values, "")
    medium_values = [5, 0, 1, 2, 3, 4]
    assert cli(medium_values, "--adaptive") == cli(medium_values)
    low = [1, 0, *range(2, 20)]
    assert cli(low, "--adaptive") == cli(low, "--simple")
    counts = {}
    for n, runs, target in ((100, 100, 1500), (500, 50, 8000)):
        counts[n] = []
        for seed in range(runs):
            values = list(range(n))
            random.Random(seed).shuffle(values)
            count = len(cli(values).splitlines())
            assert count < target, (n, seed, count)
            counts[n].append(count)
    flags = ["cc", "-Wall", "-Wextra", "-Werror", "-g",
             "-I", str(ROOT / "includes"), "-I", str(ROOT / "ft_printf")]
    if not options.valgrind:
        flags += ["-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
    sources = [p for p in (ROOT / "src").rglob("*.c") if p.name != "main.c"]
    sources += list((ROOT / "ft_printf").glob("*.c"))
    with tempfile.TemporaryDirectory(prefix="push-swap-medium-") as tmp:
        tmp = Path(tmp)
        objects = []
        for i, source in enumerate(sources):
            obj = tmp / f"source_{i}.o"
            defines = ["-Dmalloc=test_malloc", "-Dfree=test_free"]
            if source.parent.name == "operations":
                defines += [f"-D{name}=real_{name}" for name in OPS]
            subprocess.run([*flags, *defines, "-c", str(source), "-o", str(obj)], check=True)
            objects.append(str(obj))
        probe = tmp / "probe.c"
        binary = tmp / "probe"
        probe.write_text(PROBE)
        subprocess.run([*flags, str(probe), *objects, "-o", str(binary)], check=True)
        used = set()
        for values in [[], [0], [1, 0], [2, 0, 1], [3, 2, 0, 1], [4, 3, 2, 1, 0], *patterns]:
            used |= check_probe(binary, values, memory=options.valgrind)
        check_probe(binary, [2, 1, 0], memory=options.valgrind, guard=True)
        used |= check_probe(binary, [5, 2, 7, 1, 8, 4, 3, 6, 0],
                            memory=options.valgrind)
        assert {"rr", "rrr"} <= used, used
    print("PASS: all permutations 2-6; patterns through 1500; independent replay;")
    print("per-command links/identity/ranks/counters; no malloc/free; selector routing;")
    print("Valgrind" if options.valgrind else "ASan/UBSan (Valgrind not run)")
    for n, samples in counts.items():
        print(f"n={n}: min/avg/max {min(samples)}/{sum(samples)/len(samples):.1f}/{max(samples)}")


if __name__ == "__main__":
    main()
