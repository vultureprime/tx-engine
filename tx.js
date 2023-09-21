import { ethers } from "ethers";
import { Network, Alchemy } from 'alchemy-sdk';
import parquet from 'parquetjs';


const settings = {
    apiKey: "s6F6Z7zwIOKKKJGeLeThRW0v6evvlTM-",
    network: Network.OPT_MAINNET,
};


const RPC_URL = 'https://rpc.ankr.com/optimism'
const provider = new ethers.JsonRpcProvider(RPC_URL);
let cleanedData = []


const run = async (startBlock, latestBlock, index) => {
    let data = await provider.getLogs({
        "fromBlock": startBlock,
        "toBlock": latestBlock,
    })


    let partitionKey = Math.ceil(index / 50)
    if (partitionKey == 0) {
        partitionKey = 1
    }
    data.map((o) => {
        cleanedData.push({
            address: o['address'],
            data: o['data'],
            blockHash: o['blockHash'],
            blockNumber: o['blockNumber'],
            transactionHash: o['transactionHash'],
            topics: o['topics'],
            index: o['index'],
            transactionIndex: o['transactionIndex'],
            removed: o['removed'],
            partitionByBlock: partitionKey,
        })
    })


    var schema = new parquet.ParquetSchema({
        blockNumber: { type: 'INT32' },
        blockHash: { type: 'UTF8' },
        transactionIndex: { type: 'INT32' },
        removed: { type: 'BOOLEAN' },
        address: { type: 'UTF8' },
        data: { type: 'UTF8' },
        topics: { type: 'UTF8', repeated: true },
        transactionHash: { type: 'UTF8' },
        index: { type: 'INT32' },
        partitionByBlock: { type: 'INT32' }
    });
    if ((index % 50 == 0) && (index != 0)) {
        let writer = await parquet.ParquetWriter.openFile(schema, `/media/maatick/Mui_database1/oplogs/op_logs_${latestBlock}.parquet`)
        // let writer = await parquet.ParquetWriter.openFile(schema, `./${BRIDGENAME}_${BRIDFGETOKEN}_${latestBlock}.parquet`)
        for (let i = 0; i < cleanedData.length; i++) {
            await writer.appendRow(cleanedData[i])
        }
        console.log(startBlock, cleanedData.length, `write at ${index}`)
        await writer.close()
        cleanedData = []
    }
    else {
        console.log(startBlock, cleanedData.length, index)
    }
}
// 107800000
for (let i = 47501; i < 53901; i++) {
    let intialBlock = 0
    let startBlock = intialBlock + (500 * i)
    let end = startBlock + 500
    if (startBlock < 0) {
        startBlock = 0
    }
    await run(startBlock, end, i)
}
