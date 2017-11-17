from optparse import OptionParser
import configparser
import paramiko
from concurrent.futures import ProcessPoolExecutor
from conf import config
from lib import common
data=set()
#要拿到logger对象
logger1=common.get_logger(__name__) #core.src
logger2=common.get_logger('collect')
def task(line,cmd,res):
    """
      并发执行函数
      :param line:
      :param cmd:
      :param res:
      :return: result
      """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=res.get(line,'ip'),port=res.get(line,'port'),username=res.get(line,'user'),password=res.get(line,'password'))
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read()
    ssh.close()
    return result.decode('utf-8')
def main():
    """
        主函数(逻辑程序)
        :return:
    """
    parse = OptionParser(usage='"usage:%prog [options] arg1,arg2 ..."')
    parse.add_option('-u', '--user', dest='user', action='store', type=str, metavar='user', help='Input User Name!!')
    parse.add_option('-g', '--group', dest='group', type=str, metavar='group', help='Input Group Name')
    parse.add_option('-c', '--cmd', dest='command', type=str, metavar='command', help='Input Linux Command')
    options, args = parse.parse_args()
    cmd = options.command
    res = configparser.ConfigParser()
    res.read(config.SERVER_PATH)
    if ',' in  options.group:
        groupinfo=set(options.group.split(','))
        for group in groupinfo:
            groups=res.get(group, 'groups')
            if ',' in groups:
                group_list=groups.split(',')
                for info in group_list:
                    data.add(info)
            else:
                data.add(groups)
    else:
        groupinfo = res.get(options.group,'groups')
        if ',' in groupinfo:
            groupinfo=groupinfo.split(',')
            for info in groupinfo:
                data.add(info)
        else:
            data.add(groupinfo)

    if ',' in  options.user:
        userinfo=set(options.user.split(','))
        for user in userinfo:
            data.add(user)
    else:
        data.add(options.user)

    process = ProcessPoolExecutor()
    futures = []
    for line in data:
        obj=process.submit(task,line,cmd,res)
        futures.append(obj)
    process.shutdown(wait=True)
    for future in futures:
        print(future.result())
    logger1.info('successful')
