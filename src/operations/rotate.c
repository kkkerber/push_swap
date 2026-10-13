/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   rotate.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/13 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/10/13 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	ra(t_data *data)
{
	if (!data || data->a.size < 2)
		return ;
	data->a.top = data->a.top->next;
	data->a.bottom = data->a.bottom->next;
	ft_printf("ra\n");
	data->stats.ra++;
	data->stats.total++;
}

void	rb(t_data *data)
{
	if (!data || data->b.size < 2)
		return ;
	data->b.top = data->b.top->next;
	data->b.bottom = data->b.bottom->next;
	ft_printf("rb\n");
	data->stats.rb++;
	data->stats.total++;
}

void	rr(t_data *data)
{
	if (!data || (data->a.size < 2 && data->b.size < 2))
		return ;
	if (data->a.size > 1)
	{
		data->a.top = data->a.top->next;
		data->a.bottom = data->a.bottom->next;
	}
	if (data->b.size > 1)
	{
		data->b.top = data->b.top->next;
		data->b.bottom = data->b.bottom->next;
	}
	ft_printf("rr\n");
	data->stats.rr++;
	data->stats.total++;
}
