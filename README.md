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
nonempty B are left untouched. Stage 9 implements Simple for arbitrary sizes:
it finds the minimum rank, rotates it to the top by the shortest direction,
pushes it to B and repeats, then restores all nodes with pa. Sizes up to five
use the shared small sort. Simple uses O(n²) time/operations and O(1) extra space;
it allocates/frees no nodes. `--simple` works at every disorder level. Adaptive
uses it only below 20% disorder.
Stage 10 implements Medium with rank chunks of width floor(sqrt(n)), computed
using integer division. It selects the first remaining rank in the current
chunk in forward circular order and brings that node to the top using the
shortest rotation direction. Lower ranks in the chunk are rotated deeper into
B; higher ranks stay near the top. Pending rb is combined with forward A
rotation as rr. For two nodes in B, reverse rotation has the same effect as rb,
so it combines with reverse A rotation as rrr. Returning nodes always brings
the maximum rank in B to the top by the shortest direction before pa.

For width w, extracting each chunk needs at most one forward sweep of A;
reverse shortcuts cannot cost more than that sweep. Extraction therefore uses
O(n²/w) commands. Each chunk forms two blocks around the older contents of B;
its maxima can be reached from either end within O(w) rotations, giving O(nw)
return commands. With w = floor(sqrt(n)), the command count is O(n√n).
List searches can still take O(n²) CPU time; the subject measures complexity
in generated commands. Medium needs O(1) extra space and no allocation/free.
It requires dense assigned ranks 0..n-1 and empty B, and delegates sizes <= 5
to small sort. `--medium` is preserved at every disorder level; Adaptive uses
Medium from 20% to below 50%.

Stage 11 implements Complex using binary LSD radix on ranks. The maximum rank
determines the number of bit passes. Each pass processes exactly the initial
size of A: zero bits move to B with pb, one bits rotate A with ra. Returning
all of B with pa restores the order of the zero-bit group, so each pass is
stable. The next pass sorts by the next more significant bit.
For dense ranks 0..n-1, there are ceil(log2(n)) passes, each using at most 2n
commands: O(n log n) time/commands and O(1) extra space for the sorting phase.
Ranking and disorder preprocessing retain their separate O(n²) time costs.
Complex allocates/frees no nodes, preserves values/ranks and delegates sizes
up to five to small sort. Sorted input emits nothing. Explicit `--complex`
always selects Complex; Adaptive selects it at disorder >= 50%.
Stage 12 centralizes sorting in `sort_dispatch`, called by main after ranking
and original-input disorder analysis. The dispatcher records the effective
strategy before returning for empty or sorted input, delegates sizes <= 5 to
small sort, and preserves explicit selectors. Adaptive calls `sort_adaptive`,
which reuses Stage 7's integer threshold selection and runs the selected
algorithm. Default input and explicit `--adaptive` follow the same path.
Requested strategy, original inversions and total pairs remain unchanged;
the effective strategy identifies the selected family even when small sort
handles the input. Both entry points require assigned dense ranks, empty B
and previously computed disorder. They allocate no memory; a nonempty B is
left untouched.
Stage 13 prints a benchmark after sorting when `--bench` is enabled. It reports
original disorder rounded to two decimal places, requested/effective strategies,
the effective strategy family's theoretical command complexity, total commands
and all eleven counters. Small sort keeps the selected family in the report.
Output uses write to stderr without allocation; stdout remains the same command
stream as without --bench. Counters retain their full unsigned long long range.
Stage 14 completes main integration: initialize, return silently for no arguments,
parse/validate and build A, assign ranks, measure original disorder, dispatch,
print the optional benchmark, then clear memory. Parsing and validation remain
inside the parser; main only coordinates modules. Failures use the shared error
path to clear partial state, print `Error` to stderr and return 1.

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

Run `python3 tests/test_simple.py` for Simple at sizes through 1000, selector
behavior, shortest rotations, rank-only sorting, counters, ownership and memory
checks. For example: `./push_swap --simple "6 3 1 5 2 4"`.

Run `python3 tests/test_medium.py` for all permutations of sizes 2–6, patterns
through 1500 elements, explicit/Adaptive routing, independent command replay,
per-command invariants and allocation guards with ASan/UBSan. Add `--valgrind`
to use Valgrind instead. The test also checks 100 random 100-element inputs
below 1500 commands and 50 random 500-element inputs below 8000 commands.
For example: `./push_swap --medium "6 3 1 5 2 4"`.

Run `python3 tests/test_complex.py` for all permutations of sizes 0–6, exact
radix command sequences, power-of-two boundaries, patterns through 1500,
rank-only decisions, per-command links/ownership/counters and allocation guards
with ASan/UBSan. Add `--valgrind` to use Valgrind instead. A standalone probe
also checks sparse nonnegative ranks through INT_MAX to verify dynamic bit
counting. The CLI still assigns dense ranks. Twenty random inputs at each of
100 and 500 elements use 1084 and 6784 commands respectively.
For example: `./push_swap --complex "6 3 1 5 2 4"`.

Run `python3 tests/test_dispatch.py` for Stage 12 selector routing, exact
20%/50% boundaries and adjacent inversion counts, all permutations of sizes
0–5 under every selector, and patterns through 1000 elements. Direct API
checks preserve requested/effective strategies, original metrics, node
identity, ranks, circular links and operation counters, including repeated
sorting and nonempty-B guards. The suite uses ASan/UBSan by default; add
`--valgrind` for Valgrind checks.

CLI accepts separate integers (`./push_swap 3 2 1`), quoted strings
(`./push_swap "3 2 1"`) and mixed input (`./push_swap "3 2" 1`). Select at most
one of `--simple`, `--medium`, `--complex`, `--adaptive` (default), plus at most
one `--bench`. Flags occupy separate arguments and can appear before or after
numbers. Strategy selection uses original-input disorder. For example:
`./push_swap --adaptive --bench "6 3 1 5 2 4"`.
Redirect commands and metrics separately with `> operations.txt 2> benchmark.txt`.
Empty strings, whitespace-only arguments, malformed integers, overflow, numeric
duplicates, unknown/repeated flags and flags without numbers are rejected.

Run `python3 tests/test_benchmark.py` for Stage 13 percentage rounding, selector
metadata, independent command replay and counter comparison, output separation
and ordering, zero-operation input, errors, and full-width counter formatting.

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
AI assistance implemented Stage 9 minimum extraction, shared rank search with
small sort, and added arbitrary-size and selector regression tests.
AI assistance implemented Stage 10 dynamic chunks and combined rotations,
documented the command-count bound and added Medium regression tests.
AI assistance implemented Stage 11 radix sorting and CLI integration, reused
the Medium invariant probe and added exact-model and bit-boundary tests.
AI assistance implemented Stage 12 Adaptive/dispatcher integration and added
selector, threshold, metadata-preservation and direct API regression checks.
AI assistance implemented Stage 13 stderr benchmark formatting and added
command-stream, counter, rounding and metadata regression checks.
AI assistance completed Stage 14 main coordination and verified the integrated
CLI, error cleanup and benchmark paths with existing regression suites.
The learners should review and explain these changes before merging.
