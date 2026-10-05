/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stack_state.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maryl <maryl@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/05 11:23:40 by maryl             #+#    #+#             */
/*   Updated: 2026/10/05 13:19:52 by maryl            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	stack_is_sorted(t_stack *stack)
{
	t_node	*current;
	int	i;

	if (!stack || stack->size < 2)
		return (1);
	current = stack->top;
	i = stack->size - 1;
	while (i > 0)
	{
		if (current->value > current->next->value)
			return (0);
		current = current->next;
		i--;
	}
	return (1);
}