/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stack_init.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 17:40:13 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 17:48:06 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	stack_init(t_stack *stack)
{
	if (stack == NULL)
		return ;
	stack->top = NULL;
	stack->bottom = NULL;
	stack->size = 0;
	return(stack);
}