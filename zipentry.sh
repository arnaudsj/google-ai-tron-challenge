#!/bin/bash
TMP_DIR=/Users/arnaudsj/Temp
zip -0 -r $TMP_DIR/cerebron.zip `find . -path *git* -prune   -o -type f -print | grep -v -e pyc$ -e \.DS_Store$`