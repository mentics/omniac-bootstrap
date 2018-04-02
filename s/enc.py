from sys import argv
from nacl import pwhash, secret, encoding


def getContent(filename):
  with open(filename) as f:
    return f.read()
    
def writeContent(filename, content):
  with open(filename, "wb") as f:
    return f.write(content)

def encrypt(password, content):
  kdf = pwhash.argon2i.kdf
  salt = b"1234567890123456"
  ops = pwhash.argon2i.OPSLIMIT_SENSITIVE
  mem = pwhash.argon2i.MEMLIMIT_SENSITIVE

  key = kdf(secret.SecretBox.KEY_SIZE, password.encode('UTF-8'), salt, opslimit=ops, memlimit=mem)
  box = secret.SecretBox(key)
  #nonce = b"123456789012345678901234"

  encrypted = box.encrypt(content.encode('UTF-8'))
  return encrypted

passwordFile = argv[1]
contentFile = argv[2]
outputFile = argv[3]
#print("Encrypting file: "+argv[1])

toEncrypt = getContent(contentFile)
#print("TO ENCRYPT:\n" + toEncrypt)

entry = getContent(passwordFile)
key, password = entry.split('=')
password = password.strip()
print("PASSWORD: [" + password + ']')

encrypted = encrypt(password, toEncrypt)
#print("ENCRYPTED:\n"+encrypted)

writeContent(outputFile, encrypted)

print("done")
