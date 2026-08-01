/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/10 22:18:28 by maliuten          #+#    #+#             */
/*   Updated: 2026/07/17 22:17:44 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

static int	handle_specifier(char specifier, va_list args)
{
	int	count;

	count = 0;
	if (specifier == 'c')
		count += ft_putchar(va_arg(args, int));
	if (specifier == 's')
		count += ft_putstr(va_arg(args, char *));
	if (specifier == 'p')
		count += ft_putptr(va_arg(args, void *));
	if (specifier == 'd' || specifier == 'i')
		count += ft_putnbr(va_arg(args, int));
	if (specifier == 'u')
		count += ft_putnbr_unsigned(va_arg(args, unsigned int));
	if (specifier == 'x' || specifier == 'X')
		count += ft_puthex(va_arg(args, unsigned int), specifier);
	if (specifier == '%')
		count += ft_putchar('%');
	return (count);
}

int	ft_printf(const char *str, ...)
{
	int		count;
	va_list	args;

	count = 0;
	va_start(args, str);
	while (*str)
	{
		if (*str == '%')
		{
			str++;
			if (*str)
				count += handle_specifier(*str, args);
		}
		else
			count += ft_putchar(*str);
		str++;
	}
	va_end(args);
	return (count);
}
// #include <stdio.h>
// #include "ft_printf.h"
// #include <stdio.h>

// int	main(void)
// {
// 	char			c;
// 	char			*str;
// 	char			*null_str;
// 	int				n;
// 	unsigned int	u;
// 	void			*ptr;
// 	int				ft_ret;
// 	int				pr_ret;

// 	c = 'A';
// 	str = "Hello, 42!";
// 	null_str = NULL;
// 	n = -42;
// 	u = 4294967295U;
// 	ptr = &n;

// 	ft_printf("----- FT_PRINTF -----\n");
// 	ft_printf("char      : %c\n", c);
// 	ft_printf("string    : %s\n", str);
// 	ft_printf("null str  : %s\n", null_str);
// 	ft_printf("pointer   : %p\n", ptr);
// 	ft_printf("null ptr  : %p\n", NULL);
// 	ft_printf("decimal   : %d\n", n);
// 	ft_printf("integer   : %i\n", n);
// 	ft_printf("unsigned  : %u\n", u);
// 	ft_printf("hex lower : %x\n", u);
// 	ft_printf("hex upper : %X\n", u);
// 	ft_printf("percent   : %%\n");

// 	printf("\n----- PRINTF -----\n");
// 	printf("char      : %c\n", c);
// 	printf("string    : %s\n", str);
// 	printf("null str  : %s\n", null_str);
// 	printf("pointer   : %p\n", ptr);
// 	printf("null ptr  : %p\n", NULL);
// 	printf("decimal   : %d\n", n);
// 	printf("integer   : %i\n", n);
// 	printf("unsigned  : %u\n", u);
// 	printf("hex lower : %x\n", u);
// 	printf("hex upper : %X\n", u);
// 	printf("percent   : %%\n");

// 	printf("\n----- RETURN VALUE -----\n");

// 	ft_ret = ft_printf("Test: %c %s %p %d %i %u %x %X %%\n",
// 		c, str, ptr, n, n, u, u, u);
// 	pr_ret = printf("Test: %c %s %p %d %i %u %x %X %%\n",
// 		c, str, ptr, n, n, u, u, u);

// 	printf("ft_printf returned : %d\n", ft_ret);
// 	printf("printf returned    : %d\n", pr_ret);

// 	return (0);
// }