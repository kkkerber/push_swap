"""Stage 8: exhaustive permutations, independent replay and per-command invariants."""

import itertools
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OPS = ("sa", "sb", "ss", "pa", "pb", "ra", "rb", "rr", "rra", "rrb", "rrr")
PROBE = r'''
#include "push_swap.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static t_data *context;
static t_node *original[8];
static int ranks[8], values[8], count, forbid_memory;
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
static void verify(void)
{
    t_stack *stacks[2] = {&context->a, &context->b};
    t_node *node;
    int seen[8] = {0}, k, i, id;

    assert(context->a.size + context->b.size == count);
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
            assert(node && node->next && node->prev);
            assert(node->next->prev == node && node->prev->next == node);
            assert(i == 0 || node != stacks[k]->top);
            if (i == stacks[k]->size - 1) assert(node == stacks[k]->bottom);
            for (id = 0; id < count && original[id] != node; id++);
            assert(id < count && !seen[id]);
            seen[id] = 1;
            assert(node->rank == ranks[id] && node->value == values[id]);
            node = node->next;
        }
        assert(node == stacks[k]->top);
        node = stacks[k]->bottom;
        for (i = 0; i < stacks[k]->size; i++) node = node->prev;
        assert(node == stacks[k]->bottom);
    }
    for (i = 0; i < count; i++) assert(seen[i]);
}
#define WRAP(name) \
void __real_##name(t_data *data); \
void __wrap_##name(t_data *data) { __real_##name(data); verify(); }
WRAP(sa)
WRAP(pa)
WRAP(pb)
WRAP(ra)
WRAP(rra)

int main(int argc, char **argv)
{
    t_data data;
    t_node *node;
    int i, size = argc - 2;
    int rank_only = strcmp(argv[1], "ranks") == 0;
    int guarded = strcmp(argv[1], "guard") == 0;
    unsigned long long inversions, pairs;
    t_strategy effective;

    assert(size >= 0 && size <= 7);
    data_init(&data);
    context = &data;
    for (i = 0; i < size; i++)
    {
        node = node_new(rank_only ? 500 - atoi(argv[i + 2]) : atoi(argv[i + 2]));
        assert(node);
        if (rank_only) node->rank = atoi(argv[i + 2]) * 7 + 10;
        original[i] = node;
        stack_add_bottom(&data.a, node);
    }
    if (!rank_only) assert(assign_ranks(&data.a));
    count = size;
    if (guarded)
    {
        original[count] = node_new(123456);
        assert(original[count]);
        stack_add_top(&data.b, original[count++]);
    }
    for (i = 0; i < count; i++)
    {
        ranks[i] = original[i]->rank;
        values[i] = original[i]->value;
    }
    compute_disorder(&data);
    strategy_select(&data);
    inversions = data.inversions;
    pairs = data.pairs;
    effective = data.effective_strategy;
    verify();
    forbid_memory = 1;
    sort_small(NULL);
    sort_small(&data);
    verify();
    if (size <= 5 && !guarded)
    {
        assert(!data.b.size);
        node = data.a.top;
        for (i = 1; i < size; i++)
        {
            assert(node->rank < node->next->rank);
            node = node->next;
        }
    }
    else
    {
        assert(data.stats.total == 0);
        node = data.a.top;
        for (i = 0; i < size; i++)
        {
            assert(node == original[i]);
            node = node->next;
        }
    }
    /* A second call on the sorted result must produce no extra commands. */
    sort_small(&data);
    assert(data.inversions == inversions && data.pairs == pairs);
    assert(data.effective_strategy == effective);
    assert(data.stats.total == data.stats.sa + data.stats.pa + data.stats.pb
        + data.stats.ra + data.stats.rra);
    assert(!data.stats.sb && !data.stats.ss && !data.stats.rb && !data.stats.rr);
    assert(!data.stats.rrb && !data.stats.rrr);
    fprintf(stderr, "COUNTERS %llu %llu %llu %llu %llu %llu\n",
        data.stats.total, data.stats.sa, data.stats.pa, data.stats.pb,
        data.stats.ra, data.stats.rra);
    forbid_memory = 0;
    data_clear(&data);
    data_clear(&data);
    return 0;
}
'''


def replay(values, output):
    a, b = list(values), []
    assert not output or output.endswith("\n"), output
    for op in output.splitlines():
        assert op in OPS, op
        if op in ("sa", "ss") and len(a) > 1:
            a[0], a[1] = a[1], a[0]
        if op in ("sb", "ss") and len(b) > 1:
            b[0], b[1] = b[1], b[0]
        if op == "pa" and b:
            a.insert(0, b.pop(0))
        if op == "pb" and a:
            b.insert(0, a.pop(0))
        if op in ("ra", "rr") and len(a) > 1:
            a.append(a.pop(0))
        if op in ("rb", "rr") and len(b) > 1:
            b.append(b.pop(0))
        if op in ("rra", "rrr") and len(a) > 1:
            a.insert(0, a.pop())
        if op in ("rrb", "rrr") and len(b) > 1:
            b.insert(0, b.pop())
    return a, b


def check_probe(binary, values, mode="normal", memory=False):
    command = [str(binary), mode, *map(str, values)]
    if memory:
        command = ["valgrind", "--quiet", "--leak-check=full",
                   "--show-leak-kinds=all", "--errors-for-leak-kinds=all",
                   "--error-exitcode=99", *command]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, (values, result)
    ops = result.stdout.splitlines()
    expected_stats = [len(ops), *[ops.count(op) for op in ("sa", "pa", "pb", "ra", "rra")]]
    assert result.stderr == "COUNTERS " + " ".join(map(str, expected_stats)) + "\n", result
    if len(values) <= 5 and mode != "guard":
        assert replay(values, result.stdout) == (sorted(values), []), result
        assert len(ops) <= (0, 0, 1, 2, 6, 10)[len(values)], (values, result)
        if values == sorted(values):
            assert result.stdout == "", result
    else:
        assert result.stdout == "", result


def main():
    permutations = [list(p) for size in range(2, 6)
                    for p in itertools.permutations(range(size))]
    cases = [[], [0], *permutations]
    sources = [p for p in sorted((ROOT / "src").rglob("*.c")) if p.name != "main.c"]
    with tempfile.TemporaryDirectory(prefix="push-swap-small-") as temp:
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
            check_probe(binary, values)
            check_probe(binary, values, "ranks")
            for flag in ("", "--simple", "--medium", "--complex", "--adaptive"):
                args = [str(ROOT / "push_swap"), *([flag] if flag and values else []),
                        *map(str, values)]
                result = subprocess.run(args, capture_output=True, text=True)
                assert result.returncode == 0 and not result.stderr, result
                assert replay(values, result.stdout) == (sorted(values), []), result
                if values == sorted(values): assert not result.stdout, result
        for values in ([2147483647, -2147483648, 0, -1, 1],
                       [-2147483648, 2147483647], [30, -5, 10]):
            check_probe(binary, values)
        check_probe(binary, [5, 4, 3, 2, 1, 0])
        check_probe(binary, [2, 1, 0], "guard")
        for values in ([], [0], [1, 0], [2, 1, 0], [3, 2, 1, 0], [4, 3, 2, 1, 0]):
            check_probe(binary, values, memory=True)
    print("PASS: all 152 permutations (2–5), empty/singleton, all selectors,")
    print("rank-only sorting, per-command circular invariants/identity, exact counters,")
    print("independent stdout replay, no allocation/free; UBSan and 6 Valgrind paths")


if __name__ == "__main__":
    main()
