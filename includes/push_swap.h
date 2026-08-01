/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 17:25:55 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 17:26:41 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PUSH_SWAP_H
# define PUSH_SWAP_H

# include <stdlib.h>
# include <unistd.h>
# include "ft_printf.h"

typedef struct s_node
{
	int				value;
	int				rank;
	struct s_node	*next;
	struct s_node	*prev;
}	t_node;

typedef struct s_stack
{
	t_node	*top;
	t_node	*bottom;
	int		size;
}	t_stack;

typedef struct s_data
{
	t_stack	a;
	t_stack	b;
}	t_data;

/* Stack management */

t_node	*node_new(int value);
void	stack_init(t_stack *stack);
void	stack_add_top(t_stack *stack, t_node *node);
void	stack_add_bottom(t_stack *stack, t_node *node);
t_node	*stack_take_top(t_stack *stack);
void	stack_clear(t_stack *stack);
int		stack_is_sorted(t_stack *stack);

/* Push_swap commands */

void	sa(t_data *data);
void	sb(t_data *data);
void	ss(t_data *data);
void	pa(t_data *data);
void	pb(t_data *data);
void	ra(t_data *data);
void	rb(t_data *data);
void	rr(t_data *data);
void	rra(t_data *data);
void	rrb(t_data *data);
void	rrr(t_data *data);

#endif