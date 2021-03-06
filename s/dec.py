from sys import argv
from nacl import pwhash, secret, encoding


def getContent(filename, flags):
  with open(filename, 'r'+flags) as f:
    return f.read()
    
def writeContent(filename, content):
  with open(filename, 'w') as f:
    return f.write(content)

def decrypt(password, content):
  kdf = pwhash.argon2i.kdf
  salt = b"1234567890123456"
  ops = pwhash.argon2i.OPSLIMIT_SENSITIVE
  mem = pwhash.argon2i.MEMLIMIT_SENSITIVE

  key = kdf(secret.SecretBox.KEY_SIZE, password.encode('UTF-8'), salt, opslimit=ops, memlimit=mem)
  box = secret.SecretBox(key)
  #nonce = b"123456789012345678901234"

  decrypted = box.decrypt(content)#, nonce)
  return decrypted.decode('UTF-8')

  
passwordFile = argv[1]
contentFile = argv[2]
outputFile = argv[3]
#print("Decrypting file: "+contentFile)

toDecrypt = getContent(contentFile, 'b')
#print("TO DECRYPT:\n" + toDecrypt)

line = getContent(passwordFile, '')
key, password = line.split('=')
#print("PASSWORD: " + password)

decrypted = decrypt(password, toDecrypt)
#print("DECRYPTED:\n"+decrypted)

writeContent(outputFile, decrypted)

print("done")
