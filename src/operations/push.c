/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maryl <maryl@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 16:10:01 by maliuten          #+#    #+#             */
/*   Updated: 2026/10/13 17:54:53 by maryl            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	pa(t_data *data)
{
	t_node	*node;

	if (!data || data->b.size == 0)
		return ;
	node = stack_take_top(&data->b);
	stack_add_top(&data->a, node);
	ft_printf("pa\n");
	data->stats.pa++;
	data->stats.total++;
}

void	pb(t_data *data)
{
	t_node	*node;

	if (!data || data->a.size == 0)
		return ;
	node = stack_take_top(&data->a);
	stack_add_top(&data->b, node);
	ft_printf("pb\n");
	data->stats.pb++;
	data->stats.total++;
}
