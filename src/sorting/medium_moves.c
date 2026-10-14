/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   medium_moves.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/14 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/10/14 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	chunk_position(t_stack *stack, int limit)
{
	t_node	*node;
	int		position;

	node = stack->top;
	position = 0;
	while (position < stack->size && node->rank >= limit)
	{
		node = node->next;
		position++;
	}
	if (position > stack->size / 2)
		position -= stack->size;
	return (position);
}

static void	align_chunk(t_data *data, int position, int bury)
{
	if (bury && position > 0)
	{
		rr(data);
		position--;
	}
	else if (bury && position < 0 && data->b.size == 2)
	{
		rrr(data);
		position++;
	}
	else if (bury)
		rb(data);
	while (position > 0)
	{
		ra(data);
		position--;
	}
	while (position < 0)
	{
		rra(data);
		position++;
	}
}

void	medium_push_chunk(t_data *data, int limit, int middle)
{
	int	bury;

	bury = 0;
	while (data->b.size < limit)
	{
		align_chunk(data, chunk_position(&data->a, limit), bury);
		pb(data);
		bury = (data->b.top->rank < middle && data->b.size > 1);
	}
	if (bury)
		rb(data);
}

static int	maximum_position(t_stack *stack)
{
	t_node	*node;
	int		maximum;
	int		position;
	int		i;

	node = stack->top;
	maximum = node->rank;
	position = 0;
	i = 0;
	while (i < stack->size)
	{
		if (node->rank > maximum)
		{
			maximum = node->rank;
			position = i;
		}
		node = node->next;
		i++;
	}
	if (position > stack->size / 2)
		position -= stack->size;
	return (position);
}

void	medium_restore(t_data *data)
{
	int	position;

	while (data->b.size > 0)
	{
		position = maximum_position(&data->b);
		while (position > 0)
		{
			rb(data);
			position--;
		}
		while (position < 0)
		{
			rrb(data);
			position++;
		}
		pa(data);
	}
}
