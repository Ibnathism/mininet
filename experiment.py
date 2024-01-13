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
            host = self.addHost('h%s' % (h + 1), cpu=.5 / n)
            self.addLink(host, switch, bw=100, delay='5ms', loss=0, use_htb=True)
        
        self.addLink(switch, switch2, bw=10)
        host0 = self.addHost('h0', cpu=.5 / n)
        self.addLink(host0, switch2, bw=100, delay='5ms', loss=0, use_htb=True)



def perfTest():
    "Create network and run simple performance test"
    topo = SingleSwitchTopo( n=4)
    net = Mininet( topo=topo,
                   host=CPULimitedHost, link=TCLink,
                   autoStaticArp=True )
    net.start()
    net.pingAll()


    server = net.get('h0')
    
    for i in range(1, 5):
        host = net.get('h' + str(i))
        port = 12345 + i  
        
        server_cmd = 'nc -l -p ' + str(port) + ' > var/www/html/received_file' + str(i) + '.txt &' 
        server.cmdPrint(server_cmd)

        transfer_cmd = 'time nc 10.0.0.1 ' + str(port) + ' < var2/h' + str(i) + '/hello.txt &'
        host.cmdPrint(transfer_cmd)

    time.sleep(10)

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