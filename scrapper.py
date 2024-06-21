import requests, json
from bs4 import BeautifulSoup
import pandas as pd
import re

# Configurando a saída padrão para UTF-8
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# O trabalho consiste na extraçaõ de notícias do site lance
# O site tem uma estrutura interessante com elementos claros para se obter os links
# A estratégia é buscar os links das matérias com suas slugs na página principal e depois buscar os links das matérias nos caminhos dos clubes a serem explorados
# Ao extrair os links, novamente é feita uma iteração para buscar os conteúdos dos links pelas tags html com a seguinte estrutura: Título Principal(H1), Título Secundário(H2), conteúdo (p) e data da publicação (time)
# Por quetões de espaço e volume de dados, foram extraídas 5 notícias de cada time e da página principal podendo variar de acordo com a definição variável

#Especificando a url do site
url_principal = "https://www.lance.com.br/"

#Criando a array de times no formato de slugs para iteração
times = [
   "atletico-mineiro", "atletico-paranaense","bahia","botafogo", "bragantino",  "corinthians", "criciuma", "cruzeiro", "cuiaba","flamengo", "fluminense", "fortaleza", "gremio", "internacional", "palmeiras", "santos", "sao-paulo", "vasco", "vitoria"
]

#Definindo número máximo de notícias por página
maximo_noticias = 10

#Criação da varíavel onde os links serão salvos
links_gerais = []

#Criação da função para obtenção dos links das páginas de acordo com a url
def obter_links(url, n_noticias=None):
    # Criando array vazia para coleta dos links
    links = []

    # Criando o contador de notícias
    contador = 0
    
    #Obtendo os links da página principal usando o requests
    response = requests.get(url)

    # Verificando se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Parseando o conteúdo HTML da página
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrando todas as tags 'a' com atributo href
        all_links = soup.find_all('a', href=True)

        # Filtrando links que terminam com .html e não contêm "apostas"
        # Havia links de propaganda direcionando para sites de aposta que foram retirados do resultado
        html_links = [link['href'] for link in all_links if link['href'].endswith('.html') and 'apostas' not in link['href']]

        # Retornando os links
        for link in html_links:
            # Fazendo correções de link relativo e retirando excessos de barras que foram observadas
            if link.startswith('/'):
                full_link = url.strip("/") + link
            else:
                full_link = link
            links.append(full_link)

            # Verificando se foi passado o número de notícias a extrair e retorna se o valor for atingido
            if n_noticias:
                 contador += 1
                 if contador >= n_noticias:
                      return links

    else:
        print('Falha ao acessar o site')
    
    # Retornando a lista de links
    return links


# Função para extrair data e hora
def extrair_data_hora(data_str):
    match = re.search(r'Publicada em (\d{2}/\d{2}/\d{4} - \d{2}:\d{2})', data_str)
    if match:
        return match.group(1)
    return None

# Função para extrair local
def extrair_local(data_str):
    match = re.search(r'• Publicada em \d{2}/\d{2}/\d{4} - \d{2}:\d{2} • (.+)', data_str)
    if match:
        return match.group(1)
    return None



#Função para validar a estrutura do dicionário com as respectivas chaves presentes
def validar_estrutura(dicionario, chaves_esperadas):
    
    if dicionario is None:
        return False
    # Checando se todas as chaves esperadas estão presentes
    if not chaves_esperadas.issubset(dicionario.keys()):
        return False
    
    # Checando se os valores não são nulos
    for chave in chaves_esperadas:
        if dicionario[chave] is None or (isinstance(dicionario[chave], list) and not dicionario[chave]):
            return False
    
    return True

#Função para obter o conteúdo
def obter_conteudo(url):
    # Criando o dicionário vazio para coletar o conteúdo 
    conteudo = {}

    # Obtendo as páginas de conteúdo das notícias
    article_response = requests.get(url)

    # Verificando a resposta
    if article_response.status_code == 200:
                
                # Parseanso o conteúdo HTML da página da notícia
                article_soup = BeautifulSoup(article_response.content, 'html.parser')
                
                # Extraindo o conteúdo da tag <article>
                article = article_soup.find('article')

                # Prevenindo extrações de páginas que não tenham a tag <article>
                if not article:
                     return 
                
                if not article.find('h1'):
                     return {}
                # Buscando dentro do artigo o título principal e extraindo o texto pelo get_text
                conteudo["Título 1"] = article.find('h1').get_text()

                if not article.find('h2'):
                     return {}

                # Buscando dentro do artigo o título principal e extraindo o texto pelo get_text
                conteudo["Título 2"] = article.find('h2').get_text()

                if not article.find('time'):
                     return {}

                # Recuperando os dados de data e local da publicação na tag <time>
                conteudo["Data"] = extrair_data_hora(article.find('time').get_text())
                conteudo["Local"] = extrair_local(article.find('time').get_text())

                

                # Encontrando as tags de parágrafos
                paragrafos = article.find_all('p', class_="w-full")

                # Recuperando a array de parágrafos obtidos
                paragrafos = [p for p in paragrafos if not p.find('a')]

                #Criando uma string vazia para inserção do conteúdo
                conteudo["Conteúdo"] = ""
                for paragrafo in paragrafos:
                
                     # Concatenando as strings inserindo a quebra de linha no final como \n
                     conteudo["Conteúdo"] += paragrafo.get_text() + "\n"
                # conteudo["Conteúdo"] = [conteudo["Conteúdo"]]
    return conteudo


# Obtendo links da página principal:
# Chamando a função par obtenção dos links com 5 links
links = obter_links(url_principal, maximo_noticias)
# Concatenando os novos links recuperados na array de todos os links
links_gerais += links

# Imprimindo os tamanhos da array para verificação
print(len(links_gerais))

# Obtendo os links nas paginas dos times
# Iterando pelo tamanho da array de times
for i in range(len(times)):
    # Obtendo os links por time ao concatenar a string da url principal com a string da slug do time e 5 links
    links = obter_links(url_principal + times[i], maximo_noticias)

    # Adicionando os links à lista geral de links
    links_gerais += links

    # Imprimindo os tamanhos da array para verificação
    print(len(links_gerais))

# Convertendo a lista de links gerais em um conjunto para remover as duplicatas
links_gerais = set(links_gerais)


# Definindo as chaves esperadas
colunas_esperadas  = {"Título 1", "Título 2", "Data", "Local", "Conteúdo"}

#Criando o array de notícias recebidas
noticias = []

for link in links_gerais:
     conteudo = obter_conteudo(link)
     #Caso a estrutura seja válida é incorporada à lista
     if validar_estrutura(conteudo, colunas_esperadas):
          noticias.append(conteudo)
    #  print(conteudo)
    #  conteudo = pd.DataFrame(conteudo)
    #  noticias = pd.concat([noticias, conteudo], ignore_index=True)

#A lista é convertida para um datraframe
noticias = pd.DataFrame(noticias)

#Converte-se em data
noticias["Data"] = pd.to_datetime(noticias["Data"])



# Declarando o nome do arquivo a salvar os conteúdos extraídos 
arquivo = "noticias_lance.csv"

#Salvando o arquivo
noticias.to_csv(arquivo,encoding="utf-8", index=False)

