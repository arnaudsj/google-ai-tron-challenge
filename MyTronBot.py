#!/usr/bin/env python2.6

"""Template for your tron bot"""
import random
import logging
from socket import gethostname

import sys
sys.path.append("src/")
from cerebron import tron

def sum(opentilelist):
    def add(x,y): return x+y
    return reduce(add, opentilelist, 0)

def get_direction(x,y, xmpplogger):
    def ispassable(E): 
        dist, direction = E
        return board.passable(board.rel(direction))

    #for e in board.board:
    #    xmpplogger.warning(e)

    x1, y1 = board.me()
    xdir = x - x1
    ydir = y - y1
    #xmpplogger.warning("%s / %s" % (xdir, ydir))
    
    pref = []
    if xdir>0:
        pref.append((abs(xdir),tron.SOUTH))
    else:
        pref.append((abs(xdir),tron.NORTH))
            
    if ydir>0:
        pref.append((abs(ydir),tron.EAST))
    else:
        pref.append((abs(ydir),tron.WEST))
    
    #xmpplogger.warning(pref)
    
    filtered_pref = filter(ispassable, pref)
    if len(filtered_pref)>0:
        final_pref = sorted(filtered_pref, key=lambda x:(x[0], x[1]),  reverse=True)
        dist, direction = final_pref[0]
    else:
        direction = random.choice(board.moves())
    return direction
        

def which_move(board, xmpplogger):
    # fill in your code here. it must return one of the following directions:
    #   tron.NORTH, tron.EAST, tron.SOUTH, tron.WEST

    opentiles, alltiles= [], []

    for i in xrange(0, board.width):
        for j in xrange(0, board.height):
            alltiles.append((i,j))
            if board[i,j]==tron.FLOOR:
                opentiles.append((i,j))
            
    # Calculate the center of gravity of the remaining open tiles
    avg_x = sum([x for x,y in alltiles])/len(alltiles)
    avg_y = sum([y for x,y in alltiles])/len(alltiles)
    
    # GOAL #1: Get to center of map
    
    # GOAL #2: Chase opponent
    
    # GOAL #3: Optimize filling the rest of the space!
    
    #xmpplogger.warning("Deciding to go: %s" % get_direction(avg_x, avg_y,xmpplogger))

    return get_direction(avg_x, avg_y,xmpplogger)

if __name__=="__main__":
    if gethostname()=="aura.local":
        from cerebron import xmpplogger
        # Get a Jabber handler.
        jh = xmpplogger.JabberHandler()
        # Set it's formatter to the jabber formatter.
        jh.setFormatter(logging.Formatter("%(message)s"))
        # Attach to the root logger.
        r = logging.getLogger()
        r.addHandler(jh)
        # Set the root logger to log all DEBUG messages and above.
        r.setLevel(logging.WARNING)
    
        r.debug("Game has started!")
    else:
        r = None
    
    for board in tron.Board.generate():
        tron.move(which_move(board, r))
