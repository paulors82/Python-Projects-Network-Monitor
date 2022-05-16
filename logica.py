import subprocess
from openpyxl import Workbook, load_workbook
from datetime import datetime
import smtplib
import email.message
from PIL import Image
from rotas import ALGAR_PATH, ALGAR_DOWNLOAD
import io
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from time import sleep
from credentials.credentials import user, password, site
from interface import *

#MENSAGENS DE ERRO DIAGRAMA:
#CRIADA UMA LISTA ONDE CADA MENSAGEM DE ERRO OU ALERTA SERÁ INSERIDA EM UMA POSIÇÃO, AO IMPRIMR A MENSAGEM SERÁ IMPRESSA =>
#=> TODA A LISTA, PARA AS POSIÇÕES QUE NÃO HOUVER MENSAGEM DE ERRO ADICIONAR ''
texto_details_comp2 = []

#LISTAS DE APOIO PARA MENSAGENS E FAROL REFERENTE A LATENCIA
ip_slow_rede = []
ip_slow_vpn = []
ip_slow_internet = []

off_server = []


#ROTA PARA A PLANILHA
PLANILHA_PATH = 'planilha\\registro.xlsx'

def verifica_retorno(retorno) :
    x_host = 0
    x_esgotado = 0
    
    print('Verificando retorno')
    if 'Host' in retorno or 'Esgotado' in retorno or 'Falha' in retorno :
        x_host = retorno.count('Host')
        x_esgotado = retorno.count('Esgotado')
        x_falha = retorno.count('Falha')
        x = x_host + x_esgotado + x_falha
        print(retorno)
        print('Host ', x_host)
        print('Esgotado ', x_esgotado)
        print('Falha ', x_falha)
        print(x, 'Pacotes perdidos')

        if x >= 4 :
            farol = 2
            return farol

        else :
            farol = 1
            return farol    
           
    else :
        print('Não encontrou Host inacessível')
        farol = 0
        
        return farol

def verifica_latencia(retorno) :
    latencia = [str(retorno[-1].replace("msn'", "")), retorno[1]]
    print("verifica latencia: " + str(latencia))
    return latencia      

def tratamento(retorno_ping):
    print('Realizando tratamento do retorno')
    retorno = str(retorno_ping.stdout)
    retorno = retorno.replace("\\r\\", "")
    retorno = retorno.replace("=", "")
    retorno = retorno.replace(".n", " ")
    retorno = retorno.replace(":n", " ")
    retorno = retorno.split()
    return retorno    

def verifica_tarefa(ping) :
    returncode = ping.returncode
    print('verificando tarefa')
    if returncode == 1 :
        status = 2
        print('Erro resposta ping')
        return status
    else :
        #retorno_ping = str(ping.stdout)
        print('verifica tarefa ok')
        status = 0
        return status
        #tratamento(retorno_ping)

def comunica(ip):
    ping = subprocess.run(["ping","-w", "1000", ip], shell = True, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
    print('Ping realizado', ip)
    #verifica_tarefa(ping)        
    return ping

#FUNÇAO PARA INSERIR MENSAGEM NA LISTA E TRANSFORMAR A LISTA EM STRING
def texto_details2 (texto, condicional): 

    if texto not in texto_details_comp2 and condicional == 0 :
        texto_details_comp2.append(texto)
        mensagem = (' ' + str(texto_details_comp2).replace(',','\n').replace('[','').replace(']','').replace("'",""))
    elif texto in texto_details_comp2 and condicional == 1 :
        texto_details_comp2.remove(texto)
        mensagem = (' ' + str(texto_details_comp2).replace(',','\n').replace('[','').replace(']','').replace("'",""))
    else: 
        mensagem = (' ' + str(texto_details_comp2).replace(',','\n').replace('[','').replace(']','').replace("'",""))    
        
    return mensagem    

def verifica_lista_rede(ip, condicional) :
    if ip in ip_slow_rede : 
        if condicional == 0 :
            return ip_slow_rede
        else :
            ip_slow_rede.remove(ip) 
            return ip_slow_rede   

    elif condicional == 0 :
        ip_slow_rede.append(ip)
        return ip_slow_rede  

    else :
        return ip_slow_rede  

def verifica_lista_vpn(ip, condicional) :
    if ip in ip_slow_vpn : 
        if condicional == 0 :
            return ip_slow_vpn
        else :
            ip_slow_vpn.remove(ip) 
            return ip_slow_vpn   

    elif condicional == 0 :
        ip_slow_vpn.append(ip)
        return ip_slow_vpn  

    else :
        return ip_slow_vpn

def verifica_lista_internet(ip, condicional) :
    if ip in ip_slow_internet : 
        if condicional == 0 :
            return ip_slow_internet
        else :
            ip_slow_internet.remove(ip) 
            return ip_slow_internet   

    elif condicional == 0 :
        ip_slow_internet.append(ip)
        return ip_slow_internet  

    else :
        return ip_slow_internet    



def lista_off_server(ip, condicional) :
    if ip in off_server : 
        if condicional == 0 :
            return off_server
        else :
            off_server.remove(ip) 
            registro(ip, condicional)
            return off_server  

    elif condicional == 0 :
        off_server.append(ip)
        registro(ip, condicional)

        return off_server

    else :
        return off_server


# Criar Arquivo Excel com o registro de data, hora e servidor offline
def registro(ip, condicional): 
    workbook = load_workbook(filename = PLANILHA_PATH)
    sheet = workbook.active
    cont = 2
    linha = str(cont)
    while sheet["A" + linha].value != None :
        cont+=1
        linha = str(cont)
    
    data = datetime.today()
    sheet["A" + linha] = data.strftime('%d/%m/%Y')
    sheet["B" + linha] = data.strftime('%H:%M')
    sheet["C" + linha] = ip

    if condicional == 0 :
        sheet["D" + linha] = "Offline"
        status = "Offline"
        data_hora = data.strftime('%d/%m/%Y') + " " + data.strftime('%H:%M')
        valor = None
        resposta = envia_email(ip, status, data_hora, valor)
        if resposta == data_hora :
            sheet["E" + linha] = data_hora    
        
    else : 
        sheet["D" + linha] = "Online"
        status = "Online Novamente"
        data_hora = data.strftime('%d/%m/%Y') + " " + data.strftime('%H:%M')
        verifica = int(linha) - 1
        teste = True
        while teste :
            if ip == sheet["C" + str(verifica)].value :
                if sheet["E" + str(verifica)].value != None : 
                    valor = sheet["E" + str(verifica)].value    
                    envia_email(ip, status, data_hora, valor)
                    teste = False
                else:        
                    valor = None
                    envia_email(ip, status, data_hora, valor)
                    teste = False
            verifica -= 1     

        
    workbook.save(PLANILHA_PATH)

def download_algar():

    try:
        #criando o objeto option para o chromedrive
        options = webdriver.ChromeOptions()
        print('criou options')
        #opção para execução oculta do chromedriver
        options.add_argument('--headless')
        #Carregando objeto chrome driver e atribuindo a opção oculto
        print('Carregando chrome driver')
        #driver  = webdriver.Chrome('/Users/paulo.roberto/Desktop/Paulo/python/chromedriver/chromedriver', options=options)
        driver  = webdriver.Chrome('Caminho para o seu chromedriver', options=options)
        #acessando o site
        driver.get(site)
        print('Acessando o site Algar')
        sleep(2)
    except:
        print('Falha na tentativa de acesso ao site')
        return False


    try:
        #atribuindo o campo para digitar o usuário
        username = driver.find_element_by_id('name')
        #atribuindo o campo para digitar a senha
        user_password = driver.find_element_by_id('password')
        #inserindo usuário
        username.send_keys(user)
        #inserindo password
        user_password.send_keys(password)
        print('Inserido usuário e senha')
        sleep(2)
        #clicando no botão entrar
        driver.find_element_by_id('enter').click()
        print('Realizando login')
        sleep(2)
    except:
        print('Falha ao realizar login') 
        return False
        
    try:   
        print('Tentando acessar aos gráficos')
        driver.get('Endereço Geração de gráficos do Provedor')
        sleep(5)
        print('Clicando na opção para gráfico de 15 minutos')
        wait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//span/a[text()='15m']"))).click()
        
    except:
        print('Erro ao acessar gráficos')
        return False    

    try:
        #Capturando o src do gráfico
        print('Capturando o src da imagem')
        img = driver.find_element_by_id('graph_full')
        src = img.get_attribute('src')
        print(src)
        sleep(2)

        #Acessando nova página web com o src do gráfico e tirando um print
        driver.get(src)
        driver.save_screenshot(ALGAR_DOWNLOAD)
        #driver.save_screenshot(ALGAR_DOWNLOAD) CORRETO ALTERAR O DE CIMA

        print('Gráfico Salvo!')
        return True
    except:
        print('Erro ao tentar realizar download do Gráfico')
        return False    

def image():
    #Cortando a Imagem:
    try:
        image = Image.open(ALGAR_DOWNLOAD)
        image1 = image.crop((28,137,950,450))
        image1.save(ALGAR_PATH, 'png')

        print('Imagem editada com sucesso!')
        
     
        try:
            image = Image.open(ALGAR_PATH)
            image.thumbnail((740,400))
            image.save(ALGAR_PATH)
            print('Imagem redimensionada!')
            return True
        except:
            print('Erro ao redimensionar e salvar imagem')
    
    except:
        print("Erro ao cortar imagem")
        return False    


def control_image_run(image_run):
    if image_run:
        image_run = False
    else:
        image_run = True 
    return image_run       

     

def envia_email(ip, status, data_hora, valor):

    if valor != None :

        corpo_email = f"""
        <p>Mensagem Automática</p>
        <p>{ip} Offline em {valor}</p>
        <p> {ip} {status} em {data_hora}</p>
        """
    else:
        corpo_email = f"""
        <p>Mensagem Automática</p>
        <p> {ip} {status} em {data_hora}</p>
        """
    
    msg = email.message.Message()
    msg['Subject'] = f"""MENSAGEM AUTOMATICA {ip} {status}"""
    msg['From'] = 'seuemail@gmail.com'
    msg['To'] = 'destinatario@gmail.com'
    password = 'Password'
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email )

    try :
        s = smtplib.SMTP('smtp.gmail.com: 587')
        s.starttls()
        # Login Credentials for sending the mail
        s.login(msg['From'], password)
        s.sendmail(msg['From'], msg['To'].split(', '), msg.as_string().encode('utf-8'))
        print('Email enviado')
        
    except:
        return data_hora


