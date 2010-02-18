// If you want to use this file, make sure to include it in your
// submission. You may modify it and submit the modified copy, or you
// may discard it and roll your own.

/**
 * Provided code for the JavaScript starter package
 *
 * See the example bots randbot.js and wallbot.js to get started.
 */

var sys = require('sys');

exports.NORTH = 1;
exports.EAST = 2;
exports.SOUTH = 3;
exports.WEST = 4;

exports.FLOOR = ' ';
exports.WALL  = '#';
exports.ME    = '1';
exports.THEM  = '2';

exports.DIRECTIONS = [exports.NORTH, exports.EAST, exports.SOUTH, exports.WEST];

/* Report an error and exit. */

function invalid_input(message) {
    sys.error("Invalid input: " + message);
    process.exit(1);
}

/* Read stdin, and call the supplied callback function
 * for each complete line of input that is read.
 */

function forEachLineOfInput(callback) {
  var buf = "";
  process.stdio.open("ascii");
  process.stdio.addListener("data",
      function (input) {
          var index, line;
          buf = buf + input;
          while ((index = buf.indexOf('\n')) >= 0) {
              line = buf.substring(0, index+1);
              buf = buf.substring(index+1);
              callback(line);
          }
      }
  );
}



/*
 * play the game. Repeatedly read a board from stdin and then
 * call the moveFn callback function with a "board" object.
 */

exports.play = function(moveFn) {
  var lineNumber = 0;
  var width = 0;
  var height = 0;
  var data = "";
  forEachLineOfInput(
      function (line) {
          var dim;
          line = line.replace(/[\r\n]*$/g,''); // Remove end-of-line chars if present
          if (lineNumber === 0) {
              dim = line.split(" ");
              if (dim.length != 2) {
                  invalid_input("expected width, height on first line, got \"" + line + "\"");
              }
              width = parseInt(dim[0],10);
              height = parseInt(dim[1],10);
              if (width <= 0 || isNaN(width) || height <= 0 || isNaN(height)) {
                  invalid_input("expected width, height on first line, got \"" + line + "\"");
              }
          } else {
              if (line.length != width) {
                  invalid_input("malformed board, line wrong length:" + line.length);
              }
              data = data + line;
              if (lineNumber == height) {
                  sys.puts(moveFn(new exports.board(width, height, data)));
                  // Reset our accumulators.
                  lineNumber = -1;
                  data = "";
              }
          }
          lineNumber += 1;
      });
};


exports.board = function(width, height, data){
    this.state = new Array();
    this.width = width;
    this.height = height;
    this.me = {"x":0, "y":0};
    this.them = {"x":0, "y":0};

    // Init
    this.board_char_lookup = {
        ' ': 0, '#': null, '1': 1, '2': 2
    };
    
    for (var c=1; c<=data.length; c++){
        if (c==1) var xline = new Array();
        
        var cursor = this.board_char_lookup[data.charAt(c-1)];
        if (cursor==1) {
            this.me.x = c % width - 1;
            this.me.y = Math.floor(c /width);
        }
        if (cursor==2) {
            this.them.x = c % width -1;
            this.them.y = Math.floor(c /width);
        }
        
        xline.push(cursor);
        
        if (c % width == 0) {
            this.state.push(xline);
            xline = new Array();
        }
    }
    
    
    this.print = function() {
        sys.puts("(" + this.me.x + "," + this.me.y + ")")
        sys.puts("(" + this.them.x + "," + this.them.y + ")")
        for (var i=0; i<this.state.length; i++){
            sys.puts(this.state[i].join(''));
        }  
    }
    
    this.get = function(x, y) {
        //sys.puts(x+":"+y+"=>"+this.state[x][y])
        try {
            return this.state[x][y];
        } catch(e) {
            return null
        }
    }
    
    this.possible_moves = function() {
        var pmoves = [];
        if(this.get(this.me.x+1, this.me.y) == 0) pmoves.push(exports.EAST);
        if(this.get(this.me.x-1, this.me.y) == 0) pmoves.push(exports.WEST);
        if(this.get(this.me.x, this.me.y+1) == 0) pmoves.push(exports.SOUTH);
        if(this.get(this.me.x, this.me.y-1) == 0) pmoves.push(exports.NORTH);
        return pmoves;
    } 
}

