import psutil 
import requests
import socket
import ssl

def getIpPublico():
    try:
        resposta = requests.get("https://api.ipify.org")
        resposta.raise_for_status()
        return resposta.text
    
    except Exception as e:
        return f"Erro ao obter o IP público: {e}"

def getIpLocal():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_local = s.getsockname()[0]
        return ip_local
    
    except Exception as e:
        return f"Erro ao obter o IP local: {e}"

def getQuantidadeCoresProcessador():
    try:
        # Retorna o número de núcleos físicos e lógicos
        nucleos_fisicos = psutil.cpu_count(logical=False)
        nucleos_logicos = psutil.cpu_count(logical=True)
        return nucleos_fisicos, nucleos_logicos
    
    except Exception as e:
        return f"Erro ao obter a quantidade de núcleos do processador: {e}"

def getMemoriaRam():
    try:
        memoria = psutil.virtual_memory()
        total = round(memoria.total / (1024 ** 3), 2)  # Converte bytes para GB
        livre = round(memoria.available / (1024 ** 3), 2)  # Converte bytes para GB
        return total, livre
    
    except Exception as e:
        return f"Erro ao obter informações de memória RAM: {e}"

def getEspacoDisco():
    try:
        disco = psutil.disk_usage('/')
        total = round(disco.total / (1024 ** 3), 2)  # Converte bytes para GB
        livre = round(disco.free / (1024 ** 3), 2)  # Converte bytes para GB
        return total, livre
    
    except Exception as e:
        return f"Erro ao obter informações de espaço em disco: {e}"


def enviarInfo(servidor_ip, porta):
    """
    Envia as informações do sistema para o servidor via socket TCP.
    """
    try:
        # Coleta as informações do sistema
        ip_publico = getIpPublico()
        ip_local = getIpLocal()
        nucleos_fisicos, nucleos_logicos = getQuantidadeCoresProcessador()
        ram_total, ram_livre = getMemoriaRam()
        disco_total, disco_livre = getEspacoDisco()

        # Formata os dados para envio
        dados = (
            f"IP Público: {ip_publico}\n"
            f"IP Local: {ip_local}\n"
            f"Núcleos Físicos: {nucleos_fisicos}\n"
            f"Núcleos Lógicos: {nucleos_logicos}\n"
            f"Memória RAM Total: {ram_total} GB\n"
            f"Memória RAM Livre: {ram_livre} GB\n"
            f"Espaço em Disco Total: {disco_total} GB\n"
            f"Espaço em Disco Livre: {disco_livre} GB\n"
        )

        # Cria o socket TCP
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations("cert.pem")  # Certificado do servidor

        with socket.create_connection((servidor_ip, porta)) as sock:
            with context.wrap_socket(sock, server_hostname=servidor_ip) as cliente:
                cliente.sendall(dados.encode('utf-8'))  # Envia os dados
                print("Informações enviadas com sucesso!")

    except Exception as e:
        print(f"Erro ao enviar informações via socket: {e}")

# Configuração do servidor
SERVIDOR_IP = "10.0.0.102"  # Substitua pelo IP do servidor
PORTA = 5000              # Porta usada para comunicação

# Chamada das funções e exibição dos resultados
if __name__ == "__main__":
    print(f"IP Público: {getIpPublico()}")
    print(f"IP Local: {getIpLocal()}")

    nucleos_fisicos, nucleos_logicos = getQuantidadeCoresProcessador()
    print(f"Núcleos Físicos do Processador: {nucleos_fisicos}")
    print(f"Núcleos Lógicos do Processador: {nucleos_logicos}")

    ram_total, ram_livre = getMemoriaRam()
    print(f"Memória RAM Total: {ram_total} GB")
    print(f"Memória RAM Livre: {ram_livre} GB")

    disco_total, disco_livre = getEspacoDisco()
    print(f"Espaço em Disco Total: {disco_total} GB")
    print(f"Espaço em Disco Livre: {disco_livre} GB")

    enviarInfo(SERVIDOR_IP, PORTA)
