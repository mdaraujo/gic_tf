# install Nagios Cross-Platform Agent (ncpa)
# add to the apt sources list
echo "deb https://repo.nagios.com/deb/$(lsb_release -cs) /" > /etc/apt/sources.list.d/nagios.list
# add angios public GPG key
wget -qO - https://repo.nagios.com/GPG-KEY-NAGIOS-V2 | apt-key add -
# update repositories
apt update
# install ncpa
apt install ncpa

# get updated nagios check* files
wget -O /usr/local/ncpa/plugins/check_docker.py https://raw.githubusercontent.com/timdaman/check_docker/master/check_docker/check_docker.py
wget -O /usr/local/ncpa/plugins/check_swarm.py https://raw.githubusercontent.com/timdaman/check_docker/master/check_docker/check_swarm.py
chmod a+rx /usr/local/ncpa/plugins/check_docker.py /usr/local/ncpa/plugins/check_swarm.py

# symlink python3 -> python
ln -s /usr/bin/python3 /usr/local/bin/python

# replace nagios uid and gid with root
sed -i '/^#/!s/uid = nagios/uid = root/g' /usr/local/ncpa/etc/ncpa.cfg
sed -i '/^#/!s/gid = nagios/gid = root/g' /usr/local/ncpa/etc/ncpa.cfg

# add nagios user to docker - not needed
#usermod -a -G docker nagios

# restart service
systemctl restart ncpa_listener.service
