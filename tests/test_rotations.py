"""Stage 4: python3 tests/test_rotations.py [--valgrind]."""

import argparse
from pathlib import Path
import random
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
OPS = ("ra", "rb", "rr", "rra", "rrb", "rrr")
PROBE = r'''
#include "push_swap.h"
#include <assert.h>

static void build(t_stack *stack, t_node **nodes, int size, int base)
{
    int i;

    for (i = 0; i < size; i++)
    {
        nodes[i] = node_new(base + i);
        assert(nodes[i]);
        nodes[i]->rank = base + i;
        stack_add_bottom(stack, nodes[i]);
    }
}

static void check(t_stack *stack, t_node **nodes, int size, int offset,
    int base)
{
    t_node *node;
    int i;

    assert(stack->size == size);
    if (!size)
    {
        assert(!stack->top && !stack->bottom);
        return;
    }
    assert(stack->top == nodes[offset]);
    assert(stack->bottom == nodes[(offset + size - 1) % size]);
    node = stack->top;
    for (i = 0; i < size; i++)
    {
        assert(node == nodes[(offset + i) % size]);
        assert(node->value == base + (offset + i) % size);
        assert(node->rank == node->value);
        assert(node->next->prev == node && node->prev->next == node);
        node = node->next;
    }
    assert(node == stack->top);
    node = stack->bottom;
    for (i = 0; i < size; i++)
        node = node->prev;
    assert(node == stack->bottom);
}

int main(int argc, char **argv)
{
    t_data data;
    t_node *nodes[2][1000];
    void (*ops[6])(t_data *) = {ra, rb, rr, rra, rrb, rrr};
    unsigned long long *counters[6];
    unsigned long long expected[6] = {0};
    unsigned long long total = 0;
    int sizes[2], offset[2] = {0, 0};
    int i, j, op, changed, affected;

    assert(argc == 4);
    sizes[0] = atoi(argv[1]);
    sizes[1] = atoi(argv[2]);
    assert(sizes[0] >= 0 && sizes[0] <= 1000);
    assert(sizes[1] >= 0 && sizes[1] <= 1000);
    data_init(&data);
    build(&data.a, nodes[0], sizes[0], -2000);
    build(&data.b, nodes[1], sizes[1], 2000);
    counters[0] = &data.stats.ra;
    counters[1] = &data.stats.rb;
    counters[2] = &data.stats.rr;
    counters[3] = &data.stats.rra;
    counters[4] = &data.stats.rrb;
    counters[5] = &data.stats.rrr;
    /* Existing Stage 3 counters must survive every rotation. */
    data.stats.sa = 1;
    data.stats.sb = 2;
    data.stats.ss = 3;
    data.stats.pa = 4;
    data.stats.pb = 5;
    data.stats.total = 15;
    for (i = 0; i < 6; i++)
        ops[i](NULL);
    for (i = 0; argv[3][i]; i++)
    {
        op = argv[3][i] - '0';
        assert(op >= 0 && op < 6);
        changed = 0;
        for (j = 0; j < 2; j++)
        {
            affected = (op % 3 == j || op % 3 == 2);
            if (affected && sizes[j] > 1)
            {
                offset[j] = (offset[j] + (op < 3 ? 1 : sizes[j] - 1))
                    % sizes[j];
                changed = 1;
            }
        }
        ops[op](&data);
        expected[op] += changed;
        total += changed;
        check(&data.a, nodes[0], sizes[0], offset[0], -2000);
        check(&data.b, nodes[1], sizes[1], offset[1], 2000);
        for (j = 0; j < 6; j++)
            assert(*counters[j] == expected[j]);
        assert(data.stats.total == 15 + total);
        assert(data.stats.sa == 1 && data.stats.sb == 2);
        assert(data.stats.ss == 3 && data.stats.pa == 4 && data.stats.pb == 5);
    }
    data_clear(&data);
    assert(!data.a.top && !data.b.top);
    return 0;
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--valgrind", action="store_true")
    args = parser.parse_args()
    if args.valgrind and not shutil.which("valgrind"):
        parser.error("Valgrind is not installed")
    sources = sorted((ROOT / "src/core").glob("*.c"))
    sources += sorted((ROOT / "src/stack").glob("*.c"))
    sources += [ROOT / "src/operations" / name for name in
                ("rotate.c", "reverse_rotate.c")]
    sources += sorted((ROOT / "ft_printf").glob("*.c"))
    rng = random.Random(42)
    # Inverses, full cycles, then a reproducible mixed sequence.
    sequence = "031425" + "0" * 1000 + "3" * 1000
    sequence += "1" * 1000 + "4" * 1000 + "2" * 1000 + "5" * 1000
    sequence += "".join(str(rng.randrange(6)) for _ in range(1000))
    sizes = (0, 1, 2, 3, 5, 500, 1000)
    with tempfile.TemporaryDirectory(prefix="push-swap-rotations-") as tmp:
        probe = Path(tmp) / "probe.c"
        binary = Path(tmp) / "probe"
        probe.write_text(PROBE)
        flags = [] if args.valgrind else [
            "-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
        subprocess.run([
            "cc", "-Wall", "-Wextra", "-Werror", "-g", *flags,
            "-I", str(ROOT / "includes"), "-I", str(ROOT / "ft_printf"),
            str(probe), *map(str, sources), "-o", str(binary),
        ], check=True)
        for a in sizes:
            for b in sizes:
                expected = []
                for token in sequence:
                    op = int(token)
                    if ((op % 3 in (0, 2) and a > 1)
                            or (op % 3 in (1, 2) and b > 1)):
                        expected.append(OPS[op] + "\n")
                command = [str(binary), str(a), str(b), sequence]
                if args.valgrind:
                    command = ["valgrind", "--quiet", "--leak-check=full",
                               "--show-leak-kinds=all",
                               "--errors-for-leak-kinds=all",
                               "--error-exitcode=99", *command]
                result = subprocess.run(command, capture_output=True, text=True)
                assert result.returncode == 0, (a, b, result.stderr)
                assert result.stderr == "", (a, b, result.stderr)
                assert result.stdout == "".join(expected), (a, b, "stdout")
    mode = "Valgrind" if args.valgrind else "ASan/UBSan"
    print(f"PASS: 49 size pairs, {49 * len(sequence)} operations; {mode}; "
          "order, identity, ranks, links, no-op, counters and exact stdout")


if __name__ == "__main__":
    main()
