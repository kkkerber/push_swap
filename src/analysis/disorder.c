/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   disorder.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 17:27:12 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 17:39:42 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static unsigned long long	count_later_inversions(t_node *node, int remaining)
{
	t_node				*other;
	unsigned long long	count;

	other = node->next;
	count = 0;
	while (remaining > 0)
	{
		if (node->value > other->value)
			count++;
		other = other->next;
		remaining--;
	}
	return (count);
}

void	compute_disorder(t_data *data)
{
	t_node				*node;
	unsigned long long	size;
	int					remaining;

	if (!data)
		return ;
	data->inversions = 0;
	data->pairs = 0;
	if (data->a.size < 2)
		return ;
	size = data->a.size;
	data->pairs = size * (size - 1) / 2;
	node = data->a.top;
	remaining = data->a.size - 1;
	while (remaining > 0)
	{
		data->inversions += count_later_inversions(node, remaining);
		node = node->next;
		remaining--;
	}
}
