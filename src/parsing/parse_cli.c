/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parse_cli.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/16 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/09/16 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "parsing.h"

static void	input_init(t_input *input)
{
	input->values = NULL;
	input->count = 0;
	input->config.strategy = ADAPTIVE;
	input->config.strategy_seen = 0;
	input->config.bench = 0;
}

void	input_clear(t_input *input)
{
	if (!input)
		return ;
	free(input->values);
	input_init(input);
}

static int	count_values(int argc, char **argv, t_input *input)
{
	int	i;
	int	flag;
	int	count;

	i = 1;
	while (i < argc)
	{
		flag = parse_flags(argv[i], &input->config);
		if (flag < 0)
			return (0);
		if (!flag)
		{
			count = token_count(argv[i]);
			if (count <= 0 || input->count > INT_MAX - count)
				return (0);
			input->count += count;
		}
		i++;
	}
	return (argc == 1 || input->count > 0);
}

int	parse_cli(int argc, char **argv, t_input *input)
{
	if (!input)
		return (0);
	input_init(input);
	if (argc < 1 || !argv || !count_values(argc, argv, input))
		return (input_clear(input), 0);
	if (input->count == 0)
		return (1);
	if ((size_t)input->count > (size_t)-1 / sizeof(int))
		return (input_clear(input), 0);
	input->values = malloc(sizeof(int) * (size_t)input->count);
	if (!input->values || !build_values(argc, argv, input)
		|| !validate_input(input->values, input->count))
		return (input_clear(input), 0);
	return (1);
}
