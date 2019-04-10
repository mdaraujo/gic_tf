SERVICE_NAME="yolo_tf"

docker stats $(docker ps --format "{{.ID}}" --filter name=^/$SERVICE_NAME*) --no-stream --format "$(date),$(hostname),{{.MemUsage}},{{.MemPerc}},{{.CPUPerc}},{{.ID}},{{.Name}}" | grep $SERVICE_NAME >> /mnt/cifs13/yolo_tf/logs.csv
