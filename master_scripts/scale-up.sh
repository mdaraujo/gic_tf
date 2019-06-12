

# docker service scale $1=N

# min_instances_per_service=5
max_instances_per_service=10

curr_total_intances_1=$(sudo docker service ls | grep yolo_tf_service1 | awk {'print $4'} | cut -d "/" -f 2)
curr_total_intances_2=$(sudo docker service ls | grep yolo_tf_service2 | awk {'print $4'} | cut -d "/" -f 2)

curr_total_intances=$(($curr_total_intances_1>$curr_total_intances_2?$curr_total_intances_1:$curr_total_intances_2))

if [[ ( "$curr_total_intances" < $max_instances_per_service ) ]] ; then
    echo "$curr_total_intances"

