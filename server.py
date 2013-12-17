import optparse
from keyczar.keys import RsaPrivateKey,AesKey
from twisted.internet import reactor, protocol
from twisted.protocols import basic

class CryptoProtocol(basic.LineReceiver):

	def connectionMade(self):
		"""
		Runs when a connection is made. Generates a public/private key pair and sends the public key to the client"""
		self.factory.clients.append(self)
		self.file_handler = None
		self.file_data = ()
		self.key=RsaPrivateKey.Generate()
		self.pubkey=self.key.public_key
		self.transport.write(str(self.pubkey))
		print 'Connection from: %s (%d clients total)' % (self.transport.getPeer().host, len(self.factory.clients))
		
	def connectionLost(self, reason):
		self.factory.clients.remove(self)
		print 'Connection from %s lost (%d clients left)' % (self.transport.getPeer().host, len(self.factory.clients))
			
	def dataReceived(self, data):
		"""
		Runs when data is received from the client. Takes the first 261 bytes and decrypts it using the private key.
		This is the AesKey generated at the client. This is used to decrypt the rest of the data.
		"""
		straes=self.key.Decrypt(data[:261])
		self.AES=AesKey.Read(straes)
		print self.AES.Decrypt(data[261:])

class CryptoServerFactory(protocol.ServerFactory):
	
	protocol = CryptoProtocol
	
	def __init__(self):
		
		self.clients = []
	
if __name__ == '__main__':
	parser = optparse.OptionParser()
	parser.add_option('-p', '--port', action = 'store', type = 'int', dest = 'port', default = 1234, help = 'listening port')
	(options, args) = parser.parse_args()
	
	print 'Listening on port %d' % (options.port)

	reactor.listenTCP(options.port, CryptoServerFactory())
	reactor.run()
