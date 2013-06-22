#!/bin/bash

for i in `cat ~/桌面/all_words.csv`
do
    python spell_checker.py $i > /dev/null

    if [ $? -ne 0 ]
    then
	echo $i
    fi
done;
