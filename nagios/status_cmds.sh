
# Memory Usage
python check_docker.py --memory 70:80:% --containers '^yolo_tf.*'
check_xi_ncpa!-t 'yolo_tf' -P 5693 -M plugins/check_docker.py -q "args=--memory 70:80:%,args=--containers '^yolo_tf.*'"

# CPU Usage
python check_docker.py --cpu 70:90 --containers '^yolo_tf.*'
check_xi_ncpa!-t 'yolo_tf' -P 5693 -M plugins/check_docker.py -q "args=--cpu 70:90,args=--containers '^yolo_tf.*'"

# Containers Are Running
python check_docker.py --status 'running' --containers '^yolo_tf.*' 
check_xi_ncpa!-t 'yolo_tf' -P 5693 -M plugins/check_docker.py -q "args=--status 'running',args=--containers '^yolo_tf.*'"


## Copy cfg files to nagios
scp *.cfg root@192.168.215.196:/usr/local/nagios/etc/import

## Get cfg files
scp root@192.168.215.196:/usr/local/nagios/etc/contacts.cfg /home/miguel/Documents/


## Copy scale up event handler to nagios
scp yolo_tf_event_scale_up.sh root@192.168.215.196:/usr/local/nagios/libexec
