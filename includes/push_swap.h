/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maryl <maryl@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/21 18:47:24 by maryl             #+#    #+#             */
/*   Updated: 2026/07/23 21:44:11 by maryl            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PUSH_SWAP_H
# define PUSH_SWAP_H

# include <stdlib.h>
# include <unistd.h>

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
//container of the state of program, need to add more states later
typedef struct s_data
{
	t_stack	*a;
	t_stack	*b;
}	t_data;

t_node	*node_new(int value);
void	stack_add_back(t_node **stack, t_node *new_node);
t_node	*stack_last(t_node *stack);
size_t	stack_size(t_node *stack);
void	stack_clear(t_node **stack);

void	swap_stack(t_node **stack);
void	push_stack(t_node **dst, t_node **src);
void	rotate_stack(t_node **stack);
void	reverse_rotate_stack(t_node **stack);

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