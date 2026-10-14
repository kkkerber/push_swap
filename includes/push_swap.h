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

typedef enum e_strategy
{
	SIMPLE,
	MEDIUM,
	COMPLEX,
	ADAPTIVE
}	t_strategy;

typedef struct s_config
{
	t_strategy	requested_strategy;
	int			strategy_set;
	int			bench;
}	t_config;

typedef struct s_stats
{
	unsigned long long	total;
	unsigned long long	sa;
	unsigned long long	sb;
	unsigned long long	ss;
	unsigned long long	pa;
	unsigned long long	pb;
	unsigned long long	ra;
	unsigned long long	rb;
	unsigned long long	rr;
	unsigned long long	rra;
	unsigned long long	rrb;
	unsigned long long	rrr;
}	t_stats;

typedef struct s_data
{
	t_stack				a;
	t_stack				b;
	t_config			config;
	t_stats				stats;
	unsigned long long	inversions;
	unsigned long long	pairs;
	t_strategy			effective_strategy;
}	t_data;

/* Program lifecycle */

void	data_init(t_data *data);
void	data_clear(t_data *data);
int		error(t_data *data);

/* Stack management */

t_node	*node_new(int value);
void	stack_init(t_stack *stack);
void	stack_add_top(t_stack *stack, t_node *node);
void	stack_add_bottom(t_stack *stack, t_node *node);
t_node	*stack_take_top(t_stack *stack);
void	stack_clear(t_stack *stack);
int		stack_is_sorted(t_stack *stack);
int		stack_min_rank_position(t_stack *stack);

/* Ranking: sort_values requires an array of size integers. */

void	sort_values(int *values, int size);
int		assign_ranks(t_stack *stack);

/* Original-input analysis, before any Push_swap operation. */

void	compute_disorder(t_data *data);
void	strategy_select(t_data *data);

/* Small sort: assigned ranks, at most five nodes in A, empty B. */

void	sort_small(t_data *data);

/* Simple: assigned ranks and empty B; shared small sort for sizes <= 5. */

void	sort_simple(t_data *data);

/* Medium: dense ranks 0..n-1 and empty B; helpers shared by its two files. */

void	sort_medium(t_data *data);
void	medium_push_chunk(t_data *data, int limit, int middle);
void	medium_restore(t_data *data);

/* Complex: assigned nonnegative ranks, empty B; small sort for sizes <= 5. */

void	sort_complex(t_data *data);

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
