class TicTacToe:
    def __init__(self):
        self.board = [" "] * 9
        self.current_player = "X"

    def print_board(self):
        print("\n Стан поля:")
        for i in range(0, 9, 3):
            row = []
            for j in range(3):
                cell = self.board[i + j]
                row.append(str(i + j + 1) if cell == " " else cell)
            print(f" {row[0]} | {row[1]} | {row[2]} ")
            if i < 6:
                print("---+---+---")
        print()

    def check_winner(self):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Рядки
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Стовпці
            [0, 4, 8], [2, 4, 6]  # Діагоналі
        ]
        for condition in win_conditions:
            if (self.board[condition[0]] == self.board[condition[1]] ==
                    self.board[condition[2]] == self.current_player):
                return True
        return False

    def is_board_full(self):
        return " " not in self.board

    def make_move(self, move):
        try:
            move = int(move) - 1
            if move < 0 or move > 8:
                print("Помилка: введіть число від 1 до 9!")
                return False
            if self.board[move] != " ":
                print("Помилка: ця клітинка вже зайнята!")
                return False
            self.board[move] = self.current_player
            return True
        except ValueError:
            print("Помилка: введіть коректне число!")
            return False

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"

    def play(self):
        print("Ласкаво просимо до гри 'Хрестики-нулики'!")
        print("Вводьте номер клітинки (1-9) для ходу.")

        while True:
            self.print_board()
            move = input(f"Гравець {self.current_player}, ваш хід (1-9): ")

            if not self.make_move(move):
                continue

            if self.check_winner():
                self.print_board()
                print(f"Гравець {self.current_player} переміг!")
                break

            if self.is_board_full():
                self.print_board()
                print("Гра завершилася внічию!")
                break

            self.switch_player()

        while True:
            replay = input("Бажаєте зіграти ще раз? (так/ні): ").lower()
            if replay in ["так", "т"]:
                self.__init__()  # Скидаємо гру
                self.play()
                break
            elif replay in ["ні", "н"]:
                print("Дякуємо за гру!")
                break
            else:
                print("Введіть 'так' або 'ні'.")

if __name__ == "__main__":
    game = TicTacToe()
    game.play()