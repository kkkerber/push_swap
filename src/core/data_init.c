/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   data_init.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 16:15:27 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 16:46:24 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	stats_init(t_stats *stats)
{
	stats->total = 0;
	stats->sa = 0;
	stats->sb = 0;
	stats->ss = 0;
	stats->pa = 0;
	stats->pb = 0;
	stats->ra = 0;
	stats->rb = 0;
	stats->rr = 0;
	stats->rra = 0;
	stats->rrb = 0;
	stats->rrr = 0;
}

void	data_init(t_data *data)
{
	if (!data)
		return ;
	stack_init(&data->a);
	stack_init(&data->b);
	data->config.requested_strategy = ADAPTIVE;
	data->config.strategy_set = 0;
	data->config.bench = 0;
	stats_init(&data->stats);
	data->inversions = 0;
	data->pairs = 0;
	data->effective_strategy = ADAPTIVE;
}
