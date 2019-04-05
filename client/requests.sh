#!/bin/bash

for value in {1..7}
do
    echo "Request "$value
    curl -X POST -F "file=@images/person"$value".jpg" http://localhost:5000/process && echo -e "\nDone "$value"\n" &
done

wait

echo -e "\nAll done"


# for k in {1..200}
# do
#     for value in {1..7}
#     do
#         echo "Request "$value
#         curl -X POST -F "file=@images/person"$value".jpg" http://192.168.215.29:7700/process && echo -e "\nDone "$value"\n" &
#     done
# done
