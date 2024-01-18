#!/bin/bash

sudo mn -c
for i in $(seq 0 9)
do
  sudo rm -r saved_models/set1/server/user$i/*
  # sudo rm -r saved_models/set2/server/user$i/*
  # sudo rm -r saved_models/set2/users/user$i/*
done


