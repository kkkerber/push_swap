/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: maliuten <maliuten@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/01 16:15:27 by maliuten          #+#    #+#             */
/*   Updated: 2026/08/01 16:46:24 by maliuten         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "parsing.h"

int	main(int argc, char **argv)
{
	t_data	data;

	data_init(&data);
	if (!parse_input(argc, argv, &data) || !assign_ranks(&data.a))
		return (error(&data));
	compute_disorder(&data);
	strategy_select(&data);
	if (data.a.size <= 5)
		sort_small(&data);
	data_clear(&data);
	return (0);
}
