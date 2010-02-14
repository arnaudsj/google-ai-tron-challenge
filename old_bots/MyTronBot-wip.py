#!/usr/bin/env python2.6

"""Template for your tron bot"""
import random
import logging
import copy
from socket import gethostname

import sys
sys.path.append("src/")
from cerebron import tron
from cerebron import search


class TronProblem(search.Problem):
    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal.  Your subclass's constructor can add
        other arguments."""
        self.initial = initial
        self.goal = goal

    def successor(self, board):
        """Given a state, return a sequence of (action, state) pairs reachable
        from this state. If there are many successors, consider an iterator
        that yields the successors one at a time, rather than building them
        all at once. Iterators will work fine within the framework."""
        for succ in board.adjacent(board.me()):
            if board.passable(succ):
                newboard = copy.deepcopy(board)
                board[succ] = "1"
                direction = "NORTH"
                yield  (direction, newboard)
        

    def goal_test(self, board):
        """Return True if the state is a goal. The default method compares the
        state to self.goal, as specified in the constructor. Implement this
        method if checking against a single self.goal is not enough."""
        return board == self.goal

    def path_cost(self, c, board1, action, board2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def value(self):
        """For optimization problems, each state has a value.  Hill-climbing
        and related algorithms try to maximize this value."""
        return 1

        

def which_move(board, xmpplogger):

    MyTronProblem = TronProblem(board, None)
    result = search.depth_limited_search(MyTronProblem, 50)
            
    xmpplogger.warning("%s" % result)

    return 1

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
