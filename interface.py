from PySimpleGUI import PySimpleGUI as sg 
from rotas import *

#Create LAYOUT
#sg.theme('Reddit')
sg.theme('Dark')

layout = [

    [sg.Text('',size=(17,0)), sg.Text('Rede Local'), sg.Text('Internet', pad=(25,0)), sg.Text('VPN', pad=(27,0)), sg.Text('Internet Matriz')], 
    [sg.Canvas(background_color='gray', size=(620,3))],
    [sg.Text('Monitoramento', key='monitor')], 
    [sg.Text('Monitoramento em andamento', size=(30,5), background_color='black', text_color = 'white', key='details'),
     sg.Text('Rede Local Latência:      ',  background_color='black', size=(10,5), text_color = 'white', key='details_rede'),
     sg.Text('Internet Latência:     ',  background_color='black', size=(10,5), text_color = 'white', key='details_internet'),
     sg.Text('VPN Latência:      ',  background_color='black', size=(10,5), text_color = 'white', key='details_vpn'),
     sg.Text('Matriz Int. Latência:      ',  background_color='black', size=(10,5), text_color = 'white', key='details_im')],
    [sg.Text('', size=(77,5), background_color='gray', text_color = 'white', key='details_comp2')],
    [sg.Image(key='image_algar',size=(620,15) ,visible=False)]]


#create the body
main = [
        [
        sg.Text('',size=(17,0)),    
      
        sg.Image(filename=VERDE_PATH,
                 size=(60, 60), pad=(15,0), enable_events=True, key='rede_local'),
        sg.Image(filename=VERDE_PATH,
                 size=(60, 60), pad=(15,0), enable_events=True, key='internet'),
        sg.Image(filename=VERDE_PATH, 
                 size=(60, 60), pad=(15,0), enable_events=True, key='vpn'),
        sg.Image(filename=VERDE_PATH, 
                 size=(60, 60), pad=(15,0), enable_events=True, key='matriz'),
         ],

        [sg.Column(layout=layout)],

]