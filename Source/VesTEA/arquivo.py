import csv
import pandas as pd
import numpy as np
import datetime as dt


"""
Funções que interagem com os arquivos csv
"""

Player = ''
Fase = 1
Nivel = 1
Sessao = 1
ArquivoSessao = ''
ArquivoConfig = ''
ArquivoDetalhado = ''

def set_Player(A):
    global Player
    Player = A
    global ArquivoSessao
    global ArquivoConfig
    global ArquivoDetalhado
    ArquivoConfig = 'Jogadores/' + Player + '_VesTEA_config.csv'
    ArquivoSessao = 'Jogadores/' + Player + '_VesTEA_sessao.csv'
    ArquivoDetalhado = 'Jogadores/' + Player + '_VesTEA_detalhado.csv'

def get_Player():
    global Player
    return Player

def set_Fase(A):
    global Fase
    Fase = A

def get_Fase():
    global Fase
    return Fase

def set_Nivel(A):
    global Nivel
    Nivel = A

def get_Nivel():
    global Nivel
    return Nivel

def set_Sessao(A):
    global Sessao
    Sessao = A

def get_Sessao():
    global Sessao
    return Sessao

csv.register_dialect(
    'mydialect',
    delimiter = ';',
    quotechar = '"',
    doublequote = True,
    skipinitialspace = True,
    lineterminator = '\n',
    quoting = csv.QUOTE_MINIMAL)

def get_Date():
    date = dt.datetime.now()
    return date

def gravaDados(filename, Dados):# Dados é um vetor com os dados para gravar no arquivo 'filename'
    with open(filename, 'a+', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, dialect='mydialect')
        csvwriter.writerow(Dados)

def gravaArrayDados(filename, Dados):# Dados é um vetor com os dados para gravar no arquivo 'filename'
    for linha in Dados:
        with open(filename, 'a+', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, dialect='mydialect')
            csvwriter.writerow(linha)        

def grava_Sessao(jogador, hora_inicio, fase, nivel, acertos, acertos_ajuda, ajudas, erros, omissoes):
    file = 'Jogadores/'+jogador+'_VesTEA_sessao.csv'
    results = pd.read_csv(file, sep=';')
    id = len(results)
    data = get_Date().strftime("%x")
    hora = get_Date().strftime("%X")
    fields = [id, data, hora_inicio, hora, fase, nivel, acertos, acertos_ajuda, ajudas, erros, omissoes]
    with open(file,'a+', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, dialect='mydialect')
        csvwriter.writerow(fields)
    set_Sessao(id + 1)

def grava_Detalhado(jogador, data, fase, nivel, pos_jog, tipo):
    file = 'Jogadores/' + jogador + '_Player_Vestea_detalhado.csv'
    results = pd.read_csv(file, sep=';')
    id = len(results)
    hora = get_Date().strftime("%X")
    fields = [id, data, hora, fase, nivel, pos_jog, tipo]
    with open(file, 'a+', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, dialect='mydialect')
        csvwriter.writerow(fields)


#----------------------------------------------------------------------------------------------------------------------#

def lerConfigs(filename): #Apenas para os arquivos gerais, nos detalhados retorna a primeira linha de dados
    """
    Player_Vestea_config.csv = ['Nome', 'Data de Nasc.', 'Observacoes', 'Fase Atual', 'Nivel Atual', 'Sessão', 'Tempo de Ajuda',
              'Tempo Total',
              'Tempo de Exposicao', 'Tempo Vez do Jogador', 'HUD', 'Som', 'Camera', 'Largura de Projecao',
              'Altura de Projecao',
              'Largura Tela de Controle', 'Altura Tela de Controle', 'Cores', 'Sons']

    Player_Vestea_sessao.csv = ['Sessao', 'Data', 'Hora Inicio', 'Hora Fim', 'Fase Alcancada', 'Nivel Alcancado',
              'Qt Acertos sem Ajuda', 'Qt Acertos com Ajuda', 'Qt Ajudas', 'Qt Erros', 'Qt Omissões']

    Player_Vestea_detalhado = ['Sessao', 'Data', 'Hora', 'Fase', 'Nivel', 'Posicao jogador', 'Tipo de Evento']

    Fases = ['', ]

    """
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile, dialect='mydialect')
        fields = next(csvreader)  # Dados do jogador
        fields = next(csvreader)  # Configuracoes
        set_Player(fields[0])
        set_Fase(fields[3])
        set_Nivel(fields[4])
        set_Sessao(fields[5])
        return fields

#Le os pontos de calibração realizados antes do jogo
def lerCalibracao():
    pontos_calibracao = np.zeros((4, 2), int)
    df = pd.read_csv('calibracao.csv', sep=';')

    # getting value/data
    pontos_calibracao[0][0] = df["Ponto 1 x"].values[0]
    pontos_calibracao[0][1] = df["Ponto 1 y"].values[0]
    pontos_calibracao[1][0] = df["Ponto 2 x"].values[0]
    pontos_calibracao[1][1] = df["Ponto 2 y"].values[0]
    pontos_calibracao[2][0] = df["Ponto 3 x"].values[0]
    pontos_calibracao[2][1] = df["Ponto 3 y"].values[0]
    pontos_calibracao[3][0] = df["Ponto 4 x"].values[0]
    pontos_calibracao[3][1] = df["Ponto 4 y"].values[0]

    return pontos_calibracao


#----------------------------------------------------------------------------------------------------------------------#

#Manipulação de dados das Configs
def get_V_NOME():
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # getting value/data
    ret = df["Nome"].values[0]
    return ret

def set_K_NOME(a):
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # updating the column value/data
    df.loc[0, 'Nome'] = a

    # writing into the file
    df.to_csv(ArquivoConfig, sep=';', index=False)
    # print(df)


def get_V_NASC():
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # getting value/data
    ret = df["Data de Nasc."].values[0]
    return ret

def set_K_NASC(a):
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # updating the column value/data
    df.loc[0, 'Data de Nasc.'] = a

    # writing into the file
    df.to_csv(ArquivoConfig, sep=';', index=False)
    # print(df)


def get_V_OBS():
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # getting value/data
    ret = df["Observacoes"].values[0]
    return ret

def set_K_OBS(a):
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # updating the column value/data
    df.loc[0, 'Observacoes'] = a

    # writing into the file
    df.to_csv(ArquivoConfig, sep=';', index=False)
    # print(df)


def get_V_FASE():
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')
    
    # getting value/data
    ret = df["Fase Atual"].values[0]
    return ret

def set_K_FASE(a):
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')
    
    # updating the column value/data
    df.loc[0, 'Fase Atual'] = a
    
    # writing into the file
    df.to_csv(ArquivoConfig, sep=';', index=False)
    #print(df)


def get_V_NIVEL():
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # getting value/data
    ret = df["Nivel Atual"].values[0]
    return ret

def set_K_NIVEL(a):
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # updating the column value/data
    df.loc[0, 'Nivel Atual'] = a

    # writing into the file
    df.to_csv(ArquivoConfig, sep=';', index=False)
    # print(df)


def get_V_SESSAO():
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # getting value/data
    ret = df["Sessao"].values[0]
    return ret


def set_R_SESSAO(a):
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # updating the column value/data
    df.loc[0, 'Sessao'] = a

    # writing into the file
    df.to_csv(ArquivoConfig, sep=';', index=False)
    # print(df)


def get_V_HUD():
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # getting value/data
    ret = df["HUD"].values[0]
    return ret


def set_R_HUD(a):
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # updating the column value/data
    df.loc[0, 'HUD'] = a

    # writing into the file
    df.to_csv(ArquivoConfig, sep=';', index=False)
    # print(df)

def get_V_SOM():
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # getting value/data
    ret = df["Som"].values[0]
    return ret


def set_R_SOM(a):
    # reading the csv file
    df = pd.read_csv(ArquivoConfig, sep=';')

    # updating the column value/data
    df.loc[0, 'Som'] = a

    # writing into the file
    df.to_csv(ArquivoConfig, sep=';', index=False)
    # print(df)