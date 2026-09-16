/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   token_count.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/16 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/09/16 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "parsing.h"

int	parse_is_space(char c)
{
	return (c == ' ' || (c >= '\t' && c <= '\r'));
}

int	token_count(const char *arg)
{
	int	count;

	count = 0;
	while (*arg)
	{
		while (parse_is_space(*arg))
			arg++;
		if (*arg)
		{
			if (count == INT_MAX)
				return (-1);
			count++;
			while (*arg && !parse_is_space(*arg))
				arg++;
		}
	}
	return (count);
}
