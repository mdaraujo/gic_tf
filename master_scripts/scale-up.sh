# min_instances_per_service=5
max_instances_per_service=10

curr_total_intances_1=$(sudo docker service ls | grep yolo_tf_service1 | awk {'print $4'} | cut -d "/" -f 2)
curr_total_intances_2=$(sudo docker service ls | grep yolo_tf_service2 | awk {'print $4'} | cut -d "/" -f 2)

echo "curr_total_intances_1: $curr_total_intances_1"
echo "curr_total_intances_2: $curr_total_intances_2"

if [ -z "$curr_total_intances_1" ]
then
    exit 0
fi

if (( $curr_total_intances_1 < $curr_total_intances_2 )) ; then
    min_total_intances=$curr_total_intances_1
    min_service="yolo_tf_service1"
else
    min_total_intances=$curr_total_intances_2
    min_service="yolo_tf_service2"
fi


echo "min_service: $min_service"
echo "min_total_intances: $min_total_intances"

desired_instances=$((min_total_intances + 1))

if (( $desired_instances <= $max_instances_per_service )) ; then
    echo "CAN SCALE UP"
    sudo docker service scale $min_service=$desired_instances
fi
