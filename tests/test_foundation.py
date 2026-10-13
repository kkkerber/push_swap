"""Stage 1/2 regression checks; all test binaries are built in /tmp."""

from pathlib import Path
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PROBE = r'''
#include "push_swap.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>

void *__real_malloc(size_t size);
void *__wrap_malloc(size_t size)
{
    static int allocations;

    if (getenv("FOUNDATION_FAIL_AFTER") && allocations++ == 3)
        return NULL;
    if (getenv("FOUNDATION_FAIL_ALLOC"))
        return NULL;
    return __real_malloc(size);
}

static void check_stack(t_stack *stack)
{
    t_node *node;
    int i;

    assert(stack->size >= 0);
    if (stack->size == 0)
    {
        assert(stack->top == NULL && stack->bottom == NULL);
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

static void check_defaults(t_data *data)
{
    check_stack(&data->a);
    check_stack(&data->b);
    assert(data->a.size == 0 && data->b.size == 0);
    assert(data->config.requested_strategy == ADAPTIVE);
    assert(data->config.strategy_set == 0 && data->config.bench == 0);
    assert(data->effective_strategy == ADAPTIVE);
    assert(data->inversions == 0 && data->pairs == 0);
    assert(data->stats.total == 0);
    assert(data->stats.sa == 0 && data->stats.sb == 0 && data->stats.ss == 0);
    assert(data->stats.pa == 0 && data->stats.pb == 0);
    assert(data->stats.ra == 0 && data->stats.rb == 0 && data->stats.rr == 0);
    assert(data->stats.rra == 0 && data->stats.rrb == 0 && data->stats.rrr == 0);
}

static void test_size(int count, int add_top)
{
    t_stack stack;
    t_node *nodes[1000];
    t_node *taken;
    int i;

    stack_init(&stack);
    check_stack(&stack);
    assert(stack_is_sorted(&stack));
    for (i = 0; i < count; i++)
    {
        nodes[i] = node_new(i);
        assert(nodes[i]);
        assert(nodes[i]->rank == -1);
        assert(nodes[i]->next == NULL && nodes[i]->prev == NULL);
        if (add_top)
            stack_add_top(&stack, nodes[i]);
        else
            stack_add_bottom(&stack, nodes[i]);
        assert(stack.size == i + 1);
        check_stack(&stack);
    }
    assert(stack_is_sorted(&stack) == (!add_top || count < 2));
    for (i = 0; i < count; i++)
    {
        taken = stack_take_top(&stack);
        assert(taken == nodes[add_top ? count - 1 - i : i]);
        assert(taken->next == NULL && taken->prev == NULL);
        assert(taken->rank == -1);
        free(taken);
        assert(stack.size == count - i - 1);
        check_stack(&stack);
    }
    assert(stack_take_top(&stack) == NULL);
    stack_clear(&stack);
    stack_clear(&stack);
    check_stack(&stack);
}

static void test_transfers(void)
{
    t_data data;
    t_node *model[2][1000];
    t_stack *stacks[2];
    int sizes[2] = {1000, 0};
    unsigned int seed = 42;
    int i, step, source, target, bottom;
    t_node *node;

    data_init(&data);
    stacks[0] = &data.a;
    stacks[1] = &data.b;
    for (i = 0; i < 1000; i++)
    {
        model[0][i] = node_new(i);
        assert(model[0][i]);
        model[0][i]->rank = i;
        stack_add_bottom(stacks[0], model[0][i]);
    }
    for (step = 0; step < 4000; step++)
    {
        seed = seed * 1664525u + 1013904223u;
        source = (seed >> 16) & 1;
        target = 1 - source;
        bottom = (seed >> 17) & 1;
        node = stack_take_top(stacks[source]);
        if (sizes[source] == 0)
            assert(node == NULL);
        else
        {
            assert(node == model[source][0]);
            assert(node->next == NULL && node->prev == NULL);
            sizes[source]--;
            memmove(model[source], model[source] + 1,
                (size_t)sizes[source] * sizeof(t_node *));
            if (bottom)
            {
                model[target][sizes[target]] = node;
                stack_add_bottom(stacks[target], node);
            }
            else
            {
                memmove(model[target] + 1, model[target],
                    (size_t)sizes[target] * sizeof(t_node *));
                model[target][0] = node;
                stack_add_top(stacks[target], node);
            }
            sizes[target]++;
        }
        assert(data.a.size + data.b.size == 1000);
        for (target = 0; target < 2; target++)
        {
            check_stack(stacks[target]);
            assert(stacks[target]->size == sizes[target]);
            node = stacks[target]->top;
            for (i = 0; i < sizes[target]; i++)
            {
                assert(node == model[target][i]);
                assert(node->rank == node->value);
                node = node->next;
            }
        }
    }
    data_clear(&data);
    data_clear(&data);
    check_defaults(&data);
}

int main(int argc, char **argv)
{
    t_data data;
    t_node *node;
    int sizes[] = {0, 1, 2, 3, 500, 1000};
    int i;

    data_init(&data);
    check_defaults(&data);
    if (getenv("FOUNDATION_FAIL_AFTER"))
    {
        for (i = 0; i < 10; i++)
        {
            node = node_new(i);
            if (!node)
            {
                assert(i == 3 && data.a.size == 3);
                assert(error(&data) == 1);
                check_defaults(&data);
                return 1;
            }
            stack_add_bottom(&data.a, node);
            check_stack(&data.a);
        }
        assert(0);
    }
    if (getenv("FOUNDATION_FAIL_ALLOC"))
    {
        assert(node_new(42) == NULL);
        return error(&data);
    }
    if (argc > 1 && strcmp(argv[1], "error") == 0)
    {
        stack_add_bottom(&data.a, node_new(1));
        stack_add_bottom(&data.a, node_new(2));
        stack_add_top(&data.b, node_new(3));
        assert(error(&data) == 1);
        check_defaults(&data);
        return 1;
    }
    data_init(NULL);
    data_clear(NULL);
    stack_init(NULL);
    stack_clear(NULL);
    stack_add_top(NULL, NULL);
    stack_add_bottom(NULL, NULL);
    stack_add_top(&data.a, NULL);
    stack_add_bottom(&data.a, NULL);
    assert(stack_take_top(NULL) == NULL && stack_is_sorted(NULL));
    for (i = 0; i < 6; i++)
    {
        test_size(sizes[i], 0);
        test_size(sizes[i], 1);
    }
    stack_add_bottom(&data.a, node_new(INT_MIN));
    stack_add_bottom(&data.a, node_new(INT_MAX));
    assert(stack_is_sorted(&data.a));
    node = stack_take_top(&data.a);
    stack_add_bottom(&data.a, node);
    assert(!stack_is_sorted(&data.a));
    data_clear(&data);
    data_clear(&data);
    check_defaults(&data);
    test_transfers();
    puts("PASS: circular stacks, identity/order, detach, defaults and cleanup");
    return 0;
}
'''


def run(binary, args=(), *, memory=False, fail_alloc=False, partial_alloc=False):
    command = [str(binary), *args]
    if memory:
        command = ["valgrind", "--quiet", "--leak-check=full",
                   "--show-leak-kinds=all", "--errors-for-leak-kinds=all",
                   "--error-exitcode=99", *command]
    env = dict(os.environ)
    env.pop("FOUNDATION_FAIL_ALLOC", None)
    env.pop("FOUNDATION_FAIL_AFTER", None)
    if fail_alloc:
        env["FOUNDATION_FAIL_ALLOC"] = "1"
    if partial_alloc:
        env["FOUNDATION_FAIL_AFTER"] = "1"
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    if args or fail_alloc or partial_alloc:
        assert (result.returncode, result.stdout, result.stderr) == (
            1, "", "Error\n"), result
    else:
        assert result.returncode == 0 and result.stderr == "", result
        assert result.stdout.startswith("PASS:"), result
    return result.stdout.strip()


def main():
    sources = sorted((ROOT / "src/stack").glob("*.c"))
    sources += sorted((ROOT / "src/core").glob("*.c"))
    with tempfile.TemporaryDirectory(prefix="push-swap-foundation-") as temp:
        probe = Path(temp) / "probe.c"
        binary = Path(temp) / "probe"
        probe.write_text(PROBE)
        subprocess.run(["cc", "-Wall", "-Wextra", "-Werror", "-g",
                        "-fsanitize=undefined", "-fno-sanitize-recover=all",
                        "-I", str(ROOT / "includes"),
                        "-I", str(ROOT / "ft_printf"), str(probe),
                        *map(str, sources), "-Wl,--wrap=malloc",
                        "-o", str(binary)], check=True)
        print(run(binary))
        run(binary, ["error"])
        run(binary, fail_alloc=True)
        run(binary, memory=True)
        run(binary, ["error"], memory=True)
        run(binary, memory=True, fail_alloc=True)
        run(binary, partial_alloc=True)
        run(binary, memory=True, partial_alloc=True)
        printf_probe = Path(temp) / "printf_probe.c"
        printf_probe.write_text('#include "ft_printf.h"\n'
                               'int main(void) { return ft_printf("%s", "") != 0; }\n')
        printf_binary = Path(temp) / "printf_probe"
        subprocess.run(["cc", "-Wall", "-Wextra", "-Werror",
                        "-I", str(ROOT / "ft_printf"), str(printf_probe),
                        str(ROOT / "ft_printf/libftprintf.a"),
                        "-o", str(printf_binary)], check=True)
        result = subprocess.run([str(printf_binary)], capture_output=True)
        assert (result.returncode, result.stdout, result.stderr) == (0, b"", b"")
    result = subprocess.run([str(ROOT / "push_swap")], capture_output=True)
    assert (result.returncode, result.stdout, result.stderr) == (0, b"", b"")
    print("PASS: UBSan; 4 Valgrind paths; stderr error contract; ft_printf link; empty main")


if __name__ == "__main__":
    main()
