/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   swap.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maryl <maryl@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 16:10:01 by maliuten          #+#    #+#             */
/*   Updated: 2026/10/13 17:54:53 by maryl            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	sa(t_data *data)
{
	t_node	*first;
	t_node	*second;

	if (!data || data->a.size < 2)
		return ;
	first = stack_take_top(&data->a);
	second = stack_take_top(&data->a);
	stack_add_top(&data->a, first);
	stack_add_top(&data->a, second);
	ft_printf("sa\n");
	data->stats.sa++;
	data->stats.total++;
}

void	sb(t_data *data)
{
	t_node	*first;
	t_node	*second;

	if (!data || data->b.size < 2)
		return ;
	first = stack_take_top(&data->b);
	second = stack_take_top(&data->b);
	stack_add_top(&data->b, first);
	stack_add_top(&data->b, second);
	ft_printf("sb\n");
	data->stats.sb++;
	data->stats.total++;
}

void	ss(t_data *data)
{
	t_node	*first;
	t_node	*second;

	if (!data || (data->a.size < 2 && data->b.size < 2))
		return ;
	if (data->a.size >= 2)
	{
		first = stack_take_top(&data->a);
		second = stack_take_top(&data->a);
		stack_add_top(&data->a, first);
		stack_add_top(&data->a, second);
	}
	if (data->b.size >= 2)
	{
		first = stack_take_top(&data->b);
		second = stack_take_top(&data->b);
		stack_add_top(&data->b, first);
		stack_add_top(&data->b, second);
	}
	ft_printf("ss\n");
	data->stats.ss++;
	data->stats.total++;
}
