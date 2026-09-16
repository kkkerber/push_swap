This project has been created as part of the 42 curriculum by maliuten.

# ft_printf

*Because `ft_putnbr()` and `ft_putstr()` aren't enough.*

A 42 School (Common Core) project. The goal is to recode the `printf()`
function from the C standard library, using variable-length argument
lists (`va_list`, `va_start`, `va_arg`, `va_end`).

The implementation in this repository covers **only the mandatory
part** of the subject — the bonus flags (`-`, `0`, `.`, field width,
`#`, `+`, space) are **not implemented**.

---

## Table of contents

- [Description](#description)
- [Prototype](#prototype)
- [Supported conversions](#supported-conversions)
- [Project structure](#project-structure)
- [Instructions](#instructions)
- [Return value](#return-value)
- [How it works](#how-it-works)
- [Compliance with the subject](#compliance-with-the-subject)
- [Resources](#resources)
- [Author](#author)

---

## Description

| | |
|---|---|
| **Program name** | `libftprintf.a` |
| **Turn-in files** | `Makefile`, `*.h`, `*/*.h`, `*.c`, `*/*.c` |
| **Makefile rules** | `NAME`, `all`, `clean`, `fclean`, `re` |
| **Allowed external functions** | `malloc`, `free`, `write`, `va_start`, `va_arg`, `va_copy`, `va_end` |
| **Libft authorized** | yes, per the subject (not used in this project) |

Per the subject, the buffer management of the original `printf()` is
**not** reimplemented — output in this implementation goes directly
through `write()`, one character at a time.

## Prototype

```c
int ft_printf(const char *str, ...);
```

Declared in `ft_printf.h`.

## Supported conversions

The subject requires support for the conversions `cspdiuxX%`. All
eight are implemented:

| Conversion | Behavior | Implemented in |
|---|---|---|
| `%c` | Prints a single character (argument is read as `int`, then cast to `char`) | `ft_putchar` |
| `%s` | Prints a string. If `NULL` is passed, prints `(null)` | `ft_putstr` |
| `%p` | Prints a `void *` address in hexadecimal, prefixed with `0x`. If the pointer is `NULL`, prints `(nil)` | `ft_putptr` (uses `ft_puthex`) |
| `%d` | Prints a signed decimal number (argument read as `int`) | `ft_putnbr` |
| `%i` | Same behavior as `%d` (handled by the same branch of code) | `ft_putnbr` |
| `%u` | Prints an unsigned decimal number (argument `unsigned int`) | `ft_putnbr_unsigned` |
| `%x` | Prints a number in hexadecimal, lowercase (`a`–`f`) | `ft_puthex` |
| `%X` | Prints a number in hexadecimal, uppercase (`A`–`F`) | `ft_puthex` |
| `%%` | Prints a literal `%` character | `ft_putchar` |

Any character following `%` other than the eight listed above is not
handled by a dedicated case — `handle_specifier` only branches on
these eight conversions.

## Project structure

```
printf/
├── Makefile
├── ft_printf.h            # prototypes for ft_printf() and helper functions
├── ft_printf.c             # ft_printf(), format-string parsing, handle_specifier()
├── ft_printf_utils.c       # ft_putchar, ft_putstr, ft_putnbr, ft_putnbr_unsigned
└── ft_printf_utils2.c      # ft_puthex, ft_putptr
```

### `ft_printf.h`

Includes `<stdarg.h>` and `<unistd.h>`. Declares:

```c
int ft_printf(const char *str, ...);

int ft_putchar(char c);
int ft_putstr(char *s);
int ft_putnbr(long n);
int ft_putnbr_unsigned(unsigned int n);
int ft_putptr(void *p);
int ft_puthex(unsigned long long n, char specificator);
```

### `ft_printf.c`

Contains two functions:

- **`static int handle_specifier(char specifier, va_list args)`** —
  takes the conversion character and the `va_list`, and, through a
  sequence of `if` statements (not `else if`), determines which print
  function to call, accumulating a running count of printed
  characters.
- **`int ft_printf(const char *str, ...)`** — initializes the
  `va_list` via `va_start`, walks through the format string one
  character at a time:
  - if a `%` is encountered and there is a following character, it
    calls `handle_specifier` on that character;
  - otherwise it prints the character as-is via `ft_putchar`.
  Returns the total number of characters printed.

### `ft_printf_utils.c`

- `ft_putchar(char c)` — prints a single character via
  `write(1, &c, 1)`, returns `1`.
- `ft_putstr(char *s)` — if `s == NULL`, substitutes the string
  `"(null)"`; prints the string one character at a time via
  `ft_putchar`, returns the number of characters printed.
- `ft_putnbr(long n)` — recursively prints a signed number (argument
  is typed `long` so that inverting the sign is safe even for
  `INT_MIN`); if the number is negative, it first prints `-` and
  inverts the sign.
- `ft_putnbr_unsigned(unsigned int n)` — recursively prints an
  unsigned number.

### `ft_printf_utils2.c`

- `ft_puthex(unsigned long long n, char specificator)` — recursively
  converts a number to hexadecimal; depending on the passed
  specifier character (`'x'` or anything else, in this case `'X'`),
  it selects the lowercase or uppercase alphabet for digits `a`–`f` /
  `A`–`F`.
- `ft_putptr(void *p)` — if the pointer is `NULL`, prints `(nil)`; if
  the address equals `0`, prints `0x0`; otherwise prints `0x` followed
  by the address itself via `ft_puthex`, after casting it to
  `unsigned long long`.

## Instructions

### Installation

Clone the repository and move into the project directory (adjust the
URL/path to your actual repository):

```bash
git clone <your-repository-url>
cd printf
```

No external dependencies are required beyond a standard C toolchain
(`gcc`/`cc`, `make`, `ar`).

### Compilation

```bash
make          # builds libftprintf.a
make clean    # removes object files (*.o)
make fclean   # removes object files and libftprintf.a
make re       # fclean + all
```

The Makefile compiles the three source files (`ft_printf.c`,
`ft_printf_utils.c`, `ft_printf_utils2.c`) with the flags `-Wall
-Wextra -Werror`, and builds the static library with `ar rcs`, as
required by the subject. `libftprintf.a` is created inside the
project directory after running `make`.

### Execution

`ft_printf` is a library, not a standalone executable — it is meant to
be linked into your own test program.

1. Include the header in your source file:

   ```c
   #include <stdio.h>
	#include "ft_printf.h"
	#include <stdio.h>

	int	main(void)
	{
		char			c;
		char			*str;
		char			*null_str;
		int				n;
		unsigned int	u;
		void			*ptr;
		int				ft_ret;
		int				pr_ret;

		c = 'A';
		str = "Hello, 42!";
		null_str = NULL;
		n = -42;
		u = 4294967295U;
		ptr = &n;

		ft_printf("----- FT_PRINTF -----\n");
		ft_printf("char      : %c\n", c);
		ft_printf("string    : %s\n", str);
		ft_printf("null str  : %s\n", null_str);
		ft_printf("pointer   : %p\n", ptr);
		ft_printf("null ptr  : %p\n", NULL);
		ft_printf("decimal   : %d\n", n);
		ft_printf("integer   : %i\n", n);
		ft_printf("unsigned  : %u\n", u);
		ft_printf("hex lower : %x\n", u);
		ft_printf("hex upper : %X\n", u);
		ft_printf("percent   : %%\n");

		printf("\n----- PRINTF -----\n");
		printf("char      : %c\n", c);
		printf("string    : %s\n", str);
		printf("null str  : %s\n", null_str);
		printf("pointer   : %p\n", ptr);
		printf("null ptr  : %p\n", NULL);
		printf("decimal   : %d\n", n);
		printf("integer   : %i\n", n);
		printf("unsigned  : %u\n", u);
		printf("hex lower : %x\n", u);
		printf("hex upper : %X\n", u);
		printf("percent   : %%\n");

		printf("\n----- RETURN VALUE -----\n");

		ft_ret = ft_printf("Test: %c %s %p %d %i %u %x %X %%\n",
		c, str, ptr, n, n, u, u, u);
		pr_ret = printf("Test: %c %s %p %d %i %u %x %X %%\n",
		c, str, ptr, n, n, u, u, u);

		printf("ft_printf returned : %d\n", ft_ret);
		printf("printf returned    : %d\n", pr_ret);

		return (0);
	}
   ```

2. Compile and link your file against the built library:

   ```bash
   gcc -Wall -Wextra -Werror main.c -L. -lftprintf -o test
   ```

3. Run the resulting binary:

   ```bash
   ./test
   ```

## Return value

Like the original `printf()`, `ft_printf()` returns the number of
characters printed (the sum of the return values of every call to
`ft_putchar`, `ft_putstr`, `ft_putnbr`, `ft_putnbr_unsigned`,
`ft_puthex`, and `ft_putptr` made while parsing the format string).

## How it works

1. `ft_printf` walks the format string one character at a time.
2. Regular characters are printed as-is.
3. When a `%` is encountered, the next character is read and passed
   to `handle_specifier` along with the `va_list`.
4. `handle_specifier` calls `va_arg` with the correct type for the
   given conversion and delegates the actual printing to the
   corresponding helper function.
5. Printing any value ultimately reduces to a sequence of
   `write(1, &c, 1)` calls inside `ft_putchar` — no separate output
   buffering is implemented, as required by the subject.

## Compliance with the subject

- Written in C.
- Prototype matches the required one: `int ft_printf(const char *, ...)`.
- All mandatory conversions are implemented: `c s p d i u x X %`.
- The buffer management of the original `printf()` is not
  reimplemented — output goes through `write` character by character.
- Only allowed external functions are used: `malloc`, `free` (not
  actually used in the current implementation, as no dynamic
  allocation is required), `write`, `va_start`, `va_arg`, `va_copy`
  (not used — not needed by the current implementation), `va_end`.
- The library is built with `ar rcs` (no `libtool`).
- The Makefile contains the rules `NAME` (`$(NAME)`/`all`),
  `clean`, `fclean`, `re`.
- Verified by comparing the output of `ft_printf` against the
  standard `printf` on identical sets of arguments — the results,
  including the return value, match exactly.

## Resources

Classic references used while working on variadic functions and
`printf`-style formatting in C:

- `man 3 printf` — manual page for the standard `printf` family of
  functions.
- `man 3 stdarg` — manual page for `va_start`, `va_arg`, `va_copy`,
  `va_end`.
- [cppreference — Variadic functions](https://en.cppreference.com/w/c/variadic)
- [cppreference — printf format string reference](https://en.cppreference.com/w/c/io/fprintf)
- The 42 subject PDF for this project (`ft_printf`, version 9.2).

### AI usage disclosure

AI assistance was used for documentation: structuring this README, transforming the project subject into a clear checklist, and improving the explanatory sections.

AI was also used to help analyze the project subject, clarify the allowed/forbidden functions, research background info for some requirements, and write tests to check if all the cases are handled according to original function printf. The actual code implementation, debugging were done entirely by me. I fully understand how every function works and am ready to explain any part of the project during the peer evaluation.

## Author

**maliuten**
