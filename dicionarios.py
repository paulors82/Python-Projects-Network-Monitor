
dicionario_ips = {
    #Servidores rede local
    'rede_local' : ['192.168.xx.1', '192.168.xx.2'],
    'internet' : ['208.67.222.222', '8.8.8.8'],
    #servidores na matriz
    'vpn' : ['192.168.xxx.1', '192.168.xxx.6'],
    #IP público matriz
    'matriz' : ['111.11.1.111']
}

dicionario_destinos = {
    '192.168.xx.1' : 'FIREWALL',
    '192.168.xx.2' : 'FILE SERVER',
    '8.8.8.8' : 'DNS GOOGLE',
    '208.67.222.222' : 'DNS OPENDNS ',
    '192.168.xxx.6' : 'SERVIDOR MATRIZ',
    '192.168.xxx.1' : 'SERVIDOR MATRIZ',
    '111.11.1.111' : 'LINK MATRIZ'
}

dicionario_latencia = {
    'rede_local' : 'details_rede',
    'vpn' : 'details_vpn',
    'internet' : 'details_internet',
    'matriz' : 'details_im'
}

#Pegando a lista de ips do dicionário
ips =[]
for values in dicionario_ips.values() :
  x = len(values)
  while x > 0 :
    ips.append(values[x-1])
    x-=1