#!/bin/bash

for value in {1..7}
do
    echo "Request "$value
    curl -X POST -F "file=@test_images/person"$value".jpg" http://172.17.0.2:5000/process && echo -e "\nDone "$value"\n" &
done

wait

echo -e "\nAll done"
