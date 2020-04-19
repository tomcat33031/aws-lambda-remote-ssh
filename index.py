import boto3
import paramiko

def handler(event, context):
    #Get IP addresses of EC2 instances
    client = boto3.client('ec2')
    instDict=client.describe_instances(Filters=[{'Name':'tag:Name','Values':['<name ec2>']}])

    hostList=[]
    for r in instDict['Reservations']:
        for inst in r['Instances']:
            hostList.append(inst['PublicIpAddress'])

    print(hostList)
    if len(hostList) == 0:
        return{
            'message' : "Has 0 Instaces to execute commands"
        }

    s3_client = boto3.client('s3')
    #Download private key file from secure S3 bucket
    s3_client.download_file('<bucketname>','<key.pem>', '/tmp/<key.pem>')

    k = paramiko.RSAKey.from_private_key_file("/tmp/<key.pem>")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host=hostList[0]
    print("Connecting to " + host)
    c.connect( hostname = host, username = "centos", pkey = k )
    print("Connected to " + host)

    commands = [
      "<some command>"
    ]

    for command in commands:
        print("Executing {%s}" % command)
        stdin , stdout, stderr = c.exec_command(command)
        print(stdout.read())
        print(stderr.read())
        del stdin, stdout, stderr

    return{
        'message' : "Script execution completed. See Cloudwatch logs for complete output"
    }
