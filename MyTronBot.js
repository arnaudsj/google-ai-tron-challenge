// Template for your tron bot
var sys = require("sys");
var tron = require('./lib/tron');
var time = require('./lib/time');

var DEBUG = false;

/* Next test :)
function negascout(node, depth, α, β)
    if node is a terminal node or depth = 0
        return the heuristic value of node
    b := β                                          (* initial window is (-β, -α) *)
    foreach child of node
        a := -negascout (child, depth-1, -b, -α)
        if a>α
            α := a
        if α≥β
            return α                                (* Beta cut-off *)
        if α≥b                                      (* check if null-window failed high*)
           α := -negascout(child, depth-1, -β, -α)  (* full re-search *)
           if α≥β
               return α                             (* Beta cut-off *)    
        b := α+1                                    (* set new null window *)             
    return α
*/


var gnode = function(stateb) {    
    this.stateboard = new tron.stateboard(stateb);
    
    this.is_terminal = function() {
        if(this.stateboard.moves("them").length==0 || this.stateboard.moves("me").length==0) {
            return true;
        } else {
            return false;
        }
    }
    
    this.heuristic = function() {
        // Making basic heuristic based on mobility only for now
        var utility = -Infinity;
    
        if(this.stateboard.me==this.stateboard.them 
            || (this.stateboard.moves("them").length==0 
            && this.stateboard.moves("me").length==0)) utility = 0; // Did we collide or no option
        if(this.stateboard.moves("them").length==0) utility = 10; // Is P2 without option next turn
        if(this.stateboard.moves("me").length==0) utility = -10; // Is P1 without option next turn?

        return utility;
    }
    
    this.children = function() {
        var c = this.stateboard.possible_moves()
        if (DEBUG) {
            for (i=0; i<c.length; i++) {
                sys.puts("debug (new child): "+ c[i].state)
            }
        }   
        return c;
    }


}

function negamax(node, depth) {

    
    if (DEBUG) {
        node.stateboard.print();
        sys.puts(node.is_terminal()+":"+depth);
    }
    
    if (node.is_terminal() || depth <= 0) {
        /*if (DEBUG) node.stateboard.print();*/
        if (DEBUG) sys.puts("heuristic:"+node.heuristic());
        return {"alpha": node.heuristic(), "move": null}
    }
    var alpha = -Infinity;
    var best_move = 0;
    var node_children = node.children();
    for (var i=0; i<node_children.length; i++) {
        var new_val = negamax(new gnode(node_children[i]), depth-1).alpha;
        if (new_val>alpha) {
            best_move = node_children[i].my_move;
            alpha = new_val; 
            }
    }

    if (DEBUG) sys.puts("heuristic(alpha):"+alpha+" (depth:"+depth+") move => "+best_move);
    return {"alpha":alpha, "move": best_move};
}

/*
var StateBoard = {"w":board.width, "h":board.height, "state": board.state,
     "me": board.me(), "them": board.them()}  
var RootNode = new gnode(StateBoard);

var negamax_var = negamax(RootNode, 3);
//if (DEBUG) sys.puts(best_move);

var my_best_move = (negamax_var.move==0||negamax_var.move==null)?randomChoice(RootNode.stateboard.moves("me")):negamax_var.move;

if (DEBUG) sys.puts("NORTH = 1, EAST = 2, SOUTH = 3, WEST = 4");
sys.puts(my_best_move);
*/

function randomChoice(a) {
    return a[Math.floor(Math.random() * a.length)];
}
 
function which_move(board) {
    
    
    //board.print();
    
    time.time.start('thinking my move!');
    var my_best_move = randomChoice(board.possible_moves());
    time.time.stop('thinking my move!');
    //time.time.report();
    
    return my_best_move;
}

tron.play(which_move);
