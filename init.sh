#!/bin/bash

sudo apt install -y pipenv npm
pipenv install

cd Front
npm i 

pipenv shell 

cd ..
code .