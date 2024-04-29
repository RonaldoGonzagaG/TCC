from flask import Flask, request
import mysql.connector
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import urllib

# Inicializa a aplicação Flask
app = Flask(__name__)

# Inicializa a conexão com o banco de dados
db = mysql.connector.connect(
    host="127.0.0.1" #localhost,
    port=3306,
    user="root"#seu_usuario,
    password="123456"#"sua_senha",
    database=Tcc2 #"seu_banco_de_dados"
)

# Função para inserir mensagens no banco de dados
def inserir_mensagem(mensagem):
    try:
        cursor = db.cursor()
        query = "INSERT INTO mensagens (conteudo) VALUES (%s)"
        cursor.execute(query, (mensagem,))
        db.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print("Erro ao inserir mensagem no banco de dados:", err)

# Função para enviar uma mensagem pelo WhatsApp e retornar a resposta
def enviar_mensagem_e_obter_resposta(numero, mensagem):
    navegador = webdriver.Chrome(executable_path='caminho_para_o_executável_do_driver_do_Chrome')
    navegador.get(f"https://web.whatsapp.com/send?phone=55{numero}&text={urllib.parse.quote(mensagem)}")
    WebDriverWait(navegador, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='_3FRCZ copyable-text selectable-text']")))
    resposta = WebDriverWait(navegador, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='_3zb-j']")))
    navegador.quit()
    return resposta.text

# Rota para receber mensagens do WhatsApp
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    mensagem_recebida = data.get('mensagem')  # Acessando a chave 'mensagem' com segurança
    if mensagem_recebida:
        inserir_mensagem(mensagem_recebida)
        return 'Mensagem recebida e armazenada no banco de dados.'
    else:
        return 'Campo mensagem ausente', 400

if __name__ == '__main__':
    # Lê os dados do arquivo Excel
    dados_excel = pd.read_excel('caminho_para_o_arquivo_excel')

    # Itera sobre os dados do Excel e envia mensagens pelo WhatsApp
    for i, linha in dados_excel.iterrows():
        pessoa = linha['Pessoa']
        numero = linha['Numero']
        cpf = linha['CPF']
        link = linha['link']
        endereco = linha['Endereco']
        midia = linha['Midia']

        # Envia a primeira mensagem
        texto1 = f"Olá {pessoa}! Para continuarmos, precisamos da sua autorização para enviar mensagens por este meio. Concorda?"
        resposta1 = enviar_mensagem_e_obter_resposta(numero, texto1)
        inserir_mensagem(resposta1)

        # Envia a segunda mensagem
        texto2 = f"{pessoa}, você concorda com o envio de mensagens conforme a Lei Geral de Proteção de Dados? Link: {link}"
        resposta2 = enviar_mensagem_e_obter_resposta(numero, texto2)
        inserir_mensagem(resposta2)

        # Envia a primeira mensagem
        texto3 = f"Olá {pessoa}! Para continuarmos, precisamos da sua autorização para enviar mensagens por este meio. Concorda?"
        resposta3 = enviar_mensagem_e_obter_resposta(numero, texto3)
        inserir_mensagem(resposta3)

        # Envia a segunda mensagem
        texto4 = f"{pessoa}, você concorda com o envio de mensagens conforme a Lei Geral de Proteção de Dados? Link: {link}"
        resposta4 = enviar_mensagem_e_obter_resposta(numero, texto4)
        inserir_mensagem(resposta4)

    # Inicia o servidor Flask
    app.run(debug=True)
