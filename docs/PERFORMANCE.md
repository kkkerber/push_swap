# Stage 15 performance checks

Run from the repository root:

```sh
make
python3 tests/test_performance.py --valgrind
norminette src includes ft_printf
```

The full test runs 1000 seeds for 100 integers and 500 seeds for 500 integers
under each of the four selectors (6000 random sorting runs). Each seed uses
`random.Random(seed).sample(range(-1000000000, 1000000000), n)`.
An independent Python deque checker verifies sorted A and empty B before
operation counts are analyzed. Every benchmark counter is matched against
the emitted operation stream.

## Random results

| Size | Strategy | Minimum | Average | Maximum |
| --- | --- | ---: | ---: | ---: |
| 100 | Simple | 1201 | 1460.96 | 1724 |
| 100 | Medium | 694 | 754.23 | 800 |
| 100 | Complex | 1084 | 1084.00 | 1084 |
| 100 | Adaptive | 701 | 923.02 | 1084 |
| 500 | Simple | 29391 | 32290.55 | 35503 |
| 500 | Medium | 7165 | 7390.55 | 7609 |
| 500 | Complex | 6784 | 6784.00 | 6784 |
| 500 | Adaptive | 6784 | 7083.64 | 7555 |

Medium, Complex and default Adaptive meet the internal random-input budgets
of fewer than 1500 and 8000 commands in these series. No algorithm changes
were needed to meet those budgets. These are measured samples, not guarantees
for every possible permutation.

Explicit Simple retains the required quadratic minimum-extraction algorithm.
It exceeds the internal 100-element budget on some inputs and exceeds even
the 12000-command mandatory 500-element budget on these random inputs.
The suite records this limitation rather than replacing an explicit selector
with another algorithm or claiming that all selectors meet the budgets.

## Reproduction and further checks

`performance_stage15.json` stores full summaries, rotation savings and the
three worst seeds per size/selector. Recheck them after algorithm changes:

```sh
python3 tests/test_performance.py --replay docs/performance_stage15.json --valgrind
```

The initial full run repeats all 24 saved cases and requires identical command
counts and stream hashes. Replay mode checks correctness and the same performance
budgets but permits an optimized command stream to differ.

Stress cases use 95, 501, 1000 and 2048 integers: sorted, reverse, rotated,
nearly sorted, alternating and random inputs under every selector. Default
and explicit Adaptive streams must match. Signed integer extremes are included.
Valgrind checks random stress cases and the saved worst cases for all four
selectors, with leak kinds and memory errors treated as failures.

For comparison, every random operation stream is expanded from `ss`, `rr` and
`rrr` into its individual commands and checked again. The JSON report records
how many commands direct combined rotations save against that equivalent
expanded stream. This comparison preserves the algorithm's choices; it does
not claim to benchmark a separately optimized algorithm without combinations.

For exploratory runs, use `--trials-100`, `--trials-500` and `--output /tmp/report.json`
to keep small samples separate from the committed full report.
