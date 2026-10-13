"""Stage 6: independent rank expectations, atomic failure and memory checks."""

import os
from pathlib import Path
import random
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PROBE = r'''
#include "push_swap.h"
#include <assert.h>
#include <stdio.h>

static int fail_ranking;
static int allocations;
void *__real_malloc(size_t size);
void __real_free(void *ptr);
void *__wrap_malloc(size_t size)
{
    void *ptr;
    if (fail_ranking)
        return NULL;
    ptr = __real_malloc(size);
    if (ptr)
        allocations++;
    return ptr;
}
void __wrap_free(void *ptr)
{
    if (ptr)
        allocations--;
    __real_free(ptr);
}

int main(int argc, char **argv)
{
    t_data data;
    t_node *nodes[1000], *next[1000], *prev[1000];
    int sorted[1000];
    int count = argc - 1, i, success;

    assert(count <= 1000);
    data_init(&data);
    assert(assign_ranks(NULL) == 0);
    assert(assign_ranks(&data.a) == 1);
    assert(allocations == 0);
    for (i = 0; i < count; i++)
    {
        nodes[i] = node_new(atoi(argv[i + 1]));
        assert(nodes[i]);
        assert(nodes[i]->rank == -1);
        sorted[i] = nodes[i]->value;
        stack_add_bottom(&data.a, nodes[i]);
    }
    for (i = 0; i < count; i++)
    {
        next[i] = nodes[i]->next;
        prev[i] = nodes[i]->prev;
    }
    fail_ranking = getenv("RANK_FAIL") != NULL;
    success = assign_ranks(&data.a);
    assert(allocations == count);
    if (success)
    {
        assert(assign_ranks(&data.a) == 1);
        assert(allocations == count);
    }
    assert(data.a.size == count);
    assert(data.a.top == (count ? nodes[0] : NULL));
    assert(data.a.bottom == (count ? nodes[count - 1] : NULL));
    assert(!data.b.size && !data.b.top && !data.b.bottom);
    assert(data.stats.total == 0);
    assert(!data.inversions && !data.pairs);
    for (i = 0; i < count; i++)
    {
        assert(nodes[i]->value == atoi(argv[i + 1]));
        assert(nodes[i]->next == next[i] && nodes[i]->prev == prev[i]);
        assert(nodes[i]->next->prev == nodes[i]);
        assert(nodes[i]->prev->next == nodes[i]);
        if (!success)
            assert(nodes[i]->rank == -1);
    }
    if (success)
    {
        printf("RANKS");
        for (i = 0; i < count; i++)
            printf(" %d", nodes[i]->rank);
        printf("\n");
    }
    else
        printf("FAIL\n");
    sort_values(sorted, count);
    printf("SORTED");
    for (i = 0; i < count; i++)
        printf(" %d", sorted[i]);
    printf("\n");
    data_clear(&data);
    data_clear(&data);
    assert(allocations == 0);
    return !success;
}
'''


def check(binary, values, *, fail=False, memory=False):
    command = [str(binary), *map(str, values)]
    if memory:
        command = ["valgrind", "--quiet", "--leak-check=full",
                   "--show-leak-kinds=all", "--errors-for-leak-kinds=all",
                   "--error-exitcode=99", *command]
    env = dict(os.environ)
    env.pop("RANK_FAIL", None)
    if fail:
        env["RANK_FAIL"] = "1"
    success = len(values) == len(set(values)) and not (fail and values)
    expected = "FAIL\n"
    if success:
        positions = {value: rank for rank, value in enumerate(sorted(values))}
        expected = "RANKS" + "".join(f" {positions[value]}" for value in values) + "\n"
    expected += "SORTED" + "".join(f" {value}" for value in sorted(values)) + "\n"
    result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=60)
    assert (result.returncode, result.stdout, result.stderr) == (
        int(not success), expected, ""), (values, result)


def main():
    cases = [[], [0], [30, -5, 10], [-2147483648, 2147483647, 0],
             [1, 1], [2, 1, 2], [5, 1, 4, 3, 5],
             [2147483647, 2147483647], [-2147483648, -2147483648]]
    rng = random.Random(42)
    for size in (2, 3, 5, 95, 100, 500, 1000):
        values = rng.sample(range(-1000000, 1000000), size)
        cases.extend([values, sorted(values), sorted(values, reverse=True)])
    for _ in range(100):
        values = rng.sample(range(-1000000, 1000000), rng.randrange(1, 150))
        cases.extend([values, [*values, values[0]]])
    sources = sorted((ROOT / "src/stack").glob("*.c"))
    sources += sorted((ROOT / "src/core").glob("*.c"))
    sources += sorted((ROOT / "src/ranking").glob("*.c"))
    with tempfile.TemporaryDirectory(prefix="push-swap-ranking-") as temp:
        probe = Path(temp) / "probe.c"
        binary = Path(temp) / "probe"
        probe.write_text(PROBE)
        subprocess.run(["cc", "-Wall", "-Wextra", "-Werror", "-g",
                        "-fsanitize=undefined", "-fno-sanitize-recover=all",
                        "-I", str(ROOT / "includes"), "-I", str(ROOT / "ft_printf"),
                        str(probe), *map(str, sources),
                        "-Wl,--wrap=malloc", "-Wl,--wrap=free",
                        "-o", str(binary)], check=True)
        for values in cases:
            check(binary, values)
        for values in ([], [0], [3, 1, 2], cases[3], cases[4], cases[9]):
            check(binary, values, fail=True)
        memory_cases = [([], False), ([0], False), (cases[3], False),
                        (cases[4], False), (cases[9], True),
                        (list(range(999, -1, -1)), False)]
        for values, fail in memory_cases:
            check(binary, values, fail=fail, memory=True)
    print(f"PASS: {len(cases)} rank/sort cases, 6 allocation-failure cases,")
    print("unchanged values/identity/order/links, idempotence, atomic failure;")
    print("UBSan and 6 Valgrind paths")


if __name__ == "__main__":
    main()
