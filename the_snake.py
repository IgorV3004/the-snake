"""Игра Змейка на pygame.

Змейка управляется стрелками и поглощает яблоки: каждое яблоко
увеличивает длину и скорость. Яд уменьшает длину и скорость.
При столкновении с камнем или с самой собой игра начинается заново,
а все объекты перемещаются на новые места.
"""

from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки - светло-бирюзовый:
BORDER_COLOR = (93, 216, 228)

# Цвет яблока - красный:
APPLE_COLOR = (255, 0, 0)

# Цвет яда - синий:
POISON_COLOR = (0, 0, 255)

# Цвет камня - серый:
ROCK_COLOR = (128, 128, 128)

# Цвет змейки - зелёный:
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
START_SPEED = 5

# Шаг увеличения скорости:
INCREMENT_SPEED = 1

# Начальная длина змейки:
START_SNAKE_LENGTH = 1

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, surface=screen, body_color=None):
        """Задаёт поверхность, цвет и начальную позицию в центре поля."""
        self.screen = surface
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw_cell(self, position):
        """Отрисовывает одну клетку сетки с рамкой в переданной позиции."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.screen, self.body_color, rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовывает объект на экране."""
        pass


class RandomCellObject(GameObject):
    """Класс для объекта, появляющегося в случайной клетке."""

    def __init__(self, surface=screen, body_color=None,
                 occupied_positions=()):
        """Создаёт объект и сразу размещает его в свободной клетке."""
        super().__init__(surface, body_color)
        self.randomize_position(occupied_positions)

    def get_random_cell(self):
        """Возвращает координаты случайной клетки."""
        return (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )

    def randomize_position(self, occupied_positions):
        """Выбирает новую позицию, не совпадающую с занятыми клетками."""
        self.position = self.get_random_cell()
        # Генерирует позиции, пока не будет найдена свободная.
        while self.position in occupied_positions:
            self.position = self.get_random_cell()

    def draw(self):
        """Отрисовывает объект в одной клетке."""
        self.draw_cell(self.position)


class Apple(RandomCellObject):
    """Класс яблоко: увеличивает длину и скорость змейки."""

    def __init__(self, surface=screen, body_color=APPLE_COLOR,
                 occupied_positions=()):
        super().__init__(surface, body_color, occupied_positions)


class Poison(RandomCellObject):
    """Класс яд: уменьшает длину и скорость змейки."""

    def __init__(self, surface=screen, body_color=POISON_COLOR,
                 occupied_positions=()):
        super().__init__(surface, body_color, occupied_positions)


class Rock(RandomCellObject):
    """Класс камень: при столкновении с ним игра начинается заново."""

    def __init__(self, surface=screen, body_color=ROCK_COLOR,
                 occupied_positions=()):
        super().__init__(surface, body_color, occupied_positions)


class Snake(GameObject):
    """Класс змейка: хранит положение сегментов, направление и скорость."""

    def __init__(self, surface=screen, body_color=SNAKE_COLOR):
        """Создаёт змейку, которая изначально движется вправо."""
        super().__init__(surface, body_color)
        self.reset(RIGHT)

    def reset(self, direction=None):
        """Сбрасывает змейку в начальное состояние."""
        self.length = START_SNAKE_LENGTH
        self.positions = [self.position]
        # Если направление не передано, выбирается случайное из четырёх.
        self.direction = direction or choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.speed = START_SPEED

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Реализует движение змейки в текущем направлении.
        Новая голова добавляется в начало списка, лишние сегменты
        с конца обрезаются до текущей длины. Края поля замкнуты:
        при выходе за границу змейка появляется с противоположной стороны.
        """
        head_position_x, head_position_y = self.get_head_position()
        dx, dy = self.direction
        self.positions = [
            (
                (head_position_x + GRID_SIZE * dx) % SCREEN_WIDTH,
                (head_position_y + GRID_SIZE * dy) % SCREEN_HEIGHT
            )
        ] + self.positions
        del self.positions[self.length:]

    def draw(self):
        """Отрисовывает все сегменты змейки включая голову."""
        for position in self.positions:
            self.draw_cell(position)

    def update_direction(self):
        """Применяет направление при нажатии на клавишу."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def handle_keys(game_object):
    """Обрабатывает действия пользователя.
    Закрытие окна завершает программу. Стрелки задают следующее
    направление змейки, при этом разворот на 180 градусов запрещён.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def get_occupied(snake, *objects):
    """Возвращает список клеток, занятых змейкой и переданными объектами."""
    return snake.positions + [game_object.position for game_object in objects]


def is_clash(apple, poison, rock, snake):
    """Проверяет на столкновение змейки с объектами и с самой собой.
    Яблоко: змейка растёт и ускоряется, яблоко изменяет местоположение.
    Яд: змейка уменьшается и замедляется (но не меньше минимума),
    яд изменяет местоположение.
    Камень или само тело: змейка сбрасывается, все другие объекты
    изменяют своё местоположение.
    """
    head_position = snake.get_head_position()
    # Проверка столкновения с яблоком.
    if head_position == apple.position:
        apple.randomize_position(get_occupied(snake, poison, rock))
        snake.length += 1
        snake.speed += INCREMENT_SPEED
    # Проверка столкновения с ядом.
    if head_position == poison.position:
        poison.randomize_position(get_occupied(snake, apple, rock))
        if snake.length > 1 and snake.speed > 1:
            snake.length -= 1
            snake.speed -= INCREMENT_SPEED
    # Проверка столкновения с камнем и с самим собой.
    if head_position == rock.position or head_position in snake.positions[1:]:
        snake.reset()
        # Переставляем объекты по очереди, учитывая уже занятые клетки:
        apple.randomize_position(snake.positions)
        poison.randomize_position(get_occupied(snake, apple))
        rock.randomize_position(get_occupied(snake, apple, poison))


def main():
    """Функция, обеспечивающая основную логику игры."""
    pygame.init()
    # Создание объектов: объект не должен попадать на занятые клетки.
    snake = Snake(screen, SNAKE_COLOR)
    apple = Apple(screen, APPLE_COLOR, snake.positions)
    poison = Poison(screen, POISON_COLOR, get_occupied(snake, apple))
    rock = Rock(screen, ROCK_COLOR, get_occupied(snake, apple, poison))

    # Основной игровой цикл.
    while True:
        # Обработка нажатий клавиш и закрытия окна.
        handle_keys(snake)
        # Применение выбранного направления.
        snake.update_direction()
        # Движение змейки.
        snake.move()
        # Проверка и обработка столкновений.
        is_clash(apple, poison, rock, snake)
        # Отрисовка кадра.
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        poison.draw()
        rock.draw()
        snake.draw()
        pygame.display.update()
        # Установка скорости змейки.
        clock.tick(snake.speed)


if __name__ == '__main__':
    main()
