import optparse
from keyczar.keys import RsaPrivateKey,RsaPublicKey,AesKey
from twisted.internet import reactor, protocol

class CryptoClient(protocol.Protocol):    
    def dataReceived(self, data):
        "As soon as any data is received, print it, read the public key received, encrypt a string with it and send it back."
        print "Received public key is",data
        key=RsaPublicKey.Read(data)
        sym=AesKey.Generate()
        print "Generated AES key is", sym
        symenc=sym.Encrypt(self.factory.message)
        enc=key.Encrypt(str(sym))
        self.transport.write(enc+str(symenc))
    
    def connectionLost(self, reason):
        print "connection lost"

class CryptoFactory(protocol.ClientFactory):
    protocol = CryptoClient
    def __init__(self,message):
        self.message=message
    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        reactor.stop()

def main():
    parser = optparse.OptionParser()
    parser.add_option('-p', '--port', action = 'store', type = 'int', dest = 'port', default = 1234, help = 'listening port')
    parser.add_option('-m','--message',action = 'store', type = 'string',dest = 'message', default = 'Alice,Bob says Hi!', help = 'message to be sent')
    (options, args) = parser.parse_args()
    f = CryptoFactory(options.message)
    reactor.connectTCP("localhost", options.port, f)
    reactor.run()

if __name__ == '__main__':
    main()
