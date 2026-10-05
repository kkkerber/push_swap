/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stack_clear.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maryl <maryl@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/05 11:09:03 by maryl             #+#    #+#             */
/*   Updated: 2026/10/05 11:21:57 by maryl            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	stack_clear(t_stack *stack)
{
    t_node	*current;
    t_node	*next_node;
    int	count;

	if (stack == NULL)
		return ;
	current = stack->top;
    count = stack->size;
    while (count > 0)
    {
        next_node = current->next;
        free(current);
        current = next_node;
        count--;
    }
	stack->top = NULL;
	stack->bottom = NULL;
	stack->size = 0;
}
