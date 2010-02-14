#!/usr/bin/env python2.6
import random, time, sys

from socket import gethostname
if gethostname()!="aura.local":
    sys.path.append("./lib")    
from diesel import Application, Loop, sleep, fire, wait, log
   
if gethostname()=="aura.local":
    sys.path.append("./lib") 
from tronlib import tron

def getboard():
    buf = ''
    yield sleep(0.1)
    while True:
        #print move_made
        #print "waiting for stdin ..."
        board, buf = tron.Board.read(buf)
        if not board:
            break
        yield fire('board-received', board)
        #print "fired board"
        yield wait('move-made')

def actor():
    while True:
        board = yield wait('board-received')
        #print "got the board..."
        yield fire('move-made', tron.move(random_move(board)))

def random_move(board):
    move = random.choice(board.moves())
    #log.critical("made decision in: %.6fs" % (time.time()-t))
    return move


if __name__=="__main__":
    app = Application()
    app.add_loop(Loop(actor))
    app.add_loop(Loop(getboard))
    app.run()
    
#     
# def bestmove(board):
#     log.critical("received board %s" % board)
#     bestcount = -1
#     bestmove = tron.NORTH
#     for dir in board.moves:
#         dest = board.rel(dir)
#         count = 0
#         for pos in board.adjacent(dest):
#             if board[pos] == tron.FLOOR:
#                 count += 1
#         if count > bestcount:
#             bestcount = count
#             bestmove = dir
#     log.critical("choosing move: %s" % bestmove)
#     return bestmove

