# TxEngine - Dune Analytics Alternative.
[![Github All Releases](https://img.shields.io/github/downloads/vultureprime/tx-engine/total.svg)]()

TxEngine is an open-source Data Pipeline Framework designed for blockchain analytics, similar to Dune Analytics.  

Our primary goal is to assist individuals who desire to create an On-chain data pipeline. We make the setup a manageable task, even for those lacking extensive data engineer expertise.  

With our solution, you gain complete ownership - over your infrastructure, your query engine, and your data results.  

As a result, it brings ease, control, and efficiency to managing your blockchain data. 

Utilize TxEngine and take advantage of a comprehensive solution that simplifies your approach to blockchain analytics.

- Gitbook : [Home](https://txengine.gitbook.io/home/)
- Quickstart : [Quickstart](https://txengine.gitbook.io/home/get-started/quickstart)
- Feature : [Feature](https://txengine.gitbook.io/home/feature/)

## Installation
```
git clone https://github.com/vultureprime/tx-engine.git && cd tx-engine && python3 install -r requirements.txt
```

## Usage
This package offers three methods for getting blockchain data: Batching, Near Realtime, and Validation.

#### Config
![Config_tx_engine.png](https://vultureprime-research-center.s3.ap-southeast-1.amazonaws.com/Config_tx_engine.png)

You need to edit your config key 3 component in tx-engine.py.
1. Access key
2. Secret key
3. Bucket name

#### How to run
```
python3 tx-engine.py
```

## Setup resource with Terraform
#### Prerequisite 
- [Terraform](https://developer.hashicorp.com/terraform/downloads?product_intent=terraform) >= 1.57
#### Terraform config
![](https://vultureprime-research-center.s3.ap-southeast-1.amazonaws.com/tx-enine-terraform.png)

You need to edit your config 5 component in TxEngineTerraform.tf
1. bucket_raw 
2. bucket_result
3. glue_database
4. glue_crawler
5. athena_workgroup


After you complete terraform file.

Run this script.
```
export AWS_ACCESS_KEY_ID= {Access key}
export AWS_SECRET_ACCESS_KEY= {Secret key}
cd aws-setup && terraform init && terraform apply 
```

**IT NOT FINISH YET, YOU NEED TO RUN CRAWLER WITH YOURSELF VIA UI**

- Visit glue crawler under Data Catalog 
- Click Crawler name {glue_crawler}
- Click Run crawler 

![](https://uploads-ssl.webflow.com/63cb6b155c56b2dcd14e411d/65179fd846135bc56a4f817a_10.png)


#### Congrats 🎉🎉 
You already have your data platform. Feel free to query your data.

## Manual setup
- [End-to-End TxEngine to Quicksight](https://www.vultureprime.com/how-to/how-to-monitor-erc-20-transfer-event) - Thai Language

## How it work
TxEngine leverage on AWS service such as AWS S3, AWS Glue, AWS Athena and AWS Quicksight.

![](https://vultureprime-research-center.s3.ap-southeast-1.amazonaws.com/txengine-how-it-work.png)

## How do they charge 
You will charge base on aws service.

- S3 $0.023 per GB
- Glue $0.44 per hours (charge only run crawler)
- Athena $5 per 1TB data scan
- Quicksight $9 per month

Example.
Optimism logs data from genesis block to present (Block number 110144079) have size around 200GB. 
When you query the across all data will charge $1, But if you select only attribute like a "topics,data" your will got charge at $0.5. That's pretty awesome.

## Schema
For data exported into .parquet files using Batching and Near Realtime, the schema is as follows:


Default data format
```
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
```
## License
MIT

## Contributor
VulturePrime

If you are interested in our product and want to learn more, visit my x (twitter): https://twitter.com/txengine
