##
# Start yolo_tf Service
##

nginx_working_dir="/mnt/cifs13/yolo_tf/nginx"
docker stack deploy -c docker-compose.yml yolo_tf

# Update upstream servers
## get needed info
#docker node inspect self --format '{{.Spec.Role}} {{.Status.Addr}}'
swarm_master_ip=$(docker node inspect self --format '{{.Status.Addr}}')
service_ids=$(docker service ls | grep yolo_tf_service | awk {'print $1'})
upstream_conf_path="$nginx_working_dir/upstream.conf"

## create empty upstream servers conf file
ssh compute@$swarm_master_ip "echo '' > /mnt/cifs13/yolo_tf/nginx/upstream.conf"
ssh compute@$swarm_master_ip "wget -O /home/compute/scale-up.sh https://raw.githubusercontent.com/mdaraujo/gic_tf/master/master_scripts/scale-up.sh"
ssh compute@$swarm_master_ip "wget -O /home/compute/scale-down.sh https://raw.githubusercontent.com/mdaraujo/gic_tf/master/master_scripts/scale-down.sh"

ssh compute@$swarm_master_ip "wget -O \"$nginx_working_dir/nginx.conf\" https://raw.githubusercontent.com/mdaraujo/gic_tf/master/nginx/nginx.conf"
ssh compute@$swarm_master_ip "wget -O \"$nginx_working_dir/uwsgi_params\" https://raw.githubusercontent.com/mdaraujo/gic_tf/master/nginx/uwsgi_params"

## print upstream servers to upstream.conf
for id in $service_ids
do    
    ssh compute@$swarm_master_ip "echo \"server $swarm_master_ip:$(docker inspect $id --format {{.Endpoint.Ports}} | awk {'print $4'});\" >> $upstream_conf_path"
done

# Start NGINX load balancers
ssh compute@192.168.215.21 'sudo docker network create --subnet=172.100.101.0/24 yolo_tf_loadBalancer'
ssh compute@192.168.215.21 'sudo docker run -v /mnt/cifs13/yolo_tf/nginx:/etc/nginx/ --network yolo_tf_loadBalancer -p 172.100.101.1:7700:80 --name yolo_tf_LB1 nginx &' &
echo "Created yolo_tf_LB1 in 192.168.215.21"
ssh compute@192.168.215.22 'sudo docker network create --subnet=172.100.101.0/24 yolo_tf_loadBalancer'
ssh compute@192.168.215.22 'sudo docker run -v /mnt/cifs13/yolo_tf/nginx:/etc/nginx/ --network yolo_tf_loadBalancer -p 172.100.101.1:7700:80 --name yolo_tf_LB2 nginx &' &
echo "Created yolo_tf_LB2 in 192.168.215.22"

# for NODE in $(docker node ls --format '{{.ID}}'); do echo -e "${NODE} - $(docker node inspect --format '{{.Status.Addr}}' "${NODE}")"; done | awk {'print $3'}
