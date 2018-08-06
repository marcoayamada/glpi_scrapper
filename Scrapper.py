import pandas as pd
import requests
from lxml import html
from bs4 import BeautifulSoup
import re

class Scrapper:
    def __init__(self, login, senha, url):

        r""" Classe Scrapper que faz a comunicação e extração dos dados

        :login: login
        :senha: senha
        :url: url principal do sistema. Ex.: https://suporte.com.br/

        Informações sensiveis como Private. 
        """
        self.URL = url

        self.__URL_Login = url + 'front/login.php'
        self.__USERNAME = login
        self.__PASSWORD = senha

    def __abre_sessao(self):
        session_requests = requests.session()  # abrindo a sessao
        result = session_requests.get(self.URL)
        
        if result.status_code == requests.codes.ok:
            print('Status code: {0}'.format(result.status_code))
            tree = html.fromstring(result.text)
            TKN = tree.xpath("//input[@name='_glpi_csrf_token']/@value")[0]

            payload = {
                "login_name": self.__USERNAME,
                "login_password": self.__PASSWORD,
                "submit": '',
                "_glpi_csrf_token": TKN
            }
    
            # fazendo o login passo 2
            session_requests.post(self.__URL_Login, data=payload, headers=dict(referer=self.__URL_Login))
            
            # redirect para pagina principal
            result = session_requests.get(self.URL)
    
            return session_requests, result
        else:
            return result.raise_for_status()


    def busca_chamados(self, link_consulta, qtd_registros=100):

        r"""Pega uma lista de chamados

        :link_consulta: string com o link da página
        :qtd_registros: quantidade máxima de registros da extração

        :return: :class:`pandas.core.frame.DataFrame` object
        
        """

        abre_sessao = self.__abre_sessao()
        session = abre_sessao[0] #chamando a sessao aqui dentro para manter metodo como private
        response = abre_sessao[1] # pegando a pagina inicial do outro método
        
        TKN = html.fromstring(response.text).xpath("//input[@name='_glpi_csrf_token']/@value")[0] # pegando a token
        response = session.post(link_consulta, data=dict(glpilist_limit=qtd_registros, _glpi_csrf_token=TKN), headers=dict(referer=link_consulta))
        
        session.close()
        
        soup = BeautifulSoup(response.content, 'html.parser')          
        classes = ['tab_bg_1', 'tab_bg_2']
        labels = ['chamado', 'titulo', 'conteudo', 'atualizacao', 'criacao', 'requerente', 'interacoes', 'tecnico', 'grupo']
        rows = []

        for c in classes:
            trs = soup.find_all('tr', class_=c)
            for tr in trs[1:]:
                tds = tr.find_all('td')
                cell = []
                for index, td in enumerate(tds):
                    if index == 1:  # ID
                        # print(index, td.get_text().replace('\xa0', ''))
                        cell.append(td.get_text().replace('\xa0', ''))
                    elif index == 2:  # Titulo
                        # print(index, td.a.string) # Titulo
                        cell.append(td.a.string)
                        txt = td.div.get_text()  # conteudo
                        s = re.sub(
                            r'(?m)^(\*\*\*|Nome:|Matrícula:|Ramal\/Telefone para contato:|Setor\/Local:|Período em que trabalha \(manhã\/tarde\):|Nome da máquina:|Secretaria:).*\n?',
                            '', txt)
                        s = s.replace('Descreva a ocorrência:', '').replace('\n', ' ').replace('\xa0', ' ').replace(
                            '-------------------------------', '')
                        # print(index, s)
                        cell.append(s)
                    # elif index == 3: # Prioridade
                    #     print(index, td.string)
                    # elif index == 4: # Status
                    #     print(index, td.contents[1].strip())
                    elif index == 5:  # Ultima atualização
                        # print(index, td.string)
                        cell.append(td.string)
                    elif index == 6:  # Data de abertura
                        # print(index, td.string)
                        cell.append(td.string)
                    elif index == 7:  # Requerente
                        # print(index, td.get_text().split('Nome:')[0].strip())
                        cell.append(td.get_text().split('Nome:')[0].strip())
                    # elif index == 8: # Grupo requerente
                    #     print(index, td.string)
                    elif index == 9:  # num. acompanhamentos
                        # print(index, td.string)
                        cell.append(td.string)
                    # elif index == 10: # cat tarefa
                    #     print(index, td.string)
                    elif index == 11:  # tecnico
                        # print(index, td.get_text().split('Nome:')[0].strip())
                        cell.append(td.get_text().split('Nome:')[0].strip())
                    elif index == 12:  # grupo tecnico
                        # print(index, td.string)
                        if td.string != None: cell.append(td.string.split('>')[-1].strip())
                    # elif index == 13: # status aprovacao
                    #     print(index, td.string)
                    # elif index == 14: # ultima edição
                    #     # print(index, td.get_text().split('Nome:')[0].strip())
                    #     cell.append(td.get_text().split('Nome:')[0].strip())
                    # elif index == 15: # aprovador
                    #     print(index, td.get_text().split('Nome:')[0].strip())
                if len(cell) > 0: rows.append(cell)
        # print(row)
        df = pd.DataFrame.from_records(rows, columns=labels, index='chamado')

        # convertendo datas
        df.atualizacao = pd.to_datetime(df.atualizacao)
        df.criacao = pd.to_datetime(df.criacao)

        #convertendo dados categóricos
        df.interacoes = df.interacoes.astype('category')
        df.grupo = df.grupo.astype('category')

        return df

def main():
    login=''
    passw=''
    main_url=''
    search_url=''

    sc = Scrapper(login, passw, main_url)
    rtn = sc.busca_chamados(search_url)
    print(rtn.columns)

if __name__ == "__main__":
    main()