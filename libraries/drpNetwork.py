from mininet.topo import Topo

class DrpNetwork(Topo):
	def __init__(self):
		# Initialize topology
		Topo.__init__(self)

		# Add hosts and switches
		server = self.addHost('h1')
		client = self.addHost('h2')
		leftSwitch = self.addSwitch('s3')
		rightSwitch = self.addSwitch('s4')

		# Add links
		self.addLink(server, leftSwitch)
		self.addLink(leftSwitch, rightSwitch)
		self.addLink(rightSwitch, client)

topos = {'mytopo': (lambda: DrpNetwork())}
