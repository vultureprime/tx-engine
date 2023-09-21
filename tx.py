from web3 import Web3, AsyncWeb3
import json
import pandas as pd
import pyarrow as pa
import time

RPC_URL = 'https://rpc.ankr.com/optimism'
web3 = Web3(Web3.HTTPProvider(RPC_URL))
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
    start_block = start_block
    end_block = end_block
    step = 1000
    current_block = start_block
    result = []
    while current_block <= end_block:
        start = current_block
        end = current_block + step
        idx = start // 10000
        if end // 10000 > start // 10000:
            end = ((end // 10000)*10000) - 1
            result = result + run(start,end,idx)
            df = pd.json_normalize(result)
            df.to_parquet(s3_bucket , compression='snappy', index=False, partition_cols='partitionIdx', schema=schema)
            result = []
        elif end >= end_block:
            end = end_block
            result = result + run(start,end,idx)
            df = pd.json_normalize(result)
            df.to_parquet(s3_bucket , compression='snappy', index=False, partition_cols='partitionIdx' ,schema=schema)
        else :
            result = result + run(start,end,idx)
        current_block = end + 1
    df = pd.json_normalize(result)
    df.to_parquet(s3_bucket , compression='snappy', index=False, partition_cols=[ 'partitionIdx','blockNumber'])

def near_realime():
    start_block = 109840567
    result = []
    idx_size = 1000
    step_size = 500
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
            df = pd.json_normalize(result)
            df.to_parquet(s3_bucket , compression='snappy', index=False, partition_cols='partitionIdx' ,schema=schema)
            result = []
        else:
            print(start_block,end_block)
            result = result + run(start_block,end_block,idx)
            time.sleep(30)
        start_block = end_block + 1

def get_latest_block():
    latest = web3.eth.get_block('latest')['number']
    print(latest)
if web3.is_connected():
    s3_bucket = 's3://vultureprime-tx-engine/'
    # get_latest_block()
    # batch_job(0,1200)
    near_realime()
    # a= run(20000,20000,2)
    # print(a)