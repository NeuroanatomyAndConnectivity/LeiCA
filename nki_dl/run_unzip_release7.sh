#!/usr/bin/env bash

source_root_path='/scr/adenauer2/nki_r5_onwards/r6_onwards/zips/r7'
target_path='/scr/adenauer2/nki_r5_onwards/r6_onwards/dicoms'

if [ ! -d $target_path ]; then
    mkdir $target_path
fi

cd $source_root_path

for f in *zip;
do
    filename=$(basename "$f")
    filename="${filename%.*}"
    err_file=${filename}.err
    echo extracting $filename
    unzip -n -q $filename.zip -d $target_path 2> $err_file


    if [ -s $err_file ]
    then
        echo SOMETHING WENT WRONG ! ! ! $filename
    else
        echo everything is fine
        rm -f $err_file
    fi

    echo
done

