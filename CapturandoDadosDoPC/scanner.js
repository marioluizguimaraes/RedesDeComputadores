const os = require('os')
const si = require('systeminformation')

const getIP = () => {
    const interfaces = os.networkInterfaces()
    for (const name in interfaces) {
        for (const net of interfaces[name]) {
            if (net.family === 'IPv4' && !net.internal) {
                return net.address
            }
        }
    }
    return 'Não disponível'
}

const getSystemInfo = async () => {
    try {
        const userInfo = os.userInfo()
        const tempCPU = await si.cpuTemperature()
        const mem = os.totalmem()
        const freeMem = os.freemem()
        const disk = await si.fsSize()

        const systemInfo = {
            usuario: userInfo.username,
            enderessoIP: getIP(),
            processadores: os.cpus().length,
            tempCPU: tempCPU.main ? `${tempCPU.main} °C` : 'Não disponível',
            memoriaTotal: (mem / (1024 ** 3)).toFixed(2) + ' GB',
            memoriaLivre: (freeMem / (1024 ** 3)).toFixed(2) + ' GB',
            armazenamentoTotal: (disk[0].size / (1024 ** 3)).toFixed(2) + ' GB',
            armazenamentoLivre: (disk[0].available / (1024 ** 3)).toFixed(2) + ' GB'
        }

        console.log(systemInfo)

    } catch (error) {
        console.error('❌ Erro ao obter dados:', error.message)
    }
}

setInterval(getSystemInfo, 10000) // Intervalo de 10s
console.log('📌 Monitoramento iniciado. Enviando dados a cada 10 segundos...')
