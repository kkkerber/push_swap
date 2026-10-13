/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sort_values.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 17:27:12 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 17:39:42 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	sort_values(int *values, int size)
{
	int	i;
	int	j;
	int	value;

	i = 1;
	while (i < size)
	{
		value = values[i];
		j = i;
		while (j > 0 && values[j - 1] > value)
		{
			values[j] = values[j - 1];
			j--;
		}
		values[j] = value;
		i++;
	}
}
