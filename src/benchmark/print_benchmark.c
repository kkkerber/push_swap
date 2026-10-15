/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_benchmark.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 16:15:27 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 16:46:24 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "benchmark.h"

static const char	*strategy_name(t_strategy strategy)
{
	if (strategy == SIMPLE)
		return ("Simple");
	if (strategy == MEDIUM)
		return ("Medium");
	if (strategy == COMPLEX)
		return ("Complex");
	return ("Adaptive");
}

static const char	*strategy_complexity(t_strategy strategy)
{
	if (strategy == SIMPLE)
		return ("O(n^2)");
	if (strategy == MEDIUM)
		return ("O(n*sqrt(n))");
	return ("O(n log n)");
}

static void	print_disorder(const t_data *data)
{
	unsigned long long	percent;

	percent = 0;
	if (data->pairs != 0)
		percent = (unsigned long long)((long double)data->inversions
				/ data->pairs * 10000 + 0.5L);
	bench_text("Disorder: ");
	bench_number(percent / 100);
	bench_text(".");
	if (percent % 100 < 10)
		bench_text("0");
	bench_number(percent % 100);
	bench_text("%\n");
}

void	print_benchmark(const t_data *data)
{
	if (!data || !data->config.bench)
		return ;
	print_disorder(data);
	bench_text("Requested strategy: ");
	bench_text(strategy_name(data->config.requested_strategy));
	bench_text("\nEffective strategy: ");
	bench_text(strategy_name(data->effective_strategy));
	bench_text("\nTheoretical complexity: ");
	bench_text(strategy_complexity(data->effective_strategy));
	bench_text("\n");
	bench_stats(&data->stats);
}
