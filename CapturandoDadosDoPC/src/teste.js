const { error } = require('console');
const net = require('net');
const si = require('systeminformation');

const client = new net.Socket();

client.connect(3000, '255.255.255.255', async () => {
    console.log('Conectado ao servidor');
    try{
        const memInfo = await si.mem();
        const diskInfo = await si.fsSize();
        const tempInfo = await si.cpuTemperature();
        const cpuInfo = await si.cpu();

        const disk1 = diskInfo[0]; // Pega a informação do primeiro disco - Geralmente o disco C.

        client.write(`Mémoria RAM livre: ${memInfo.free}`);
        client.write(`Espaço em disco livre: ${disk1.available}\n`);
        client.write(`Temperatura:  ${tempInfo.main}\n`); 
        client.write(`Cores:  ${cpuInfo.cores}`); 

    } catch {
        console.error('Erro ao obter informações de memória: ', error);
    } finally{
        console.log("Dados enviados com sucesso!");
        client.end();
    }
    
    client.end();
});