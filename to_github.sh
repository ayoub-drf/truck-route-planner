#!/bin/bash


git add .
echo "Enter the commit message"
read msg
git commit -m "$msg"
git push -u origin main


# docker run -d -p 6379 redis
