import socket  # UDP e TCP
import threading # Para criar Threads
import time 
import psutil  # informações do sistema 
import os  # Para interagir com o sistema operacional
from cryptography.fernet import Fernet  # Para criptografar/descriptografar dados
import wmi

# Função para coletar informações do sistema
def coletar_informacoes():
    try:
        # Cria um dicionário para armazenar as informações coletadas
        info = {
            "nome_usuario": os.getlogin(),  # Nome do usuário logado no sistema
            "ipv4": socket.gethostbyname(socket.gethostname()),  # Endereço IPv4 local do dispositivo
            "cores": psutil.cpu_count(logical=True),  # Número de núcleos lógicos da CPU
            "ram_total": round(psutil.virtual_memory().total / (1024 ** 3), 2),  # Memória RAM total (em GB)
            "ram_livre": round(psutil.virtual_memory().available / (1024 ** 3), 2),  # Memória RAM disponível (em GB)
            "disco_total": round(psutil.disk_usage('/').total / (1024 ** 3), 2),  # Espaço total no disco principal (em GB)
            "disco_livre": round(psutil.disk_usage('/').free / (1024 ** 3), 2),  # Espaço livre no disco principal (em GB)
        }

        return info 
    
    except Exception as e:
        print(f"Erro ao coletar informações: {e}")  # Imprime mensagem de erro em caso de falha
        return {}  # Retorna um dicionário vazio em caso de erro

# Classe principal do cliente
class Cliente:
    def __init__(self, broadcast_port=50000):  # Construtor da classe
        self.broadcastPort = broadcast_port  # Porta usada para escutar broadcasts UDP
        self.servidorEndereco = None  # Armazena o endereço do servidor (IP e porta)
        self.key = None  # Chave de criptografia recebida do servidor
        self.cipherSuite = None  # Objeto usado para criptografar/descriptografar dados

    # Método para iniciar o cliente
    def iniciar(self):
        # Inicia uma thread para escutar mensagens de broadcast UDP
        threading.Thread(target=self.escutarBroadcast).start()

    # Método para escutar mensagens de broadcast UDP
    def escutarBroadcast(self):
        socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP
        socketUDP.bind(('', self.broadcastPort))  # Vincula o socket à porta especificada
        print("Escutando broadcast...") 

        while True:  # Loop infinito para escutar mensagens
            mensagem, _ = socketUDP.recvfrom(1024)  # Recebe uma mensagem UDP (tamanho máximo de 1024 bytes)
            mensagem = mensagem.decode()  # Decodifica a mensagem de bytes para string
            
            if mensagem.startswith("SERVIDOR_TCP:"):  # Verifica se a mensagem começa com "SERVIDOR_TCP:"
                _, ip_servidor, porta = mensagem.split(":")  # Extrai o IP e a porta do servidor
                self.servidorEndereco = (ip_servidor, int(porta))  # Define o endereço completo do servidor
                print(f"Servidor encontrado: {self.servidorEndereco}")  # Informa o endereço do servidor encontrado
                break  # Sai do loop após encontrar o servidor
        
        # Fechando socket UDP
        socketUDP.close()  
        
        # Conectando ao servidor via TCP
        self.conectarServidorTCP()  

    # Método para conectar-se ao servidor via TCP
    def conectarServidorTCP(self):
        socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket TCP
        socketTCP.connect(self.servidorEndereco)  # Conecta-se ao servidor usando o endereço obtido
        
        self.key = socketTCP.recv(1024)  # Recebe a chave de criptografia enviada pelo servidor
        self.cipherSuite = Fernet(self.key)  # Configura o objeto de criptografia com a chave recebida
        print("Conectado ao servidor.")
        
        # Inicia uma thread para enviar informações ao servidor
        threading.Thread(target=self.enviarInformacoes, args=(socketTCP,)).start()

    # Método para enviar informações ao servidor via TCP
    def enviarInformacoes(self, tcp_socket):
        while True:  # Loop infinito para enviar informações periodicamente
            informacoes = coletar_informacoes()  # Coleta informações do sistema
            dadosCriptografados = self.criptografar(informacoes)  # Criptografa os dados
            tcp_socket.send(dadosCriptografados)  # Envia os dados criptografados ao servidor
            time.sleep(30)

    # Método para criptografar dados
    def criptografar(self, dados):
        return self.cipherSuite.encrypt(str(dados).encode())  # Converte os dados em string, codifica em bytes e criptografa

# Execução principal do programa
if __name__ == "__main__":
    cliente = Cliente()
    cliente.iniciar()