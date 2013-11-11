#!/bin/bash
cd pre-reque
rpm -Uvh python-argparse-1.2.1-2.el6.noarch.rpm
yum -y install python-setuptools.noarch

tar -zxvf ntplib-0.3.1.tar.gz
cd ntplib-0.3.1
python setup.py install

cd ..
tar -zxvf lockfile-0.9.1.tar.gz
cd lockfile-0.9.1
python setup.py install

cd ..
tar -zxvf python-daemon-1.6.tar.gz
cd python-daemon-1.6
python setup.py install

cd ..
tar -zxvf daemon-runner-0.0.14.tar.gz
cd daemon-runner-0.0.14
python setup.py install

cd ..
tar -zxvf suds-0.4.tar.gz
cd suds-0.4
python setup.py install

cd ..
tar -zxvf pycontrol-2.1.tar.gz
cd pycontrol-2.1
python setup.py install

cd ..
tar -zxvf mysql-connector-python-1.0.12.tar.gz
cd mysql-connector-python-1.0.12
python setup.py install

cd .. 
tar -zxvf psutil-1.1.2.tar.gz
cd psutil-1.1.2/
python setup.py install

cd ..
cp zabbix_sender /opt/dpcollector/bin/
cp init-start-script /etc/init.d/dpcollector

if [ ! -f /opt/dpcollector/dpcollector.conf ]; then
	cp /opt/dpcollector/dpcollector.conf /opt/dpcollector/
fi
