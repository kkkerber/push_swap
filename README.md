*This project has been created as part of the 42 curriculum by maliuten, vakhapil.*

# push_swap

## Description

Stage 1/2 foundation and Stage 3 swap/push commands for Push_swap. Stacks are circular doubly
linked lists with cached top, bottom and size. Traversals are bounded by size.
Nodes start detached with rank -1. Taking a node transfers ownership to the
caller; clearing a stack frees its nodes. Initialize data before using or
clearing it, including after a partially completed stack construction.

The public commands `sa`, `sb`, `ss`, `pa` and `pb` are implemented. Each
command changes the stacks, prints its name immediately and updates its own
counter and the total. No-ops print and count nothing. `ss` changes each eligible
stack directly and prints/counts once. Push moves existing nodes without
allocation or freeing. Rotation commands, parsing, ranking, sorting and benchmark
output are not implemented.
The current executable initializes and clears its context without output.

## Instructions

Run `make` to build, then `./push_swap` for the empty lifecycle smoke check.
Run `make clean`, `make fclean` or `make re` for build cleanup/rebuild.
The existing ft_printf library is built and linked through its own Makefile.
Run `python3 tests/test_foundation.py` for stack and lifecycle tests, including
Valgrind memory checks. Run `python3 tests/test_operations.py` for Stage 3
commands checked against an independent model, exact output/counters, circular
links, ownership and unchanged values/ranks. The tests require Python 3, cc
and Valgrind.

## Resources

- Team development plan: https://docs.google.com/document/d/1PUejcCwN77Q7NWbvMKPuRhWws-oXIzLYB7asaUVcJbo/edit
- `man 3 malloc`, `man 3 free`, `man 2 write`.

## Contributions and AI usage

The repository history records contributions by both learners. Existing stack
code was retained; AI assistance helped prepare the Stage 1/2 lifecycle,
correct singleton extraction, normalize formatting and add regression tests.
AI assistance also implemented and tested the Stage 3 commands using the
existing stack primitives and direct per-command output/counters.
The learners should review and explain these changes before merging.
