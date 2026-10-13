/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stack_search.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 17:27:12 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 17:39:42 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	stack_min_rank_position(t_stack *stack)
{
	t_node	*node;
	int		minimum;
	int		position;
	int		i;

	if (!stack || stack->size == 0)
		return (-1);
	node = stack->top;
	minimum = node->rank;
	position = 0;
	i = 0;
	while (i < stack->size)
	{
		if (node->rank < minimum)
		{
			minimum = node->rank;
			position = i;
		}
		node = node->next;
		i++;
	}
	return (position);
}
