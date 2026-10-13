/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   build_stack.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/13 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/10/13 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "parsing.h"

static int	build_stack(t_stack *stack, const t_input *input)
{
	t_node	*node;
	int		i;

	i = 0;
	while (i < input->count)
	{
		node = node_new(input->values[i]);
		if (!node)
			return (0);
		stack_add_bottom(stack, node);
		i++;
	}
	return (1);
}

int	parse_input(int argc, char **argv, t_data *data)
{
	t_input	input;

	if (!data)
		return (0);
	if (!parse_cli(argc, argv, &input))
		return (data_clear(data), 0);
	if (!build_stack(&data->a, &input))
	{
		input_clear(&input);
		return (data_clear(data), 0);
	}
	data->config = input.config;
	input_clear(&input);
	return (1);
}
