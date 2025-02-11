import socket
import threading
import time
import psutil
import os
import platform
from cryptography.fernet import Fernet

# Função para coletar informações do sistema
def coletar_informacoes():
    try:
        info = {
            "cores": psutil.cpu_count(logical=True),
            "ram_total": round(psutil.virtual_memory().total / (1024 ** 3), 2),
            "ram_livre": round(psutil.virtual_memory().available / (1024 ** 3), 2),
            "disco_total": round(psutil.disk_usage('/').total / (1024 ** 3), 2),
            "disco_livre": round(psutil.disk_usage('/').free / (1024 ** 3), 2),
            "temperatura": psutil.sensors_temperatures().get('coretemp', [{}])[0].get('current', 0),
            "nome_usuario": os.getlogin(),
            "ipv4": socket.gethostbyname(socket.gethostname())
        }
        return info
    except Exception as e:
        print(f"Erro ao coletar informações: {e}")
        return {}

# Classe principal do cliente
class Cliente:
    def __init__(self, broadcast_port=50000):
        self.broadcast_port = broadcast_port
        self.servidor_endereco = None
        self.key = None
        self.cipher_suite = None

    def iniciar(self):
        # Thread para escutar broadcast UDP
        threading.Thread(target=self.escutar_broadcast).start()

    def escutar_broadcast(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('', self.broadcast_port))
        print("Escutando broadcast...")
        while True:
            mensagem, _ = udp_socket.recvfrom(1024)
            mensagem = mensagem.decode()
            if mensagem.startswith("SERVIDOR_TCP:"):
                _, porta = mensagem.split(":")
                self.servidor_endereco = ('', int(porta))
                print(f"Servidor encontrado: {self.servidor_endereco}")
                break

        udp_socket.close()
        self.conectar_servidor()

    def conectar_servidor(self):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect(self.servidor_endereco)
        self.key = tcp_socket.recv(1024)  # Recebe a chave de criptografia
        self.cipher_suite = Fernet(self.key)
        print("Conectado ao servidor.")

        threading.Thread(target=self.enviar_informacoes, args=(tcp_socket,)).start()

    def enviar_informacoes(self, tcp_socket):
        while True:
            informacoes = coletar_informacoes()
            dados_criptografados = self.criptografar(informacoes)
            tcp_socket.send(dados_criptografados)
            time.sleep(30)

    def criptografar(self, dados):
        return self.cipher_suite.encrypt(str(dados).encode())


if __name__ == "__main__":
    cliente = Cliente()
    cliente.iniciar()