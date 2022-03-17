"""
Load airports file onto BigQuery. Includes Helper functions
to drop/create BigQuery table
"""

from time import perf_counter
import pandas as pd
from google.cloud import bigquery

from utils import logger


def load_from_file(file_path:str) -> pd.DataFrame:
    """
    load airports file using pandas. Can use gcs path like:
        gs://my-bucket-name/deb-airports.csv
    
    To load files from GCS you MUST install gcsfs pypi package. Please
    look at the requirements.txt

    """
    logger.info(f"loading airports data file from: {file_path}")
    # read the airports file
    df = pd.read_csv(file_path, header=0)
    # bugfix: rename longitude column from `long` to `lng`
    if 'long' in df.columns:
        df = df.rename(columns={'long': 'lng'})
    return df


def load_bigquery_table(data: pd.DataFrame, table_name:str) -> int:
    # make sure data is a valid pandas DataFrame
    assert isinstance(data, pd.DataFrame) and len(data.index), "data must be a valid DataFrame and include records!"
    # setup bigquery client
    client = bigquery.Client()
    table = bigquery.Table(table_name)
    # provide a table schema that's used to create bigquery table
    schema = [
            bigquery.SchemaField('iata', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('name', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('city', 'STRING', mode='NULLABLE'),
            bigquery.SchemaField('state', 'STRING', mode='NULLABLE'),
            bigquery.SchemaField('country', 'STRING', mode='NULLABLE'),
            bigquery.SchemaField('lat', 'FLOAT', mode='NULLABLE'),
            bigquery.SchemaField('lng', 'FLOAT', mode='NULLABLE'),
            bigquery.SchemaField('dst', 'STRING', mode='NULLABLE'),
            bigquery.SchemaField('tz', 'STRING', mode='NULLABLE'),
            bigquery.SchemaField('utc_offset', 'FLOAT', mode='NULLABLE'),
            ]
    # bigquery job config to set various load configuration
    jc = bigquery.LoadJobConfig(
        source_format='PARQUET',
        write_disposition='WRITE_APPEND',
        create_disposition='CREATE_IF_NEEDED',
        autodetect=False,
        schema=schema,
    )
    logger.info("preparing to write {} records to bigquery {} table...".format(len(data.index), table_name))
    t0 = perf_counter()
    # use load from dataframe client method
    job = client.load_table_from_dataframe(data, destination=table, job_config=jc)
    job.result()

    # print logs
    t = perf_counter() - t0
    logger.info("write completed")
    table = client.get_table(table_name)
    logger.info("loaded {} records in {:0.3f} seconds. {} rows/sec".format(len(data.index), t, round(len(data) / t, 0)))
    logger.info("bigquery table {} has {} rows".format(table.full_table_id, table.num_rows))

    return table.num_rows
