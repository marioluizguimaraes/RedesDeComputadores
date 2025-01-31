const net = require('net')
const dgram = require('dgram')
const crypto = require('crypto')

const SERVER_PORT = 4000
const BROADCAST_PORT = 5000
const CLIENTS = new Map()


const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
})


const udpServer = dgram.createSocket('udp4')

udpServer.on('listening', () => {
    udpServer.setBroadcast(true)
    console.log(`Servidor UDP pronto para broadcast na porta ${BROADCAST_PORT}`)
})


setInterval(() => {
    const message = JSON.stringify({ serverIp: getLocalIp(), serverPort: SERVER_PORT, publicKey })
    udpServer.send(message, BROADCAST_PORT, `${getLocalIp()}`, (err) => {
        if (err) console.error('Erro ao enviar broadcast:', err.message)
    })
}, 5000)


const tcpServer = net.createServer((socket) => {
    console.log(`Cliente conectado: ${socket.remoteAddress}:${socket.remotePort}`)

    // Receber dados do cliente
    socket.on('data', (encryptedData) => {
        try {
            
            const decryptedData = crypto.privateDecrypt(privateKey, encryptedData).toString('utf-8')
            const clientInfo = JSON.parse(decryptedData)

            
            CLIENTS.set(socket, clientInfo)

            console.log('Dados recebidos:', clientInfo)
        } catch (error) {
            console.error('Erro ao processar dados:', error.message)
        }
    })

    socket.on('close', () => {
        CLIENTS.delete(socket)
        console.log('Cliente desconectado')
    })
})

tcpServer.listen(SERVER_PORT, () => {
    console.log(`Servidor TCP rodando na porta ${SERVER_PORT}`)
})

function getLocalIp() {
    const interfaces = require('os').networkInterfaces()
    for (const name in interfaces) {
        for (const net of interfaces[name]) {
            if (net.family === 'IPv4' && !net.internal) {
                return net.address
            }
        }
    }
}
