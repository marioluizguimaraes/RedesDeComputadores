const net = require('net')
const dgram = require('dgram')
const os = require('os')
const si = require('systeminformation')
const crypto = require('crypto')

const BROADCAST_PORT = 5000
let SERVER_IP = null
let SERVER_PORT = null
let PUBLIC_KEY = null

const udpClient = dgram.createSocket('udp4')

udpClient.on('message', (msg, rinfo) => {
    try {
        const data = JSON.parse(msg.toString())
        SERVER_IP = data.serverIp
        SERVER_PORT = data.serverPort
        PUBLIC_KEY = data.publicKey

        console.log(`Servidor encontrado: ${SERVER_IP}:${SERVER_PORT}`)
        connectToServer()
    } catch (error) {
        console.error('Erro ao processar broadcast:', error.message)
    }
})

udpClient.bind(BROADCAST_PORT, () => {
    console.log(`Aguardando broadcast na porta ${BROADCAST_PORT}...`)
})

const connectToServer = () => {
    if (!SERVER_IP || !SERVER_PORT) return

    const client = new net.Socket()
    client.connect(SERVER_PORT, SERVER_IP, async () => {
        console.log('Conectado ao servidor')

        const systemInfo = await getSystemInfo()

        const encryptedData = crypto.publicEncrypt(PUBLIC_KEY, Buffer.from(JSON.stringify(systemInfo)))

        client.write(encryptedData)
    })

    client.on('close', () => {
        console.log('Conexão encerrada')
    })
}

const getSystemInfo = async () => {

    const userInfo = os.userInfo()
    const tempCPU = await si.cpuTemperature()
    const mem = os.totalmem()
    const freeMem = os.freemem()

    return {
        usuario: userInfo.username,
        endereçoIP: getIPv4(),
        processadores: os.cpus().length,
        tempCPU: tempCPU.main ? `${tempCPU.main} °C` : 'Não disponível',
        memoriaTotal: (mem / (1024 ** 3)).toFixed(2) + ' GB',
        memoriaLivre: (freeMem / (1024 ** 3)).toFixed(2) + ' GB'
    }
}

const getIPv4 = () =>{
    const interfaces = os.networkInterfaces()
    for (const name in interfaces) {
        for (const net of interfaces[name]) {
            if (net.family === 'IPv4' && !net.internal) {
                return net.address
            }
        }
    }
}