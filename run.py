# Add two numbers
import os, time
import json, boto3, kubernetes
from nacl import pwhash, secret, utils, encoding

InstanceRoleKey = 'Role'

def getBinaryContent(filename):
    with open(filename, 'rb') as f:
        return f.read()

def writeTextContent(filename, content):
    with open(filename, "w") as f:
        return f.write(content)

def decrypt(password, content):
  kdf = pwhash.argon2i.kdf
  salt = b"1234567890123456"
  ops = pwhash.argon2i.OPSLIMIT_SENSITIVE
  mem = pwhash.argon2i.MEMLIMIT_SENSITIVE

  key = kdf(secret.SecretBox.KEY_SIZE, password.encode('UTF-8'), salt,
            opslimit=ops, memlimit=mem)
  box = secret.SecretBox(key)

  decrypted = box.decrypt(content)
  return decrypted.decode('UTF-8')

def getConfig(filename, password):
  content = getBinaryContent(filename)
  return decrypt(password, content)

def ensureKeyPair(client, kpName, filename):
    print('Ensuring key pair '+kpName)
    fileExists = os.path.isfile(filename)
    try:
        keyPairInfo = client.describe_key_pairs(KeyNames=[kpName])
        keyExists = any(i['KeyName'] == KeyPairName for i in keyPairInfo['KeyPairs'])
    except:
        keyExists = False
    if not fileExists or not keyExists:
        if fileExists:
            print('Deleting '+filename)
            os.remove(filename)
        if keyExists:
            print('Deleting AWS key pair '+kpName)
            client.delete_key_pair(KeyName=kpName)
        print('Creating key pair')
        key_pair = client.create_key_pair(KeyName=KeyPairName)
        print('Writing key pair to '+filename)
        writeTextContent(filename, key_pair['KeyMaterial'])

def createInstance(ec2, role, instanceType, imageId, kpName):
    print('Creating '+instanceType+' with image '+imageId+' with access key '+kpName)
    instances = ec2.create_instances(
            ImageId=imageId,
            InstanceType=instanceType,
            KeyName=kpName,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[{
                'ResourceType': 'instance', 'Tags': [{
                    'Key': InstanceRoleKey,
                    'Value': role
            }]}])
    return instances[0]

def waitFor(client, instance, checkSeconds):
    state = 'pending'
    while state == 'pending':
        time.sleep(checkSeconds)
        resp = client.describe_instance_status(
                InstanceIds=[ instance['id'] ],
                IncludeAllInstances=True)
        instance = next(x for x in resp['InstanceStatuses'] if x['InstanceId'] == instance.id)
        status = instance['InstanceState']['Name']
        print('Instance '+instance['InstanceIdd']+' is in state '+status)
    return instance

def findRole(client, role):
#    try:
        print('Searching for instance with role '+role)
        instances = client.describe_instances(Filters=[{
            'Name': 'tag:'+InstanceRoleKey,
            'Values': [ role ]
        }])
        instance = instances['Reservations'][0]['Instances'][0]
        if instance['State']['Name'] == 'pending':
            instance = waitFor(client, instance['InstanceId'], 2)
        print('Found instance with info: '+str(instance))
        return instance if instance['State']['Name'] == 'running' else None
#    except Exception as e:
#        print(e)
#        return None

def ensureInstance(client, role, instanceType, imageId, kpName):
    instance = findRole(client, role)
    if instance == None:
        print('Instance not found...')
        instance = createInstance(ec2, role, instanceType, imageId, kpName)
        instance = waitFor(client, instance, 2)
    print('Found instance with role '+role)
    return instance

      
### Constants ###
KeyPairName = 'OmniacKeyPair'
KeyPairFilename = 's/.privatekey.pem'
ConfigFilename = 's/.config.encrypted'
T1MicroAmiId = 'ami-7b78ec03'
T2MicroAmiId = 'ami-2773e75f'
InstanceType = 't2.micro'
InstanceRole = 'KuberAdmin'

### Script ###
password = os.environ['CONFIG_PASSWORD'].strip()
if not password:
    raise ValueError("CONFIG_PASSWORD not set")
config = json.loads(getConfig(ConfigFilename, password))
creds = config['aws']['credentials']

print('Getting AWS client')
client = boto3.client('ec2', region_name='us-west-2',
        aws_access_key_id=creds['aws_access_key_id'],
        aws_secret_access_key=creds['aws_secret_access_key'])
print('Getting AWS resource')
ec2 = boto3.resource('ec2', region_name='us-west-2',
        aws_access_key_id=creds['aws_access_key_id'],
        aws_secret_access_key=creds['aws_secret_access_key'])


ensureKeyPair(client, KeyPairName, KeyPairFilename)
ensureInstance(client, InstanceRole, InstanceType, T2MicroAmiId, KeyPairName)


#response = client.request_spot_instances(
#    InstanceCount=1,
#    LaunchSpecification={
#      'ImageId': t2MicroAmiId,
#      'InstanceType': 't2.micro'
#    },
#    SpotPrice='0.0100')
#print(response)


print("done")
