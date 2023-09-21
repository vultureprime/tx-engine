from web3 import Web3, AsyncWeb3
import json
import pandas as pd
import pyarrow as pa
import time

def run(fromBlock,toBlock,idx):
    cleaned_data = []
    response = web3.eth.get_logs({
            "fromBlock": fromBlock,
            "toBlock": toBlock,
        })
    logs = json.loads(Web3.to_json(response))
    for log in logs:
        cleaned_data.append({
            "blockNumber": log['blockNumber'],
            "index": log['logIndex'],
            "address": log['address'],
            "data": log['data'],
            "blockHash": log['blockHash'],
            "transactionHash": log['transactionHash'],
            "topics": log['topics'],
            "transactionIndex": log['transactionIndex'],
            "removed": log['removed'],
            "partitionIdx" : idx
        })
    return cleaned_data 

def batch_job(start_block,end_block):
    start_block = start_block
    end_block = end_block
    index_size = 10000
    step = 1000
    current_block = start_block
    result = []
    while current_block <= end_block:
        start = current_block
        end = current_block + step
        idx = start // index_size
        if end // index_size > start // index_size:
            end = ((end // index_size)*index_size) - 1
            result = result + run(start,end,idx)
            save_to_s3(result,s3_bucket)
            result = []
        elif end >= end_block:
            end = end_block
            result = result + run(start,end,idx)
            save_to_s3(result,s3_bucket)
        else :
            result = result + run(start,end,idx)
        current_block = end + 1
    save_to_s3(result,s3_bucket)

def near_realime(start_block):
    start_block = start_block
    result = []
    idx_size = 1000
    step_size = 500    
    while True:
        end_block = web3.eth.get_block('latest')['number']
        idx = start_block // idx_size
        if end_block - start_block > idx_size:
            end_block = start_block + step_size
            # print(start_block,end_block , "Next")
            # result = result + run(start_block,end_block,idx)
        if end_block // idx_size > start_block // idx_size:
            end_block = ((end_block // idx_size)*idx_size) - 1
            print(start_block,end_block , "AND Save")
            result = result + run(start_block,end_block,idx)
            save_to_s3(result,s3_bucket)
            result = []
        else:
            print(start_block,end_block)
            result = result + run(start_block,end_block,idx)
            time.sleep(30)
        start_block = end_block + 1

def get_latest_block():
    latest = web3.eth.get_block('latest')['number']
    print(latest)
    return latest
    
def save_to_s3(data,bucket):
    schema = pa.schema([
            ('blockNumber', pa.int32()),
            ('index', pa.int32()),
            ('address', pa.string()),
            ('data', pa.string()),
            ('blockHash', pa.string()),
            ('topics', pa.list_(pa.string())),
            ('transactionIndex', pa.int32()),
            ('removed', pa.bool_()),
            ('partitionIdx', pa.int32())
        ])
    df = pd.json_normalize(data)
    df.to_parquet(bucket , compression='snappy', index=False, partition_cols='partitionIdx', schema=schema)

if "__name__" == "__main__":
    RPC_URL = 'https://rpc.ankr.com/optimism'
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    job = 'batch'
    if web3.is_connected():
        s3_bucket = 's3://vultureprime-tx-engine/'
        if job == 'batch':
            batch_job(0,1200)
        elif job == 'realtime':
            near_realime(109840567)
        else:
            print("invalid")
    else:
        print("Connection is not good")
