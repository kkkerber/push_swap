/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   assign_ranks.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 17:27:12 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 17:39:42 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	*copy_values(t_stack *stack)
{
	t_node	*node;
	int		*values;
	int		i;

	if ((size_t)stack->size > (size_t)-1 / sizeof(int))
		return (NULL);
	values = malloc(sizeof(int) * (size_t)stack->size);
	if (!values)
		return (NULL);
	node = stack->top;
	i = 0;
	while (i < stack->size)
	{
		values[i++] = node->value;
		node = node->next;
	}
	return (values);
}

static int	has_duplicates(int *values, int size)
{
	int	i;

	i = 1;
	while (i < size)
	{
		if (values[i - 1] == values[i])
			return (1);
		i++;
	}
	return (0);
}

static void	set_ranks(t_stack *stack, int *values)
{
	t_node	*node;
	int		i;
	int		rank;

	node = stack->top;
	i = 0;
	while (i < stack->size)
	{
		rank = 0;
		while (rank < stack->size && values[rank] != node->value)
			rank++;
		node->rank = rank;
		node = node->next;
		i++;
	}
}

int	assign_ranks(t_stack *stack)
{
	int	*values;

	if (!stack)
		return (0);
	if (stack->size == 0)
		return (1);
	values = copy_values(stack);
	if (!values)
		return (0);
	sort_values(values, stack->size);
	if (has_duplicates(values, stack->size))
	{
		free(values);
		return (0);
	}
	set_ranks(stack, values);
	free(values);
	return (1);
}
