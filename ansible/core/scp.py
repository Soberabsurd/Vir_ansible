from optparse import OptionParser
import configparser
import paramiko
from concurrent.futures import ProcessPoolExecutor
from conf import config
from lib import common


#要拿到logger对象
logger1=common.get_logger(__name__) #core.src
logger2=common.get_logger('collect')
futures = []
data=set()
# cmd = 'scp '
def put(line,res,local,remote):
    """
    并发执行函数
    :param line:
    :param res:
    :param local:
    :param remote:
    :return:
    """
    # cmd=cmd+local+' '+res.get(line,'user')+'@'+res.get(line,'ip')+':/'+remote

    transport = paramiko.Transport((res.get(line,'ip'),int(res.get(line,'port'))))
    transport.connect(username=res.get(line,'user'), password=res.get(line,'password'))

    sftp = paramiko.SFTPClient.from_transport(transport)
    # sftp.put(r'%s' % local, remote)
    sftp.put(local, remote)
    transport.close()
    logger1.info('upload successful')
def get(line,res,local,remote):
    """
    :param line:
    :param res:
    :param local:
    :param remote:
    :return:
    """
    transport = paramiko.Transport((res.get(line, 'ip'), int(res.get(line, 'port'))))
    transport.connect(username=res.get(line, 'user'), password=res.get(line, 'password'))
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.get(remote,local)
    transport.close()
    logger1.info('download successful')
def main():
    """
    主函数(逻辑程序)
    :return:
    """
    process = ProcessPoolExecutor()
    parse = OptionParser(usage='"usage:%prog [options] arg1,arg2 ..."')
    parse.add_option('-u', '--user', dest='user', action='store', type=str, metavar='user', help='Input User Name!!')
    parse.add_option('-g', '--group', dest='group', type=str, metavar='group', help='Input Group Name')
    parse.add_option('-a', '--action', dest='action', type=str, metavar='action', help='Input Action Name')
    parse.add_option('-l', '--local', dest='local', type=str, metavar='local', help='Input Local Route')
    parse.add_option('-r', '--remote', dest='remote', type=str, metavar='remote', help='Input Remote Route')
    options, args = parse.parse_args()
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


    if options.action == 'put':
        for line in data:
            obj=process.submit(put,line,res,options.local,options.remote)
            futures.append(obj)
    elif options.action == 'get':
        for line in data:
            obj = process.submit(get, line,res,options.local,options.remote)
            futures.append(obj)
    else:
        print('parameter only is "put" or "get"')
        process.shutdown(wait=True)
        exit()
    process.shutdown(wait=True)
    # for future in futures:
    #     print(future.result())
