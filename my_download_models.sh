#!/usr/bin/env bash

echo "Downloading config files..."

mkdir cfg
wget -O cfg/openimages.data https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/openimages.data
wget -O cfg/yolov3-openimages.cfg https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-openimages.cfg

wget -O cfg/coco.data https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/coco.data
wget -O cfg/yolov3.cfg https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg

echo "Modify config parameters to enable Testing mode"
sed -i '/batch=64/c\# batch=64' cfg/yolov3-openimages.cfg
sed -i '/subdivisions=16/c\# subdivisions=16' cfg/yolov3-openimages.cfg
sed -i '/# batch=1/c\batch=1' cfg/yolov3-openimages.cfg
sed -i '/# subdivisions=1/c\subdivisions=1' cfg/yolov3-openimages.cfg

mkdir data
wget -O data/openimages.names https://raw.githubusercontent.com/pjreddie/darknet/master/data/openimages.names

wget -O data/coco.names https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
 


echo "Downloading yolov3 weights"
mkdir weights
wget -O weights/yolov3-openimages.weights https://pjreddie.com/media/files/yolov3-openimages.weights
wget -O weights/yolov3.weights https://pjreddie.com/media/files/yolov3.weights
wget -O weights/yolov3-spp.weights https://pjreddie.com/media/files/yolov3-spp.weights
