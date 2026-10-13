# Push_swap project instructions

This repository implements the 42 Push_swap project, subject version 1.1.

## Source of truth

Before changing architecture or implementing a new stage, read:

- `docs/PROJECT_PLAN.md`
- `docs/SUBJECT_NOTES.md`
- `README.md`

If project documentation conflicts with the official subject, the official subject has priority.

## Fixed architecture

Do not redesign the architecture unless explicitly requested.

The project uses a circular doubly linked list.

`t_node` contains:

- `int value`
- `int rank`
- `t_node *prev`
- `t_node *next`

`t_stack` contains:

- `t_node *top`
- `t_node *bottom`
- `int size`

### Circular stack invariants

Empty stack:

- `top == NULL`
- `bottom == NULL`
- `size == 0`

One node:

- `top == bottom`
- `top->next == top`
- `top->prev == top`
- `size == 1`

Two or more nodes:

- `top->prev == bottom`
- `bottom->next == top`

For every node:

- `node->next->prev == node`
- `node->prev->next == node`

Never traverse a circular list with `while (node)`.

All traversals must be bounded by `stack->size`.

## Memory ownership

Each `t_node` is allocated exactly once and freed exactly once.

`pa` and `pb` move existing nodes between stacks.

They must not allocate or free nodes.

`stack_take_top` only detaches a node and returns it.

`stack_clear` must free exactly the original number of nodes and restore:

- `top = NULL`
- `bottom = NULL`
- `size = 0`

Cleanup must be safe for:

- empty state
- partially initialized state
- fully initialized state

## Operations

All 11 Push_swap operations must exist as public functions:

- `sa`
- `sb`
- `ss`
- `pa`
- `pb`
- `ra`
- `rb`
- `rr`
- `rra`
- `rrb`
- `rrr`

Each public operation must:

1. check whether the operation changes the stack
2. modify the stack
3. print its own operation name immediately
4. update statistics

Algorithms never print operation names directly.

Combined operations must be direct operations.

Do not implement `ss` by calling public `sa` and `sb`.

Do not implement `rr` by calling public `ra` and `rb`.

Do not implement `rrr` by calling public `rra` and `rrb`.

Otherwise multiple operation names would be printed.

`ss`, `rr`, and `rrr` count as one Push_swap operation.

If an operation changes nothing, it must not print anything and must not increment counters.

## Output rules

`stdout` must contain only valid Push_swap operation names.

Errors must go to `stderr`:

`Error\n`

Benchmark output must also go to `stderr`.

No debug output is allowed in the final program.

## Rank

The field name is always `rank`.

Rank represents the position of `value` in the fully sorted set.

Minimum value gets rank `0`.

Maximum value gets rank `n - 1`.

Rank never changes during Push_swap operations.

Rank is not the current position of a node in a stack.

## Disorder

Disorder must be computed before the first Push_swap operation.

It is based on inversion count.

Adaptive thresholds:

- `disorder < 0.2` -> Simple
- `0.2 <= disorder < 0.5` -> Medium
- `disorder >= 0.5` -> Complex

Boundary rules:

- exactly `0.2` belongs to Medium
- exactly `0.5` belongs to Complex

Store inversion count and total pair count.

Avoid division by zero for `n < 2`.

## Sorting strategies

### Simple

Complexity target:

`O(n²)`

Use minimum extraction.

General idea:

1. find the minimum rank in stack A
2. rotate it to the top using the shortest direction
3. `pb`
4. repeat
5. return everything with `pa`

Explicit `--simple` must always use Simple.

### Medium

Complexity target:

`O(n√n)`

Use a dynamic chunk/window strategy.

Chunk parameters must depend on the actual input size.

Do not hardcode logic only for 100 or 500 elements.

When both stacks need rotations in the same direction, use direct `rr` or `rrr`.

### Complex

Complexity target:

`O(n log n)`

Use binary LSD radix sort based on ranks.

For every bit:

- bit 0 -> `pb`
- bit 1 -> `ra`

After each pass, return all elements from B to A using `pa`.

Bit count must be computed dynamically from the maximum rank.

### Adaptive

Default strategy.

Use disorder:

- low disorder -> Simple
- medium disorder -> Medium
- high disorder -> Complex

Explicit selectors must never be overridden by Adaptive.

## Small sort

For size <= 5 use the shared small-sort implementation.

Expected behavior:

- 0 or 1 element -> no operations
- 2 elements -> `sa` only if needed
- 3 elements -> handle all permutations
- 4 or 5 elements -> move minimum ranks to B, sort 3, return with `pa`

Use ranks, not raw values.

Already sorted input must produce no operations.

## CLI

Support:

- separate integer arguments
- quoted strings
- mixed input
- `--simple`
- `--medium`
- `--complex`
- `--adaptive`
- `--bench`

Default selector:

`--adaptive`

Reject:

- malformed integers
- integer overflow
- duplicates
- empty string input
- whitespace-only string
- unknown flags
- more than one strategy selector
- repeated `--bench`

Flags must match exactly.

Negative numbers such as `-5` must be treated as numbers, not flags.

## Parsing

Use strict integer parsing.

Values must fit in the C `int` range.

Duplicates are numeric duplicates.

Examples:

- `3` and `03` are duplicates
- `0` and `-0` are duplicates
- `5` and `+5` are duplicates

After full validation, build stack A preserving the original input order.

The first integer becomes the top of stack A.

## Benchmark

Benchmark output appears only with `--bench`.

It must be printed after sorting.

Output goes only to `stderr`.

It must include:

- disorder percentage with two decimal places
- requested strategy
- effective strategy
- theoretical complexity
- total operation count
- counts of all 11 operations

The sum of all operation counters must equal total operations.

## Performance targets

For 100 random numbers:

- pass: less than 2000 operations
- good: less than 1500
- excellent: less than 700

For 500 random numbers:

- pass: less than 12000 operations
- good: less than 8000
- excellent: less than 5500

Internal project target:

- below 1500 for 100
- below 8000 for 500

## Coding rules

- C only
- Norminette compliant
- compile with `-Wall -Wextra -Werror`
- no global variables
- no forbidden functions
- no generic `utils.c`
- functions used only inside one `.c` file should be `static`
- preserve module boundaries
- use descriptive names

Avoid names such as:

- `helper`
- `do_it`
- `temp_function`
- `sort_stuff`

## Working method

Before implementing a stage:

1. inspect current repository state
2. read the relevant section in `docs/PROJECT_PLAN.md`
3. implement only the requested stage
4. do not start later stages unless explicitly requested
5. compile with required flags
6. run relevant tests
7. run Norminette
8. run Valgrind when memory is involved
9. report changed files
10. explain important design decisions

Do not rewrite working code unnecessarily.

Correctness comes before optimization.