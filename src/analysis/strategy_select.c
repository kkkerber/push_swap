/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   strategy_select.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 17:27:12 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 17:39:42 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	strategy_select(t_data *data)
{
	if (!data)
		return ;
	if (data->config.requested_strategy != ADAPTIVE)
		data->effective_strategy = data->config.requested_strategy;
	else if (data->pairs == 0 || data->inversions < data->pairs / 5
		+ (data->pairs % 5 != 0))
		data->effective_strategy = SIMPLE;
	else if (data->inversions < data->pairs / 2 + data->pairs % 2)
		data->effective_strategy = MEDIUM;
	else
		data->effective_strategy = COMPLEX;
}
