import os 
import boto3
import dotenv
from sqlalchemy import func, select, text
from sqlalchemy.engine import create_engine
from llama_index import SQLDatabase,service_context
from llama_index.indices.struct_store import NLSQLTableQueryEngine
from llama_index.llms import OpenAI

dotenv.load_dotenv()

AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
AWS_REGION = os.environ['AWS_REGION']
S3_STAGING_DIR = os.environ['S3_STAGING_DIR']
DATABASE = os.environ['DATABASE']
WORKGROUP = os.environ['WORKGROUP']
TABLE = os.environ['TABLE']
boto3.client(
    'athena',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)
llm = OpenAI(model="gpt-4",temperature=1, max_tokens=1024)

conn_str = "awsathena+rest://:@athena.{region_name}.amazonaws.com:443/"\
           "{database}?s3_staging_dir={s3_staging_dir}?work_group={workgroup}"
engine = create_engine(conn_str.format(
    region_name=AWS_REGION,
    schema_name="default",
    s3_staging_dir=S3_STAGING_DIR,
    database=DATABASE,
    workgroup=WORKGROUP
))

service_context = ServiceContext.from_defaults(
  llm=llm
)

sql_database = SQLDatabase(engine, include_tables=[TABLE])

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=[TABLE],
    service_context=service_context
)
query_str = (
    "Which blocknumber has the most transactions?"
)
response = query_engine.query(query_str)

print(response.metadata['sql_query'])
print(response.metadata)
print(response)