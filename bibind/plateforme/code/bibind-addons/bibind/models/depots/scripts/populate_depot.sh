#!/bin/bash
clear
echo "============================================"
echo "git clone too empty"
echo "==========================================="
echo "depot : "
DIRECTORY=$1
GIT_PROJET=$2
APP_URL=$3
APP_NAME=$4
PROJET_DIRECTORY=$5



cd /home/odoo

if [ -f $DIRECTORY ]; then
   cd $DIRECTORY
else
   mkdir $DIRECTORY
   cd $DIRECTORY
fi

if [ -f $PROJET_DIRECTORY ]; then
   cd $PROJET_DIRECTORY
else
   mkdir $PROJET_DIRECTORY
   cd $PROJET_DIRECTORY
fi

git clone $GIT_PROJET my_app


cd my_app

echo "============================================"
echo "APP Install Script"
echo "============================================"
#download wordpress
curl -O $APP_URL
#unzip wordpress
tar -zxvf $APP_NAME.tar.gz
#change dir to wordpress
cd $APP_NAME
#copy file to parent dir
cp -rf . ..
#move back to parent dir
cd ..
#remove files from wordpress folder
rm -R $APP_NAME
#

git add .

git commit -m"initialise"

git push origin master

exit 1
