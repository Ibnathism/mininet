#!/bin/bash

sudo mn -c
for i in $(seq 0 9)
do
  sudo rm -r saved_models/server/user$i/*
done


