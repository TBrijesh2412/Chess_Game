import pygame
import sys

WIDTH, HEIGHT = 480, 480
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

LIGHT_COLOR = (240, 217, 181)  
DARK_COLOR = (181, 136, 99)   
HIGHLIGHT_COLOR = (246, 246, 105, 100) 
LAST_MOVE_COLOR = (246, 246, 105)     
DOT_COLOR = (0,0,0)                   

PIECE_VALUES = {1:1,2:3,3:3,4:5,5:9,6:1000}

def load_images():
    images = {}
    for color in ['white','black']:
        images[color] = {}
        for piece in ['pawn','knight','bishop','rook','queen','king']:
            images[color][piece] = pygame.transform.scale(
                pygame.image.load(f'img/{color}/{piece}.png'), (SQUARE_SIZE,SQUARE_SIZE))
    return images

def create_board():
    board = [[0]*8 for _ in range(8)]
    # Pawns
    for i in range(8):
        board[1][i] = -1
        board[6][i] = 1
    # Rooks
    board[0][0] = board[0][7] = -4
    board[7][0] = board[7][7] = 4
    # Knights
    board[0][1] = board[0][6] = -2
    board[7][1] = board[7][6] = 2
    # Bishops
    board[0][2] = board[0][5] = -3
    board[7][2] = board[7][5] = 3
    # Queens
    board[0][3] = -5
    board[7][3] = 5
    # Kings
    board[0][4] = -6
    board[7][4] = 6
    return board


def draw_board(win, board, images, selected=None, valid_moves=[], last_move=None):
    for r in range(8):
        for c in range(8):
            color = LIGHT_COLOR if (r+c)%2==0 else DARK_COLOR
            pygame.draw.rect(win,color,(c*SQUARE_SIZE,r*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE))
            
            if last_move:
                (r1,c1),(r2,c2) = last_move
                if (r,c)==(r1,c1) or (r,c)==(r2,c2):
                    pygame.draw.rect(win,LAST_MOVE_COLOR,(c*SQUARE_SIZE,r*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE))
            
            if selected == (r,c):
                pygame.draw.rect(win,(246,246,105),(c*SQUARE_SIZE,r*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE),3)
            
            if (r,c) in valid_moves:
                center = (c*SQUARE_SIZE+SQUARE_SIZE//2, r*SQUARE_SIZE+SQUARE_SIZE//2)
                pygame.draw.circle(win,DOT_COLOR,center,8)

            piece = board[r][c]
            if piece !=0:
                clr = 'white' if piece>0 else 'black'
                name = {1:'pawn',2:'knight',3:'bishop',4:'rook',5:'queen',6:'king'}[abs(piece)]
                win.blit(images[clr][name],(c*SQUARE_SIZE,r*SQUARE_SIZE))

def in_bounds(r,c): return 0<=r<8 and 0<=c<8
def get_moves_no_check(board,r,c):
    piece = board[r][c]
    if piece==0: return []
    moves=[]
    color = 1 if piece>0 else -1
    ptype = abs(piece)
    directions=[]
    if ptype==1:  # pawn
        dir = -1 if color==1 else 1
        if in_bounds(r+dir,c) and board[r+dir][c]==0:
            moves.append((r+dir,c))
            if (r==6 and color==1) or (r==1 and color==-1):
                if board[r+2*dir][c]==0:
                    moves.append((r+2*dir,c))
        for dc in [-1,1]:
            if in_bounds(r+dir,c+dc) and board[r+dir][c+dc]*color<0:
                moves.append((r+dir,c+dc))
    elif ptype==2:  # knight
        for dr,dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            rr,cc = r+dr,c+dc
            if in_bounds(rr,cc) and board[rr][cc]*color<=0:
                moves.append((rr,cc))
    elif ptype==3: directions=[(-1,-1),(-1,1),(1,-1),(1,1)]
    elif ptype==4: directions=[(-1,0),(1,0),(0,-1),(0,1)]
    elif ptype==5: directions=[(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    elif ptype==6:
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr==0 and dc==0: continue
                rr,cc=r+dr,c+dc
                if in_bounds(rr,cc) and board[rr][cc]*color<=0:
                    moves.append((rr,cc))
    for dr,dc in directions:
        rr,cc=r+dr,c+dc
        while in_bounds(rr,cc):
            if board[rr][cc]*color>0: break
            moves.append((rr,cc))
            if board[rr][cc]*color<0: break
            rr+=dr; cc+=dc
    return moves

def is_in_check(board,color):
    king_pos=None
    target = 6*color
    for r in range(8):
        for c in range(8):
            if board[r][c]==target:
                king_pos=(r,c)
                break
    if not king_pos: return True
    enemy = -color
    for r in range(8):
        for c in range(8):
            if board[r][c]*enemy>0:
                moves = get_moves_no_check(board,r,c)
                if king_pos in moves:
                    return True
    return False

def get_legal_moves(board,r,c):
    moves=[]
    for m in get_moves_no_check(board,r,c):
        orig = board[r][c]
        dst = board[m[0]][m[1]]
        board[m[0]][m[1]] = board[r][c]
        board[r][c] = 0
        if not is_in_check(board,1 if orig>0 else -1):
            moves.append(m)
        board[r][c] = orig
        board[m[0]][m[1]] = dst
    return moves

def evaluate(board):
    score=0
    for r in board:
        for c in r:
            if c!=0:
                val=PIECE_VALUES[abs(c)]
                score += val if c>0 else -val
    return score

def alphabeta(board,depth,alpha,beta,maximizing):
    moves=[]
    color=1 if maximizing else -1
    for r in range(8):
        for c in range(8):
            if board[r][c]*color>0:
                for move in get_legal_moves(board,r,c):
                    moves.append((r,c,move[0],move[1]))
    if depth==0 or not moves: return evaluate(board), None
    best_move=None
    if maximizing:
        max_eval=-float('inf')
        for r1,c1,r2,c2 in moves:
            captured=board[r2][c2]
            board[r2][c2]=board[r1][c1]
            board[r1][c1]=0
            eval,_=alphabeta(board,depth-1,alpha,beta,False)
            board[r1][c1]=board[r2][c2]
            board[r2][c2]=captured
            if eval>max_eval:
                max_eval=eval
                best_move=(r1,c1,r2,c2)
            alpha=max(alpha,eval)
            if beta<=alpha: break
        return max_eval,best_move
    else:
        min_eval=float('inf')
        for r1,c1,r2,c2 in moves:
            captured=board[r2][c2]
            board[r2][c2]=board[r1][c1]
            board[r1][c1]=0
            eval,_=alphabeta(board,depth-1,alpha,beta,True)
            board[r1][c1]=board[r2][c2]
            board[r2][c2]=captured
            if eval<min_eval:
                min_eval=eval
                best_move=(r1,c1,r2,c2)
            beta=min(beta,eval)
            if beta<=alpha: break
        return min_eval,best_move

def main():
    pygame.init()
    win=pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Chess AI Fast - Chess.com Style")
    clock=pygame.time.Clock()
    images=load_images()
    board=create_board()
    selected=None
    valid_moves=[]
    turn_white=True
    font=pygame.font.SysFont(None,30)
    last_move=None
    running=True

    while running:
        draw_board(win, board, images, selected, valid_moves, last_move)
        pygame.display.flip()
        clock.tick(60)

        any_moves=False
        for r in range(8):
            for c in range(8):
                if board[r][c]*(1 if turn_white else -1)>0:
                    if get_legal_moves(board,r,c):
                        any_moves=True
        if not any_moves:
            text="Stalemate"
            for r in range(8):
                for c in range(8):
                    if board[r][c]*(1 if turn_white else -1)>0:
                        if is_in_check(board,1 if turn_white else -1):
                            text="White Wins" if not turn_white else "Black Wins"
            img=font.render(text,True,(255,0,0))
            win.blit(img,(WIDTH//2 - img.get_width()//2, HEIGHT//2 - img.get_height()//2))
            pygame.display.flip()
            pygame.time.delay(5000)
            running=False
            continue

        if not turn_white:
            _,move=alphabeta(board,3,-float('inf'),float('inf'),False)
            if move:
                r1,c1,r2,c2=move
                board[r2][c2]=board[r1][c1]
                board[r1][c1]=0
                if abs(board[r2][c2])==1 and r2==7:
                    board[r2][c2]=5
                last_move=((r1,c1),(r2,c2))
            turn_white=True
            continue

        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.MOUSEBUTTONDOWN:
                x,y=pygame.mouse.get_pos()
                row,col=y//SQUARE_SIZE,x//SQUARE_SIZE
                if selected:
                    if (row,col) in valid_moves:
                        board[row][col]=board[selected[0]][selected[1]]
                        board[selected[0]][selected[1]]=0
                        if abs(board[row][col])==1 and row==0:
                            board[row][col]=5
                        last_move=((selected[0],selected[1]),(row,col))
                        turn_white=False
                    selected=None
                    valid_moves=[]
                elif board[row][col]>0:
                    selected=(row,col)
                    valid_moves=get_legal_moves(board,row,col)

    pygame.quit()
    sys.exit()

if __name__=="__main__":
    main()

