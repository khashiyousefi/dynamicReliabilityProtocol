from mininet.net import Mininet
from mininet.cli import CLI
from mininet.topo import Topo, SingleSwitchTopo
from mininet.log import lg, info

def main():
	lg.setLogLevel('info')
	net = Mininet(SingleSwitchTopo(k=2))
	net.start()

	server = net.get('h1')
	serverIP = server.IP()
	info('server IP: ' + serverIP)
	info('server start')
	process = server.popen('python serverDRP.py -i %s &' % serverIP)

	info('client start')
	client = net.get('h2')
	client.cmd('python clientDRP.py -o test_ouput.txt -i %s &' % serverIP)
	info('end')

	CLI(net)
	process.terminate()
	net.stop()

if __name__ == '__main__':
	main()
