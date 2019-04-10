#!/bin/bash
MACHINES="1 2 4 5 6 8 9 10 11 12 13"
if [[ ! -z $1 ]]; then
    MACHINES=("$1")
fi

while :
do
    for i in ${MACHINES}; do
        echo "compute$i"
        ssh compute@192.168.215.$(python3 -c "print($i+20,end='')") 'sudo sh /mnt/cifs13/yolo_tf/stats_logger.sh'
    done
done
