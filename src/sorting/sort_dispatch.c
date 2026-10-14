/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_dispatch.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/14 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/10/14 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	ranks_are_sorted(t_stack *stack)
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

void	sort_dispatch(t_data *data)
{
	if (!data || data->b.size != 0)
		return ;
	strategy_select(data);
	if (data->a.size < 2 || ranks_are_sorted(&data->a))
		return ;
	if (data->a.size <= 5)
		sort_small(data);
	else if (data->config.requested_strategy == ADAPTIVE)
		sort_adaptive(data);
	else if (data->effective_strategy == SIMPLE)
		sort_simple(data);
	else if (data->effective_strategy == MEDIUM)
		sort_medium(data);
	else if (data->effective_strategy == COMPLEX)
		sort_complex(data);
}
