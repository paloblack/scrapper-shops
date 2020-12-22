import paramiko

ssh_client =paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname='almamarket.com',port='18765',username='u322-ehag6zw9kpvu',password='4&F4&*22@tb3',key_filename='private.txt')
