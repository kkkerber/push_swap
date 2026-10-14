/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_complex.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/14 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/10/14 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	complex_is_sorted(t_stack *stack)
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

static int	rank_bit_count(t_stack *stack)
{
	t_node	*node;
	int		maximum;
	int		remaining;
	int		bits;

	node = stack->top;
	maximum = 0;
	remaining = stack->size;
	while (remaining-- > 0)
	{
		if (node->rank > maximum)
			maximum = node->rank;
		node = node->next;
	}
	bits = 0;
	while (maximum > 0)
	{
		maximum >>= 1;
		bits++;
	}
	return (bits);
}

static void	radix_pass(t_data *data, int bit)
{
	int	remaining;

	remaining = data->a.size;
	while (remaining-- > 0)
	{
		if ((data->a.top->rank >> bit) & 1)
			ra(data);
		else
			pb(data);
	}
	while (data->b.size > 0)
		pa(data);
}

void	sort_complex(t_data *data)
{
	int	bits;
	int	bit;

	if (!data || data->b.size != 0 || data->a.size < 2
		|| complex_is_sorted(&data->a))
		return ;
	if (data->a.size <= 5)
		return (sort_small(data));
	bits = rank_bit_count(&data->a);
	bit = 0;
	while (bit < bits)
	{
		radix_pass(data, bit);
		bit++;
	}
}
