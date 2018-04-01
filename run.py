# Add two numbers
import json, boto3, kubernetes, os
from nacl import pwhash, secret, utils, encoding


def getConfig():
  content = getContent('s/config.encrypted')
  print('encrypted content: '+content)
  password = os.environ['CONFIG_PASSWORD']
  print('env var psw: ['+password+']')
  password = 'testing'
  if not password:
    raise ValueError("CONFIG_PASSWORD not set")
  return decrypt(password, content)

def decrypt(password, content):
  kdf = pwhash.argon2i.kdf
  salt = b"1234567890123456"
  ops = pwhash.argon2i.OPSLIMIT_SENSITIVE
  mem = pwhash.argon2i.MEMLIMIT_SENSITIVE

  key = kdf(secret.SecretBox.KEY_SIZE, password.encode('UTF-8'), salt, opslimit=ops, memlimit=mem)
  box = secret.SecretBox(key)
  nonce = b"123456789012345678901234"

  toDecrypt = encoding.Base64Encoder.decode(content.encode('UTF-8'))
  decrypted = box.decrypt(toDecrypt, nonce)
  return decrypted.decode('UTF-8')

def getContent(filename):
  with open(filename) as f:
      return f.read()

config = json.loads(getConfig())
creds = config['aws']['credentials']
ec2 = boto3.resource('ec2',
    aws_access_key_id=creds['aws_access_key_id'],
    aws_secret_access_key=creds['aws_secret_access_key'])
print("Instace statuses:")
print(ec2.meta.client.describe_instance_status())

print("done")
