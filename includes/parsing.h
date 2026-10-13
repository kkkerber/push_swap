/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parsing.h                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: vakhapil <vakhapil@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/16 19:00:00 by vakhapil          #+#    #+#             */
/*   Updated: 2026/09/16 19:00:00 by vakhapil         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PARSING_H
# define PARSING_H

# include <limits.h>
# include "push_swap.h"

typedef struct s_input
{
	int			*values;
	int			count;
	t_config	config;
}	t_input;

int		parse_input(int argc, char **argv, t_data *data);
int		parse_cli(int argc, char **argv, t_input *input);
void	input_clear(t_input *input);
int		parse_flags(const char *arg, t_config *config);
int		parse_is_space(char c);
int		token_count(const char *arg);
int		parse_integer(const char **cursor, int *value);
int		build_values(int argc, char **argv, t_input *input);
int		validate_input(const int *values, int count);

#endif
