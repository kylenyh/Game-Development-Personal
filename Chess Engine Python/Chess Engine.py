class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.inCheckFlag = False  # Rename to avoid conflict with method name
        self.enpassantPossible = ()  # coordinates for the square where an en passant capture is possible 
        self.enpassantPossible_log = [self.enpassantPossible]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                             self.currentCastlingRights.bks, self.currentCastlingRights.bqs)]
        self.recursionFlag = False



    def fen(self):
            fen = ""
            for row in self.board:
                empty_squares = 0
                for square in row:
                    if square == "--":
                        empty_squares += 1
                    else:
                        if empty_squares > 0:
                            fen += str(empty_squares)
                            empty_squares = 0
                        fen += square[1].upper() if square[0] == 'w' else square[1].lower()
                if empty_squares > 0:
                    fen += str(empty_squares)
                fen += "/"
            fen = fen[:-1]  # remove trailing slash

            fen += " w" if self.whiteToMove else " b"

            castling_rights = ""
            if self.currentCastlingRights.wks:
                castling_rights += "K"
            if self.currentCastlingRights.wqs:
                castling_rights += "Q"
            if self.currentCastlingRights.bks:
                castling_rights += "k"
            if self.currentCastlingRights.bqs:
                castling_rights += "q"
            if castling_rights == "":
                castling_rights = "-"
            fen += " " + castling_rights

            if self.enpassantPossible:
                fen += " " + self.getRankFile(self.enpassantPossible[0], self.enpassantPossible[1])
            else:
                fen += " -"

            fen += " 0 1"  # halfmove clock and fullmove number, these can be more accurately implemented if needed
            return fen
        




    def getRankFile(self, row, col):
            ranksToRows = {7: "1", 6: "2", 5: "3", 4: "4", 3: "5", 2: "6", 1: "7", 0: "8"}
            filesToCols = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
            return filesToCols[col] + ranksToRows[row]



    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        # Handle castling
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # King-side castling
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            elif move.endCol - move.startCol == -2:  # Queen-side castling
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

        # Update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False

        self.enpassantPossible_log.append(self.enpassantPossible)

        # Update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                                self.currentCastlingRights.bks, self.currentCastlingRights.bqs))

        # Handle en passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        # Handle pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # Update en passant possibility
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()








    def updateCastleRights(self, move):
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False










    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # Swap players

            # Update the king's location if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)

            # Undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            self.enpassantPossible_log.pop()
            self.enpassantPossible = self.enpassantPossible_log[-1]

            # Undo castle rights
            self.castleRightsLog.pop()  # Get rid of the new castle rights from the move we are undoing
            self.currentCastlingRights = self.castleRightsLog[-1]  # Set the current castle rights to the last one in the list

            # Undo the castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # King-side
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # Queen-side
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'
            self.checkMate = False
            self.staleMate = False









    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                        self.currentCastlingRights.bks, self.currentCastlingRights.bqs)

        moves = self.getAllPossibleMoves()
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights

        return moves





    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])










    def squareUnderAttack(self, row, col):
        if self.recursionFlag:
            return False

        self.recursionFlag = True
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        self.recursionFlag = False

        for move in oppMoves:
            if move.endRow == row and move.endCol == col:
                return True
        return False









    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)
        return moves










    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(row, col, moves)








    def getKingsideCastleMoves(self, row, col, moves):
        if col + 2 <= 7:
            if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
                if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                    moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove=True))








    def getQueensideCastleMoves(self, row, col, moves):
        if col - 3 >= 0:
            if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--":
                if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                    moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))








    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove:
            if self.board[row - 1][col] == "--":
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--" and self.board[row - 1][col] == "--":
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == "b":
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
                elif (row - 1, col - 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row - 1, col - 1), self.board, isEnpassantMove=True)) 
            if col + 1 <= 7:
                if self.board[row - 1][col + 1][0] == "b":
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
                elif (row - 1, col + 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row - 1, col + 1), self.board, isEnpassantMove=True)) 
        else:
            if self.board[row + 1][col] == "--":
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--" and self.board[row + 1][col] == "--":
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
                elif (row + 1, col - 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row + 1, col - 1), self.board, isEnpassantMove=True)) 
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
                elif (row + 1, col + 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row + 1, col + 1), self.board, isEnpassantMove=True)) 









    def getRookMoves(self, row, col, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row, end_col = row + d[0] * i, col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    else:
                        break









    def getKnightMoves(self, row, col, moves):
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        ally_color = "w" if self.whiteToMove else "b"
        for m in knight_moves:
            end_row, end_col = row + m[0], col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == "--" or end_piece[0] != ally_color:
                    moves.append(Move((row, col), (end_row, end_col), self.board))










    def getBishopMoves(self, row, col, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row, end_col = row + d[0] * i, col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    else:
                        break









    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)









    def getKingMoves(self, row, col, moves):
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        ally_color = "w" if self.whiteToMove else "b"
        for m in king_moves:
            end_row, end_col = row + m[0], col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == "--" or end_piece[0] != ally_color:
                    if not self.squareUnderAttack(end_row, end_col):
                        print(f"King move to {end_row}, {end_col} is valid")  # Debug statement
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    else:
                        print(f"King move to {end_row}, {end_col} is under attack")  # Debug statement
                else:
                    print(f"King move to {end_row}, {end_col} blocked by ally")  # Debug statement
            else:
                print(f"King move to {end_row}, {end_col} out of bounds")  # Debug statement

        self.getCastleMoves(row, col, moves)










class CastleRights:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs








class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}









    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # Pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        # En passant 
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        # castling
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
      
      
      
      
      
      
      
        
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False







    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)






    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]






# Instantiate the game state to test functionality
game_state = GameState()
valid_moves = game_state.getValidMoves()
for move in valid_moves:
    print(f"Valid move: {move.getChessNotation()}")





# Example move to test castling (assuming appropriate conditions are met)
example_castle_move = Move((7, 4), (7, 6), game_state.board, isCastleMove=True)
game_state.makeMove(example_castle_move)
print(f"Board after castling: {game_state.board}")
