import socket
import threading
import time
from cryptography.fernet import Fernet

# Classe para representar cada cliente conectado
class Cliente:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.nome_usuario = None
        self.ip = addr[0]
        self.dados = {}

    def enviar_comando(self, comando):
        try:
            self.conn.send(comando.encode())
        except Exception as e:
            print(f"Erro ao enviar comando para {self.nome_usuario}: {e}")

    def fechar_conexao(self):
        try:
            self.conn.close()
            print(f"Conexão com {self.nome_usuario} encerrada.")
        except Exception as e:
            print(f"Erro ao fechar conexão com {self.nome_usuario}: {e}")


# Classe principal do servidor
class Servidor:
    def __init__(self, broadcast_port=50000, tcp_port=60000):
        self.broadcast_port = broadcast_port
        self.tcp_port = tcp_port
        self.clientes = []
        self.running = True
        self.key = Fernet.generate_key()  # Chave de criptografia
        self.cipher_suite = Fernet(self.key)

    def iniciar(self):
        # Thread para broadcast UDP
        threading.Thread(target=self.broadcast_udp).start()

        # Iniciar servidor TCP
        self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_tcp.bind(('', self.tcp_port))
        self.socket_tcp.listen(5)
        print(f"Servidor TCP ouvindo na porta {self.tcp_port}...")

        # Thread para ler comandos do terminal
        threading.Thread(target=self.ler_comandos).start()

        while self.running:
            conn, addr = self.socket_tcp.accept()
            cliente = Cliente(conn, addr)
            self.clientes.append(cliente)
            threading.Thread(target=self.lidar_cliente, args=(cliente,)).start()

    def broadcast_udp(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        ip_servidor = socket.gethostbyname(socket.gethostname())  # Obtém o IP do servidor
        mensagem = f"SERVIDOR_TCP:{ip_servidor}:{self.tcp_port}"  # Inclui o IP na mensagem
        while self.running:
            udp_socket.sendto(mensagem.encode(), ('<broadcast>', self.broadcast_port))
            time.sleep(30)

    def lidar_cliente(self, cliente):
        try:
            # Envia a chave de criptografia para o cliente
            cliente.conn.send(self.key)
            while self.running:
                dados_criptografados = cliente.conn.recv(1024)
                if not dados_criptografados:
                    print(f"Cliente {cliente.nome_usuario} desconectado.")
                    break

                dados = self.descriptografar(dados_criptografados)
                if not cliente.nome_usuario:
                    cliente.nome_usuario = dados.get("nome_usuario", "Desconhecido")
                    print(f"Novo cliente conectado: {cliente.nome_usuario} ({cliente.ip})")

                cliente.dados = dados
                print(f"Dados recebidos de {cliente.nome_usuario}: {dados}")
        except Exception as e:
            print(f"Erro ao lidar com cliente {cliente.nome_usuario}: {e}")
        finally:
            self.remover_cliente(cliente)

    def remover_cliente(self, cliente):
        if cliente in self.clientes:
            self.clientes.remove(cliente)
            cliente.fechar_conexao()

    def ler_comandos(self):
        while self.running:
            comando = input("Digite um comando (help para lista): ").strip().lower()
            if comando == "help":
                print("Comandos disponíveis:")
                print("- listar: Mostra todos os clientes conectados.")
                print("- info <nome/ip>: Mostra informações de um cliente específico.")
                print("- media: Mostra a média das informações numéricas de todos os clientes.")
                print("- desconectar <nome/ip>: Desconecta um cliente específico.")
                print("- sair: Encerra o servidor.")
            elif comando == "listar":
                for cliente in self.clientes:
                    print(f"{cliente.nome_usuario} ({cliente.ip})")
            elif comando.startswith("info"):
                _, identificador = comando.split(maxsplit=1)
                cliente = self.encontrar_cliente(identificador)
                if cliente:
                    print(f"Informações de {cliente.nome_usuario}: {cliente.dados}")
                else:
                    print("Cliente não encontrado.")
            elif comando == "media":
                self.calcular_media()
            elif comando.startswith("desconectar"):
                _, identificador = comando.split(maxsplit=1)
                cliente = self.encontrar_cliente(identificador)
                if cliente:
                    self.remover_cliente(cliente)
                    print(f"Cliente {cliente.nome_usuario} desconectado.")
                else:
                    print("Cliente não encontrado.")
            elif comando == "sair":
                self.running = False
                for cliente in self.clientes:
                    cliente.fechar_conexao()
                print("Encerrando servidor...")
                break

    def encontrar_cliente(self, identificador):
        for cliente in self.clientes:
            if identificador == cliente.nome_usuario or identificador == cliente.ip:
                return cliente
        return None

    def calcular_media(self):
        if not self.clientes:
            print("Nenhum cliente conectado.")
            return

        total_cores = total_ram_total = total_ram_livre = total_disco_total = total_disco_livre = total_temp = 0
        count = len(self.clientes)

        for cliente in self.clientes:
            dados = cliente.dados
            total_cores += dados.get("cores", 0)
            total_ram_total += dados.get("ram_total", 0)
            total_ram_livre += dados.get("ram_livre", 0)
            total_disco_total += dados.get("disco_total", 0)
            total_disco_livre += dados.get("disco_livre", 0)
            total_temp += dados.get("temperatura", 0)

        print("Médias:")
        print(f"- Cores: {total_cores / count:.2f}")
        print(f"- RAM Total: {total_ram_total / count:.2f} GB")
        print(f"- RAM Livre: {total_ram_livre / count:.2f} GB")
        print(f"- Disco Total: {total_disco_total / count:.2f} GB")
        print(f"- Disco Livre: {total_disco_livre / count:.2f} GB")
        print(f"- Temperatura: {total_temp / count:.2f} °C")

    def criptografar(self, dados):
        return self.cipher_suite.encrypt(str(dados).encode())

    def descriptografar(self, dados_criptografados):
        return eval(self.cipher_suite.decrypt(dados_criptografados).decode())


if __name__ == "__main__":
    servidor = Servidor()
    servidor.iniciar()