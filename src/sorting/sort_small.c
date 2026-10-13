/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_small.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 17:27:12 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 17:39:42 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	small_is_sorted(t_stack *stack)
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

static void	sort_three(t_data *data)
{
	int	first;
	int	second;
	int	third;

	first = data->a.top->rank;
	second = data->a.top->next->rank;
	third = data->a.bottom->rank;
	if (first > second && first > third)
		ra(data);
	else if (second > first && second > third)
		rra(data);
	if (data->a.top->rank > data->a.top->next->rank)
		sa(data);
}

static int	minimum_position(t_stack *stack)
{
	t_node	*node;
	int		minimum;
	int		position;
	int		i;

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

static void	move_minimum(t_data *data)
{
	int	position;

	position = minimum_position(&data->a);
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

void	sort_small(t_data *data)
{
	if (!data || data->b.size != 0 || data->a.size > 5
		|| data->a.size < 2 || small_is_sorted(&data->a))
		return ;
	if (data->a.size == 2)
	{
		sa(data);
		return ;
	}
	while (data->a.size > 3)
		move_minimum(data);
	sort_three(data);
	while (data->b.size > 0)
		pa(data);
}
