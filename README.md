*This project has been created as part of the 42 curriculum by maliuten, vakhapil.*

# push_swap

## Description

Stage 1/2 foundation and Stage 3/4 commands for Push_swap. Stacks are circular
doubly linked lists with cached top, bottom and size. Traversals are bounded by size.
Nodes start detached with rank -1. Taking a node transfers ownership to the
caller; clearing a stack frees its nodes. Initialize data before using or
clearing it, including after a partially completed stack construction.

The public commands `sa`, `sb`, `ss`, `pa` and `pb` are implemented. Each
command changes the stacks, prints its name immediately and updates its own
counter and the total. No-ops print and count nothing. `ss` changes each eligible
stack directly and prints/counts once. Push moves existing nodes without
allocation or freeing. Stage 4 rotations (`ra`, `rb`, `rr`, `rra`, `rrb`, `rrr`)
are also implemented with direct output and counters. Stage 5 parses and
validates CLI arguments, then builds stack A in input order with B empty.
Stage 6 assigns ranks after parsing: the minimum receives 0 and the maximum
receives n - 1. It sorts a temporary copy using insertion sort, checks adjacent
duplicates, then finds each node value in that copy. Values, node order and
circular links stay unchanged. Ranking takes O(n²) time and O(n) temporary
space; allocation failure or duplicates leave ranks untouched.
Sorting the stacks and benchmark output are not implemented yet: valid inputs
currently produce no output, invalid inputs print `Error` to stderr and return 1.

## Instructions

Run `make` to build, then `./push_swap` for the empty lifecycle smoke check.
Run `make clean`, `make fclean` or `make re` for build cleanup/rebuild.
The existing ft_printf library is built and linked through its own Makefile.
Run `python3 tests/test_foundation.py` for stack and lifecycle tests, including
Valgrind memory checks. Run `python3 tests/test_operations.py` for Stage 3
commands checked against an independent model, exact output/counters, circular
links, ownership and unchanged values/ranks. The tests require Python 3, cc
and Valgrind.
Run `python3 tests/test_rotations.py` for Stage 4 checks with ASan/UBSan, or
`python3 tests/test_rotations.py --valgrind` for Valgrind memory checks.
Run `python3 tests/test_parsing.py` for Stage 5 parser, stack construction and
main checks with ASan/UBSan, or add `--valgrind` for Valgrind checks. These tests
also force failure of the values array, each allocation in a 16-node stack,
and the ranking array used by main.
Run `python3 tests/test_ranking.py` for Stage 6 ranks, integer boundaries,
duplicate/allocation failure, unchanged nodes and links, UBSan and Valgrind.

CLI accepts separate integers (`./push_swap 3 2 1`), quoted strings
(`./push_swap "3 2 1"`) and mixed input (`./push_swap "3 2" 1`). Select at most
one of `--simple`, `--medium`, `--complex`, `--adaptive` (default), plus at most
one `--bench`. Flags occupy separate arguments and can appear before or after
numbers. Strategy and benchmark flags are stored for the later sorting stages.
Empty strings, whitespace-only arguments, malformed integers, overflow, numeric
duplicates, unknown/repeated flags and flags without numbers are rejected.

## Resources

- Team development plan: https://docs.google.com/document/d/1PUejcCwN77Q7NWbvMKPuRhWws-oXIzLYB7asaUVcJbo/edit
- `man 3 malloc`, `man 3 free`, `man 2 write`.

## Contributions and AI usage

The repository history records contributions by both learners. Existing stack
code was retained; AI assistance helped prepare the Stage 1/2 lifecycle,
correct singleton extraction, normalize formatting and add regression tests.
AI assistance also implemented and tested the Stage 3 commands using the
existing stack primitives and direct per-command output/counters.
Stage 5 reuses the standalone parser from `origin/feature/parsing` (`ffdc674`);
AI assistance adapted its configuration types, integrated stack construction
and added portable allocation-failure and CLI regression checks.
AI assistance implemented Stage 6 ranking, explained the temporary-array
approach and added rank, ownership and allocation-failure regression tests.
The learners should review and explain these changes before merging.
