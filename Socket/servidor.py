import socket

def iniciarServidor(ip, porta):

    try:
        # Cria o socket TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.bind((ip, porta))  # Associa o socket ao IP e porta
            servidor.listen(1)          # Aguarda conexões
            print(f"Servidor aguardando conexão em {ip}:{porta}...")

            conexao, endereco = servidor.accept()  # Aceita a conexão
            with conexao:
                print(f"Conexão estabelecida com {endereco}")
                dados = conexao.recv(4096).decode('utf-8')  # Recebe os dados
                print("Informações recebidas:\n")
                print(dados)

    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")

# Configuração do servidor
SERVIDOR_IP = "0.0.0.0"  # Escuta em todas as interfaces de rede
PORTA = 5000            # Porta usada para comunicação

if __name__ == "__main__":
    iniciarServidor(SERVIDOR_IP, PORTA)