/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parse_flags.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/16 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/09/16 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "parsing.h"

static int	flag_equal(const char *arg, const char *flag)
{
	while (*arg && *arg == *flag)
	{
		arg++;
		flag++;
	}
	return (*arg == *flag);
}

static int	strategy_flag(const char *arg)
{
	if (flag_equal(arg, "--simple"))
		return (SIMPLE);
	if (flag_equal(arg, "--medium"))
		return (MEDIUM);
	if (flag_equal(arg, "--complex"))
		return (COMPLEX);
	if (flag_equal(arg, "--adaptive"))
		return (ADAPTIVE);
	return (-1);
}

int	parse_flags(const char *arg, t_config *config)
{
	int	strategy;

	if (arg[0] != '-' || arg[1] != '-')
		return (0);
	if (flag_equal(arg, "--bench"))
	{
		if (config->bench)
			return (-1);
		config->bench = 1;
		return (1);
	}
	strategy = strategy_flag(arg);
	if (strategy < 0 || config->strategy_seen)
		return (-1);
	config->strategy = strategy;
	config->strategy_seen = 1;
	return (1);
}
