/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stack_add.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 17:48:47 by maliuten          #+#    #+#             */
/*   Updated: 2026/09/16 21:03:47 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	stack_add_top(t_stack *stack, t_node *node)
{
	if (stack == NULL || node == NULL)
		return	;
		
	if (stack->size == 0)
	{
		node->next = node;
		node->prev = node;
		stack->top = node;
		stack->bottom = node;
		stack->size = 1;
		return	;
	}
	if (stack->size > 0)
	{
		node->next = stack->top;
		node->prev = stack->bottom;
		stack->bottom->next = node;
		stack->top->prev = node;
		stack->top = node;
		stack->size++;
		return	;
	}
	
}