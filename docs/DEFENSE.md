# Defense preparation

This guide is a rehearsal aid for both maliuten and vakhapil. It does not
certify readiness. Each learner should explain the complete pipeline without
reading prepared answers and make at least one small change independently.

## Source map and execution order

| Module | Explain |
| --- | --- |
| `src/main.c` | Initialization, silent empty exit, error short-circuit, successful cleanup |
| `src/parsing/` | Exact flags, strict integer boundaries, duplicate validation, ordered construction |
| `src/stack/` | Circular invariants, detached nodes, ownership, bounded traversal |
| `src/operations/` | Mutate, print, count; direct combinations; no allocation |
| `src/ranking/` | Temporary insertion-sorted copy, immutable dense ranks |
| `src/analysis/` | Original inversions/pairs, exact integer threshold selection |
| `src/sorting/` | Small sort, three families, Adaptive and dispatch |
| `src/benchmark/` | stderr formatting, original metrics, full-width counters |
| `ft_printf/` | Static library integration and immediate operation output |

For `./push_swap --adaptive --bench "6 3 1 5 2 4"`, explain every step:
parse values/config; validate before constructing A; assign ranks
`[5,2,0,4,1,3]`; count 9 inversions out of 15 pairs; choose Complex at 60%;
run three radix passes; print the report; free both stacks. Original inversion
counts survive sorting. A parsing/ranking failure prints only `Error\n` to
stderr, clears owned memory and returns 1.

## Stack and memory questions

1. Draw an empty, singleton and three-node stack. Mark top, bottom, prev, next.
   Show why a `while (node)` traversal never terminates on a populated stack.
2. Detach the top of a singleton. Both stack endpoints become NULL, size is 0,
   and both detached-node links are NULL. Who owns that node now?
3. Trace `pb` and `pa` with node addresses. Explain why they must not allocate
   or free, and why values/ranks remain unchanged.
4. Walk through `stack_clear`: save next before free, iterate the original
   size, never dereference a freed node, then reset endpoints/size.
5. Force an allocation failure during partial construction. Follow parser
   cleanup and the shared error path; explain why repeated cleanup is safe.
6. Explain why rotations need only update endpoints, and why swapping values
   without their ranks would violate the rank/value relationship.

## Operation examples

Top is on the left:

```text
A=[2,0,1], B=[]
ra  -> A=[0,1,2], B=[]
pb  -> A=[1,2],   B=[0]
pa  -> A=[0,1,2], B=[]
```

If both A and B contain two nodes, `rr` changes both stacks but emits one line
and increments only rr and total. If one stack has fewer than two nodes, the
other can still rotate. If neither changes, nothing prints or increments.
Explain why implementing `rr` through public `ra`/`rb` would break this rule.

## Rank, disorder and dispatcher questions

- For `[42,-7,0]`, justify ranks `[2,0,1]`. Why is rank unaffected by rotation?
- Explain numeric duplicates: `03` equals `3`, and `-0` equals `+0`.
- Show that total pairs is n(n-1)/2 and empty/singleton disorder is zero.
- With ten pairs, 1 inversion chooses Simple, 2 chooses Medium and 5 chooses
  Complex. Derive the integer tests using ceil(pairs/5) and ceil(pairs/2).
- Why must inversion analysis precede the first command? What would sorted
  final A report if disorder were recomputed afterward?
- Explain requested versus effective strategy and why explicit `--simple`
  remains Simple even for reverse input.
- For three reverse elements with `--complex`, the family remains Complex in
  metrics while shared small sort executes. Already sorted input emits nothing.

## Algorithm walkthroughs

### Small sort

For `[2,1,0]`, `ra` gives `[1,0,2]` and `sa` gives `[0,1,2]`.
For four/five nodes, trace extraction of minima, sorting the remaining three
and restoration. Explain why testing sizes 2–5 means 2!+3!+4!+5!=152 cases.

### Simple

Start with ranks `[3,1,0,2,5,4]`. The minimum is at position 2, so two forward
rotations are shorter than four reverse rotations. Extract minima in ascending
order into B; B stores them in descending order. Returning with `pa` produces
ascending A. Derive the sum of at most floor(k/2)+1 commands per extraction
plus n restorations. Explain why explicit Simple exceeded the 500-element
budget in the measured series, without claiming that sorting is incorrect.

### Medium

For n=100, width is 10; for n=501, width is 22. The same integer square-root
calculation works at arbitrary sizes. Identify the current exclusive rank
limit and the lower/upper split used to arrange B. Trace a pending bury
rotation combined with A's next forward rotation as `rr`.

Explain the two-node-B `rrr` case: forward and reverse B rotation are equivalent
only at size two. Locate that guard in `medium_moves.c`. Do not generalize it
to bigger stacks. Restoration always extracts B's maximum through the shorter
rotation direction. Explain the command bound O(n²/w + nw) with w≈√n, and why
linked-list searching can still consume O(n²) CPU time.

### Complex

A hand-sized radix pass can be demonstrated on ranks `[3,0,2,1]` (the actual
CLI uses small sort for this size). For bit zero: rotate 3, push 0, push 2,
rotate 1; A contains `[3,1]`, B `[2,0]`. Restore B with `pa` twice to obtain
`[0,2,3,1]`. Processing bit one then yields `[0,1,2,3]`.

Explain stability: the zero group reverses on the way into B and again on
return, while the one group preserves its cyclic processing order. Every
pass processes its initial A size exactly once. The maximum rank determines
the bit count, giving ceil(log2(n)) passes and at most 2n commands per pass.
Remember that actual CLI preprocessing is O(n²), even with Complex selected.

## Benchmark and tests

Explain why benchmark uses `write(2, ...)` while commands use `ft_printf`.
Point out the bench guard, post-sort call, original inversion fields,
64-bit counters and rounding to two decimal places. Confirm that the eleven
counters sum to total and combined commands count once.

Use the full result report to explain sample size, minimum/average/maximum,
worst seeds, correctness-before-counting and the Simple limitation. Expanding
`rr` into `ra`/`rb` compares equivalent streams; it is not a separate sorting
algorithm. Valgrind checks memory errors/leaks; ASan/UBSan catch different
classes of runtime errors. A successful Python replay checks final sorted A
and empty B; pointer/link probes check internal invariants as well.

## Practical rehearsal

Each learner should perform these in a disposable working copy, run the
relevant tests and restore the original behavior afterward:

1. Add an explanation comment to `stack_take_top`, then trace a singleton
   through push and cleanup on paper with concrete node addresses.
2. Temporarily change Medium's dynamic chunk width, preserving dependence on
   n. Run `test_medium.py` and replay saved worst seeds; discuss count changes.
3. Temporarily disable one combined rotation in Medium by using its individual
   public operations. Confirm final order, counters and the increased count.
4. Add a parser regression case for equivalent signed/zero-padded numbers.
5. Diagnose a deliberate counter increment on a no-op using operation tests.
6. Explain a new permutation of six ranks under each selector without looking
   at prepared traces, then compare against the emitted command stream.

For the actual hand-in, both learners must independently confirm their ability
to explain and modify every module and verify the official subject/evaluation
requirements. The source and documentation are prepared; this personal review
and attendance cannot be established automatically.
