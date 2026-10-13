/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   build_values.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/16 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/09/16 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "parsing.h"

int	build_values(int argc, char **argv, t_input *input)
{
	const char	*cursor;
	int			i;
	int			index;

	i = 0;
	index = 0;
	while (++i < argc)
	{
		cursor = argv[i];
		if (cursor[0] == '-' && cursor[1] == '-')
			continue ;
		while (*cursor)
		{
			while (parse_is_space(*cursor))
				cursor++;
			if (*cursor && (index >= input->count
					|| !parse_integer(&cursor, &input->values[index++])))
				return (0);
		}
	}
	return (index == input->count);
}
