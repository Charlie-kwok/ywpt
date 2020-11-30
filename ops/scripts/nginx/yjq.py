#! coding:utf-8

import paramiko,time,sys



def sftp_Connect(hostname):
#用来连接远程服务器，用sftp
    transport  = paramiko.Transport((hostname,22))
    private_key  = paramiko.RSAKey.from_private_key_file('sigoadmin')
    transport.connect(username='sigoadmin',pkey=private_key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp
def ssh_Connect(hostname):
#用来连接远程服务器，执行shell命令
    ssh  = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key  = paramiko.RSAKey.from_private_key_file('sigoadmin')
    ssh.connect(hostname=hostname,username='sigoadmin',port=22,pkey=private_key)
    invoke = ssh.invoke_shell()
    invoke.keep_this = ssh
    return invoke


class Order:
#连接远程服务器后，执行命令类
    def __init__(self,hostname):
        self.invoke= ssh_Connect(hostname)
        time.sleep(0.5)
    def command(self,order):
        self.invoke.send('{order}\n'.format(order=order))
        result = ''
        while True:
            time.sleep(0.5)
            res = self.invoke.recv(65535).decode('utf8')
            result += res
            if result:
                sys.stdout.write(result.strip('\n'))
                time.sleep(1)
            if res.endswith('# ') or res.endswith('$ ')or res.endswith(': '):
                time.sleep(1)
                break
    def finished(self):
        self.invoke.send("echo 'ByeBye'")
        self.invoke.close()


class transport_file:
#传输文件
    def __init__(self,hostname):
        self.sftp = sftp_Connect(hostname)
        self.hostname = hostname
    def get_file(self):
        self.sftp.get('/home/sigoadmin/grey_rule.conf', '../conf/now.conf')
        self.sftp.close()
    def put_env_file(self,env):
        if env == 'grey':
            answer = input('当前环境为正式环境，是否切换到灰度[N/Y] ? ： ')
            if answer.lower() == 'y':
                print('切换到灰度中，请稍等。')
                self.sftp.put('../conf/{env}.conf'.format(env=env), '/home/sigoadmin/grey_rule.conf')
            else:
                exit(1)
        if env == 'prod':
            answer = input('当前环境为灰度环境，是否切换到正式[N/Y] ? :')
            if answer.lower() == 'y':
                print('切换到正式中，请稍等。')
                self.sftp.put('../conf/{env}.conf'.format(env=env), '/home/sigoadmin/grey_rule.conf')
            else:
                exit(1)
        a = Order(self.hostname)
        a.command('sudo nginx -t')
        print('\n整体已经完成。')

if __name__ == '__main__':
    transport_file('10.0.180.44').get_file()
    with open('../conf/now.conf','r',encoding='utf-8') as f:
        a = f.readline().split()[2].split(';')[0]
        f.close()
    if a == '0':
        env ='grey'
    elif a == '1':
        env ='prod'
    else:
        env = ''
    transport_file('10.0.180.44').put_env_file(env)




