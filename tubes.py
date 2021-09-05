from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import Node
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.util import pmonitor
from mininet.cli import CLI
from signal import SIGINT
from time import time, sleep
import os

#Ryan Abdurohman (1301191171)
#IF-43-10 S-1 Informatika

def testIperf( net, server, client ):
    popens = {}
    tperf = 20
    tout = ( tperf + 1 ) * 4
    stopPerf = time() + tout + 5
    inv = 2
    
    popens[ net[ server ] ] = net[ server ].popen( 'iperf -s -t '+str( tout ) )
    popens[ net[ client ] ] = net[ client ].popen( 'iperf -c '+net[ server ].IP()+' -i '+str(inv)+' -t '+str( tperf ) )

    logserver = logclient1 = logclient2 = logclient3 = ""

    for host, line in pmonitor(popens, timeoutms=(tperf + tout) * 4):
        if host:
            if host.name == server: logserver += (host.name +": "+line)
            elif host.name == client: logclient1 += (host.name +": "+line)
            # elif host.name == clients[1]: logclient2 += (host.name +": "+line)
            # elif host.name == clients[2]: logclient3 += (host.name +": "+line)

        if time() >= stopPerf:
            for p in popens.values(): p.send_signal(SIGINT)

    print(logserver)
    print(logclient1)
    print(logclient2)
    print(logclient3)
    

class LinuxRouter( Node ):
	"""A Node with IP forwarding enabled.
	Means that every packet that is in this node, comunicate freely with its interfaces."""

	def config( self, **params ):
		super( LinuxRouter, self).config( **params )
		self.cmd( 'sysctl net.ipv4.ip_forward=1' )

	def terminate( self ):
		self.cmd( 'sysctl net.ipv4.ip_forward=0' )
		super( LinuxRouter, self ).terminate()

class simpleTopo:
    def __init__(self):
        self.net = Mininet( link=TCLink )
        #Add Router
        self.r1 = self.net.addHost('r1', cls=LinuxRouter, ip='10.0.0.2/24')
        self.r2 = self.net.addHost('r2', cls=LinuxRouter, ip='10.0.1.1/24')
        self.r3 = self.net.addHost('r3', cls=LinuxRouter, ip='10.0.7.1/24')
        self.r4 = self.net.addHost('r4', cls=LinuxRouter, ip='10.0.6.2/24')

        #Add Host
        self.h1 = self.net.addHost('h1', ip='10.0.0.1/24')
        self.h2 = self.net.addHost('h2', ip='10.0.7.2/24')

    def addLink(self, buff):
        self.net.addLink(self.h1, self.r1, intfName1='h1-eth0',intfName2='r1-eth0', bw=1)
        self.net.addLink(self.h1, self.r2, intfName1='h1-eth1',intfName2='r2-eth0', bw=1)
        self.net.addLink(self.h2, self.r3, intfName1='h2-eth0',intfName2='r3-eth0',bw=1, max_queue_size=buff)#, use_htb=True) 
        self.net.addLink(self.h2, self.r4, intfName1='h2-eth1',intfName2='r4-eth0',bw=1 ) 
        self.net.addLink(self.r1, self.r3, intfName1='r1-eth1', intfName2='r3-eth1', bw=0.5, max_queue_size=buff)#, use_htb=True)
        self.net.addLink(self.r1, self.r4, intfName1='r1-eth2', intfName2='r4-eth2', bw=1)
        self.net.addLink(self.r2, self.r3, intfName1='r2-eth2', intfName2='r3-eth2', bw=1, max_queue_size=buff)#, use_htb=True)
        self.net.addLink(self.r2, self.r4, intfName1='r2-eth1', intfName2='r4-eth1', bw=0.5)
    
    def configIP(self):

        self.h1.cmd('ifconfig h1-eth1 10.0.1.2 netmask 255.255.255.0')
        self.h2.cmd('ifconfig h2-eth0 10.0.7.2 netmask 255.255.255.0')
        self.h2.cmd('ifconfig h2-eth1 10.0.6.1 netmask 255.255.255.0')

        self.r1.cmd( 'ip addr add 10.0.0.2/24 brd + dev r1-eth0' )
        self.r1.cmd( 'ip addr add 10.0.2.1/24 brd + dev r1-eth1' )
        self.r1.cmd( 'ip addr add 10.0.3.1/24 brd + dev r1-eth2' )

        self.r2.cmd( 'ip addr add 10.0.1.1/24 brd + dev r2-eth0' )
        self.r2.cmd( 'ip addr add 10.0.4.2/24 brd + dev r2-eth1' )
        self.r2.cmd( 'ip addr add 10.0.5.2/24 brd + dev r2-eth2' )

        self.r3.cmd( 'ip addr add 10.0.7.1/24 brd + dev r3-eth0' )
        self.r3.cmd( 'ip addr add 10.0.2.2/24 brd + dev r3-eth1' )
        self.r3.cmd( 'ip addr add 10.0.5.1/24 brd + dev r3-eth2' )

        self.r4.cmd( 'ip addr add 10.0.6.2/24 brd + dev r4-eth0' )
        self.r4.cmd( 'ip addr add 10.0.4.1/24 brd + dev r4-eth1' )
        self.r4.cmd( 'ip addr add 10.0.3.2/24 brd + dev r4-eth2' )
        
    
    def ping(self):
        info( '\n ------HOST 1 PING ROUTER 1------ \n' )
        self.h1.cmdPrint( 'ping -c 3 10.0.0.2' )
        sleep(2)
        info( '\n ------HOST 1 PING ROUTER 2------ \n' )
        self.h1.cmdPrint( 'ping -c 3 10.0.1.1' )
        sleep(2)
        info( '\n ------HOST 2 PING ROUTER 3------ \n' )
        self.h2.cmdPrint( 'ping -c 3 10.0.7.1' )
        sleep(2)
        info( '\n ------HOST 2 PING ROUTER 4------ \n' )
        self.h2.cmdPrint( 'ping -c 3 10.0.6.2' )
        sleep(2)
        info( '\n ------ROUTER 1 PING ROUTER 4------ \n' )
        self.r1.cmdPrint( 'ping -c 3 10.0.3.2' )
        sleep(2)
        info( '\n ------ROUTER 1 PING ROUTER 3------ \n' )
        self.r1.cmdPrint( 'ping -c 3 10.0.2.2' )
        sleep(2)
        info( '\n ------ROUTER 1 PING HOST 1------ \n' )
        self.r1.cmdPrint( 'ping -c 3 10.0.0.1' )
        sleep(2)
        info( '\n ------ROUTER 2 PING HOST 1------ \n' )
        self.r2.cmdPrint( 'ping -c 3 10.0.1.2' )
        sleep(2)
        info( '\n ------ROUTER 2 PING ROUTER 4------ \n' )
        self.r2.cmdPrint( 'ping -c 3 10.0.4.1' )
        sleep(2)
        info( '\n ------ROUTER 2 PING ROUTER 3------ \n' )
        self.r2.cmdPrint( 'ping -c 3 10.0.5.1' )
        sleep(2)
        info( '\n ------ROUTER 3 PING ROUTER 1------ \n' )
        self.r3.cmdPrint( 'ping -c 3 10.0.2.1' )
        sleep(2)
        info( '\n ------ROUTER 3 PING HOST 2------ \n' )
        self.r3.cmdPrint( 'ping -c 3 10.0.7.2' )
        sleep(2)
        info( '\n ------ROUTER 3 PING ROUTER 2------ \n' )
        self.r3.cmdPrint( 'ping -c 3 10.0.5.2' )
        sleep(2)
        info( '\n ------ROUTER 4 PING HOST 2------ \n' )
        self.r4.cmdPrint( 'ping -c 3 10.0.6.1' )
        sleep(2)
        info( '\n ------ROUTER 4 PING ROUTER 1------ \n' )
        self.r4.cmdPrint( 'ping -c 3 10.0.3.1' )
        sleep(2)
        info( '\n ------ROUTER 4 PING ROUTER 2------ \n' )
        self.r4.cmdPrint( 'ping -c 3 10.0.4.2' )
    
    def staticRoute(self):
        self.r1.cmd('ip route add 10.0.7.1 via 10.0.2.2 dev r1-eth1')
        self.r1.cmd('ip route add 10.0.7.2 via 10.0.2.2 dev r1-eth1')
        self.r1.cmd('ip route add 10.0.6.1 via 10.0.3.2 dev r1-eth2')
        self.r1.cmd('ip route add 10.0.6.2 via 10.0.3.2 dev r1-eth2')
        self.r1.cmd('ip route add 10.0.4.1 via 10.0.3.2 dev r1-eth2')
        self.r1.cmd('ip route add 10.0.4.2 via 10.0.3.2 dev r1-eth2')
        self.r1.cmd('ip route add 10.0.1.1 via 10.0.2.2 dev r1-eth1')
        self.r1.cmd('ip route add 10.0.1.2 via 10.0.2.2 dev r1-eth1')
        self.r1.cmd('ip route add 10.0.5.1 via 10.0.2.2 dev r1-eth1')
        self.r1.cmd('ip route add 10.0.5.2 via 10.0.2.2 dev r1-eth1')

        self.r2.cmd('ip route add 10.0.6.1 via 10.0.4.1 dev r2-eth1')
        self.r2.cmd('ip route add 10.0.6.2 via 10.0.4.1 dev r2-eth1')
        self.r2.cmd('ip route add 10.0.7.1 via 10.0.5.1 dev r2-eth2')
        self.r2.cmd('ip route add 10.0.7.2 via 10.0.5.1 dev r2-eth2')
        self.r2.cmd('ip route add 10.0.2.1 via 10.0.5.1 dev r2-eth2')
        self.r2.cmd('ip route add 10.0.2.2 via 10.0.5.1 dev r2-eth2')
        self.r2.cmd('ip route add 10.0.0.1 via 10.0.4.1 dev r2-eth1')
        self.r2.cmd('ip route add 10.0.0.2 via 10.0.4.1 dev r2-eth1')
        self.r2.cmd('ip route add 10.0.3.2 via 10.0.4.1 dev r2-eth1')
        self.r2.cmd('ip route add 10.0.3.1 via 10.0.4.1 dev r2-eth1')

        self.r3.cmd('ip route add 10.0.0.1 via 10.0.2.1 dev r3-eth1')
        self.r3.cmd('ip route add 10.0.0.2 via 10.0.2.1 dev r3-eth1')
        self.r3.cmd('ip route add 10.0.1.1 via 10.0.5.2 dev r3-eth2')
        self.r3.cmd('ip route add 10.0.1.2 via 10.0.5.2 dev r3-eth2')
        self.r3.cmd('ip route add 10.0.4.1 via 10.0.5.2 dev r3-eth2')
        self.r3.cmd('ip route add 10.0.4.2 via 10.0.5.2 dev r3-eth2')
        self.r3.cmd('ip route add 10.0.6.1 via 10.0.5.2 dev r3-eth2')
        self.r3.cmd('ip route add 10.0.6.2 via 10.0.5.2 dev r3-eth2')
        self.r3.cmd('ip route add 10.0.3.1 via 10.0.2.1 dev r3-eth1')
        self.r3.cmd('ip route add 10.0.3.2 via 10.0.2.1 dev r3-eth1')

        self.r4.cmd('ip route add 10.0.1.1 via 10.0.4.2 dev r4-eth1')
        self.r4.cmd('ip route add 10.0.1.2 via 10.0.4.2 dev r4-eth1')
        self.r4.cmd('ip route add 10.0.0.1 via 10.0.3.1 dev r4-eth2')
        self.r4.cmd('ip route add 10.0.0.2 via 10.0.3.1 dev r4-eth2')
        self.r4.cmd('ip route add 10.0.2.1 via 10.0.3.1 dev r4-eth2')
        self.r4.cmd('ip route add 10.0.2.2 via 10.0.3.1 dev r4-eth2')
        self.r4.cmd('ip route add 10.0.5.1 via 10.0.4.2 dev r4-eth1')
        self.r4.cmd('ip route add 10.0.5.2 via 10.0.4.2 dev r4-eth1')
        self.r4.cmd('ip route add 10.0.7.1 via 10.0.4.2 dev r4-eth1')
        self.r4.cmd('ip route add 10.0.7.2 via 10.0.4.2 dev r4-eth1')

        #self.h1.cmd('ip rule add 10.0.0.1 from table 1')
        #self.h1.cmd('ip rule add 10.0.1.2 from table 2')
        #self.h1.cmd('ip route add 10.0.0.0/24 dev h1-eth0 scope link table 1')
        self.h1.cmd('ip route add default via 10.0.0.2 dev h1-eth0')
        #self.h1.cmd('ip route add 10.0.1.0/24 dev h1-eth0 scope link table 2')
        self.h1.cmd('ip route add default via 10.0.1.1 dev h1-eth1')
        self.h1.cmd('ip route add default scope global nexthop via 10.0.0.2 dev h1-eth0')

        #self.h2.cmd('ip rule add 10.0.7.2 from table 3')
        #self.h2.cmd('ip rule add 10.0.6.1 from table 4')
        #self.h2.cmd('ip route add 10.0.7.0/24 dev h2-eth0 scope link table 3')
        self.h2.cmd('ip route add default via 10.0.7.1 dev h2-eth0')
        #self.h2.cmd('ip route add 10.0.6.0/24 dev h2-eth1 scope link table 4')
        self.h2.cmd('ip route add default via 10.0.6.2 dev h2-eth1')
        self.h2.cmd('ip route add default scope global nexthop via 10.0.7.1 dev h2-eth0')

    def setCBQ(self):
        # Set Queue Discipline to CBQ
        # reset queue discipline
        self.r3.cmd( 'tc qdisc del dev r3-eth0 root' ) 

        # add queue discipline root here
        self.r3.cmd( 'tc qdisc add dev r3-eth0 root handle 1: cbq rate 1Mbit avpkt 1000' ) 
        
        # add queue discipline classes here 
        self.r3.cmd( 'tc class add dev r3-eth0 parent 1: classid 1:1 cbq rate 500Kbit avpkt 1000 bounded' ) 
        self.r3.cmd( 'tc class add dev r3-eth0 parent 1: classid 1:2 cbq rate 500Kbit avpkt 1000 isolated' ) 

        # add queue discipline filters
        #self.r3.cmd( 'tc filter add dev r3-eth0 parent 1: protocol ip u32 match ip src 10.0.7.2 flowid 1:1' ) #ip h2 (server)
        #self.r3.cmd( 'tc filter add dev r3-eth0 parent 1: protocol ip u32 match ip src 10.0.1.2 flowid 1:2' ) #ip h1 (client)
        self.r3.cmdPrint( 'tc qdisc show dev r3-eth0' )
        info( '\n' )
    
    def setHTB(self):
        # Set Queue Discipline to htb
        info( '\n*** Queue Discipline :\n' )
        
        # reset queue discipline
        self.r3.cmdPrint( 'tc qdisc del dev r3-eth0 root' ) 

        # add queue discipline root
        self.r3.cmdPrint( 'tc qdisc add dev r3-eth0 root handle 1: htb ' ) 

        #Add classs for root
        self.r3.cmdPrint( 'tc class add dev r3-eth0 parent 1: classid 1:1 htb rate 500Kbit ' )
        
        # add queue dicipline classes  
        self.r3.cmdPrint( 'tc class add dev r3-eth0 parent 1: classid 1:2 htb rate 500Kbit ' )

        # add queue dicipline filters (can use port to divide based on data delivery port)
        self.r3.cmdPrint( 'tc filter add dev r3-eth0 parent 1: protocol ip prio 1 u32 match ip src 10.0.7.2 flowid 1:2' ) 
        self.r3.cmdPrint( 'tc filter add dev r3-eth0 parent 1: protocol ip prio 1 u32 match ip src 10.0.1.2 flowid 1:1' ) 
        
        self.r3.cmdPrint( 'tc qdisc show dev r3-eth0' )
        info( '\n' )

        
    def start(self, b):
        self.addLink(b)
        self.configIP()
        self.staticRoute()
        self.net.build()
        self.net.start()
        self.setCBQ()
        #self.setHTB()
        #self.ping()
        #info('\n---------Buffer Size: '+str(b)+'---------')
        #testIperf( self.net, 'h2', 'h1' )
        info( '\n' )
        CLI(self.net)
        self.net.stop()

if __name__ == '__main__':
    b = 20
    os.system('mn -c')
    os.system( 'clear' )
    setLogLevel( 'info' )
    topogw = simpleTopo()
    topogw.start(b)
