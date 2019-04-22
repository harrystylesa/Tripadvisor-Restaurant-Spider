import telnetlib

print('------------------------connect---------------------------')
# 连接Telnet服务器
try:
    tn = telnetlib.Telnet('117.191.11.71', port='8080', timeout=20)
except:
    print('失败')
else:
    print('成功')
