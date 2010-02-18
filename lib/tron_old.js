exports.stateboard = function(sb){
    
    //sys.puts(sb["state"]);
    
    this.width = sb["w"];
    this.height = sb["h"];
    this.state = sb["state"];
    this.me = sb["me"];
    this.them = sb["them"];

    this.print = function() {
        for (y=0; y<this.height; y++) {
            var line = "";
            for (x=0; x<this.width; x++) {
                line += this.state[y*this.width+x];
            }
            sys.puts(line);
        }
    }

    this.coordX = function(coord) {
            var y = Math.floor(coord / this.width);
            return coord - y * this.width;
        }

    /* Compute all four adjacent locations to a given origin.
       If the given location is at an edge, some of the adjacent
       data will become -1.
     */
    this.adjacent = function (origin) {
            return [this.rel(exports.NORTH, origin),
                this.rel(exports.EAST, origin),
                this.rel(exports.SOUTH, origin),
                this.rel(exports.WEST, origin)];
         }

     /* Is a given coordinate out of bounds? */
     this.isOutOfBounds = function (coord) {
             return coord < 0 || coord >= this.state.length;
         }

     /* Return true if the given index is passable.
      * out-of-bounds coordinates are not passible.
      */
     this.passable = function (index) {
             if (this.isOutOfBounds(index)) {
                 return false;
             }
             return this.state[index] == exports.FLOOR;
         }
         
     /* Compute a new index that is in a relative offset from a given origin.
      * If you don't pass in an origin, it defaults to "me".
      * If the new index would cross a boundary of the map
      * the return index is -1.
      */
     this.rel = function (direction, origin) {
            //sys.puts(this.state);
             if (direction == exports.NORTH) {
                 if (origin < this.width) {
                     return -1;
                 }
                 return origin - this.width;
             } else if (direction == exports.SOUTH) {
                 if (origin >= this.state.length - this.width) {
                     return -1;
                 }
                 return origin + this.width;
             } else if (direction == exports.EAST) {
                 if (this.coordX(origin) == this.width - 1) {
                     return -1;
                 }
                 return origin + 1;
             } else if (direction == exports.WEST) {
                 if (this.coordX(origin) === 0) {
                     return -1;
                 }
                 return origin - 1;
             } else {
                 throw "Invalid direction";
             }
          }

      /* Return all the possible legal moves from the player's current
         location. If there are no legal moves, return [tron.NORTH], just
         to make it easier for simple algorithms.
       */
      this.moves = function(who) {
              var myCoord;
              if (who=="me") {
                  myCoord = this.me;
              } else {
                  myCoord = this.them;
              }
              var adjacents = this.adjacent(myCoord);
              var moves = [];
              var i;
              var coord;
              var dir;
              for (i = 0; i < adjacents.length; i++) {
                  dir = exports.DIRECTIONS[i];
                  coord = adjacents[i];
                  if (this.passable(coord)) {
                      moves.push(dir);
                  }
              }
              return moves;
          }
          
    this.move = function(my_move, their_move) {
        var new_state = new Array();
        for (i=0; i<this.state.length; i++) { new_state[i]=this.state[i] }
        new_state[this.me] = '#';
        new_state[this.them] = '#';
        new_state[this.rel(my_move,this.me)] = 1;
        new_state[this.rel(their_move,this.them)] = 2;
        return new_state;   
    }

    this.possible_moves = function() {
        var possible_moves = [];
        var my_moves = this.moves("me");
        var their_moves = this.moves("them");
        for (var m=0; m<my_moves.length; m++) {
            for (var n=0; n<their_moves.length; n++){
                /*sys.puts( "me"+ this.rel(my_moves[m],this.me) +"\n" 
                    + "them" + this.rel(their_moves[n],this.them) + "\n"
                    + "state" + this.move(my_moves[m],their_moves[n])
                );*/
                possible_moves.push(
                    {"w": this.width,
                    "h": this.height,
                    "me": this.rel(my_moves[m],this.me), 
                    "them": this.rel(their_moves[n],this.them),
                    "state": this.move(my_moves[m],their_moves[n]),
                    "my_move": my_moves[m]
                });
            }
        }
        return possible_moves;
    }
}

/* The Board object */
exports.board = function(width, height, data) {
    this.width = width
    this.height = height
    this.data = data
    
    var new_board = [];
    for (c=0; c<this.data.length; c++){new_board[c] = this.data.charAt(c)}
    this.state = new_board;
    
    /* Convert a (y, x) coordinate into an index into the data string. */
    this.YXtoCoord = function (y, x) {
            if (x < 0 || x >= this.width || y < 0 || y >= this.height ) {
                return -1;
            }
            return y * this.width + x;
        }
        
    /* Extract the x value of a coordinate */
    this.coordX = function(coord) {
            var y = Math.floor(coord / this.width);
            return coord - y * this.width;
        }
    
    /* Extract the y value of a coordinate */
    this.coordY = function(coord) {
            return Math.floor(coord / this.width);
        }
        
    /* Look up the given (y, x) coord in the data string. */
    this.atYX = function (y, x) {
            return this.data.charAt(this.YXToCoord(y, x));
        }
        
    /* Look up the given index in the data string. */
    this.at = function (coord) {
            if (this.isOutOfBounds(coord)) {
                return exports.WALL;
            }
            return this.data.charAt(coord);
        }
        
    /* Is a given coordinate out of bounds? */
    this.isOutOfBounds = function (coord) {
            return coord < 0 || coord >= this.data.length;
        }
        
    /* Find the index of a given element. Throws an exception if missing. */
    this.find = function (item) {
            var index = this.data.indexOf(item);
            if (index < 0) {
                throw "Not found";
            }
            return index;
        }
        
    /* Return the index of player 1, also known as "me". */
    this.me = function () {
            return this.find(exports.ME);
        }
        
    /* Return the index of player 2, also known as "them". */
    this.them = function () {
            return this.find(exports.THEM);
        }
        
    /* Return true if the given index is passable.
     * out-of-bounds coordinates are not passible.
     */
    this.passable = function (index) {
            if (this.isOutOfBounds(index)) {
                return false;
            }
            return this.data[index] == exports.FLOOR;
        }
        
    /* Compute a new index that is in a relative offset from a given origin.
     * If you don't pass in an origin, it defaults to "me".
     * If the new index would cross a boundary of the map
     * the return index is -1.
     */
    this.rel = function (direction, origin) {
            if (origin === undefined) {
                origin = this.me();
            }
            if (direction == exports.NORTH) {
                if (origin < this.width) {
                    return -1;
                }
                return origin - this.width;
            } else if (direction == exports.SOUTH) {
                if (origin >= this.data.length - this.width) {
                    return -1;
                }
                return origin + this.width;
            } else if (direction == exports.EAST) {
                if (this.coordX(origin) == this.width - 1) {
                    return -1;
                }
                return origin + 1;
            } else if (direction == exports.WEST) {
                if (this.coordX(origin) === 0) {
                    return -1;
                }
                return origin - 1;
            } else {
                throw "Invalid direction";
            }
         }
         
     /* Compute all four adjacent locations to a given origin.
        If the given location is at an edge, some of the adjacent
        data will become -1.
      */
     this.adjacent = function (origin) {
             return [this.rel(exports.NORTH, origin),
                 this.rel(exports.EAST, origin),
                 this.rel(exports.SOUTH, origin),
                 this.rel(exports.WEST, origin)];
          }
      /* Return all the possible legal moves from the player's current
         location. If there are no legal moves, return [tron.NORTH], just
         to make it easier for simple algorithms.
       */
      this.moves = function(who) {
              var myCoord;
              if (who=="me") {
                  myCoord = this.me();
              } else {
                  myCoord = this.them();
              }
              var adjacents = this.adjacent(myCoord);
              var moves = [];
              var i;
              var coord;
              var dir;
              for (i = 0; i < adjacents.length; i++) {
                  dir = exports.DIRECTIONS[i];
                  coord = adjacents[i];
                  if (this.passable(coord)) {
                      moves.push(dir);
                  }
              }
              if (moves.length === 0) {
                  // it seems we have already lost
                  return [exports.NORTH];
              }
              return moves;
          }
}