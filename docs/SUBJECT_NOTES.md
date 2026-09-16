# Push_swap subject notes

Based on official Push_swap subject version 1.1.

## General requirements

- project is written in C
- Norminette required
- compile with `-Wall -Wextra -Werror`
- no global variables
- memory leaks are not tolerated
- crashes such as segfault, double free and invalid access are not acceptable
- Makefile must contain at least:
  - `$(NAME)`
  - `all`
  - `clean`
  - `fclean`
  - `re`
- unnecessary relinking is forbidden
- Libft is authorized
- allowed external functions include:
  - `read`
  - `write`
  - `malloc`
  - `free`
  - `exit`
  - own ft_printf or equivalent

## Group project

This project must be completed by exactly two learners.

Requirements:

- both learners contribute meaningfully
- both learners understand all algorithms
- both logins are present in repository
- README documents both contributions
- both learners attend defense
- each learner can explain any part of the code

## Stack model

There are two stacks:

- `a`
- `b`

Initially:

- `a` contains all input integers
- `b` is empty

The first integer is the top of stack A.

Goal:

- stack A sorted ascending
- smallest value on top
- stack B empty

## Allowed operations

### Swap

`sa`  
Swap first two elements of A.

`sb`  
Swap first two elements of B.

`ss`  
Perform `sa` and `sb` simultaneously.

### Push

`pa`  
Take top of B and move it to top of A.

`pb`  
Take top of A and move it to top of B.

### Rotate

`ra`  
Move first element of A to the bottom.

`rb`  
Move first element of B to the bottom.

`rr`  
Perform `ra` and `rb` simultaneously.

### Reverse rotate

`rra`  
Move last element of A to the top.

`rrb`  
Move last element of B to the top.

`rrr`  
Perform `rra` and `rrb` simultaneously.

## Mandatory algorithms

The binary must contain four strategies.

### Simple

Required complexity:

`O(n²)`

Examples accepted by subject:

- insertion sort adaptation
- selection sort adaptation
- bubble sort adaptation
- min/max extraction

### Medium

Required complexity:

`O(n√n)`

Examples:

- chunk-based sorting
- block partitioning
- bucket adaptations
- range-based strategies

### Complex

Required complexity:

`O(n log n)`

Examples:

- radix sort
- merge sort adaptation
- quick sort adaptation
- heap sort adaptation
- other valid approaches

### Adaptive

Must select internal method according to disorder.

Required ranges:

- `disorder < 0.2` -> `O(n²)`
- `0.2 <= disorder < 0.5` -> `O(n√n)`
- `disorder >= 0.5` -> `O(n log n)`

## Complexity model

Complexity is measured in number of generated Push_swap operations.

It is not based only on classical array algorithm complexity.

## Disorder

Disorder is based on inversions.

For all pairs `i < j`:

if:

`a[i] > a[j]`

then that pair is an inversion.

Formula:

`disorder = inversions / total_pairs`

Where:

`total_pairs = n * (n - 1) / 2`

Disorder must be measured before any operation is performed.

## Program

Binary name:

`push_swap`

Accepted strategy selectors:

- `--simple`
- `--medium`
- `--complex`
- `--adaptive`

If no selector is given:

`--adaptive`

must be used.

Optional benchmark flag:

`--bench`

Selectors must work for all valid sizes and disorder values.

## Program output

Normal output:

- Push_swap operation names only
- one operation per line
- no extra text

No arguments:

- print nothing

Errors:

`Error\n`

to `stderr`.

Errors include:

- non-integer arguments
- integer overflow
- duplicates

## Benchmark mode

When `--bench` is present, after sorting print to `stderr`:

- disorder percentage with two decimals
- strategy name
- theoretical complexity
- total number of operations
- count of:
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

Operation stream must remain on `stdout`.

## Performance requirements

For 100 random numbers:

- pass: < 2000 operations
- good: < 1500
- excellent: < 700

For 500 random numbers:

- pass: < 12000 operations
- good: < 8000
- excellent: < 5500

## README requirements

The first line must be italicized and follow:

`This project has been created as part of the 42 curriculum by <login1>, <login2>.`

README must include:

- Description
- Instructions
- Resources
- explanation of AI usage
- detailed explanation and justification of chosen algorithms

## Evaluation

Only repository contents are evaluated.

During defense, a small modification may be requested.

Both learners must be able to explain and modify any part of the project.