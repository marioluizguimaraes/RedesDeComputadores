// Importa módulos necessários
const net = require('net') // Comunicação via TCP
const dgram = require('dgram') // Comunicação via UDP (broadcast)
const os = require('os') // Informações do sistema operacional
const si = require('systeminformation') // Informações detalhadas do hardware

// Porta onde o para escutar o broadcast
const BROADCAST_PORT = 5000

// Dados do servidor
let SERVER_IP = null
let SERVER_PORT = null

// Socket UDP pra achar o servidor
const udpClient = dgram.createSocket('udp4')

// Coleta de informações do PC
const getSystemInfo = async () => {
    const userInfo = os.userInfo() // Usuário logado
    const tempCPU = await si.cpuTemperature() // Temperatura da CPU
    const mem = os.totalmem() // Quantidade total de memória RAM
    const freeMem = os.freemem() // Quantidade de memória RAM livre
    const ip = getIP() // Endereço IP local da máquina

    // Retorna um objeto com as informações do sistema
    return {
        usuario: userInfo.username,
        ip,
        processadores: os.cpus().length,
        tempCPU: tempCPU.main ? `${tempCPU.main} °C` : 'Não disponível',
        memoriaTotal: (mem / (1024 ** 3)).toFixed(2) + ' GB', // Converte bytes para GB
        memoriaLivre: (freeMem / (1024 ** 3)).toFixed(2) + ' GB' // Converte bytes para GB
    }
}

// Escuta mensagens de broadcast
udpClient.bind(BROADCAST_PORT, () => {
    console.log(`Aguardando broadcast na porta ${BROADCAST_PORT}...`)
})

udpClient.on('message', (msg, rinfo) => {
    try {
        // Converte a mensagem recebida para um objeto JSON
        const data = JSON.parse(msg.toString())

        // Obtém o IP e a porta do servidor 
        SERVER_IP = data.serverIp
        SERVER_PORT = data.serverPort

        console.log(`Servidor encontrado: ${SERVER_IP}:${SERVER_PORT}`)

        // Conecta via TCP
        conectarServidor()

    } catch (error) {
        console.error('Erro ao processar broadcast:', error.message)
    }
})


// Conecta ao servidor via TCP
const conectarServidor = () => {
    // Verifica sinal de um servido
    if (!SERVER_IP || !SERVER_PORT) return

    // Cria um socket TCP
    const tcpClient = new net.Socket()

    // Conecta ao servidor usando IP e porta
    tcpClient.connect(SERVER_PORT, SERVER_IP, async () => {
       
        // Obtém as informações do sistema
        const systemInfo = await getSystemInfo()

        // Envia as informações para o servidor em formato JSON
        tcpClient.write(JSON.stringify(systemInfo))
        console.log('Dados enviados com sucesso!')
    })
}

// Função para obter o endereço IPv4 da máquina
const getIP = () => {
    // Obtém todas as interfaces de rede
    const interfaces = require('os').networkInterfaces()

    // Percorre todas as interfaces de rede
    for (const name in interfaces) {
        for (const net of interfaces[name]) {
            if (net.family === 'IPv4' && !net.internal) {
                return net.address
            }
        }
    }
}