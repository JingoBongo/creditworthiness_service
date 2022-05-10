import socket
hostname = socket.getfqdn()
print("IP Address:",socket.gethostbyname_ex(hostname)[2][1])

# from requests import get
#
# ip = get('https://api.ipify.org').text
# print('My public IP address is:'+ str(ip))