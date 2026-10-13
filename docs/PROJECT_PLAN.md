# Push_swap development plan

42 • Subject version 1.1 • Mandatory only • 2 learners

## Fixed decisions

- Circular doubly linked list
- `top->prev == bottom`
- `bottom->next == top`
- Node field is named `rank`
- Minimum gets rank `0`
- Maximum gets rank `n - 1`
- Mandatory part only
- All 11 Push_swap commands are explicit public functions
- Every operation modifies the stack, prints its own name and updates statistics
- `ss`, `rr`, `rrr` are called directly by algorithms when both stacks need the same action
- Ready-made `ft_printf` is linked as a library
- Implementation must work for arbitrary valid input size
- 100 and 500 are only evaluation sizes

## Development workflow

Implementation -> review -> tests -> optimization

Do not start sorting algorithms before stack structure and all operations are fully tested.

Each module must pass:

- compilation
- Norminette
- tests
- Valgrind where relevant

Every function must be understood by both learners.

Commit small complete changes.

Never traverse a circular list using `while (node)`.

All traversals are bounded by `stack->size`.

## Stage 1 — Project skeleton, Makefile, ft_printf integration

Goal:

- create stable build
- integrate existing ft_printf library
- initialize and clear `t_data`
- empty execution prints nothing

Files:

- `Makefile`
- `includes/push_swap.h`
- `src/main.c`
- `src/core/data_init.c`
- `src/core/data_clear.c`
- `src/core/error.c`

Tasks:

- define `t_node`
- define `t_stack`
- define `t_strategy`
- define `t_config`
- define `t_stats`
- define `t_data`
- default strategy is Adaptive
- `bench = 0`
- all stats initialized to 0
- link existing ft_printf library through its own Makefile
- create unified error path
- create initial README

Completion criteria:

- build succeeds with required flags
- repeated `make` does not relink unnecessarily
- ft_printf links correctly
- `./push_swap` with no arguments prints nothing
- cleanup is safe

## Stage 2 — Circular stack core

Goal:

Implement safe circular doubly linked stack primitives.

Files:

- `src/stack/node_create.c`
- `src/stack/stack_init.c`
- `src/stack/stack_add.c`
- `src/stack/stack_take.c`
- `src/stack/stack_clear.c`
- `src/stack/stack_state.c`

Required functions:

- `node_new`
- `stack_init`
- `stack_add_top`
- `stack_add_bottom`
- `stack_take_top`
- `stack_clear`
- `stack_is_sorted`

Rules:

- `node_new` creates a detached node
- new node starts with `rank = -1`
- new node starts with `prev = NULL`
- new node starts with `next = NULL`
- adding first node makes it point to itself
- stack operations preserve circular invariants
- `stack_take_top` does not free
- detached node must have `prev = NULL`, `next = NULL`
- `stack_clear` frees exactly `size` nodes

Tests:

- empty stack
- one node
- two nodes
- three nodes
- 500 nodes
- 1000 nodes
- repeated clear
- take until empty
- Valgrind

## Stage 3 — sa, sb, ss, pa, pb

Files:

- `src/operations/swap.c`
- `src/operations/push.c`
- `src/benchmark/stats.c`

Rules:

- each public operation directly modifies the stack
- prints immediately
- increments its own counter
- increments total
- no-op prints nothing
- `ss` is direct and must not call public `sa` and `sb`
- `pa` and `pb` move existing nodes
- no malloc/free inside push

## Stage 4 — Rotate and reverse rotate

Files:

- `src/operations/rotate.c`
- `src/operations/reverse_rotate.c`

Operations:

- `ra`
- `rb`
- `rr`
- `rra`
- `rrb`
- `rrr`

Rules:

- `ra/rb` move top/bottom to `next`
- `rra/rrb` move top/bottom to `prev`
- `rr` is direct
- `rrr` is direct
- combined operation prints once
- combined operation increments total once
- command prints if at least one stack changes
- algorithms must choose combined operations before execution

## Stage 5 — Parser and CLI flags

Files:

- `src/parsing/parse_cli.c`
- `src/parsing/parse_flags.c`
- `src/parsing/token_count.c`
- `src/parsing/parse_integer.c`
- `src/parsing/build_values.c`
- `src/parsing/validate_input.c`

Support:

- `./push_swap 3 2 1`
- `./push_swap "3 2 1"`
- mixed arguments
- whitespace inside quoted strings

Flags:

- `--simple`
- `--medium`
- `--complex`
- `--adaptive`
- `--bench`

Rules:

- maximum one strategy selector
- maximum one `--bench`
- flags only on exact match
- `-5` is a number
- only flags without numbers -> error
- allocate one exact-size int array
- build stack A only after validation
- first integer becomes top
- error path cleans all allocated memory

Parser edge cases:

- `INT_MIN`
- `INT_MAX`
- `+0`
- `-0`
- leading zeros
- empty string
- whitespace-only string
- single sign
- letters
- decimals
- overflow
- duplicate numeric representations

## Stage 6 — Ranking

Files:

- `src/ranking/sort_values.c`
- `src/ranking/assign_ranks.c`

Tasks:

- copy all values to an array
- sort with own sorting function
- do not use `qsort`
- detect duplicates in sorted copy
- assign ranks to nodes
- traverse exactly `a.size` nodes
- free temporary array

Expected:

- minimum -> rank 0
- maximum -> rank n - 1
- values unchanged
- all ranks unique

## Stage 7 — Disorder

Files:

- `src/analysis/disorder.c`
- `src/analysis/strategy_select.c`

Compute:

- total pairs
- inversion count
- disorder

Rules:

- calculate before first operation
- for `n < 2`, disorder = 0
- avoid division by zero
- save integer inversion count and pair count
- benchmark percentage calculated later

Thresholds:

- `< 0.2` -> Simple
- `0.2 <= disorder < 0.5` -> Medium
- `>= 0.5` -> Complex

## Stage 8 — Small sort

File:

- `src/sorting/sort_small.c`

Requirements:

- 0/1 -> nothing
- 2 -> `sa` if needed
- all 6 permutations for 3
- 4/5:
  - move minimum ranks to B
  - sort three
  - restore with `pa`

Use ranks.

Test all 152 permutations for sizes 2–5.

## Stage 9 — Simple strategy

File:

- `src/sorting/sort_simple.c`

Algorithm:

1. find minimum rank
2. calculate its position
3. use shortest rotation direction
4. move minimum to top
5. `pb`
6. repeat
7. restore all with `pa`

Complexity target:

`O(n²)`

## Stage 10 — Medium strategy

File:

- `src/sorting/sort_medium.c`

Algorithm family:

- dynamic chunks/windows
- chunk count or width depends on `sqrt(n)`
- no hardcoding only for 100/500
- send smaller ranks deeper in B
- keep larger ranks closer to top
- choose shortest rotation direction
- use direct `rr` and `rrr` when both stacks rotate together
- when restoring, bring maximum rank in B to top using shortest direction

Complexity target:

`O(n√n)`

## Stage 11 — Complex strategy

File:

- `src/sorting/sort_complex.c`

Use binary LSD radix on ranks.

Algorithm:

1. calculate number of bits needed for maximum rank
2. for each bit:
   - process exactly the original size of A
   - bit 0 -> `pb`
   - bit 1 -> `ra`
3. return all B to A with `pa`
4. repeat for next bit

Complexity target:

`O(n log n)`

## Stage 12 — Adaptive and dispatcher

Files:

- `src/sorting/sort_adaptive.c`
- `src/sorting/sort_dispatch.c`

Rules:

- already sorted -> no operations
- size <= 5 -> small sort
- explicit selector uses its own strategy
- Adaptive uses disorder
- default equals `--adaptive`
- save both requested and effective strategy

## Stage 13 — Benchmark mode

Files:

- `src/benchmark/stats.c`
- `src/benchmark/print_benchmark.c`

Benchmark must show:

- disorder percentage with two decimals
- requested strategy
- effective strategy
- theoretical complexity
- total operations
- all 11 counters

Output:

- only in `stderr`
- only with `--bench`

`stdout` remains pure operation stream.

## Stage 14 — Final main integration

File:

- `src/main.c`

Main should only coordinate:

1. initialize
2. handle `argc == 1`
3. parse input
4. validate
5. assign ranks
6. compute disorder
7. dispatch sorting
8. print benchmark if enabled
9. clear memory
10. return status

No parser logic, stack logic or sorting logic inside `main`.

## Stage 15 — Performance hardening

Tests:

- 1000 random tests for n=100
- 300–500 random tests for n=500
- stress 95, 501, 1000+
- checker before operation count analysis
- collect minimum/average/maximum
- save worst seeds
- rerun worst seeds after optimization
- compare combined rotations against individual rotations
- Valgrind
- Norminette

Targets:

100:

- mandatory < 2000
- internal target < 1500

500:

- mandatory < 12000
- internal target < 8000

## Stage 16 — README and defense

README must document:

- project goal
- build and execution
- selectors
- benchmark
- data structures
- all 11 operations
- rank
- disorder
- all strategies
- complexity arguments
- ft_printf integration
- testing
- contributions
- resources
- AI usage

Both learners must be able to explain and modify any part of the project.

## Final architecture

Circular `t_stack`
+ `rank`
+ 11 direct public operations
+ explicit `ss/rr/rrr`
+ ft_printf inside operations
+ stderr-safe benchmark/error
+ four mandatory strategies