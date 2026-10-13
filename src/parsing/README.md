# Parsing module

`parsing.h` uses the shared `t_strategy`, `t_config` and `t_data` definitions
from `push_swap.h`. There are no duplicate strategy or configuration types.

`parse_cli(argc, argv, &input)` fills a fresh `t_input` with one exact-size
values array, preserving input order. It returns 1 on success and 0 on invalid
input or allocation failure. Failure frees the array and resets the input.
Call `input_clear` after success and before reusing an input that owns memory.

`parse_input(argc, argv, &data)` requires a context initialized with `data_init`
and empty stacks. It validates the complete input before allocating any nodes,
builds A using `stack_add_bottom`, copies the requested configuration and frees
the temporary values array. B stays empty and every new node has rank -1.
On failure it releases the array and any partially built stack and resets data.
Both functions leave printing to the caller; main uses `error(&data)` exactly
once on failure. Repeated cleanup is safe after initialization or parsing.

No arguments succeeds with empty stacks. Flags without numbers fail. Flags
must occupy separate arguments and match exactly; they may precede or follow
numbers. At most one selector and one `--bench` are accepted. Default strategy
is ADAPTIVE. The effective sorting strategy is not selected by this module.

Separate, quoted and mixed numeric arguments are supported. Space and ASCII
whitespace from tab through carriage return are separators. Conversion checks
the int range before multiplying or adding. Numeric duplicates are rejected
by `validate_input` in O(n²) time and O(1) extra space. Ranking remains Stage 6.

`python3 tests/test_parsing.py` checks parsing, circular stack order, CLI output
and cleanup under ASan/UBSan, including failures at every allocation position
for a 16-node input. Add `--valgrind` to run with Valgrind instead. Test binaries
and allocation instrumentation are confined to a temporary directory.
