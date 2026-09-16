# Parsing module

`#include "parsing.h"` to use the module. It does not depend on stack operations.

```c
t_input input;

if (!parse_cli(argc, argv, &input))
{
    write(2, "Error\n", 6);
    return (1);
}
/* Use input.values[0..input.count-1] in original argument order. */
/* input.config.strategy defaults to ADAPTIVE; bench defaults to 0. */
input_clear(&input);
```

`parse_cli` returns 1 on success and 0 on invalid input or allocation failure.
The caller supplies a fresh `t_input`; it must call `input_clear` before reusing
an input that already owns an array. Failure frees the array and resets all
fields. Repeated `input_clear` calls are safe after parsing. The module itself
prints nothing, so the caller controls the single `Error\n` diagnostic.

No arguments succeeds with zero values. Flags without numbers are rejected.
Flags must occupy separate arguments, may appear before or after numbers, and
match exactly. At most one strategy selector and one `--bench` are accepted.
Numbers may be separate, quoted, or mixed. Space, tab, newline, vertical tab,
form feed, and carriage return are separators. Empty arguments, malformed
numbers, overflow, and numeric duplicates are rejected.

- `parse_cli.c`: initializes the result and coordinates counting, allocation,
  parsing, validation, and cleanup.
- `parse_flags.c`: recognizes selectors and benchmark mode.
- `token_count.c`: counts whitespace-delimited tokens without allocating.
- `parse_integer.c`: strictly converts decimal integers with overflow checks.
- `build_values.c`: fills one exact-size array, preserving order.
- `validate_input.c`: checks numeric duplicates in O(n²) time and O(1) extra space.

The existing `main.c` remains a skeleton. Building stack A from the validated
array and connecting parsing to `main` are integration steps once stack creation,
insertion, and cleanup are available. `t_data` is unchanged.

Run `python3 tests/test_parsing.py` from the repository root. The tests require
`cc`, Python 3, and Valgrind, and use a temporary standalone caller. They check
valid and invalid CLI inputs, original order, flags, integer limits, duplicates,
repeated cleanup, and allocation failure.
