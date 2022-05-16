from PySimpleGUI import PySimpleGUI as sg 
from logica import *
from dicionarios import *
from interface import *                


#Função carregamento

def carregando(x):
    if x == 0 :
        asterisco = ' * '
        texto = 'Monitoramento ' + asterisco
        janela.Element('monitor').Update(texto)
    else : 
        dot = x
        asterisco = ' * '        
        while dot > 0 :
            asterisco += ' * '
            texto = 'Monitoramento ' + asterisco
            dot = dot - 1
           
        janela.Element('monitor').Update(texto)    

        
     
def ler_tela() :
    event, values_read = janela.read(timeout=25)
    print('Leitura da tela')  
    fechar = 0            
                         
    if event == sg.WIN_CLOSED :
        fechar = 1
        
    return fechar    

def error_graphic():
    #em caso de falha em qualquer momento no download e tratamento do gráfico torna a janela como visible=False
    janela.Element('image_algar').Update(visible=False)    


#HABILITANDO A JANELA
janela = sg.Window('Monitoramento de Rede', layout=main, finalize=True)

#VARIÁVEIS AUXILIARES PARA TESTE SE ALGUM SERVIDOR NÃO ESTÁ RESPONDENDO
off_server = [] 
on_server = False

#LISTAS AUXILIARES PARA FUNÇÕES DE VERIFICAÇÃO FAROL LATENCIA:
ip_slow_rede = []
ip_slow_internet = []
ip_slow_vpn = []

#iniciando com False variável para controlar acesso ao site algar e baixar o gráfico de consumo
image_run = False


while True:
    user_action = ler_tela()
    if user_action == 1 :
        janela.AutoClose
        break
      
    
    else :
        #Chamando função para baixar e formatar o gráfico de consumo algar
        if image_run:
            status_download = download_algar()
            if status_download:
                status_image = image()
                if status_image:
                    janela.Element('image_algar').Update(filename=ALGAR_PATH, visible=True)
                else:
                    error_graphic()    
            else: 
                error_graphic()         
                   
                    

        image_run = control_image_run(image_run)            
            

        cont = len(ips) #VERIFICANDO A QUANTIDADE DE IPS PARA REALIZAR O LOOPING BUSCANDO DA LISTA CRIADA ATRAVÉS DO DICIONARIO DE IPS
        x = 0
        while x < cont :
            carregando(x)  
            comunica_result = comunica(ips[x]) #CHAMANDO A FUNÇÃO COMUNICA PARA INICIAR O PING NO IP ESPECIFICO, RETORNA O RESULTADO DO PING 
            
           # user_action = ler_tela() #Leitura de tela !!!!!!!!!!!!!!!!!
            if ler_tela() == 1 :
                janela.AutoClose
                break

            status = verifica_tarefa(comunica_result) #CHAMANDO FUNÇÃO VERIFICA_TAREFA, RETORNA SE HOUVE ERRO NO PING "esgotado tempo limite"

            if ler_tela() == 1 :
                janela.AutoClose
                break


            if status == 0 : #Se for igual a lista é porque o status foi 0 (sem erro) e consta também o farol no campo 1 da lista
                retorno = tratamento(comunica_result) #CHAMANDO FUNÇÃO TRATAMENTO TENDO COMO PARAMETRO O RETORNO DA FUNÇÃO COMUNICA, REMOVE CARACTERES E TRANSFORMA EM LISTA 
                print('Chamando verifica_retorno')
                if ler_tela() == 1 :
                    janela.AutoClose
                    break

                farol = verifica_retorno(retorno) #CHAMANDO A FUNÇÃO VERIFICA_RETORNO, TENDO COMO PARAMETRO O RETORNO DA FUNÇÃO TRATAMENTO, VERIFICA SE HOUVE HOST INACESSÍVEL NO PING

                for keys, values in dicionario_ips.items() : #VERIFICAR NO DICIONARIO DE IPS O SEGUIMENTO QUE PERTENCE PARA ALTERAÇÃO DO FAROL
                    if ips[x] in values :
                        if farol == 0 : #RETORNO DA FUNÇAO VERIFICA RETORNO COM O STATUS QUE O FAROL DEVE TER, 0 = VERDE, 1 = AMARELO, 2 = VERMELHO
                            print('Entrou farol = 0')
                            if ler_tela() == 1 :
                                janela.AutoClose
                                break

                            latencia = verifica_latencia(retorno)

                            if keys == 'rede_local' : 
                                on_server = True
                                print('on_server = True')

                            if keys == 'rede_local' and ips[x] in off_server : #APAGANDO A MENSAGEM DO CAMPO DA TELA DETAILS_COMP CASO O SERVIDOR VOLTE A PINGAR
                                condicional = 1 #VARIÁVEL AUXILIAR PARA CONTROLAR MENSAGENS DA TELA SE 0 = INSERIR MENSAGEM / SE 1 = REMOVER MENSAGEM DA LISTA
                                off_server = lista_off_server(ips[x], condicional)
                                mensagem = texto_details2(dicionario_destinos[ips[x]] + ' OFFLINE', condicional) #CHAMANDO FUNÇÃO PARA INSERÇÃO MENSAGEM NA LISTA E TRANSFORMAÇÃO DA LISTA EM STRING
                                janela.Element('details_comp2').Update(mensagem)
                                
                            if len(off_server) > 0 and keys == 'rede_local' : #SE ALGUM SERVIDOR DA REDE LOCAL RESPONDER, MAS AINDA TIVER ALGUM OFFLINE, FAROL FICA AMARELO
                                janela.Element(keys).Update(filename=AMARELO_PATH,size=(60, 60))

                            else :    
                                janela.Element(keys).Update(filename=VERDE_PATH,size=(60, 60)) #ALTERANDO A COR DO FAROL UTILIZANDO A KEY CAPTADA NO FOR DO INICIO
                                janela.Element('details').Update(keys + ' CONEXÃO OK!') #INSERINDO INFORMAÇÃO NA TELA COM O SERVIÇO E O STATUS
                                
                                if keys == 'rede_local' : #VERIFICANDO QUAL CONEXÃO ESTA SENDO TESTADA PARA INSERIR A LATENCIA
                                    janela.Element('details_rede').Update('Rede Local Latência:      ' + latencia[0] + 'ms') #INSERINDO LATENCIA NO CAMPO CORRESPONDENTE
                                    if int(latencia[0]) > 5 : #VERIFICANDO LATENCIA PARA ALTERAR COR DO FAROL DA LATENCIA
                                        janela.Element('details_rede').Update(background_color = 'orange')
                                        condicional = 0
                                        ip_slow_rede = verifica_lista_rede(latencia[1], condicional)
                                        mensagem = texto_details2(dicionario_destinos[ips[x]] + ' APRESENTANDO LENTIDÃO', condicional) #CHAMANDO FUNÇÃO PARA INSERÇÃO MENSAGEM NA LISTA E TRANSFORMAÇÃO DA LISTA EM STRING
                                        janela.Element('details_comp2').Update(mensagem) #INSERINDO NO CAMPO DETAILS_COMP2 A LISTA DE MENSAGENS DE ALERTA
                                    elif latencia[1] in ip_slow_rede : #VERIFICANDO SE O ENDREÇO EU ESTAVA LENTO AGORA ESTÁ OK
                                            condicional = 1
                                            ip_slow_rede = verifica_lista_rede(latencia[1], condicional)
                                            mensagem = texto_details2(dicionario_destinos[ips[x]] + ' APRESENTANDO LENTIDÃO', condicional) #CHAMANDO FUNÇÃO PARA INSERÇÃO MENSAGEM NA LISTA E TRANSFORMAÇÃO DA LISTA EM STRING
                                            janela.Element('details_comp2').Update(mensagem)
                                            if len(ip_slow_rede) == 0 :
                                                janela.Element('details_rede').Update(background_color = 'green')  
                                            
                                    elif len(ip_slow_rede) == 0 :
                                        janela.Element('details_rede').Update(background_color = 'green')             

                                if keys == 'internet' :  #VERIFICANDO QUAL CONEXÃO ESTA SENDO TESTADA PARA INSERIR A LATENCIA
                                    janela.Element('details_internet').Update('Internet Latência:     ' + latencia[0] + 'ms') #INSERINDO LATENCIA NO CAMPO CORRESPONDENTE
                                    if int(latencia[0]) > 60 : #VERIFICANDO LATENCIA PARA ALTERAR COR DO FAROL DA LATENCIA
                                        janela.Element('details_internet').Update(background_color = 'orange')
                                        condicional = 0
                                        ip_slow_internet = verifica_lista_internet(latencia[1], condicional)
                                        mensagem = texto_details2(dicionario_destinos[ips[x]] + ' APRESENTANDO LENTIDÃO', condicional) #CHAMANDO FUNÇÃO PARA INSERÇÃO MENSAGEM NA LISTA E TRANSFORMAÇÃO DA LISTA EM STRING
                                        janela.Element('details_comp2').Update(mensagem) #INSERINDO NO CAMPO DETAILS_COMP2 A LISTA DE MENSAGENS DE ALERTA
                                    elif latencia[1] in ip_slow_internet : #VERIFICANDO SE O ENDREÇO QUE ESTAVA LENTO AGORA ESTÁ OK
                                            condicional = 1
                                            ip_slow_internet = verifica_lista_internet(latencia[1], condicional)
                                            mensagem = texto_details2(dicionario_destinos[ips[x]] + ' APRESENTANDO LENTIDÃO', condicional) #CHAMANDO FUNÇÃO PARA INSERÇÃO MENSAGEM NA LISTA E TRANSFORMAÇÃO DA LISTA EM STRING
                                            janela.Element('details_comp2').Update(mensagem)
                                            if len(ip_slow_internet) == 0 :
                                                janela.Element('details_internet').Update(background_color = 'green')  
                                    
                                    elif len(ip_slow_internet) == 0 :
                                        janela.Element('details_internet').Update(background_color = 'green')               

                                if keys == 'vpn' :  #VERIFICANDO QUAL CONEXÃO ESTA SENDO TESTADA PARA INSERIR A LATENCIA
                                    janela.Element('details_vpn').Update('VPN Latência:      ' + latencia[0] + 'ms') #INSERINDO LATENCIA NO CAMPO CORRESPONDENTE
                                    if int(latencia[0]) > 150 : #VERIFICANDO LATENCIA PARA ALTERAR COR DO FAROL DA LATENCIA
                                        janela.Element('details_vpn').Update(background_color = 'orange')
                                        condicional = 0
                                        ip_slow_vpn = verifica_lista_vpn(latencia[1], condicional)
                                        mensagem = texto_details2(dicionario_destinos[ips[x]] + ' APRESENTANDO LENTIDÃO', condicional) #CHAMANDO FUNÇÃO PARA INSERÇÃO MENSAGEM NA LISTA E TRANSFORMAÇÃO DA LISTA EM STRING
                                        janela.Element('details_comp2').Update(mensagem) #INSERINDO NO CAMPO DETAILS_COMP2 A LISTA DE MENSAGENS DE ALERTA
                                    elif latencia[1] in ip_slow_vpn : #VERIFICANDO SE O ENDREÇO EU ESTAVA LENTO AGORA ESTÁ OK
                                            condicional = 1
                                            ip_slow_vpn = verifica_lista_vpn(latencia[1], condicional)
                                            mensagem = texto_details2(dicionario_destinos[ips[x]] + ' APRESENTANDO LENTIDÃO', condicional) #CHAMANDO FUNÇÃO PARA INSERÇÃO MENSAGEM NA LISTA E TRANSFORMAÇÃO DA LISTA EM STRING
                                            janela.Element('details_comp2').Update(mensagem)
                                            if len(ip_slow_vpn) == 0 :
                                                janela.Element('details_vpn').Update(background_color = 'green')  
                                            
                                    elif len(ip_slow_vpn) == 0 :
                                        janela.Element('details_vpn').Update(background_color = 'green')    

                                if keys == 'matriz' :  #VERIFICANDO QUAL CONEXÃO ESTA SENDO TESTADA PARA INSERIR A LATENCIA
                                    janela.Element('details_im').Update('Matriz Int. Latência:      ' + latencia[0] + 'ms') #INSERINDO LATENCIA NO CAMPO CORRESPONDENTE
                                    if int(latencia[0]) > 80 : #VERIFICANDO LATENCIA PARA ALTERAR COR DO FAROL DA LATENCIA
                                        janela.Element('details_im').Update(background_color = 'orange') 
                                        condicional = 0 #VARIÁVEL AUXILIAR PARA CONTROLAR MENSAGENS DA TELA SE 0 = INSERIR MENSAGEM / SE 1 = REMOVER MENSAGEM DA LISTA
                                        mensagem = texto_details2(dicionario_destinos[ips[x]] + ' APRESENTANDO LENTIDÃO', condicional) #CHAMANDO FUNÇÃO PARA INSERÇÃO MENSAGEM NA LISTA E TRANSFORMAÇÃO DA LISTA EM STRING
                                        janela.Element('details_comp2').Update(mensagem)
                                    else :
                                        condicional = 1 #VARIÁVEL AUXILIAR PARA CONTROLAR MENSAGENS DA TELA SE 0 = INSERIR MENSAGEM / SE 1 = REMOVER MENSAGEM DA LISTA
                                        mensagem = texto_details2(dicionario_destinos[ips[x]] + ' APRESENTANDO LENTIDÃO', condicional) #CHAMANDO FUNÇÃO PARA INSERÇÃO MENSAGEM NA LISTA E TRANSFORMAÇÃO DA LISTA EM STRING
                                        janela.Element('details_comp2').Update(mensagem)                                        
                                        janela.Element('details_im').Update(background_color = 'green') 

                                        
                                
                                
                            print(on_server, keys)
                            
                           
                        elif farol == 1 : #Em caso de perda de pacotes retorna farol amarelo
                            if ler_tela() == 1 :
                                janela.AutoClose
                                break

                            janela.Element(keys).Update(filename=AMARELO_PATH,size=(60, 60))
                            janela.Element('details').Update(keys + ' CONEXÃO APRESENTANDO INSTABILIDADE!')

                            janela.Element(dicionario_latencia[keys]).Update(background_color = 'orange') #Alterando farol latencia usando o dicionario latencia criado


                            if keys == 'rede_local':
                                on_server = False
                                condicional = 0 #VARIÁVEL AUXILIAR PARA CONTROLAR MENSAGENS DA TELA SE 0 = INSERIR MENSAGEM / SE 1 = REMOVER MENSAGEM DA LISTA
                                off_server = lista_off_server(ips[x], condicional)
                                mensagem = texto_details2(dicionario_destinos[ips[x]] + ' OFFLINE', condicional) #CHAMANDO FUNÇÃO PARA INSERÇÃO MENSAGEM NA LISTA E TRANSFORMAÇÃO DA LISTA EM STRING
                                janela.Element('details_comp2').Update(mensagem)

                            
                        else : #FAROL VERMELHO
                            if ler_tela() == 1 :
                                janela.AutoClose
                                break

                            print(on_server, off_server, ips[x])  
                            janela.Element(dicionario_latencia[keys]).Update(background_color = 'red') #Alterando farol latencia 

                            if keys == 'rede_local' and on_server : #CASO SEJA UM SERVIDOR DA REDE LOCAL, MAS ALGUM OUTRO SERVIDOR DA REDE JÁ TENHA RESPONDIDO, FAROL AMARELO E NÃO VERMELHO
                                janela.Element(keys).Update(filename=AMARELO_PATH,size=(60, 60))
                                janela.Element('details').Update(keys + ' SEM CONEXÃO!')
                                on_server = False
                            else :    
                                janela.Element(keys).Update(filename=VERMELHO_PATH,size=(60, 60)) #ALTERANDO FAROL PARA VERMELHO NO CAMPO CORRESPONDENTE "KEYS"
                                janela.Element('details').Update(keys + ' SEM CONEXÃO!')
                                on_server = False

                            if keys == 'rede_local': #SE FOR REDE_LOCAL COM STATUS DO FAROL 2, INSERINDO MENSAGEM DE OFFLINE COM O RESPECTIVO SERVIDOR
                                condicional = 0 #VARIÁVEL AUXILIAR PARA CONTROLAR MENSAGENS DA TELA SE 0 = INSERIR MENSAGEM / SE 1 = REMOVER MENSAGEM DA LISTA
                                off_server = lista_off_server(ips[x], condicional)
                                mensagem = texto_details2(dicionario_destinos[ips[x]] + ' OFFLINE', condicional) #CHAMANDO FUNÇÃO PARA INSERÇÃO MENSAGEM NA LISTA E TRANSFORMAÇÃO DA LISTA EM STRING
                                janela.Element('details_comp2').Update(mensagem)
                            
                                 

            else : #STATUS DE ERRO DO TESTE DE COMUNICAÇÃO = 1, FALHA NA TENTATIVA DE PING
                
                print('Entrou no status = 1')
                                
                for keys, values in dicionario_ips.items() :
                    if ips[x] in values :
                        if ler_tela() == 1 :
                            janela.AutoClose
                            break

                        janela.Element(dicionario_latencia[keys]).Update(background_color = 'red') #Alterando farol latencia 

                        janela.Element(keys).Update(filename=VERMELHO_PATH,size=(60, 60))
                        janela.Element('details').Update(keys + ' SEM CONEXÃO!')
                        if keys == 'rede_local':
                            condicional = 0 #VARIÁVEL AUXILIAR PARA CONTROLAR MENSAGENS DA TELA SE 0 = INSERIR MENSAGEM / SE 1 = REMOVER MENSAGEM DA LISTA
                            off_server = lista_off_server(ips[x], condicional)
                            mensagem = texto_details2(dicionario_destinos[ips[x]] + ' OFFLINE', condicional) #CHAMANDO FUNÇÃO PARA INSERÇÃO MENSAGEM NA LISTA E TRANSFORMAÇÃO DA LISTA EM STRING
                            janela.Element('details_comp2').Update(mensagem)
                        
                        break

            x+=1
            print("Fim do looping")
                        
            
           
     
  