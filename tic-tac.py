from typing import List

def tic_tac_toe_checker(board: List[List[str]]) -> str:
    # Проверка столбцов и строк
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != "-":
            return f"{board[i][0]} ура победа!"
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != "-":
            return f"{board[0][i]} ура победа!"

    # Проверка диагоналей
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != "-":
        return f"{board[0][0]} ура победа!"
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != "-":
        return f"{board[0][2]} ура победа!"

    # Проверка на незавершённую игру
    for row in board:
        if "-" in row:
            return "unfinished!"

    # Если нет победителя и есть только заполненные клетки, это ничья
    return "ничья!"

if __name__ == '__main__':
    #табло
    board = [
        ["-", "-", "o"],
        ["-", "x", "o"],
        ["x", "o", "x"]
    ]
    print(tic_tac_toe_checker(board))
