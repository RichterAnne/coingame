import sys, json
import gnupg
import pyaudio, audioop
from twisted.internet import protocol, reactor
from twisted.internet.protocol import Factory

class EchoClient(protocol.Protocol):
  
    def __init__(self):
        #Buffer to save Audio-Binary
        self.buffer = []
        self.callflag = 1
        #Init GPG-Object
        self.gpg = gnupg.GPG(gnupghome='/home/kalipso/.gnupg')
        #PyAudio Chunk
        self.CHUNK = 1024
        self.frames = []
        #Pyaudio Object
        self.p = pyaudio.PyAudio()
        #Pyaudio Stream
        self.stream = self.p.open(format=pyaudio.paInt16,
			channels=18,
			rate=44100,
			input=True,
			output=True,
			frames_per_buffer=1024)
  
    def dataReceived(self, data):
        #When dataReceived play it
        self.de_play(data)
        self.sendMic()

    def connectionMade(self):
        self.sendMic()

    def checklen(self):
        #Waits till buffer has the size of n (later waits for button event)
        n = 10
        if (len(self.buffer) > n):
            self.en_send()
        else:
            self.sendMic()

    def de_play(self, data):
       	#Plays received audio, but first it gets decrypted 
        data = data.decode('utf-8')
        decrypted_data = self.gpg.decrypt(data, passphrase='test')
        print("DECRYPTED: " + str(decrypted_data))
        self.buffer = ""
        """
        for i in range(0,1000):
            self.stream.write(str(decrypted_data), self.CHUNK)
        """
    def en_send(self):
       	#Sends recorded Audio, but first it gets encrypted 
        bytearray = bytes(self.buffer) #Formats List into array of Bytes bytes([17, 24, 121, 1, 12, 222, 34, 76])
        encrypted_ascii_data = self.gpg.encrypt(bytearray, 'bla@bla.de')
        encrypted_string = str(encrypted_ascii_data)   
        self.transport.write(encrypted_string.encode('utf-8'))
     

    def sendMic(self):
       	#Reads Microphone input
        #Should get merged with checklen() 
        #self.buffer.append(self.stream.read(self.CHUNK))
        self.buffer.append("TEST")
        self.checklen()
		
class EchoFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        return EchoClient()
    def clientConnectionFailed(self, connector, reason):
        print("Connection Failed")
        reactor.stop()
    def clientConnectionLost(self, connector, reason):
        print("Connection Lost")
        reactor.stop()

reactor.connectTCP("localhost", 7000, EchoFactory())
print("Start")
reactor.run()
