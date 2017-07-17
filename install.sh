#Runs both libpydhcpserver and staticDHCPd's installation scripts
cd libpydhcpserver
/usr/bin/env python setup.py install
cd ..

cd staticDHCPd
/usr/bin/env python setup.py install
cd ..

sudo cp conf.py /etc/staticDHCPd/conf.py

sudo cp dhcp.ini /etc/staticDHCPd/dhcp.ini
