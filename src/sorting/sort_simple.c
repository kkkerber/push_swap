/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_simple.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 17:27:12 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 17:39:42 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	simple_is_sorted(t_stack *stack)
{
	t_node	*node;
	int		remaining;

	node = stack->top;
	remaining = stack->size - 1;
	while (remaining > 0)
	{
		if (node->rank > node->next->rank)
			return (0);
		node = node->next;
		remaining--;
	}
	return (1);
}

static void	move_minimum(t_data *data)
{
	int	position;

	position = stack_min_rank_position(&data->a);
	if (position <= data->a.size / 2)
	{
		while (position > 0)
		{
			ra(data);
			position--;
		}
	}
	else
	{
		position = data->a.size - position;
		while (position > 0)
		{
			rra(data);
			position--;
		}
	}
	pb(data);
}

void	sort_simple(t_data *data)
{
	if (!data || data->b.size != 0 || data->a.size < 2
		|| simple_is_sorted(&data->a))
		return ;
	if (data->a.size <= 5)
	{
		sort_small(data);
		return ;
	}
	while (data->a.size > 0)
		move_minimum(data);
	while (data->b.size > 0)
		pa(data);
}
