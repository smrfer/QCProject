#!/bin/bash
directory="/state/partition1/data/archive/miseq/"
destination="/home/sr/SAV/Data/"

for folder in "$directory"*/; do
echo $folder
cd $folder
outdir=${PWD##*/}
#fn=${fn%*/}
#echo $fn
#for files in $folder*.xml; do
#echo $files

mkdir -p "$destination$outdir" 
cp $folder*.xml $destination$outdir
cp $folder*.csv $destination$outdir
mkdir -p "$destination$outdir""/InterOp/" 
cp -r $folder"InterOp/." $destination$outdir"/InterOp/"
done
#done
