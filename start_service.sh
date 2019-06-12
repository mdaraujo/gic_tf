##
# Start yolo_tf Service
##

docker stack deploy -c docker-compose.yml yolo_tf

# Update upstream servers
## get needed info
swarm_master_ip=$(docker node inspect self --format '{{.Status.Addr}}')
container_ids=$(docker service ls | grep yolo_tf_service | awk {'print $1'})
upstream_conf_path="/mnt/cifs13/yolo_tf/nginx/upstream.conf"

## create empty upstream servers conf file
ssh compute@$swarm_master_ip "echo '' > /mnt/cifs13/yolo_tf/nginx/upstream.conf"

## print upstream servers to upstream.conf
for id in $container_ids
do    
    ssh compute@$swarm_master_ip "echo \"server $swarm_master_ip:$(docker inspect $id --format {{.Endpoint.Ports}} | awk {'print $4'});\" >> $upstream_conf_path"
done

# Start NGINX load balancers
docker network create --subnet=172.100.101.0/24 yolo_tf_loadBalancer
ssh compute@192.168.215.21 'sudo docker run -v /mnt/cifs13/yolo_tf/nginx:/etc/nginx/ --network yolo_tf_loadBalancer -p 172.100.101.1:7700:80 --name yolo_tf_LB1 nginx &' &
echo "Created yolo_tf_LB1 in 192.168.215.21"
ssh compute@192.168.215.22 'sudo docker run -v /mnt/cifs13/yolo_tf/nginx:/etc/nginx/ --network yolo_tf_loadBalancer -p 172.100.101.1:7700:80 --name yolo_tf_LB2 nginx &' &
echo "Created yolo_tf_LB2 in 192.168.215.22"
