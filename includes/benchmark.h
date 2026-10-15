/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   benchmark.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 16:15:27 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 16:46:24 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef BENCHMARK_H
# define BENCHMARK_H

# include "push_swap.h"

void	bench_text(const char *text);
void	bench_number(unsigned long long value);
void	bench_field(const char *name, unsigned long long value);
void	bench_stats(const t_stats *stats);

#endif
