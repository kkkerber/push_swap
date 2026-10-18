*This project has been created as part of the 42 curriculum by maliuten, vakhapil.*

# push_swap

## Description

Push_swap generates commands that sort a stack of distinct C integers using a
second stack and eleven allowed operations. The first input integer is the top
of A; B starts empty. The result is ascending A (minimum on top) and empty B.
This repository implements the mandatory part of subject version 1.1, with
Simple, Medium, Complex and default Adaptive selectors.

The implementation uses circular doubly linked stacks, immutable ranks,
original-input inversion analysis and direct public operations. The program
writes commands to stdout, errors and optional benchmark metrics to stderr.

## Instructions

Build with a C compiler and Make:

```sh
make
./push_swap 3 2 1
./push_swap "3 2" 1
./push_swap --medium "6 3 1 5 2 4"
./push_swap --adaptive --bench "6 3 1 5 2 4"
```

`make` uses `cc -Wall -Wextra -Werror`. The bundled `ft_printf` is built with
its own Makefile and linked as `ft_printf/libftprintf.a`; no external library
installation is needed. Its `ft_printf` prints operation names immediately.
Header dependencies are tracked and an unchanged `make` does not relink.
`make clean` removes objects, `make fclean` also removes the executable/library,
and `make re` rebuilds everything.

Input can mix separate arguments and whitespace-separated quoted strings.
Each token must be an optional single sign followed by decimal digits, within
`INT_MIN..INT_MAX`. Numeric duplicates are rejected (`3`/`03`, `0`/`-0`,
`5`/`+5`). Negative integers are numbers. Flags match whole arguments exactly
and can precede or follow numbers.

| Option | Behavior |
| --- | --- |
| `--simple` | Minimum extraction at every disorder level |
| `--medium` | Dynamic rank chunks at every disorder level |
| `--complex` | Binary LSD radix at every disorder level |
| `--adaptive` | Choose a family from original disorder; default |
| `--bench` | Print metrics after sorting to stderr |

At most one selector and one `--bench` are accepted. Unknown/repeated flags,
flags without numbers, empty/whitespace-only arguments, malformed integers,
overflow and duplicates return status 1 with exactly `Error\n` on stderr and
no stdout. No arguments return status 0 without output. Valid sorted input
emits no commands; with `--bench`, it still reports metrics.

### Benchmark

```sh
./push_swap --adaptive --bench "6 3 1 5 2 4" > operations.txt 2> benchmark.txt
```

The report contains original disorder rounded to two decimal places,
requested and effective strategy, the effective family's theoretical command
complexity, total operations and all eleven counters. For this example,
disorder is `60.00%`, requested strategy is Adaptive and effective is Complex.
The three complexity labels are `O(n^2)`, `O(n*sqrt(n))` and `O(n log n)`.
For size <= 5, metrics retain the selected family although small sort runs.
The counter sum equals the total; a combined command counts once. Formatting
uses `write(2, ...)`, supports unsigned long long counters and allocates no
memory. The command stream is identical with and without `--bench`.

## Data structures and ownership

`t_node` holds `value`, `rank`, `prev` and `next`; `t_stack` holds `top`,
`bottom` and `size`. Empty stacks have null endpoints and size 0. A singleton
points to itself. Otherwise `top->prev == bottom` and `bottom->next == top`.
Every node satisfies `next->prev == node` and `prev->next == node`.
Traversals are bounded by size because the links never reach NULL.

Nodes are allocated once. `stack_take_top` detaches without freeing and resets
both links to NULL. `pa`/`pb` move those same nodes without allocation/free.
`stack_clear` frees exactly the original size and resets both endpoints/size;
cleanup also handles empty and partially constructed states.

### Operations

| Command | Effect |
| --- | --- |
| `sa` | Swap the first two nodes of A |
| `sb` | Swap the first two nodes of B |
| `ss` | Swap the first two nodes of each eligible stack |
| `pa` | Move B's top node to A's top |
| `pb` | Move A's top node to B's top |
| `ra` | Move A's top to its bottom |
| `rb` | Move B's top to its bottom |
| `rr` | Rotate both stacks forward |
| `rra` | Move A's bottom to its top |
| `rrb` | Move B's bottom to its top |
| `rrr` | Reverse rotate both stacks |

Each public operation checks eligibility, mutates the stack, prints its own
name and updates its counter/total. No-ops print/count nothing. Combined
operations modify each eligible stack directly and print/count once if either
changes; they never call their public single-stack counterparts. Rotations
only move the cached endpoints through circular links.

## Ranking, disorder and routing

After CLI validation, A is built in input order. Ranking sorts a temporary
value copy with insertion sort, checks adjacent duplicates defensively and
assigns each node its index in that copy. For input `[42, -7, 0]`, ranks are
`[2, 0, 1]`. Values and node order stay unchanged. Minimum rank is 0 and maximum
is n-1. Rank is fixed across operations and differs from current stack position.
The temporary array is freed; ranking failure leaves ranks unassigned.

Before any operation, analysis stores inversions and total pairs:

```text
inversions = number of pairs i < j with value[i] > value[j]
pairs = n * (n - 1) / 2
disorder = inversions / pairs   (0 for n < 2)
```

Adaptive compares integer counts with ceiling thresholds, avoiding division
by zero, floating-point boundary decisions and multiplication of counters.

| Original disorder | Effective family | Command complexity |
| --- | --- | --- |
| `< 0.2` | Simple | O(n²) |
| `>= 0.2` and `< 0.5` | Medium | O(n√n) |
| `>= 0.5` | Complex | O(n log n) |

The dispatcher records the effective family, skips sorted input, uses shared
small sort for size <= 5, then runs the selected algorithm. Explicit selectors
are preserved. Original metrics and requested strategy stay unchanged.
`main` only coordinates initialization, empty execution, parsing/validation,
ranking, disorder, dispatch, optional benchmark and cleanup.

## Algorithms and complexity arguments

The subject's complexity model counts generated Push_swap commands. CPU time
and preprocessing are separate: CLI duplicate validation, ranking and disorder
each take O(n²) time. Ranking needs O(n) temporary storage; the stacks themselves
use O(n) nodes. Sorting allocates no nodes and uses O(1) extra storage.

### Small sort

Zero/one element requires nothing; two use `sa` only if needed. For three,
move the maximum to the bottom with `ra` or `rra`, then swap the first two
if needed. For four/five, extract minimum ranks to B by shortest rotations,
sort three and restore with `pa`. Minima return in ascending order. All 152
permutations for sizes 2–5 are tested. These fixed cases take O(1) commands.

### Simple: minimum extraction

Find A's minimum rank, rotate it to the top by the shorter direction and `pb`.
Repeat until A is empty, then restore everything with `pa`. Extracted minima
accumulate in descending order in B, so restoring them produces ascending A.
At remaining size k, extraction costs at most floor(k/2) rotations and a push;
summing over k gives O(n²) commands. Minimum searches also take O(n²) CPU time.
This strategy is straightforward to explain and implements the required
quadratic family; low inversion count does not guarantee a small command count.

### Medium: dynamic chunks

Use chunk width w = floor(sqrt(n)), computed dynamically with integer division.
For each rank interval, select the first eligible node in forward circular
order and bring that node to the top by the shortest direction. Push it to B;
lower ranks are buried with a pending `rb`, while higher ranks stay near the
top. Combine that pending rotation with a forward A rotation using direct `rr`.
For a two-node B, `rrb` has the same effect as `rb`, allowing direct `rrr` with
a reverse A rotation. Restore by moving B's maximum to the top via the shorter
direction, then `pa`.

Extracting a chunk needs at most a forward sweep of A; reverse shortcuts cost
no more than that sweep. Across chunks this gives O(n²/w) commands. Each chunk
forms two blocks around older B contents; successive maxima are accessible
within O(w) rotations, giving O(nw) restoration commands. Taking w ≈ √n yields
O(n√n). Linked-list searches can still require O(n²) CPU time. The width works
for arbitrary valid input sizes and uses no 100/500-specific cases.

### Complex: binary LSD radix

Compute the bit count from the maximum rank. For each bit, process exactly
the pass's original A size: zero goes to B with `pb`, one stays in A through
`ra`. Return all B with `pa`. Rotating the ones preserves their order, and
the two transfers reverse the zero group twice, preserving its order too.
After each stable pass, ranks are sorted by all bits processed so far.
After all bits, ranks and therefore values are sorted.

Dense ranks need ceil(log2(n)) passes, each with at most 2n commands, giving
O(n log n) sorting commands/time. This avoids sign handling and dependence on
raw integer magnitude. The complete program retains O(n²) preprocessing time.

### Adaptive and measured limits

Adaptive follows the prescribed disorder thresholds above, sharing the same
algorithms and small sort. It does not promise the fewest commands on each
input. Stage 15 ran 1000 random inputs of size 100 and 500 of size 500 per
selector, with independent command replay before counting.

| Strategy | Maximum at 100 | Maximum at 500 |
| --- | ---: | ---: |
| Simple | 1724 | 35503 |
| Medium | 800 | 7609 |
| Complex | 1084 | 6784 |
| Adaptive | 1084 | 7555 |

Medium, Complex and Adaptive met internal random-series targets (<1500/<8000).
Explicit Simple exceeds those budgets and the mandatory 500-element budget
in these samples. Measurements do not prove bounds for all permutations.

## Testing

Test tools: Python 3, `cc`, Valgrind, Norminette and compiler sanitizer support.
The Python checker replays commands independently; no official checker binary
is bundled. Probes build in temporary directories. Run tests from the root:

```sh
make
python3 tests/test_benchmark.py
python3 tests/test_performance.py --replay docs/performance_stage15.json --valgrind
norminette src includes ft_printf
```

| Test file in `tests/` | Coverage |
| --- | --- |
| `test_foundation.py` | Lifecycle, stack invariants, ownership, memory |
| `test_operations.py` | Swap/push, no-ops, direct combinations, output/counters |
| `test_rotations.py` | All rotations, links, combined counts |
| `test_parsing.py` | CLI cases, boundaries, partial construction/allocation failures |
| `test_ranking.py` | Dense ranks, unchanged values/links, duplicate/allocation failures |
| `test_analysis.py` | Inversions, exact 20%/50% boundaries, selectors |
| `test_small.py` | All permutations of sizes 2–5, rank-based decisions |
| `test_simple.py` | Minimum extraction, arbitrary sizes, ownership/counters |
| `test_medium.py` | Dynamic chunks, combined rotations, random operation budgets |
| `test_complex.py` | Stable radix model, bit boundaries, sizes through 1500 |
| `test_dispatch.py` | All selectors, metadata, sorted input and small-sort routing |
| `test_benchmark.py` | Rounding, all counters, stream isolation/order, 64-bit output |
| `test_performance.py` | 6000 random runs, stress to 2048, worst seeds, replay |

Run an individual suite with `python3 tests/<file>.py`. Rotations, parsing,
Medium, Complex and dispatcher accept `--valgrind` instead of their default
ASan/UBSan mode. Other suites include their own memory probes. If LeakSanitizer
cannot run under the environment's process tracing, use
`ASAN_OPTIONS=detect_leaks=0 python3 tests/<file>.py` for ASan/UBSan and run
Valgrind separately for leaks; disabling leak detection is not a leak check.

An optional third-party Linux tester is available from
[gemartin99/Push-Swap-Tester](https://github.com/gemartin99/Push-Swap-Tester).
Keep its download local (the directory is ignored by Git):

```sh
git clone https://github.com/gemartin99/Push-Swap-Tester.git tools/Push-Swap-Tester
bash tests/run_external_tester.sh 200 200
```

The launcher builds the project and runs the upstream mandatory suite from its
own directory, where `traces.txt` is written. Valgrind is required. Its older
performance scores differ from subject 1.2: a performance `KO` can accompany a
correct checker result and a count that meets this subject's thresholds.
Its memory checks do not use Valgrind's `--error-exitcode`, so use the project's
memory tests for reliable leak checks. Bonus mode requires a learner-written
`checker`, which this mandatory-only project does not provide.

Full performance reproduction:

```sh
python3 tests/test_performance.py --valgrind
```

This writes `docs/performance_stage15.json` after all checks pass. For smaller
exploratory samples, set `--trials-100`, `--trials-500` and a separate `--output`.
Every random stream is also checked with combined commands expanded into
individual operations; recorded rotation savings refer to that equivalent
stream. Valgrind covers saved worst cases and representative stress inputs.

## Contributions

The git history records the following module work under the contributors'
author identities; it does not by itself establish individual understanding.

| Contributor | Work recorded in the repository |
| --- | --- |
| maliuten (mmmaryl / Mariia identities) | Stack foundation/lifecycle, swap/push, ranking, disorder, small sort, Simple, benchmark, main integration, performance tests and merges |
| vakhapil (kerber / Valeriia identities) | Parser and CLI integration, rotations, Medium, Complex, Adaptive/dispatcher, associated tests and documentation |

Both learners must understand and be able to modify every module and attend
the defense.

## Resources

- Official Push_swap subject: project requirements, allowed operations,
  strategy complexities, disorder thresholds and evaluation criteria.
- Local manuals: `man 3 malloc`, `man 3 free`, `man 2 write`.

## AI usage

AI was used to help write this README, understand the subject and all its requirements, and explain how the project and individual functions work. AI also assisted with testing across project modules, as well as performance analysis.

The project authors are maliuten and vakhapil, who are responsible for the whole project, inluding implementation, algorithm choices, testing, error checks and corrections, and submitted code.