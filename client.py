import socket

#you can change these in your own code
HOST,PORT = "0.0.0.0",31337
SIZE=1024

#same error class from server script
class GameError:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#raw tlv methods, in case you need to use them
def sendtlv(sock,tid,tstr):
    s = "{}{}".format(tid,chr(len(tstr))) + tstr
    sock.sendall(s)

def gettlv(tlv):
    tid = tlv[0]
    leng = ord(tlv[1])
    if not leng == len(tlv[2:]):
        raise GameError("tlv length doesn't match")
    text = tlv[2:]
    return tid,text

#A lot of the methods in this class are borrowed from the server script
class Robot:
    def __init__(self,ID):
        #set up socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ID = ID
        self.board = [[ 0 for y in range(0,SIZE)] for x in range(0,SIZE)]
        
    #connects to server, ideally should be called right after __init__
    def connect(self):
        self.sock.connect((HOST,PORT))
        sendtlv(self.sock,'I',self.ID)
        i,player = gettlv(self.sock.recv(1024))
        if i=='S':
            self.player = player
        else:
            raise GameError("Server did not respond with player number")

    #gets cell and board's x and y, accounting for oob
    def getcell(self,x,y):
        # returns 0 if off the board
        if x < 0 or x >= SIZE or y < 0 or y >= SIZE:
            return 0
        return self.board[x][y]

    #sends a list of moves to server
    #moves should be formatted like [(x1,y1),(x2,y2)...]
    def send_moves(self,moves):
        out = ""
        for move in moves:
            x1 = chr(move[0] % 256)
            x2 = chr(int(move[0] / 256))
            y1 = chr(move[1] % 256)
            y2 = chr(int(move[1] / 256))
            out += x1+x2+y1+y2
        sendtlv(self.sock,'M',out)

    #gets moves from text part of tlv
    #returns same format as above
    def get_moves(self,tlv):
        if(len(tlv)%4!=0):
            raise GameError("Input moves are not the right length")
        movs = [(ord(tlv[i]) + 256*ord(tlv[i+1]),ord(tlv[i+2]) + 256*ord(tlv[i+3])) for i in range(0,len(tlv),4)]
        return movs

    #executes a step using GOL rules
    #returns a new board
    def get_step(self,board):
        newboard = [[0 for i in range(SIZE)] for i in range(SIZE)]
        for x in range(SIZE):
            for y in range(SIZE):
                neighbors = [board[x-1][y-1],board[x][y-1],board[x+1][y-1],board[x-1][y],board[x+1][y],board[x-1][y+1],board[x][y+1],board[x+1][y+1]]
                p1neighbors = sum([1 if c==1 else 0 for c in neighbors])
                p2neighbors = sum([1 if c==2 else 0 for c in neighbors])
                if board[x][y] == 0:
                    if p1neighbors == 3 and p2neighbors == 0:
                        newboard[x][y] = 1
                    if p2neighbors == 3 and p1neighbors == 0:
                        newboard[x][y] = 2
                elif board[x][y] == 1:
                    if p1neighbors < 2 or p1neighbors > 3:
                        newboard[x][y] = 0
                    if p1neighbors == 2 or p1neighbors == 3:
                        newboard[x][y] = 1
                elif board[x][y] == 2:
                    if p2neighbors < 2 or p2neighbors > 3:
                        newboard[x][y] = 0
                    if p2neighbors == 2 or p2neighbors == 3:
                        newboard[x][y] = 1
        return newboard

    #executes GOL step on the internal board
    def step(self):
        self.board = self.get_step(self.board)

    #applies moves in format listed above to board passed in as argument.
    #if you want to do it to you self.board, go ahead. You can also do it
    #to temporary boards if you want to check possibilities
    #the player attribute determines which player the move will be for,
    #either yourself (self.player) or the other player (3 - self.player)
    def apply_moves(self,moves,board,player):
        for i in moves:
            if board[i[0]][i[1]] == 0:
                board[i[0]][i[1]] = player

    #returns response from server
    def get_response(self):
        return gettlv(self.sock.recv(2048))

    #An easy way to get the response from the server, and act upon it.
    def act_on_response(self):
        i,text = self.get_response()
        if i is 'M':
            self.apply_moves(get_moves(text),self.board,(3-self.player))
            return i,self.board
        if i is 'G':
            self.step()
            return i,1
        if i is 'T':
            return i,2
        if i is 'B':
            self.sock.detach()
            return i,0

    
