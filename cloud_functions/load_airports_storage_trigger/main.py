# local imports
from utils import logger, config
from utils.airports_processor import load_from_file, load_bigquery_table


def dsadeb_airports_loader_storage_trigger(event, context):

    try:
        # lets print some logs regarding our trigger
        logger.info(f"Event ID: {context.event_id}, Event Type: '{context.event_type}'")

        # get the event information including bucket and files name
        bucket = event['bucket']
        filename = event['name']
        metadata = event['metageneration']
        created_time = event['timeCreated']
        logger.info(f"bucket: '{bucket}', file: '{filename}' created: {str(created_time)}")
        
        # setup the config params
        airport_filepath = f"gs://{bucket}/{filename}"
        # load the airports file into dataframe
        df = load_from_file(airport_filepath)

        # get bigquery table configuration (from config.yml)
        project = config['gcp_project']
        dataset = config['bigquery_dataset']
        table_name = config['bigquery_table']
        bigquery_tablename = f"{project}.{dataset}.{table_name}"
        # load the dataframe into bigquery
        load_bigquery_table(df, bigquery_tablename)

        # print success
        logger.info("function completed successfully")

    except Exception as err:
        # print the error message to logs
        logger.error(str(err))
