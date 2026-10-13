/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parse_integer.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/16 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/09/16 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "parsing.h"

static int	parse_digits(const char **cursor, unsigned int limit,
		unsigned int *number)
{
	unsigned int	digit;

	*number = 0;
	if (**cursor < '0' || **cursor > '9')
		return (0);
	while (**cursor >= '0' && **cursor <= '9')
	{
		digit = **cursor - '0';
		if (*number > (limit - digit) / 10)
			return (0);
		*number = *number * 10 + digit;
		(*cursor)++;
	}
	return (**cursor == '\0' || parse_is_space(**cursor));
}

int	parse_integer(const char **cursor, int *value)
{
	unsigned int	number;
	unsigned int	limit;
	int				negative;

	while (parse_is_space(**cursor))
		(*cursor)++;
	negative = (**cursor == '-');
	if (**cursor == '-' || **cursor == '+')
		(*cursor)++;
	limit = INT_MAX;
	if (negative)
		limit = (unsigned int)INT_MAX + 1;
	if (!parse_digits(cursor, limit, &number))
		return (0);
	if (negative && number == (unsigned int)INT_MAX + 1)
		*value = INT_MIN;
	else if (negative)
		*value = -(int)number;
	else
		*value = (int)number;
	return (1);
}
