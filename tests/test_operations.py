"""Stage 3 tests against a Python model; standalone probes build in /tmp."""

from pathlib import Path
import itertools
import random
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = {"a": "sa", "b": "sb", "s": "ss", "p": "pa", "q": "pb"}
PROBE = r'''
#include "push_swap.h"
#include <assert.h>
#include <stdio.h>

static int forbid_allocations;
void *__real_malloc(size_t size);
void __real_free(void *ptr);
void *__wrap_malloc(size_t size)
{
    assert(!forbid_allocations);
    return __real_malloc(size);
}
void __wrap_free(void *ptr)
{
    assert(!forbid_allocations);
    __real_free(ptr);
}

static void check_stack(t_stack *stack, t_node **nodes, int *seen, int count)
{
    t_node *node;
    int i, id;

    assert(stack->size >= 0 && stack->size <= count);
    if (!stack->size)
    {
        assert(!stack->top && !stack->bottom);
        return;
    }
    assert(stack->top && stack->bottom);
    assert(stack->top->prev == stack->bottom);
    assert(stack->bottom->next == stack->top);
    node = stack->top;
    for (i = 0; i < stack->size; i++)
    {
        assert(node && node->next && node->prev);
        assert(node->next->prev == node && node->prev->next == node);
        assert(i == 0 || node != stack->top);
        id = node->rank;
        assert(id >= 0 && id < count);
        assert(node == nodes[id] && node->value == id * 7 - 1000);
        assert(!seen[id]);
        seen[id] = 1;
        if (i == stack->size - 1)
            assert(node == stack->bottom);
        node = node->next;
    }
    assert(node == stack->top);
    node = stack->bottom;
    for (i = 0; i < stack->size; i++)
    {
        assert(i == 0 || node != stack->bottom);
        if (i == stack->size - 1)
            assert(node == stack->top);
        node = node->prev;
    }
    assert(node == stack->bottom);
}

static void check_data(t_data *data, t_node **nodes, int count)
{
    int seen[1000] = {0};
    int i;

    assert(data->a.size + data->b.size == count);
    check_stack(&data->a, nodes, seen, count);
    check_stack(&data->b, nodes, seen, count);
    for (i = 0; i < count; i++)
        assert(seen[i] == 1);
    assert(data->stats.ra == 0 && data->stats.rb == 0 && data->stats.rr == 0);
    assert(data->stats.rra == 0 && data->stats.rrb == 0 && data->stats.rrr == 0);
    assert(data->config.requested_strategy == ADAPTIVE);
    assert(!data->config.strategy_set && !data->config.bench);
    assert(!data->inversions && !data->pairs);
    assert(data->effective_strategy == ADAPTIVE);
}

static void dump(t_data *data)
{
    t_stack *stacks[2] = {&data->a, &data->b};
    t_node *node;
    int k, i;

    printf("STATE %llu %llu %llu %llu %llu %llu %d %d",
        data->stats.total, data->stats.sa, data->stats.sb,
        data->stats.ss, data->stats.pa, data->stats.pb,
        data->a.size, data->b.size);
    for (k = 0; k < 2; k++)
    {
        node = stacks[k]->top;
        for (i = 0; i < stacks[k]->size; i++)
        {
            printf(" %d", node->rank);
            node = node->next;
        }
    }
    printf("\n");
    fflush(stdout);
}

int main(int argc, char **argv)
{
    t_data data;
    t_node *nodes[1000];
    int count_a, count_b, count, i;
    char *command;

    assert(argc == 4);
    count_a = atoi(argv[1]);
    count_b = atoi(argv[2]);
    count = count_a + count_b;
    assert(count >= 0 && count <= 1000);
    data_init(&data);
    for (i = 0; i < count; i++)
    {
        nodes[i] = node_new(i * 7 - 1000);
        assert(nodes[i]);
        nodes[i]->rank = i;
        if (i < count_a)
            stack_add_bottom(&data.a, nodes[i]);
        else
            stack_add_bottom(&data.b, nodes[i]);
    }
    forbid_allocations = 1;
    sa(NULL); sb(NULL); ss(NULL); pa(NULL); pb(NULL);
    check_data(&data, nodes, count);
    dump(&data);
    command = argv[3];
    while (*command)
    {
        if (*command == 'a') sa(&data);
        else if (*command == 'b') sb(&data);
        else if (*command == 's') ss(&data);
        else if (*command == 'p') pa(&data);
        else if (*command == 'q') pb(&data);
        else assert(0);
        check_data(&data, nodes, count);
        dump(&data);
        command++;
    }
    forbid_allocations = 0;
    data_clear(&data);
    data_clear(&data);
    return 0;
}
'''


def expected_output(count_a, count_b, sequence):
    a = list(range(count_a))
    b = list(range(count_a, count_a + count_b))
    counters = dict.fromkeys(COMMANDS.values(), 0)
    lines = []

    def snapshot():
        values = [sum(counters.values()), *counters.values(), len(a), len(b), *a, *b]
        lines.append("STATE " + " ".join(map(str, values)))

    snapshot()
    for code in sequence:
        command = COMMANDS[code]
        changed = False
        if command in ("sa", "ss") and len(a) >= 2:
            a[0], a[1] = a[1], a[0]
            changed = True
        if command in ("sb", "ss") and len(b) >= 2:
            b[0], b[1] = b[1], b[0]
            changed = True
        if command == "pa" and b:
            a.insert(0, b.pop(0))
            changed = True
        if command == "pb" and a:
            b.insert(0, a.pop(0))
            changed = True
        if changed:
            lines.append(command)
            counters[command] += 1
        snapshot()
    return "\n".join(lines) + "\n"


def check(binary, count_a, count_b, sequence, *, memory=False):
    command = [str(binary), str(count_a), str(count_b), sequence]
    if memory:
        command = ["valgrind", "--quiet", "--leak-check=full",
                   "--show-leak-kinds=all", "--errors-for-leak-kinds=all",
                   "--error-exitcode=99", *command]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0 and not result.stderr, (command, result)
    assert result.stdout == expected_output(count_a, count_b, sequence), (
        count_a, count_b, sequence, result.stdout)


def main():
    sources = sorted((ROOT / "src/stack").glob("*.c"))
    sources += sorted((ROOT / "src/core").glob("*.c"))
    sources += sorted((ROOT / "src/operations").glob("*.c"))
    cases = []
    for a, b in itertools.product(range(5), repeat=2):
        for code in COMMANDS:
            cases.append((a, b, code))
        for sequence in ("ss", "ab", "aa", "bb", "qp", "pq", "q" * 8 + "p" * 8):
            cases.append((a, b, sequence))
    # Every three-command sequence for empty/singleton/two-node states.
    for a, b in itertools.product(range(3), repeat=2):
        for sequence in itertools.product(COMMANDS, repeat=3):
            cases.append((a, b, "".join(sequence)))
    rng = random.Random(42)
    for a, b in ((0, 0), (1, 0), (0, 1), (2, 2), (3, 5), (500, 500)):
        cases.append((a, b, "".join(rng.choices(list(COMMANDS), k=2000))))
    with tempfile.TemporaryDirectory(prefix="push-swap-operations-") as temp:
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
        for case in cases:
            check(binary, *case)
        for case in ((0, 0, "abs pq".replace(" ", "")),
                     (1, 0, "qpsqp"), (2, 2, "sabspq"), cases[-1]):
            check(binary, *case, memory=True)
    print(f"PASS: {len(cases)} model cases, exact output/counters, immediate output,")
    print("node identity/rank, circular invariants, no malloc/free in commands;")
    print("UBSan and 4 Valgrind paths")


if __name__ == "__main__":
    main()
