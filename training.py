import client

#this is a test script I am making to make sure
#the server and client work as intended

class SquareBot(client.Robot):
    def run(self):
        self.connect()
        print("Connected to server")
        x=0
        y=0
        mcode = 'N'   #stands for none
        while not (mcode is 'B'):
            mcode, resp = self.act_on_response()
            if mcode is 'T':
                #just places down consecutive stable formations
                #and only one of them. how stupid.
                block = [(x,y),(x+1,y),(x+1,+1),(x,y+1)]
                x+=3
                if(x>1020):
                    x=0
                    y+=3
                self.apply_moves(block,self.board,1)
                self.send_moves(block)
                
        print("done with match")

sq1 = SquareBot("SquareBot1")
sq2 = SquareBot("SquareBot2")

if input("Enter which to run: ") is "1":
    sq1.run()
else:
    sq2.run()
                
        
        
        
