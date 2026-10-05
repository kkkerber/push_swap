/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stack_take.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maryl <maryl@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/05 10:40:24 by maryl             #+#    #+#             */
/*   Updated: 2026/10/05 11:05:27 by maryl            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

t_node	*stack_take_top(t_stack *stack)
{
    t_node  *node;
    t_node  *new_top;

    if (!stack || stack->size == 0)
        return ;
    node = stack->top;
    if (stack->size == 1)
    {
        stack->top = NULL;
        stack->bottom = NULL;
        stack->size = 0;
        node->next = NULL;
        node->prev = NULL;
        return ;
    }
    new_top = node->next;
    stack->top = new_top;
    stack->bottom->next = new_top;
    new_top->prev = stack->bottom;
    node->next = NULL;
    node->prev = NULL;
    stack->size--;
    return (node);
}
