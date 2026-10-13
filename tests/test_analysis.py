"""Stage 7: independent inversion model and exact integer boundaries."""

import itertools
from pathlib import Path
import random
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FLAGS = ("--simple", "--medium", "--complex", "--adaptive")
PROBE = r'''
#include "parsing.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static int forbid_memory;
void *__real_malloc(size_t size);
void __real_free(void *ptr);
void *__wrap_malloc(size_t size)
{
    assert(!forbid_memory);
    return __real_malloc(size);
}
void __wrap_free(void *ptr)
{
    assert(!forbid_memory);
    __real_free(ptr);
}

int main(int argc, char **argv)
{
    t_data data;
    t_node *nodes[1000], *next[1000], *prev[1000], *node;
    int values[1000], ranks[1000], count, i;
    t_config config;
    unsigned long long inversions, pairs;
    t_strategy effective;

    data_init(&data);
    compute_disorder(NULL);
    strategy_select(NULL);
    if (argc == 5 && strcmp(argv[1], "threshold") == 0)
    {
        data.config.requested_strategy = atoi(argv[2]);
        data.inversions = strtoull(argv[3], NULL, 10);
        data.pairs = strtoull(argv[4], NULL, 10);
        forbid_memory = 1;
        strategy_select(&data);
        printf("%d\n", data.effective_strategy);
        return 0;
    }
    assert(parse_input(argc, argv, &data));
    assert(assign_ranks(&data.a));
    config = data.config;
    count = data.a.size;
    assert(count <= 1000);
    node = data.a.top;
    for (i = 0; i < count; i++)
    {
        nodes[i] = node;
        next[i] = node->next;
        prev[i] = node->prev;
        values[i] = node->value;
        ranks[i] = node->rank;
        node = node->next;
    }
    data.inversions = 999;
    data.pairs = 999;
    forbid_memory = 1;
    compute_disorder(&data);
    strategy_select(&data);
    inversions = data.inversions;
    pairs = data.pairs;
    effective = data.effective_strategy;
    compute_disorder(&data);
    strategy_select(&data);
    assert(data.inversions == inversions && data.pairs == pairs);
    assert(data.effective_strategy == effective);
    assert(data.a.size == count && !data.b.size);
    assert(data.a.top == (count ? nodes[0] : NULL));
    assert(data.a.bottom == (count ? nodes[count - 1] : NULL));
    assert(data.config.requested_strategy == config.requested_strategy);
    assert(data.config.strategy_set == config.strategy_set);
    assert(data.config.bench == config.bench);
    assert(data.stats.total == 0);
    assert(!data.stats.sa && !data.stats.sb && !data.stats.ss);
    assert(!data.stats.pa && !data.stats.pb);
    assert(!data.stats.ra && !data.stats.rb && !data.stats.rr);
    assert(!data.stats.rra && !data.stats.rrb && !data.stats.rrr);
    for (i = 0; i < count; i++)
    {
        assert(nodes[i]->next == next[i] && nodes[i]->prev == prev[i]);
        assert(nodes[i]->value == values[i] && nodes[i]->rank == ranks[i]);
    }
    printf("%llu %llu %d %d\n", inversions, pairs,
        data.config.requested_strategy, effective);
    fflush(stdout);
    /* Operations must not update the saved original-input disorder. */
    ra(&data);
    pb(&data);
    assert(data.inversions == inversions && data.pairs == pairs);
    assert(data.effective_strategy == effective);
    forbid_memory = 0;
    data_clear(&data);
    data_clear(&data);
    return 0;
}
'''


def selection(inversions, pairs, requested):
    if requested != 3:
        return requested
    if not pairs or inversions * 5 < pairs:
        return 0
    return 1 if inversions * 2 < pairs else 2


def run(binary, args, expected, memory=False):
    command = [str(binary), *map(str, args)]
    if memory:
        command = ["valgrind", "--quiet", "--leak-check=full",
                   "--show-leak-kinds=all", "--errors-for-leak-kinds=all",
                   "--error-exitcode=99", *command]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    assert (result.returncode, result.stdout, result.stderr) == (0, expected, ""), (
        args, result)


def check_values(binary, values, requested=3, memory=False):
    inversions = sum(left > right for i, left in enumerate(values) for right in values[i+1:])
    pairs = len(values) * (len(values) - 1) // 2
    effective = selection(inversions, pairs, requested)
    expected = f"{inversions} {pairs} {requested} {effective}\n"
    if len(values) > 1:
        expected += "ra\n"
    if values:
        expected += "pb\n"
    args = [FLAGS[requested], "--bench", *map(str, values)] if values else []
    run(binary, args, expected, memory)


def main():
    cases = []
    for size in range(1, 6):
        cases.extend(list(itertools.permutations(range(size))))
    cases.append([])
    cases.extend([[0, 2, 1, 4, 3], [2, 0, 4, 3, 1],
                  [-2147483648, 2147483647, 0], [2147483647, -2147483648]])
    rng = random.Random(42)
    for size in (95, 100, 500, 1000):
        values = rng.sample(range(-1000000, 1000000), size)
        cases.extend([values, sorted(values), sorted(values, reverse=True)])
    for _ in range(50):
        cases.append(rng.sample(range(-1000, 1000), rng.randrange(2, 60)))
    sources = sorted((ROOT / "src").rglob("*.c"))
    sources = [source for source in sources if source.name != "main.c"]
    with tempfile.TemporaryDirectory(prefix="push-swap-analysis-") as temp:
        probe = Path(temp) / "probe.c"
        binary = Path(temp) / "probe"
        probe.write_text(PROBE)
        subprocess.run(["cc", "-Wall", "-Wextra", "-Werror", "-g",
                        "-fsanitize=undefined", "-fno-sanitize-recover=all",
                        "-I", str(ROOT / "includes"), "-I", str(ROOT / "ft_printf"),
                        str(probe), *map(str, sources),
                        str(ROOT / "ft_printf/libftprintf.a"),
                        "-Wl,--wrap=malloc", "-Wl,--wrap=free",
                        "-o", str(binary)], check=True)
        for values in cases:
            for requested in range(4) if values else (3,):
                check_values(binary, values, requested)
        boundaries = 0
        for pairs in (0, 1, 2, 3, 5, 10, 11, 2**32, 2**63, 2**64-1):
            candidates = {0, pairs}
            for threshold in ((pairs + 4)//5, (pairs + 1)//2):
                candidates.update(value for value in (threshold-1, threshold, threshold+1)
                                  if 0 <= value <= pairs)
            for inversions in candidates:
                for requested in range(4):
                    run(binary, ["threshold", requested, inversions, pairs],
                        f"{selection(inversions, pairs, requested)}\n")
                    boundaries += 1
        for values in ([], [0], [0, 2, 1, 4, 3], [2, 0, 4, 3, 1],
                       list(range(999, -1, -1))):
            check_values(binary, values, memory=True)
    print(f"PASS: {len(cases)} inversion inputs with selectors; {boundaries} exact boundaries;")
    print("unchanged nodes/config/counters, preserved original disorder after operations,")
    print("no allocation/free, UBSan and 5 Valgrind paths")


if __name__ == "__main__":
    main()
