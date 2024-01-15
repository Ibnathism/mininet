#!/usr/bin/env python

"""
Simple example of setting network and CPU parameters

NOTE: link params limit BW, add latency, and loss.
There is a high chance that pings WILL fail and that
iperf will hang indefinitely if the TCP handshake fails
to complete.
"""

from sys import argv
import time
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost, OVSKernelSwitch, DefaultController
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info

class SingleSwitchTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self, n=2):
        switch = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        for h in range(n):
            # Each host gets 50%/n of system CPU
            host = self.addHost('h%s' % (h), cpu=.5 / (n+1))
            self.addLink(host, switch, bw=100, delay='5ms', loss=0, use_htb=True)
        
        self.addLink(switch, switch2, bw=10)
        server = self.addHost('server', cpu=.5 / (n+1))
        self.addLink(server, switch2, bw=100, delay='5ms', loss=0, use_htb=True)



def perfTest():
    "Create network and run simple performance test"
    topo = SingleSwitchTopo( n=10)
    net = Mininet( topo=topo,
                   host=CPULimitedHost, link=TCLink,
                   autoStaticArp=True )
    net.start()
    # net.pingAll()


    server = net.get('server')
    server_IP = server.IP()
    port_counter = 0
    for j in range (0, 10): 
        for i in range(0, 10):
            host = net.get('h' + str(i))
            port = 12345 + port_counter  
            
            server_cmd = 'nc -l -p ' + str(port) + ' > saved_models/server/user' + str(i) + '/u' + str(i) + '_r' + str(j) + '.pth &'  # '/hello.txt &'
            
            server.cmdPrint(server_cmd)

            transfer_cmd = 'time nc ' + server_IP + ' ' + str(port) + ' < saved_models/users/user' + str(i) + '/u' + str(i) + '_r' + str(j) + '.pth &' # '/hello.txt &'
            
            host.cmdPrint(transfer_cmd)

            time.sleep(100)
            port_counter = port_counter + 1
        
        time.sleep(100)

    

    # Debugging
    # h1.cmd('jobs')
    # h4.cmd('jobs')
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    # Debug for now
    if 'testmode' in argv:
        setLogLevel( 'debug' )
    # Prevent test_simpleperf from failing due to packet loss
    # perfTest( lossy=( 'testmode' not in argv ) )
    perfTest()