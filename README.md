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
Stage 7 counts original-input inversions and total pairs after ranking and before
any operation. Adaptive selects Simple below 20%, Medium from 20% to below 50%,
and Complex from 50%. Empty/singleton input has zero disorder. Explicit selectors
are preserved; requested and effective strategies are stored separately.
Threshold comparisons use integer ceilings without floating point or multiplying
counters. Analysis takes O(n²) time and O(1) extra space.
Stage 8 sorts inputs of up to five elements by rank using only public commands.
For three nodes it moves the maximum to the bottom and swaps the first two if
needed. For four/five it moves minima to B using shortest rotations, sorts three
and returns the minima with pa. Already sorted input emits nothing.
The small-sort API requires assigned ranks and empty B; unsupported sizes or a
nonempty B are left untouched. Strategies for larger inputs and benchmark output
are not implemented yet: larger valid inputs currently produce no operations.
Invalid inputs print `Error` to stderr and return 1.

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

Run `python3 tests/test_analysis.py` for Stage 7 pair counts, exhaustive small
permutations, exact thresholds, explicit selectors, mutation and memory checks.

Run `python3 tests/test_small.py` for all 152 permutations of sizes 2–5,
per-command invariants, rank-only decisions, independent output replay and memory
checks. Inputs up to five elements now emit sorting operations; all selectors
share this small-sort base case.

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
AI assistance implemented Stage 7 inversion counting and integer strategy
selection, explained the thresholds and added independent-model tests.
AI assistance implemented Stage 8 small sort, explained the maximum/minimum
steps and added exhaustive permutations and command-stream regression tests.
The learners should review and explain these changes before merging.
