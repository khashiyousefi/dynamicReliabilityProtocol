from mininet.net import Mininet
from mininet.cli import CLI
from mininet.topo import Topo, SingleSwitchTopo
from libraries.drpNetwork import *

def main():
	net = Mininet(SingleSwitchTopo(k=2))
	net.start()

	server = net.get('h1')
	process = server.popen('python serverDRP.py -r 2')

	client = net.get('h2')
	client.cmd('python clientDRP.py')

	CLI(net)
	process.terminate()
	net.stop()

if __name__ == '__main__':
	main()
