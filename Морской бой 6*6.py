from random import randint
# Формируем класс для точки
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class BoardException(Exception): #общий класс, содержит в себе все остальные виды исключений
    pass


class BoardOutException(BoardException):
    def __str__(self): return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self): return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException): #исключение только для того, что бы размещать нормально корабли
    pass

# Формируем класс для корабля


class Ship:
    def __init__(self, long, bow, direction):
        self.long = long
        self.bow = bow
        self.direction = direction
        self.health = long

    @property
    def dots(self):
        ship_list = []
        for i in range(self.long):
            point_x = self.bow.x
            point_y = self.bow.y

            if self.direction == 0:
                point_x += i

            elif self.direction == 1:
                point_y += i

            ship_list.append(Dot(point_x, point_y))

        return ship_list

    def shooten(self, shot):
        return shot in self.dots


# Формируем класс для доски
class Board:
    def __init__(self, size=6, hid=False):
        self.size = size
        self.hid = hid
        self.field = [["O"] * size for i in range(size)]

        self.count = 0  # количество пораженных кораблей

        self.busy = []  # занятые точки (кораблем или вывстрелом)
        self.ships = []  # список кораблей доски

    def add_ship(self, ship):  # проверяет что каждая точка корабля не выходт за границы и не занята, иначе исключение!
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:  # проходим по всем точкам корабля и ставим квадрат, так же добавляем в список занятых
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)  # добавляем список собственных кораблей
        self.contour(ship)  # обводим его по контуру

    def contour(self, ship,
                verb=False):  # метод помечает соседние клетки от кораблей, для того что бы нельзя было поставить корабли рядом
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        numbering = ""
        numbering += " | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            numbering += f"\n{i + 1} | " + " | ".join(row) + " |"

        return numbering

    def out(self, d):  # проверяет находится ли точка за пределами доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):  # выстрел
        if self.out(d):  # если точка выходит за границы
            raise BoardOutException()

        if d in self.busy:  # если точка уже занята
            raise BoardUsedException()

        self.busy.append(d)  # говорим что точка занята, теперь

        for ship in self.ships:
            if d in ship.dots:  # если корабль подстрелен
                ship.lives -= 1  # уменьшаем длинну корабля
                self.field[d.x][d.y] = "X"  # ставим Х на место ранения
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False  # возвращаем False т.к. дальше нет хода
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):  # когда начинаем игру, список бизи надо обнулить
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):  # при попытке вызвать его будет еррор, он должен быть у потомков этого класса
        raise NotImplementedError()

    def move(self):  # пытаемся сделать выстрел в бесконечном цикле
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AL(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход").split()
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AL(co, pl)  # игрок принявший доску co
        self.us = User(pl, co)  # игрок принявший доску pl

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):  # ставим корабли
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:  # в бесконечном цикле для каждой длинны корабля
            while True:
                attempts += 1
                if attempts > 2000:  # если количетво попыток создать доску больше 2 тысяч вернем НОН
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):  # игровой цикл
        num = 0
        while True:  # если номер хода четный - пользователь, иначе комп
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()  # нужно ли повторить ход
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():  # количетсво пораженных короблей
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.defeat():
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
