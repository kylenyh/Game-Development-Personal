import sys
import pygame as py
from ChessEngine import GameState, Move
import SmartFinder






py.init()
width, height = 850, 600  # Size of the chess game window
dimension = 8  # Dimensions of a chess board are 8x8
square_size = height // dimension
move_log_panel_width = 250
move_log_panel_height = 600
max_fps = 100
images = {}  # Global dictionary of images








def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        images[piece] = py.transform.scale(py.image.load("images/" + piece + ".png"), (square_size, square_size))







def main():
    screen = py.display.set_mode((width, height))
    clock = py.time.Clock()
    moveLogfont = py.font.SysFont("Arial", 12, False, False)
    loadImages()
    game_state = GameState()
    validMoves = game_state.getValidMoves()
    moveMade = False  # Flag variable for when a move is made
    running = True
    square_selected = ()  # No square is selected, keeps track of the last click of the user
    player_clicks = []  # Keeps track of player clicks (two tuples: [(6, 4), (4, 4)])
    gameOver = False  # Game is not over yet
    playerOne = True # If a human is playing white, then this will be true. If an AI is playing, then this will be false 
    playerTwo = False # Same as above but for black

    while running:
        humanTurn = (game_state.whiteToMove and playerOne) or (not game_state.whiteToMove and playerTwo)
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = py.mouse.get_pos()  # Get mouse position
                    col = location[0] // square_size
                    row = location[1] // square_size
                    print(f"Clicked on square: {row, col}")
                    if square_selected:
                        player_clicks.append((row, col))  # Append second click
                        print(f"Player clicks: {player_clicks}")
                        if len(player_clicks) == 2:  # Two clicks = one move attempt
                            start_row, start_col = player_clicks[0]
                            end_row, end_col = player_clicks[1]
                            move = Move((start_row, start_col), (end_row, end_col), game_state.board)
                            if move in validMoves:
                                for i in range(len(validMoves)):
                                    if move == validMoves[i]:
                                        move.isCastleMove = validMoves[i].isCastleMove  # Set castle move attribute
                                        break
                                print(f"Executing move from {start_row, start_col} to {end_row, end_col}")
                                game_state.makeMove(move)  # Make the move
                                moveMade = True
                                square_selected = ()  # Reset selection
                            else:
                                print(f"Move not valid")
                            square_selected = ()  # Reset selection
                            player_clicks = []  # Clear clicks
                    else:
                        square_selected = (row, col)  # First click
                        player_clicks = [square_selected]
                    
            elif event.type == py.KEYDOWN:
                if event.key == py.K_z:  # Undo with 'z'
                    game_state.undoMove()
                    moveMade = True
                if event.key == py.K_r:  # reset the game when 'r' is pressed
                    game_state = GameState()
                    validMoves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    moveMade = False
                    gameOver = False
                    print("Game reset")
                if event.key == py.K_s:  # Surrender with 's'
                    gameOver = True
                    if game_state.whiteToMove:
                        drawText(screen, "White surrenders. Black wins!")
                    else:
                        drawText(screen, "Black surrenders. White wins!")
                    
        # AI move finder 
        if not gameOver and not humanTurn:
            AI_move = SmartFinder.findBestMove(game_state, validMoves)
            if AI_move is None:
                AI_move = SmartFinder.findRandomMove(validMoves)
                print("Random move made by AI:", AI_move.getChessNotation())
            else:
                print("API best move:", AI_move.getChessNotation())
            game_state.makeMove(AI_move)
            moveMade = True


        if moveMade:
            validMoves = game_state.getValidMoves()  # Recalculate valid moves if necessary
            moveMade = False  # Reset the flag after updating
        
        if not gameOver:
            drawGameState(screen, game_state, validMoves, square_selected, moveLogfont)

        if game_state.checkMate:
            gameOver = True
            if game_state.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif game_state.staleMate:
            gameOver = True
            drawText(screen, "Stalemate, game ends in a draw")
        elif game_state.inCheck():
            highlightKing(screen, game_state, True)
        else:
            highlightKing(screen, game_state, False)

        py.display.flip()
        clock.tick(max_fps)










def highlightSquare(screen, GameState, ValidMoves, square_selected):
    if square_selected != ():
        row, col = square_selected
        if GameState.board[row][col][0] == ('w' if GameState.whiteToMove else 'b'):
            highlighted_square = py.Surface((square_size, square_size))
            highlighted_square.set_alpha(100)
            highlighted_square.fill(py.Color("blue"))
            screen.blit(highlighted_square, (col * square_size, row * square_size))
            highlighted_square.fill(py.Color("yellow"))
            for move in ValidMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(highlighted_square, (move.endCol * square_size, move.endRow * square_size))
                    
   
   
   
   
   
                    
def drawMoveLog(screen, game_state, font):
    moveLogRect = py.Rect(width - move_log_panel_width, 0, move_log_panel_width, move_log_panel_height)
    py.draw.rect(screen, py.Color('black'), moveLogRect)
    moveLog = game_state.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + moveLog[i].getChessNotation() + " "
        if i + 1 < len(moveLog):  # Make sure the second move is valid
            moveString += moveLog[i + 1].getChessNotation()
            if moveLog[i + 1].pieceCaptured != "--":
                moveString += " x" + moveLog[i + 1].pieceCaptured[1].upper()
        moveTexts.append(moveString)
    
    padding = 5
    textY = padding
    lineSpacing = 2
    for i in range(len(moveTexts)):
        text = font.render(moveTexts[i], True, py.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(text, textLocation)
        textY += text.get_height() + lineSpacing

  
   
    



def drawGameState(screen, game_state, validMoves, square_selected, moveLogFont):
    drawBoard(screen)
    drawMoveLog(screen, game_state, moveLogFont)
    highlightSquare(screen, game_state, validMoves, square_selected)
    for row in range(dimension):
        for col in range(dimension):
            piece = game_state.board[row][col]
            if piece != "--":  # Draw piece if it's not an empty square
                screen.blit(images[piece], (col * square_size, row * square_size))










def drawBoard(screen):
    global colors
    colors = [py.Color("white"), py.Color("skyblue")]
    for row in range(dimension):
        for col in range(dimension):
            color = colors[(row + col) % 2]
            py.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))


    
    # Draw the ranks and files
    font = py.font.SysFont("Arial", 18, True, False)
    for row in range(dimension):
        rank_label = font.render(str(8 - row), True, py.Color("black"))
        screen.blit(rank_label, (5, row * square_size + square_size // 3))
    for col in range(dimension):
        file_label = font.render(chr(col + 97), True, py.Color("black"))
        screen.blit(file_label, (col * square_size + square_size // 3, height - 20))











def drawText(screen, text):
    font = py.font.SysFont("Arial", 20, True, False)
    text_object = font.render(text, True, py.Color("purple"))
    text_location = py.Rect(0, 0, width, height).move(width / 2 - text_object.get_width() / 2,
                                                      height / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, True, py.Color('orange'))
    screen.blit(text_object, text_location.move(2, 2))










def highlightKing(screen, game_state, inCheck):
    if inCheck:
        if game_state.whiteToMove:
            kingPosition = game_state.whiteKingLocation
        else:
            kingPosition = game_state.blackKingLocation
        highlighted_square = py.Surface((square_size, square_size))
        highlighted_square.set_alpha(100)
        highlighted_square.fill(py.Color("red"))
        screen.blit(highlighted_square, (kingPosition[1] * square_size, kingPosition[0] * square_size))









def choosePromotionPiece(self, row, col, color):
    # Create a small window for piece selection
    options = ['Q', 'R', 'B', 'N']
    selection = None
    while selection not in options:
        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                sys.exit()
            elif event.type == py.KEYDOWN:
                if event.key == py.K_q:
                    selection = 'Q'
                elif event.key == py.K_h:
                    selection = 'R'
                elif event.key == py.K_b:
                    selection = 'B'
                elif event.key == py.K_n:
                    selection = 'N'
        # Draw the board and options
        self.drawPromotionOptions(row, col, color, options)
    return selection







def drawPromotionOptions(self, row, col, color, options):
    screen.fill(py.Color("black"))
    # Draw the promotion options
    for i, option in enumerate(options):
        piece = color + option
        screen.blit(images[piece], (col * square_size, row * square_size + i * square_size))
    py.display.flip()



if __name__ == "__main__":
    main()
