/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stats.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 16:15:27 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 16:46:24 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "benchmark.h"

void	bench_text(const char *text)
{
	int	length;

	length = 0;
	while (text[length])
		length++;
	write(2, text, length);
}

void	bench_number(unsigned long long value)
{
	char	digits[20];
	int		index;

	index = 20;
	while (value >= 10)
	{
		digits[--index] = '0' + value % 10;
		value /= 10;
	}
	digits[--index] = '0' + value;
	write(2, digits + index, 20 - index);
}

void	bench_field(const char *name, unsigned long long value)
{
	bench_text(name);
	bench_text(": ");
	bench_number(value);
	bench_text("\n");
}

void	bench_stats(const t_stats *stats)
{
	bench_field("Total operations", stats->total);
	bench_field("sa", stats->sa);
	bench_field("sb", stats->sb);
	bench_field("ss", stats->ss);
	bench_field("pa", stats->pa);
	bench_field("pb", stats->pb);
	bench_field("ra", stats->ra);
	bench_field("rb", stats->rb);
	bench_field("rr", stats->rr);
	bench_field("rra", stats->rra);
	bench_field("rrb", stats->rrb);
	bench_field("rrr", stats->rrr);
}
