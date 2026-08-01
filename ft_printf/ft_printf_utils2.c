/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf_utils2.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/17 18:06:56 by maliuten          #+#    #+#             */
/*   Updated: 2026/07/17 20:48:33 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

int	ft_puthex(unsigned long long n, char specificator)
{
	int	count;

	count = 0;
	if (n >= 16)
		count += ft_puthex(n / 16, specificator);
	if (n % 16 < 10)
		count += ft_putchar((n % 16) + '0');
	if (n % 16 >= 10)
	{
		if (specificator == 'x')
			count += ft_putchar(((n % 16) - 10) + 'a');
		else
			count += ft_putchar(((n % 16) - 10) + 'A');
	}
	return (count);
}

int	ft_putptr(void *p)
{
	unsigned long long	ptr;
	int					count;

	if (!p)
		return (ft_putstr("(nil)"));
	ptr = (unsigned long long)p;
	count = 0;
	if (ptr == 0)
	{
		count += ft_putstr("0x0");
		return (count);
	}
	count += ft_putstr("0x");
	count += ft_puthex(ptr, 'x');
	return (count);
}
