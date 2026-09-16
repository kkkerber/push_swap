"""Run with python3 tests/test_parsing.py; builds only the parsing module."""

import os
from pathlib import Path
import random
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PROBE = r'''
#include "parsing.h"
#include <assert.h>
#include <stdio.h>
#include <unistd.h>

void *__real_malloc(size_t size);

void *__wrap_malloc(size_t size)
{
    if (getenv("PARSER_FAIL_ALLOC"))
        return (NULL);
    return (__real_malloc(size));
}

int main(int argc, char **argv)
{
    t_input input;
    int success;
    int i;

    success = parse_cli(argc, argv, &input);
    if (success)
    {
        printf("%d %d %d", input.config.strategy,
            input.config.bench, input.count);
        i = 0;
        while (i < input.count)
            printf(" %d", input.values[i++]);
        printf("\n");
    }
    else
    {
        assert(input.values == NULL && input.count == 0);
        assert(input.config.strategy == ADAPTIVE);
        assert(input.config.bench == 0 && input.config.strategy_seen == 0);
        write(2, "Error\n", 6);
    }
    input_clear(&input);
    input_clear(&input);
    input_clear(NULL);
    assert(input.values == NULL && input.count == 0);
    assert(parse_cli(0, NULL, &input) == 0);
    assert(parse_cli(argc, argv, NULL) == 0);
    return (!success);
}
'''


def check(binary, args, expected, *, valgrind=False, fail_alloc=False):
    command = [str(binary), *args]
    if valgrind:
        command = [
            "valgrind", "--quiet", "--leak-check=full",
            "--show-leak-kinds=all", "--errors-for-leak-kinds=all",
            "--error-exitcode=99", *command,
        ]
    env = dict(os.environ)
    env.pop("PARSER_FAIL_ALLOC", None)
    if fail_alloc:
        env["PARSER_FAIL_ALLOC"] = "1"
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    if expected is None:
        assert (result.returncode, result.stdout, result.stderr) == (
            1, "", "Error\n"
        ), (args, result)
    else:
        assert result.returncode == 0 and not result.stderr, (args, result)
        assert list(map(int, result.stdout.split())) == expected, (args, result)


def main():
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
    with tempfile.TemporaryDirectory(prefix="push-swap-parser-") as temp:
        probe = Path(temp) / "probe.c"
        binary = Path(temp) / "probe"
        probe.write_text(PROBE)
        subprocess.run([
            "cc", "-Wall", "-Wextra", "-Werror", "-g",
            "-fsanitize=undefined", "-fno-sanitize-recover=all",
            "-I", str(ROOT / "includes"), str(probe),
            *map(str, sorted((ROOT / "src/parsing").glob("*.c"))),
            "-Wl,--wrap=malloc", "-o", str(binary),
        ], check=True)
        for args, expected in cases:
            check(binary, args, expected)
        memory_cases = [cases[0], cases[1], cases[4], (["1", "01"], None),
                        (["1", "2147483648"], None), (["--bench"], None)]
        for args, expected in memory_cases:
            check(binary, args, expected, valgrind=True)
        check(binary, ["1"], None, fail_alloc=True, valgrind=True)
        print(f"PASS: {len(cases)} parser cases; 7 Valgrind cases, including allocation failure")


if __name__ == "__main__":
    main()
