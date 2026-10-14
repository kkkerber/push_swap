/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_medium.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/14 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/10/14 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	chunk_width(int size)
{
	int	width;

	width = 1;
	while (width + 1 <= size / (width + 1))
		width++;
	return (width);
}

static int	medium_is_sorted(t_stack *stack)
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

void	sort_medium(t_data *data)
{
	int	width;
	int	limit;
	int	count;

	if (!data || data->b.size != 0 || data->a.size < 2
		|| medium_is_sorted(&data->a))
		return ;
	if (data->a.size <= 5)
		return (sort_small(data));
	width = chunk_width(data->a.size);
	limit = 0;
	while (data->a.size > 0)
	{
		count = width;
		if (count > data->a.size)
			count = data->a.size;
		limit += count;
		medium_push_chunk(data, limit, limit - count / 2);
	}
	medium_restore(data);
}
