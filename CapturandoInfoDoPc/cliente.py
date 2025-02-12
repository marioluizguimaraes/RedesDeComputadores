# Importações de bibliotecas necessárias
import socket  # Para comunicação de rede (UDP e TCP)
import threading  # Para executar tarefas em paralelo (threads)
import time  # Para pausar a execução do programa
import psutil  # Para coletar informações do sistema (CPU, memória, disco, etc.)
import os  # Para interagir com o sistema operacional (ex.: obter nome do usuário logado)
from cryptography.fernet import Fernet  # Para criptografar/descriptografar dados

# Função para coletar informações do sistema
def coletar_informacoes():
    try:
        # Cria um dicionário para armazenar as informações coletadas
        info = {
            "cores": psutil.cpu_count(logical=True),  # Número de núcleos lógicos da CPU
            "ram_total": round(psutil.virtual_memory().total / (1024 ** 3), 2),  # Memória RAM total (em GB)
            "ram_livre": round(psutil.virtual_memory().available / (1024 ** 3), 2),  # Memória RAM disponível (em GB)
            "disco_total": round(psutil.disk_usage('/').total / (1024 ** 3), 2),  # Espaço total no disco principal (em GB)
            "disco_livre": round(psutil.disk_usage('/').free / (1024 ** 3), 2),  # Espaço livre no disco principal (em GB)
            "temperatura": 0,  # Temperatura do processador (valor padrão 0, caso não esteja disponível)
            "nome_usuario": os.getlogin(),  # Nome do usuário logado no sistema
            "ipv4": socket.gethostbyname(socket.gethostname())  # Endereço IPv4 local do dispositivo
        }

        # Tenta obter a temperatura apenas se o método estiver disponível
        if hasattr(psutil, "sensors_temperatures"):  # Verifica se o método sensors_temperatures está disponível
            temperaturas = psutil.sensors_temperatures()  # Obtém as temperaturas do sistema
            if temperaturas and 'coretemp' in temperaturas:  # Verifica se há temperaturas disponíveis para 'coretemp'
                info["temperatura"] = temperaturas['coretemp'][0].current  # Atualiza a temperatura no dicionário
        else:
            print("A leitura de temperatura não está disponível!") 

        return info  # Retorna o dicionário com as informações coletadas
    
    except Exception as e:
        print(f"Erro ao coletar informações: {e}")  # Imprime mensagem de erro em caso de falha
        return {}  # Retorna um dicionário vazio em caso de erro

# Classe principal do cliente
class Cliente:
    def __init__(self, broadcast_port=50000):  # Construtor da classe
        self.broadcast_port = broadcast_port  # Porta usada para escutar broadcasts UDP
        self.servidor_endereco = None  # Armazena o endereço do servidor (IP e porta)
        self.key = None  # Chave de criptografia recebida do servidor
        self.cipher_suite = None  # Objeto usado para criptografar/descriptografar dados

    # Método para iniciar o cliente
    def iniciar(self):
        # Inicia uma thread para escutar mensagens de broadcast UDP
        threading.Thread(target=self.escutar_broadcast).start()

    # Método para escutar mensagens de broadcast UDP
    def escutar_broadcast(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP
        udp_socket.bind(('', self.broadcast_port))  # Vincula o socket à porta especificada
        print("Escutando broadcast...")  # Informa que o cliente está aguardando broadcasts

        while True:  # Loop infinito para escutar mensagens
            mensagem, _ = udp_socket.recvfrom(1024)  # Recebe uma mensagem UDP (tamanho máximo de 1024 bytes)
            mensagem = mensagem.decode()  # Decodifica a mensagem de bytes para string
            if mensagem.startswith("SERVIDOR_TCP:"):  # Verifica se a mensagem começa com "SERVIDOR_TCP:"
                _, ip_servidor, porta = mensagem.split(":")  # Extrai o IP e a porta do servidor
                self.servidor_endereco = (ip_servidor, int(porta))  # Define o endereço completo do servidor
                print(f"Servidor encontrado: {self.servidor_endereco}")  # Informa o endereço do servidor encontrado
                break  # Sai do loop após encontrar o servidor

        udp_socket.close()  # Fecha o socket UDP
        self.conectar_servidor()  # Conecta-se ao servidor via TCP

    # Método para conectar-se ao servidor via TCP
    def conectar_servidor(self):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket TCP
        tcp_socket.connect(self.servidor_endereco)  # Conecta-se ao servidor usando o endereço obtido
        self.key = tcp_socket.recv(1024)  # Recebe a chave de criptografia enviada pelo servidor
        self.cipher_suite = Fernet(self.key)  # Configura o objeto de criptografia com a chave recebida
        print("Conectado ao servidor.")  # Informa que a conexão foi estabelecida
        # Inicia uma thread para enviar informações ao servidor
        threading.Thread(target=self.enviar_informacoes, args=(tcp_socket,)).start()

    # Método para enviar informações ao servidor
    def enviar_informacoes(self, tcp_socket):
        while True:  # Loop infinito para enviar informações periodicamente
            informacoes = coletar_informacoes()  # Coleta informações do sistema
            dados_criptografados = self.criptografar(informacoes)  # Criptografa os dados
            tcp_socket.send(dados_criptografados)  # Envia os dados criptografados ao servidor
            time.sleep(30)  # Pausa por 30 segundos antes de enviar novamente

    # Método para criptografar dados
    def criptografar(self, dados):
        return self.cipher_suite.encrypt(str(dados).encode())  # Converte os dados em string, codifica em bytes e criptografa

# Execução principal do programa
if __name__ == "__main__":
    cliente = Cliente()  # Cria uma instância da classe Cliente
    cliente.iniciar()  # Inicia o cliente