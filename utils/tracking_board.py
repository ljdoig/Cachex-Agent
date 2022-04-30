from referee.board import Board
from utils.player_logic import parse, action_to_move, move_to_action

_ACTION_STEAL = "STEAL"
_ACTION_PLACE = "PLACE"

_OPPONENT = {"red": "blue", "blue": "red", None: None}


class TrackingBoard(Board):
    def __init__(self, player, n):
        super().__init__(n)
        self.player = player
        self.move_history = []
        self.possible_moves = {(p, r) for p in range(n) for r in range(n)}
        if n % 2 == 1:
            self.centre = (n // 2, n // 2)
            self.possible_moves.remove(self.centre)
        else:
            self.centre = None

    def update(self, player, action):
        move = action_to_move(action)
        if len(self.move_history) == 1:
            self.possible_moves.remove(_ACTION_STEAL)
        if move == _ACTION_STEAL:
            self.swap()
            last_captures = None
            self.possible_moves = {(r, p) for p, r in self.possible_moves}
        else:
            self.possible_moves.remove(move)
            last_captures = self.place(player, move)
            if len(last_captures) != 0:
                for captured_coord in last_captures:
                    self.possible_moves.add(captured_coord)
            if len(self.move_history) == 0:
                self.possible_moves.add(_ACTION_STEAL)
                if self.centre is not None:
                    self.possible_moves.add(self.centre)
        print(self.possible_moves)
        self.move_history.append((move, player, last_captures))

    def undo_last_move(self):
        move, player, last_captures = self.move_history.pop(-1)
        if move == _ACTION_STEAL:
            self.unswap()
        else:
            self.unplace(move, player, last_captures)

    def unswap(self):
        self.swap()
        self.possible_moves = {(r, p) for p, r in self.possible_moves}
        self.possible_moves.add(_ACTION_STEAL)

    def unplace(self, coord, player, last_captures):
        self[coord] = None
        self.possible_moves.add(coord)
        if len(last_captures) != 0:
            for captured_coord in last_captures:
                self[captured_coord] = _OPPONENT[player]
                self.possible_moves.remove(captured_coord)
        elif len(self.move_history) == 0:
            self.possible_moves.remove(_ACTION_STEAL)
            if self.centre is not None:
                self.possible_moves.remove(self.centre)
        elif len(self.move_history) == 1:
            self.possible_moves.add(_ACTION_STEAL)

    # def get_greedy_move(self):
    #     return max(self.possible_moves, key=lambda move: self.evaluate_after_move(move))
    #
    # def evaluate_after_move(self, move):
    #     self.update(move)
    #     value = self.evaluate()
    #     self.undo_last_move()
    #     return value