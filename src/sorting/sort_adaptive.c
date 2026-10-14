/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_adaptive.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/14 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/10/14 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	sort_adaptive(t_data *data)
{
	if (!data || data->b.size != 0)
		return ;
	strategy_select(data);
	if (data->effective_strategy == SIMPLE)
		sort_simple(data);
	else if (data->effective_strategy == MEDIUM)
		sort_medium(data);
	else if (data->effective_strategy == COMPLEX)
		sort_complex(data);
}
