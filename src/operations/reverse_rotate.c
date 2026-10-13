/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   reverse_rotate.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/13 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/10/13 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	rra(t_data *data)
{
	if (!data || data->a.size < 2)
		return ;
	data->a.top = data->a.top->prev;
	data->a.bottom = data->a.bottom->prev;
	ft_printf("rra\n");
	data->stats.rra++;
	data->stats.total++;
}

void	rrb(t_data *data)
{
	if (!data || data->b.size < 2)
		return ;
	data->b.top = data->b.top->prev;
	data->b.bottom = data->b.bottom->prev;
	ft_printf("rrb\n");
	data->stats.rrb++;
	data->stats.total++;
}

void	rrr(t_data *data)
{
	if (!data || (data->a.size < 2 && data->b.size < 2))
		return ;
	if (data->a.size > 1)
	{
		data->a.top = data->a.top->prev;
		data->a.bottom = data->a.bottom->prev;
	}
	if (data->b.size > 1)
	{
		data->b.top = data->b.top->prev;
		data->b.bottom = data->b.bottom->prev;
	}
	ft_printf("rrr\n");
	data->stats.rrr++;
	data->stats.total++;
}
