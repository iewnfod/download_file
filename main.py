import bottle
import os
import _thread
import smtplib
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

host = input('Host: ')
port = input('Port: ')

# 书写日志
def log(msg, level, exit_code = 0, exit_explain = ''):
    level_dict = {1: '[INFO]\t\t', 2: '[WARNING]\t', 3: '[ERROR]\t\t', 4: '[FATAL]\t\t'}
    msg = level_dict[level] + msg + f'\t\texit_code = [{exit_code}]'

    if exit_code != 0 or exit_explain != '':
        msg += '\t\t' + exit_explain

    print(msg)

    with open('log.txt', 'r') as f:
        m = f.read()
    with open('log.txt', 'w') as f:
        f.write(m + str(msg) + '\n')

# 下载
def download(url):
    url = url.split(' ')
    for i in range(len(url)):
        url[i] = chr(int(url[i]))
    url = ''.join(url)

    log(msg = '开始下载: ' + '"' + url + '"', level = 1)

    name = url.split('/')[-1]
    if name == '':
        name = url.split('/')[-2]
    result = os.system(f'wget \"{url}\" -O ./download/{name}') >> 8

    print(result)

    if result == 0:
        log(msg = '下载完成: ' + '"' + url + '"', level = 1)
    else:
        log(msg = '下载失败: ' + '"' + url + '"', level = 2, exit_code = result, exit_explain={
            1: '通用错误代码', 
            2: '解析错误', 
            3: '文件IO错误', 
            4: '网络失败', 
            5: 'SSL认证失败', 
            6: '用户名或密码认证错误', 
            7: '协议错误', 
            8: '服务端产生错误回应'
        }[result])
    
    if result != 0:
        os.system('rm ./download/'+name)

def start_download(content):
    name, target = content.split('|')
    name = name.strip()
    filepath = './download/' + name

    from_address = 'shangzhiqiuyue@outlook.com'
    password = 'Wuziqian1212'

    content = MIMEText('Download file: ' + name)

    file = MIMEApplication(open(filepath, 'rb').read())
    file.add_header('Content-Disposition', 'attachment', filename=name)

    m = MIMEMultipart()
    m.attach(content)
    m.attach(file)

    m['Subject'] = 'Download file: ' + name

    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
    except:
        log('邮件发送失败', 3, exit_code=1, exit_explain='smtp连接错误')
        return
    try:
        server.ehlo()
        server.starttls()
        server.login(from_address, password)
    except:
        log('邮件发送失败', 3, exit_code=2, exit_explain='邮箱登录错误')
        return
    try:
        server.sendmail(from_address, target, m.as_string())
        server.quit()
        log('邮件发送成功', 1)
        return
    except:
        log('邮件发送失败', 3, exit_code=3)
        return


# 下载路径
@bottle.route('/d/<url>')
def d(url):
    _thread.start_new_thread(download, (url, ))

# 下载展示
@bottle.route('/download')
def show_download():
    names = []
    for file in os.listdir('./download'):
        if not os.path.isdir(file):
            names.append(file)

    t = '\n'.join(names)
    # print(t)

    return bottle.template('download.html', t=t)

# 下载
@bottle.route('/download/<content>')
def sd(content):
        _thread.start_new_thread(start_download, (content, ))

# 删除
@bottle.route('/r/<name>')
def r(name):
    name = name.strip()
    try:
        os.system('rm ./download/'+name)
        log('删除文件\"'+name+'\"成功', 1)
    except:
        log('删除文件\"'+name+'\"失败', 3, exit_code=1)

# index
@bottle.route('/')
def index():
    return bottle.template('index.html')

# log
@bottle.route('/log')
def get_log():
    with open('log.txt', 'r') as f:
        t = f.read()
    # print(t)
    t = t.replace('\t\t', '-|-')
    t = t.replace('\t', '-|-')
    # print(t)
    return bottle.template('log.html', t=t)

# 启动
bottle.run(host=host, port=port)
