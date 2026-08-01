NAME := push_swap

CC := cc
CFLAGS := -Wall -Wextra -Werror
CPPFLAGS := -Iincludes -Ift_printf
DEPFLAGS := -MMD -MP

SRC_DIR := src
OBJ_DIR := obj

FT_PRINTF_DIR := ft_printf
FT_PRINTF_LIB := $(FT_PRINTF_DIR)/libftprintf.a

SRCS := $(shell find $(SRC_DIR) -type f -name "*.c")
OBJS := $(patsubst $(SRC_DIR)/%.c,$(OBJ_DIR)/%.o,$(SRCS))
DEPS := $(OBJS:.o=.d)

FT_PRINTF_FILES := $(shell find $(FT_PRINTF_DIR) -type f \
	\( -name "*.c" -o -name "*.h" -o -name "Makefile" \))

all: $(NAME)

$(NAME): $(OBJS) $(FT_PRINTF_LIB)
	$(CC) $(CFLAGS) $(OBJS) $(FT_PRINTF_LIB) -o $(NAME)

$(FT_PRINTF_LIB): $(FT_PRINTF_FILES)
	$(MAKE) -C $(FT_PRINTF_DIR)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(CPPFLAGS) $(DEPFLAGS) -c $< -o $@

clean:
	rm -rf $(OBJ_DIR)
	$(MAKE) -C $(FT_PRINTF_DIR) clean

fclean: clean
	rm -f $(NAME)
	$(MAKE) -C $(FT_PRINTF_DIR) fclean

re: fclean all

-include $(DEPS)

.PHONY: all clean fclean re