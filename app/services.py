
class Services:

    def sample(self):
        board = []
        for i in range(6):  # create a list with nested lists
            board.append([])
            print(board)
            for n in range(6):
                board[i].append("O")

        print(board)
        return board
