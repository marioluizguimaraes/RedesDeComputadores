# Importações de bibliotecas necessárias
import socket  # Para comunicação de rede (UDP e TCP)
import threading  # Para executar tarefas em paralelo (threads)
import time  # Para pausar a execução do programa
from cryptography.fernet import Fernet  # Para criptografar/descriptografar dados

# Classe para representar cada cliente conectado
class Cliente:
    def __init__(self, conn, addr):
        self.conn = conn  # Conexão TCP com o cliente
        self.addr = addr  # Endereço do cliente (IP e porta)
        self.nome_usuario = None  # Nome do usuário logado no cliente (inicialmente vazio)
        self.ip = addr[0]  # IP do cliente
        self.dados = {}  # Dicionário para armazenar os dados enviados pelo cliente

    # Método para enviar um comando ao cliente
    def enviar_comando(self, comando):
        try:
            self.conn.send(comando.encode())  # Envia o comando codificado em bytes ao cliente
        except Exception as e:
            print(f"Erro ao enviar comando para {self.nome_usuario}: {e}")  # Imprime mensagem de erro

    # Método para fechar a conexão com o cliente
    def fechar_conexao(self):
        try:
            self.conn.close()  # Fecha a conexão TCP com o cliente
            print(f"Conexão com {self.nome_usuario} encerrada.")  # Informa que a conexão foi encerrada
        except Exception as e:
            print(f"Erro ao fechar conexão com {self.nome_usuario}: {e}")  # Imprime mensagem de erro


# Classe principal do servidor
class Servidor:
    def __init__(self, broadcast_port=50000, tcp_port=60000):
        self.broadcast_port = broadcast_port  # Porta usada para enviar mensagens de broadcast UDP
        self.tcp_port = tcp_port  # Porta usada para aceitar conexões TCP
        self.clientes = []  # Lista para armazenar os clientes conectados
        self.running = True  # Controla se o servidor está em execução
        self.key = Fernet.generate_key()  # Gera uma chave de criptografia
        self.cipher_suite = Fernet(self.key)  # Configura o objeto de criptografia com a chave gerada

    # Método para iniciar o servidor
    def iniciar(self):
        # Inicia uma thread para enviar mensagens de broadcast UDP
        threading.Thread(target=self.broadcast_udp).start()
        # Cria um socket TCP para aceitar conexões
        self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket TCP
        self.socket_tcp.bind(('', self.tcp_port))  # Vincula o socket à porta TCP especificada
        self.socket_tcp.listen(5)  # Coloca o socket em modo de escuta (máximo de 5 conexões pendentes)
        print(f"Servidor TCP ouvindo na porta {self.tcp_port}...")  # Informa que o servidor está ouvindo
        # Inicia uma thread para ler comandos do terminal
        threading.Thread(target=self.ler_comandos).start()
        # Loop principal para aceitar novas conexões TCP
        while self.running:
            conn, addr = self.socket_tcp.accept()  # Aceita uma nova conexão TCP
            cliente = Cliente(conn, addr)  # Cria um objeto Cliente para representar o cliente conectado
            self.clientes.append(cliente)  # Adiciona o cliente à lista de clientes conectados
            # Inicia uma thread para lidar com o cliente
            threading.Thread(target=self.lidar_cliente, args=(cliente,)).start()

    # Método para enviar mensagens de broadcast UDP
    def broadcast_udp(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria um socket UDP
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Habilita o envio de broadcast
        ip_servidor = socket.gethostbyname(socket.gethostname())  # Obtém o IP do servidor
        mensagem = f"SERVIDOR_TCP:{ip_servidor}:{self.tcp_port}"  # Cria a mensagem de broadcast com IP e porta TCP
        while self.running:  # Loop infinito para enviar mensagens de broadcast
            udp_socket.sendto(mensagem.encode(), ('<broadcast>', self.broadcast_port))  # Envia a mensagem para todos na rede
            time.sleep(30)  # Pausa por 30 segundos antes de enviar novamente

    # Método para lidar com a comunicação com um cliente específico
    def lidar_cliente(self, cliente):
        try:
            cliente.conn.send(self.key)  # Envia a chave de criptografia ao cliente
            while self.running:  # Loop infinito para receber dados do cliente
                dados_criptografados = cliente.conn.recv(1024)  # Recebe dados criptografados do cliente (tamanho máximo de 1024 bytes)
                if not dados_criptografados:  # Verifica se a conexão foi encerrada pelo cliente
                    print(f"Cliente {cliente.nome_usuario} desconectado.")
                    break  # Sai do loop se o cliente desconectar
                dados = self.descriptografar(dados_criptografados)  # Descriptografa os dados recebidos
                if not cliente.nome_usuario:  # Define o nome do usuário se ainda não foi definido
                    cliente.nome_usuario = dados.get("nome_usuario", "Desconhecido")  # Obtém o nome do usuário dos dados
                    print(f"\nNovo cliente conectado: {cliente.nome_usuario} ({cliente.ip})")  # Informa que um novo cliente foi conectado
                cliente.dados = dados  # Atualiza os dados do cliente
                print(f"Dados recebidos")
                #print(f"Dados recebidos de {cliente.nome_usuario}: {dados}")  # Exibe os dados recebidos
        except Exception as e:
            print(f"Erro ao lidar com cliente {cliente.nome_usuario}: {e}")  # Imprime mensagem de erro
        finally:
            self.remover_cliente(cliente)  # Remove o cliente da lista de clientes conectados

    # Método para remover um cliente da lista de clientes conectados
    def remover_cliente(self, cliente):
        if cliente in self.clientes:  # Verifica se o cliente está na lista
            self.clientes.remove(cliente)  # Remove o cliente da lista
            cliente.fechar_conexao()  # Fecha a conexão com o cliente

    # Método para ler comandos digitados no terminal
    def ler_comandos(self):
        while self.running:  # Loop infinito para ler comandos
            comando = input("Digite um comando (help para lista):").strip().lower()  # Lê o comando do terminal
            if comando == "help":  # Exibe a lista de comandos disponíveis
                print("Comandos disponíveis:")
                print("- listar: Mostra todos os clientes conectados.")
                print("- info [ip]: Mostra informações de um cliente específico.")
                print("- media: Mostra a média das informações numéricas de todos os clientes.")
                print("- desconectar [ip]: Desconecta um cliente específico.")
                print("- sair: Encerra o servidor.")
            elif comando == "listar":  # Lista todos os clientes conectados
                for cliente in self.clientes:
                    print(f"{cliente.nome_usuario} ({cliente.ip})")
            elif comando.startswith("info"):  # Exibe informações de um cliente específico
                _, identificador = comando.split(maxsplit=1)  # Divide o comando em duas partes (comando e identificador)
                cliente = self.encontrar_cliente(identificador)  # Procura o cliente pelo nome ou IP
                if cliente:
                    print(f"Informações de {cliente.nome_usuario}:")
                    for chave, valor in cliente.dados.items():
                        print(f"  - {chave}: {valor}")  # Exibe as informações do cliente
                else:
                    print("Cliente não encontrado.")  # Informa que o cliente não foi encontrado
            elif comando == "media":  # Calcula a média das informações numéricas de todos os clientes
                self.calcular_media()
            elif comando.startswith("desconectar"):  # Desconecta um cliente específico
                _, identificador = comando.split(maxsplit=1)  # Divide o comando em duas partes (comando e identificador)
                cliente = self.encontrar_cliente(identificador)  # Procura o cliente pelo nome ou IP
                if cliente:
                    self.remover_cliente(cliente)  # Remove o cliente da lista
                    print(f"Cliente {cliente.nome_usuario} desconectado.")  # Informa que o cliente foi desconectado
                else:
                    print("Cliente não encontrado.")  # Informa que o cliente não foi encontrado
            elif comando == "sair":  # Encerra o servidor
                self.running = False  # Altera o estado do servidor para "não rodando"
                for cliente in self.clientes:  # Fecha a conexão com todos os clientes conectados
                    cliente.fechar_conexao()
                print("Encerrando servidor...")  # Informa que o servidor está sendo encerrado
                break  # Sai do loop

    # Método para encontrar um cliente pelo nome ou IP
    def encontrar_cliente(self, identificador):
        for cliente in self.clientes:  # Itera sobre a lista de clientes
            if identificador == cliente.nome_usuario or identificador == cliente.ip:  # Verifica se o identificador corresponde ao nome ou IP
                return cliente  # Retorna o cliente encontrado
        return None  # Retorna None se o cliente não for encontrado

    # Método para calcular a média das informações numéricas de todos os clientes
    def calcular_media(self):
        if not self.clientes:  # Verifica se há clientes conectados
            print("Nenhum cliente conectado.")  # Informa que não há clientes conectados
            return
        total_cores = total_ram_total = total_ram_livre = total_disco_total = total_disco_livre = total_temp = 0  # Inicializa variáveis para calcular totais
        count = len(self.clientes)  # Número de clientes conectados
        for cliente in self.clientes:  # Itera sobre os clientes conectados
            dados = cliente.dados  # Obtém os dados do cliente
            total_cores += dados.get("cores", 0)  # Soma o número de núcleos de CPU
            total_ram_total += dados.get("ram_total", 0)  # Soma a memória RAM total
            total_ram_livre += dados.get("ram_livre", 0)  # Soma a memória RAM livre
            total_disco_total += dados.get("disco_total", 0)  # Soma o espaço total no disco
            total_disco_livre += dados.get("disco_livre", 0)  # Soma o espaço livre no disco
            total_temp += dados.get("temperatura", 0)  # Soma a temperatura do processador
        # Exibe as médias calculadas
        print("Médias:")
        print(f"- Cores: {total_cores / count:.2f}")
        print(f"- RAM Total: {total_ram_total / count:.2f} GB")
        print(f"- RAM Livre: {total_ram_livre / count:.2f} GB")
        print(f"- Disco Total: {total_disco_total / count:.2f} GB")
        print(f"- Disco Livre: {total_disco_livre / count:.2f} GB")
        print(f"- Temperatura: {total_temp / count:.2f} °C")

    # Método para criptografar dados
    def criptografar(self, dados):
        return self.cipher_suite.encrypt(str(dados).encode())  # Converte os dados em string, codifica em bytes e criptografa

    # Método para descriptografar dados
    def descriptografar(self, dados_criptografados):
        return eval(self.cipher_suite.decrypt(dados_criptografados).decode())  # Descriptografa os dados e converte de volta para dicionário


# Execução principal do programa
if __name__ == "__main__":
    servidor = Servidor()  # Cria uma instância da classe Servidor
    servidor.iniciar()  # Inicia o servidor