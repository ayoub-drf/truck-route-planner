#!/bin/bash


git add .
echo "Enter the commit message"
read msg
git commit -m "
feat: render duty status overlay on image and enable logsheet download

- Added functionality to draw the current duty status directly onto the image.
- Implemented a feature to generate and download the logsheet.

"
git push -u origin main


# docker run -d -p 6379 redis
