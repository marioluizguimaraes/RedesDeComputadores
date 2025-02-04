const net = require('net') // Comunicação via TCP
const dgram = require('dgram') // Comunicação via UDP (broadcast)

// Portas para os servidores
const SERVER_PORT = 4000 // Porta usada para o servidor TCP
const BROADCAST_PORT = 5000 // Porta usada para o envio de broadcast UDP

// Map para armazenar os clientes conectados e seus dados
const CLIENTS = new Map()

// Servidor UDP
const udpServer = dgram.createSocket('udp4')

//  Começa a escutar na porta:
udpServer.on('listening', () => {
    udpServer.setBroadcast(true) // Permite envio de pacotes para toda a rede
    console.log(`Servidor UDP pronto para broadcast na porta ${BROADCAST_PORT}`)
})

// Envia o broadcast UDP a cada 5 segundos
setInterval(() => {
    console.log('Enviando')
    // Monta um JSON com o IP e a porta do servidor TCP
    const message = JSON.stringify({ 
        serverIp: getIp(), 
        serverPort: SERVER_PORT 
    })

    // Envia a mensagem para a porta de broadcast
    udpServer.send(message, BROADCAST_PORT, (err) => {
        if (err) console.error('Erro ao enviar broadcast:', err.message)
    })
}, 10000) // Repetição a cada tempo

// Criação do servidor TCP
const tcpServer = net.createServer((socket) => {
    // Quando um cliente se conecta, exibe seu IP e porta
    console.log(`Cliente conectado: ${socket.remoteAddress}`)

    // Evento acionado quando o servidor recebe dados do cliente
    socket.on('data', (data) => {
        try {
            // Converte os dados recebidos de JSON para objeto
            const clientInfo = JSON.parse(data.toString('utf-8'))

            // Armazena as informações do cliente no Map
            CLIENTS.set(socket, clientInfo)

            console.log('Dados recebidos:', clientInfo)
        } catch (error) {
            console.error('Erro ao processar dados:', error.message)
        }
    })

    // Evento acionado quando um cliente se desconecta
    socket.on('close', () => {
        CLIENTS.delete(socket) // Remove o cliente do Map
        console.log('Cliente desconectado')
    })
})

// Servidor TCP começa a escutar na porta definida
tcpServer.listen(SERVER_PORT, () => {
    console.log(`Servidor TCP rodando na porta ${SERVER_PORT}`)
})

// Função para obter o endereço IP local da máquina
function getIp() {
    // Obtém todas as interfaces de rede disponíveis
    const interfaces = require('os').networkInterfaces()

    // Percorre todas as interfaces para encontrar o IPv4 da máquina
    for (const name in interfaces) {
        for (const net of interfaces[name]) {
            if (net.family === 'IPv4' && !net.internal) { 
                return net.address
            }
        }
    }
}
