"""Stage 5: python3 tests/test_parsing.py [--valgrind]. Builds in a temp dir."""

import argparse
import os
from pathlib import Path
import random
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
ALLOCATOR = r'''
#include <assert.h>
#include <stdlib.h>

static int calls;
static int live;

void *test_malloc(size_t size)
{
    void *result;
    const char *fail = getenv("PARSER_FAIL_AT");

    if (fail && calls++ == atoi(fail))
        return NULL;
    if (!fail)
        calls++;
    result = malloc(size);
    if (result)
        live++;
    return result;
}

void test_free(void *ptr)
{
    if (ptr)
    {
        assert(live > 0);
        live--;
    }
    free(ptr);
}

int test_calls(void) { return calls; }
int test_live(void) { return live; }
'''

PROBE = r'''
#include "parsing.h"
#include <assert.h>
#include <stdio.h>

int test_calls(void);
int test_live(void);

static void check_empty(t_data *data)
{
    assert(!data->a.top && !data->a.bottom && data->a.size == 0);
    assert(!data->b.top && !data->b.bottom && data->b.size == 0);
    assert(data->config.requested_strategy == ADAPTIVE);
    assert(!data->config.strategy_set && !data->config.bench);
    assert(test_live() == 0);
}

int main(int argc, char **argv)
{
    t_data data;
    t_input input;
    t_node *node;
    int success, i;

    data_init(&data);
    success = parse_input(argc, argv, &data);
    assert(data.stats.total == 0 && !data.inversions && !data.pairs);
    assert(data.stats.sa == 0 && data.stats.sb == 0 && data.stats.ss == 0);
    assert(data.stats.pa == 0 && data.stats.pb == 0);
    assert(data.stats.ra == 0 && data.stats.rb == 0 && data.stats.rr == 0);
    assert(data.stats.rra == 0 && data.stats.rrb == 0 && data.stats.rrr == 0);
    assert(data.effective_strategy == ADAPTIVE);
    if (success)
    {
        assert(test_live() == data.a.size);
        assert(test_calls() == (data.a.size ? data.a.size + 1 : 0));
        assert(!data.b.top && !data.b.bottom && data.b.size == 0);
        if (data.a.size)
        {
            assert(data.a.top->prev == data.a.bottom);
            assert(data.a.bottom->next == data.a.top);
        }
        printf("%d %d %d", data.config.requested_strategy,
            data.config.bench, data.a.size);
        node = data.a.top;
        for (i = 0; i < data.a.size; i++)
        {
            assert(node && node->rank == -1);
            assert(node->next->prev == node && node->prev->next == node);
            assert(i == 0 || node != data.a.top);
            if (i == data.a.size - 1)
                assert(node == data.a.bottom);
            printf(" %d", node->value);
            node = node->next;
        }
        assert(node == data.a.top);
        printf("\n");
    }
    else
    {
        check_empty(&data);
        /* Invalid input is rejected before any nodes are allocated. */
        if (!getenv("PARSER_FAIL_AT"))
            assert(test_calls() <= 1);
        assert(error(&data) == 1);
    }
    data_clear(&data);
    data_clear(&data);
    check_empty(&data);
    assert(!parse_input(0, NULL, &data));
    assert(!parse_input(argc, argv, NULL));
    assert(!parse_cli(0, NULL, &input));
    assert(!parse_cli(argc, argv, NULL));
    input_clear(&input);
    input_clear(&input);
    input_clear(NULL);
    assert(!input.values && !input.count);
    assert(input.config.requested_strategy == ADAPTIVE);
    assert(!input.config.strategy_set && !input.config.bench);
    check_empty(&data);
    return !success;
}
'''


def check(binary, args, expected, *, memory=False, fail_at=None, app=False):
    command = [str(binary), *args]
    if memory:
        command = ["valgrind", "--quiet", "--leak-check=full",
                   "--show-leak-kinds=all", "--errors-for-leak-kinds=all",
                   "--error-exitcode=99", *command]
    env = dict(os.environ)
    env.pop("PARSER_FAIL_AT", None)
    if fail_at is not None:
        env["PARSER_FAIL_AT"] = str(fail_at)
    result = subprocess.run(command, capture_output=True, text=True,
                            env=env, timeout=30)
    if expected is None:
        assert (result.returncode, result.stdout, result.stderr) == (
            1, "", "Error\n"), (args, fail_at, result)
    else:
        assert result.returncode == 0 and not result.stderr, (args, result)
        if app:
            values = expected[3:]
            from test_small import replay
            assert replay(values, result.stdout) == (sorted(values), []), (args, result)
            if values == sorted(values):
                assert result.stdout == "", (args, result)
        else:
            assert list(map(int, result.stdout.split())) == expected, (args, result)


def cases_for_parser():
    cases = [
        ([], [3, 0, 0]),
        (["3", "2", "1"], [3, 0, 3, 3, 2, 1]),
        (["3 2", "1", "-5 +7"], [3, 0, 5, 3, 2, 1, -5, 7]),
        (["\t\n3\v2\f1\r "], [3, 0, 3, 3, 2, 1]),
        (["-2147483648", "2147483647"], [3, 0, 2, -2147483648, 2147483647]),
        (["-0"], [3, 0, 1, 0]),
        (["+0000005"], [3, 0, 1, 5]),
        (["0" * 2000 + "1"], [3, 0, 1, 1]),
        (["-" + "0" * 2000 + "2147483648"], [3, 0, 1, -2147483648]),
    ]
    for strategy, flag in enumerate(["--simple", "--medium", "--complex", "--adaptive"]):
        cases.extend([
            ([flag, "--bench", "2 1"], [strategy, 1, 2, 2, 1]),
            (["2", flag, "1", "--bench"], [strategy, 1, 2, 2, 1]),
            ([flag], None),
            ([flag, flag, "1"], None),
        ])
        for other in ["--simple", "--medium", "--complex", "--adaptive"]:
            cases.append(([flag, other, "1"], None))
    for arg in [
        "", " \t\r\n", "+", "-", "1a", "a1", "1.0", "1,2", "1+2",
        "--1", "+-1", "++1", "0x10", "2147483648", "-2147483649",
        "9" * 2000, "--unknown", "--simplex", "--bench=1", "--Bench",
        "--", "--simple 1", "1 --bench", "１", "1\u00a02",
    ]:
        cases.append(([arg], None))
    for args in [
        ["3", "03"], ["0", "-0"], ["5", "+5"], ["1 2", "2"],
        ["1", ""], ["1", "\t"], ["--bench"],
        ["--bench", "--bench", "1"], ["--bench", "--simple"],
    ]:
        cases.append((args, None))
    rng = random.Random(42)
    for _ in range(200):
        values = rng.sample(range(-1000000, 1000000), rng.randint(1, 100))
        args = []
        for start in range(0, len(values), 3):
            args.append("\t".join(map(str, values[start:start + 3])))
        cases.append((args, [3, 0, len(values), *values]))
        cases.append(([*args, str(values[0])], None))
    for count in (500, 1000, 1500):
        values = rng.sample(range(-100000, 100000), count)
        cases.append(([" ".join(map(str, values))], [3, 0, count, *values]))
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--valgrind", action="store_true")
    options = parser.parse_args()
    if options.valgrind and not shutil.which("valgrind"):
        parser.error("Valgrind is not installed")
    cases = cases_for_parser()
    sources = sorted((ROOT / "src/parsing").glob("*.c"))
    sources += sorted((ROOT / "src/stack").glob("*.c"))
    sources += sorted((ROOT / "src/core").glob("*.c"))
    sources += sorted((ROOT / "src/ranking").glob("*.c"))
    sources += sorted((ROOT / "src/analysis").glob("*.c"))
    sources += sorted((ROOT / "src/sorting").glob("*.c"))
    sources += sorted((ROOT / "src/operations").glob("*.c"))
    sources += sorted((ROOT / "ft_printf").glob("*.c"))
    flags = ["cc", "-Wall", "-Wextra", "-Werror", "-g",
             "-I", str(ROOT / "includes"), "-I", str(ROOT / "ft_printf")]
    if not options.valgrind:
        flags += ["-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
    with tempfile.TemporaryDirectory(prefix="push-swap-parser-") as tmp:
        tmp = Path(tmp)
        objects = []
        # Instrument project allocations only; no GNU linker extension needed.
        for i, source in enumerate(sources):
            obj = tmp / f"source_{i}.o"
            subprocess.run([*flags, "-Dmalloc=test_malloc", "-Dfree=test_free",
                            "-c", str(source), "-o", str(obj)], check=True)
            objects.append(str(obj))
        probe = tmp / "probe.c"
        allocator = tmp / "allocator.c"
        probe.write_text(PROBE)
        allocator.write_text(ALLOCATOR)
        binary = tmp / "probe"
        app = tmp / "push_swap"
        for output, entry in [(binary, probe), (app, ROOT / "src/main.c")]:
            subprocess.run([*flags, str(entry), str(allocator), *objects,
                            "-o", str(output)], check=True)
        for args, expected in cases:
            check(binary, args, expected, memory=options.valgrind)
            check(app, args, expected, memory=options.valgrind, app=True)
        # Fail the values array and every node allocation, including late failure.
        values = list(range(16))
        failure_args = ["--medium", "--bench", " ".join(map(str, values))]
        for fail_at in range(len(values) + 1):
            for output in (binary, app):
                check(output, failure_args, None, memory=options.valgrind,
                      fail_at=fail_at, app=(output == app))
        # The first allocation past the end must not be attempted.
        expected = [1, 1, len(values), *values]
        check(binary, failure_args, expected, memory=options.valgrind,
              fail_at=len(values) + 1)
        # Main owns one additional temporary array during ranking.
        check(app, failure_args, None, memory=options.valgrind,
              fail_at=len(values) + 1, app=True)
    mode = "Valgrind" if options.valgrind else "ASan/UBSan"
    print(f"PASS: {len(cases)} cases for parser/stack and main; "
          f"17 parser allocation failure positions plus ranking failure; {mode}; "
          "allocation balance, "
          "order, circular links, flags and exact error output")


if __name__ == "__main__":
    main()
