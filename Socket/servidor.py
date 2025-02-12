import socket
import ssl

def iniciarServidor(ip, porta):

    try:
         # Cria o socket TCP
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")  # Certificado e chave privada

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.bind((ip, porta))  # Associa o socket ao IP e porta
            servidor.listen(1)          # Aguarda conexões
            print(f"Servidor aguardando conexão em {ip}:{porta}...")

            with context.wrap_socket(servidor, server_side=True) as tls_servidor:
                conexao, endereco = tls_servidor.accept()  # Aceita a conexão

                with conexao:
                    print(f"Conexão estabelecida com {endereco}")
                    dados = conexao.recv(4096).decode('utf-8')  # Recebe os dados
                    print("Informações recebidas:\n")
                    print(dados)

    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")

# Configuração do servidor
SERVIDOR_IP = "10.0.0.102"  # Escuta em todas as interfaces de rede
PORTA = 5000            # Porta usada para comunicação

if __name__ == "__main__":
    iniciarServidor(SERVIDOR_IP, PORTA)