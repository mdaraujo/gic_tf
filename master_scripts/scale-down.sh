#!/bin/bash

min_instances_per_service=5

curr_total_intances_1=$(sudo docker service ls | grep yolo_tf_service1 | awk {'print $4'} | cut -d "/" -f 2)
curr_total_intances_2=$(sudo docker service ls | grep yolo_tf_service2 | awk {'print $4'} | cut -d "/" -f 2)

echo "curr_total_intances_1: $curr_total_intances_1"
echo "curr_total_intances_2: $curr_total_intances_2"

if [ -z "$curr_total_intances_1" ]
then
    exit 0
fi

if (( $curr_total_intances_1 > $curr_total_intances_2 )) ; then
    max_total_intances=$curr_total_intances_1
    max_service="yolo_tf_service1"
else
    max_total_intances=$curr_total_intances_2
    max_service="yolo_tf_service2"
fi


echo "max_service: $max_service"
echo "max_total_intances: $max_total_intances"

desired_instances=$((max_total_intances - 1))

if (( $desired_instances >= $min_instances_per_service )) ; then
    echo "CAN SCALE DOWN"
    sudo docker service scale $max_service=$desired_instances
fi
