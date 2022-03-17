
## Introduction to Serverless Computing

What does Serverless Cloud Computing mean?

The term 'serverless' is any architecture that you use Cloud services only based on demand; you run code as needed without 
provisioning dedicated servers or Virtual Machines (VMs) or otherwise managing any infrastructure. With Serverless, your code only runs when there's data to be 
processed (based on some events) and you only get charged for the duration that your code runs.

Traditionally on the Cloud, people provisioned dedicated VMs; the VM ran all the time and you got charged by hour 
regardless of how fully utilized that machine was or how much code you ran on it. Of course, this was left room for improvement
since you had to pay all the time, even when the machine was running idle (for example when there was no activity 
on your website or new data coming into your pipeline). Data Engineers now are widely transforming their pipelines
using Serverless services since they'll pay only for what they use!

There are many benefits to the Serverless architecture that we will explain below.

## Advantages of Serverless Computing

1. **Cost**

    With Serverless services, you only pay for the amount of time your code runs! Since you don't manage any servers,
    you don't have any downtime and you don't pay anything for when resources are idle and there's no activity in your
    pipeline. Furthermore, most serverless resource costs are calculated by milliseconds or microseconds, so you can 
    optimize your code to have minimum runtime.

1. **Ease of development**

    As you'll see later in this episode, Serverless resources are extremely easy to provision since there are no servers
    or VMs to manage. You just write code and don't worry about how it runs on the Cloud; the Cloud service takes care
    of all that for you! Without serverless architecture, you had to provision a VM, upload your code, make sure the VM stays up, 
    provision more VMs if your demand increased, delete your VMs when there was no activity, and so on. Serverless eliminates the need for the developer to do any of these management tasks, saving a lot of work!

1. **Scalability**

    The Cloud takes care of scaling up or down your code based on demand. If there are more events (like REST calls or more 
    files being uploaded) the Cloud automatically provisions more instances of your code to scale up. Scaling down also happens
    automatically.

1. **Real-time / Event-driven**

    Serverless resources are instantiated in real-time based on various Cloud events like a file being uploaded to GCS, or
    a REST request sent to your API, or a message being posted to Pub/Sub. We will explain Cloud Pub/Sub later but for
    now just know that Pub/Sub (Publication/Subscription) is a service where many different programs or services can post messages (or events), which can be read from a queue and processed as they arrive. These messages are things like an IoT device sending your room temperature to the Cloud,
    or your Lyft app posting your current GPS location, or GrubHub posting your order message to be dispatch to
    the restaurant and consequently to a delivery driver, or the Kayak website posting your ticket request message and a 
    background process confirms your flight and sends you a confirmation email. Your code runs every time there's a message 
    in real-time (milliseconds) and you can react to the message. This is how modern apps are responsive in real-time.

## GCP Serverless Services

You have already used many serverless cloud services: 
- BigQuery is serverless, your SQL code runs without you standing
up a database 
- In the docker chapter, you also launched a docker image using GCP Cloud Run
- In the REST chapter, you
launched your flask webserver on GCP AppEngine without actually standing up a webserver

You can see  the full list of [GCP Serverless](https://cloud.google.com/serverless) services. To list a few:

1. **Cloud Functions** for running code that reacts to Cloud events such as Pub/Sub messages or REST web calls.
2. **Cloud Run** for running docker containers.
3. **App Engine** for running web servers or REST servers.
4. **Cloud Workflow** for orchestrating serverless pipelines.

In this chapter we will focus on **[Cloud Functions](https://cloud.google.com/functions)** which are the most widely
used (and easiest) serverless resource.

While the above services are the main "serverless" products listed on GCP, there are many other inherently serverless products
that typically go unmentioned! To name a few:

1. **BigQuery**: runs SQL queries on terabytes of data without managing an database
1. **Google Cloud Storage**: stores and accesses petabytes of files without any servers
1. **Cloud Pub/Sub**: scales up/down to manage millions of events per minute
1. **Cloud Logging**: aggregates all your application logs.

It's worth mentioning that there are pseudo or **semi-serverless** resources like **Google Kubernetes Engine** where docker images
are spun up/down based on need. 

## Serverless Architecture

In general, there are two main types of architecture used when developing Cloud Functions:

1. Stream/Event Processing Architecture: the Cloud Function runs on a single event
1. Micro-Batch Processing Architecture: the Cloud Function runs periodically on a small batch of events

### Stream/Event Processing Architecture

This is where your function responds in real-time to a single Cloud Event. The Cloud Event could be a message uploaded to Cloud Pub/Sub or
a file being uploaded to Google Cloud Storage. This architecture relies on Cloud Functions framework to scale and is beneficial since it
runs in real-time.

### Micro-Batch Processing Architecture

In analytical data processing, most of the time a single event is not enough data to react to. For example, a single GPS
location event in your route to a destination is not enough to change your arrival ETA; but a few minutes of you picking up 
speed getting past a traffic jam is enough to register your speed and correctly updating your ETA. In analytical data 
processing, we often want to wait until there's enough data to process events that could change our prediction. 
This is called *micro-batching*. In the next chapter, you will work on examples of this in detail.

# GCP Cloud Function Types

Google Cloud functions are categorized by the type of the event that triggers them. Google keeps adding [Cloud Events](https://cloud.google.com/functions/docs/calling) that can 
trigger functions; but the main ones are:

1. HTTP Trigger: function is triggered by a HTTP REST/Web call. This is the focus of this episode.
1. Cloud Storage Trigger: function is triggered when a file is uploaded (deleted or modified) on Cloud Storage. You'll see this in episode 2.
1. Cloud Pub/Sub Event Trigger: function is triggered when new messages/events are posted to a Cloud Pub/Sub topic. You'll see this in Chapter 9.

To see the full list of events that can trigger Cloud Functions, run:

```bash
gcloud functions event-types list
```

# Your first Cloud Function

As your first Cloud Function example we're going to create a HTTP triggered function that executes upon HTTP REST requests.

This function uses the pypi `howdoi` package to answer various programming questions. You can ask the function any sort of 
programming question (like: "parse a string as date in python") and the _howdoi_ package will search the web and provide the
most appropriate answer. To get familiar with howdoi package visit their [homepage](https://pypi.org/project/howdoi/). It's
a pretty cool package 😉

A Google Cloud Function is simply a directory that contains python code. The most simple version of a function is a directory
with a `main.py` and a `requirements.txt` file. 

Create a directory called `./cloud_functions/howdoi` and create two files under it for `main.py` and `requirements.txt`. Edit your `main.py` to include the skeleton of you Cloud Function:

```python
from flask import Request


def simple_function(request: Request):
    name = request.args.get("name", "Anonymous")
    return f"hello {name}", 200
```

You can name your function anything you want, here we've called it `howdoi_function`. The function takes a normal flask 
_`Request`_ argument which includes the HTTP request parameters and return the standard flask tuple with your data and the
http response code. You can also add a third tuple element with your http response headers.

Before we improve our function code, let's add our pypi packages to our `requirements.txt` file:

```text
Flask==2.0.1
howdoi==2.0.19
```

Now that you have all the required packages configured, edit your `main.py` to include the following code:

```python
from flask import Request
from datetime import datetime
from howdoi import howdoi


# howdoi module setup not to use SSL, this breaks sometimes!
howdoi.VERIFY_SSL_CERTIFICATE = False
howdoi.SCHEME = 'http://'


def simple_function(request: Request):
    name = request.args.get("name", "Anonymous")
    return f"hello {name}", 200


def howdoi_function(request: Request):
    question = request.args.get('question', None)
    if question is None:
        answer = "You forgot to provide a question!"
    else:
        # use the howdoi lib for an answer
        answer = howdoi.howdoi(question)
    
    # send back response
    response_headers = {
        'content-type': 'text/plain',
        'server-time': str(datetime.now()),
    }
    # the return is a regular flask return tuple: (data, http resp code, headers)
    return answer, 200, response_headers
```

In the function above, you can see that:

- We submit our question to howdoi module and return the response as plain text.
- Cloud function return is a standard flask tuple response as (data, http response code, headers)
- The two lines on top are a workaround for a possible howdoi error. Sometimes this error appears if howdoi is not able to authenticate SSL certificates when searching for answers online.
  
  ```python
  howdoi.VERIFY_SSL_CERTIFICATE = False
  howdoi.SCHEME = 'http://'
  ```

## Test your function locally

Before submitting the Cloud Function to Google, we can test our function locally to ensure that our code runs fine. 

First, install the Cloud Functions framework in a python virtualenv:

```bash
pip install functions-framework
```

Now inside your function directory, run the following command:

```bash
cd cloud_functions/howdoi
functions_framework --target=howdoi_function --port=8080
```

- The `--target` flag sets the name of your function inside `main.py`.
- `--port` flag sets the post where your function will be hosted on localhost.
- Please refer to google docs for more detail on [deploying your function locally](https://cloud.google.com/functions/docs/running/function-frameworks).

Your function is running on port 8080 and is ready to use now. You can test it by using `curl`:

```bash
curl -X POST -d '{"question": "parse a date string in python"}' -H "Content-type: application/json" http://localhost:8080
```

To stop your local function just CTRL+C out of the terminal.

## Deploying your function to Google

Deploying your function to Google Cloud is just as easy as running it locally. You can do so via a single `gcloud` command line. Run the following in your `cloud_functions/howdoi` directory:

```bash
gcloud functions deploy dsa-howdoi-function \
   --entry-point howdoi_function \
   --runtime python37 \
   --trigger-http \
   --allow-unauthenticated
```

The above command has few parameters:

1. The first parameter is the globally unique name for your cloud function. Make sure to include something unique (like your name) to make the function globally unique. For example: `dsa-johndoe-howdoi-function`.
1. The `--entry-point` flag is simply the name of your function inside `main.py`.
1. `--trigger-http` flag lets Cloud Function know to trigger your function upon HTTP request calls.
1. `--allow-unauthenticated` flag disables any http security on your function and enables the function to be called anonymously. Alternatively, you can peek at google docs for [securing] your function authentication tokens.
1. Please refer to [google docs](https://cloud.google.com/functions/docs/deploying/filesystem) for more detail on deploying your function.

Deploying your function takes a few minutes... After it's completed, you should see a message like:

```text
Deploying function (may take a while - up to 2 minutes)...done.
availableMemoryMb: 256
buildId: 817abb34-0be0-4eb1-a535-e7b29315f31d
buildName: projects/88141792430/locations/us-central1/builds/817abb34-0be0-4eb1-a535-e7b29315f31d
entryPoint: howdoi_function
httpsTrigger:
  securityLevel: SECURE_OPTIONAL
  url: https://us-central1-deb-01.cloudfunctions.net/dsa-howdoi-function
ingressSettings: ALLOW_ALL
labels:
  deployment-tool: cli-gcloud
name: projects/deb-01/locations/us-central1/functions/dsa-howdoi-function
runtime: python37
serviceAccountEmail: deb-01@appspot.gserviceaccount.com
sourceUploadUrl: https://storage.googleapis.com/gcf-upload-us-central1-0ebb2a32-c9d6-48a0-a4cc-d0f80ea7b62a/87febfda-a9b7-4364-b607-b964f29f6061.zip
status: ACTIVE
timeout: 60s
updateTime: '2021-09-17T23:43:58.672Z'
versionId: '1'
```

You can use the return URL to test your function via either Postman or curl or `gcloud` command line:

Using glcoud:

```bash
gcloud functions call dsa-howdoi-function --data '{"question": "iterate through list comprehension in python"}'
```

Using curl:
```bash
curl -X POST -d '{"question": "iterate through list comprehension in python"}' -H "Content-type: application/json" https://us-central1-deb-01.cloudfunctions.net/dsa-howdoi-function
```

Or Postman:

![postman example](imgs/postman_02.png)


## Adding Local Packages

Local packages in Cloud Functions work just as regular python packages; create a python package subdirectory including `__init__.py` 
and add you python modules under it. Let's create our regular `utils` package and add python logging:

Create a directory called `utils` and add an `__init__.py` file containing:

```python
import logging
import sys

# setup logging and logger
logging.basicConfig(format='[%(levelname)-5s][%(asctime)s][%(module)s:%(lineno)04d] : %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)
logger: logging.Logger = logging
```

Now, add an import statement to your `main.py` to import the logger and use it:

```python
# local package imports
from utils import logger

...

logger.info(f"new question: '{question}'")
```

Re-deploy your Cloud Functions and use `gcloud` command line to view the logs for your function:

```bash
# deploy the cloud function
gcloud functions deploy dsa-howdoi-function --entry-point howdoi_function --runtime python37 --trigger-http --allow-unauthenticated

# list your function logs
gcloud functions logs read dsa-howdoi-function
```

**NOTE:** `gcloud functions deploy` deploys all your local files onto the cloud. This includes any subdirectories and files under your cloud function directory. To ignore files you can add a `.gcloudignore` file in the same syntax as `.gitignore` to exclude things that you don't want to be uploaded.

```



# Storage Triggered Function

## Overview

From the [Cloud Functions documentation](https://cloud.google.com/functions/docs):

> Google Cloud Functions is a lightweight, event-based, asynchronous compute solution that allows you to create small, single-purpose 
> functions that respond to cloud events without the need to manage a server or a runtime environment.


Cloud Functions are the easy to execute code on various Cloud. This is where you package python (or other supported languages, ie: Java, Go, ...) code to run on the Cloud on-demand. This is completely serverless and often referred to as **micro-service** data processing. You can use Cloud Functions to trigger to process data on-demand based on HTTP requests or when an action is taken on the Cloud like a file being loaded onto GCS or and event posted to Cloud Pub/Sub.

Cloud Functions are the most effective way to write **event-based micro-services** to process data. 

They work the best for handling smaller data volumes like single files (csv, audio, video, ...) typically within a GB or less; while other tools like Spark (Cloud Dataproc) are better for processing data at bulk.


# Load Airports 

In this section, we will create a GCS triggered Cloud function that loads an airports data file from Cloud Storage onto BigQuery.

We will use pandas to read the data file and create a helper function which uses the `google.cloud.bigquery` module to load the dataframe into BigQuery.

Got to the directory called `cloud_functions/load_airports_storage_trigger`:

```bash
cd ./cloud_functions/load_airports_storage_trigger
```

View the content of the file called `utils/airports_processor.py`:

```python
from time import perf_counter
import pandas as pd
from google.cloud import bigquery

from utils import logger


def load_from_file(file_path:str) -> pd.DataFrame:
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

```

This module includes two main function:

1. `load_from_file()`:

    Using pandas we will read our airports data file into a dataframe and perform some basic checks and transforms. Since we added the `gcsfs` pypi package to our _requirements.txt_ file, pandas is able to directly read from `gs://` paths.

1. `load_bigquery_table()`:

    Using the bigquery client `load_table_from_dataframe()` method, we'll load the dataframe into our BigQuery table. This method is also able to create the table if needed using the settings provided.

**NOTE:** The airport data files used in this episode are included under: `./data/`

<br/><br/>

View the content of `main.py`:

```python
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

```

**NOTE:**

1. This function gets automatically called by google cloud as soon as someone loads a new data file to a cloud storage bucket.
2. You can see that our function now takes two parameters called `event` and `context`. _event_ includes information about the google cloud storage event that has triggered this function call while _context_ includes information about this particular function instance.
3. `event` is a python dict containing the google cloud storage bucket and file path that has triggered the function.
4. We use the same _utils_ functions to process and load our data file onto bigquery.

<br/>

## Setup

Unlike the Cloud Function example in our previous episode, this Function uses other Cloud services such as Cloud Storage and BigQuery. Since we use other services, we need to ensure that our function is setup with a service account that has permission to use those services. In this example, we will use the same service account called `deb-01-sa`. You must create and use your own service account.

Before testing our function, you need to:

1. Create a service account to use with this Function. We're assuming you already have a service account. You can also create one specifically for this function; in a production environment make sure you always do this! Do NOT use your default one.
1. Create a Storage Bucket to upload our airports file to.
1. Upload source airports data file onto a GCS bucket
1. Create a BigQuery dataset for this example. We're assuming you already have one.
1. Ensure your service account has correct permissions to access both Storage bucket and BigQuery 
1. Ensure your service account has permission to publish to Pub/Sub to trigger the Cloud Function

### Create a GCS bucket and upload airports file

```bash
# create a bucket, replace your project name and location
# gsutil mb -p <PROJECT_ID> -c standard -l <REGION> -b on gs://<BUCKET_NAME>
gsutil mb -p deb-01 -c standard -l us-central1 -b on gs://<%YOUR_BUCKET_NAME%>

# upload airports file to your bucket
gsutil cp ./data/deb-airports-OR.csv gs://dsa-deb-ch8/airports/

# list your bucket for the airports file path
gsutil ls gs://dsa-deb-ch8/airports

```

### Set IAM Roles for your Service Account

Before testing your function ensure that your current service account set by `GOOGLE_APPLICATION_CREDENTIALS` has permission to access both your GCS bucket and BigQuery. Make sure the service account is `Storage Admin` and `BigQuery Admin`. 

**NOTE:** In production, always create a new service account for your function.

Use the Cloud Console or `gcloud` to set the permissions for your service account. It's much easier to use Cloud Console; but we're including `gcloud` instructions here:

```bash
# list your service accounts on this project
gcloud iam service-accounts list

DISPLAY NAME                            EMAIL                                              DISABLED
deb-01-sa                               deb-01-sa@deb-01.iam.gserviceaccount.com           False
App Engine default service account      deb-01@appspot.gserviceaccount.com                 False
Compute Engine default service account  88141792430-compute@developer.gserviceaccount.com  False

# here we're using the service account: deb-01-sa@deb-01.iam.gserviceaccount.com
# list roles on your service account, replace your project name and service account name
gcloud projects get-iam-policy deb-01  \
 --flatten="bindings[].members" \
 --format='table(bindings.role)' \
 --filter="bindings.members:deb-01-sa@deb-01.iam.gserviceaccount.com"

ROLE
roles/appengine.appCreator
roles/appengine.appViewer
roles/bigquery.admin
roles/bigquery.dataEditor
roles/bigquery.dataViewer
roles/datastore.owner
roles/file.editor
roles/file.viewer
roles/logging.logWriter
roles/pubsub.editor
roles/storage.objectAdmin

# make sure you have bigquery.dataEditor and storage.objectAdmin
# you can add these by the following commands
# gcloud projects add-iam-policy-binding PROJECT_ID \
#     --member="serviceAccount:SERVICE_ACCOUNT_ID@PROJECT_ID.iam.gserviceaccount.com" \
#     --role="ROLE_NAME"
gcloud projects add-iam-policy-binding deb-01 \
    --member="serviceAccount:deb-01-sa@deb-01.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding deb-01 \
    --member="serviceAccount:deb-01-sa@deb-01.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

Since Storage Triggers actually use Pub/Sub events in the background to trigger functions, we need to ensure that our service account associated with this function has access to publish to Pub/Sub. Make sure you add at least `roles/pubsub.publisher` role to your service account. You can do this by `gcloud` or on the Cloud Console.

```bash
gcloud projects add-iam-policy-binding deb-01 \
    --member="serviceAccount:deb-01-sa@deb-01.iam.gserviceaccount.com" \
    --role="roles/pubsub.admin"

gcloud projects add-iam-policy-binding deb-01 \
    --member="serviceAccount:deb-01-sa@deb-01.iam.gserviceaccount.com" \
    --role="roles/pubsub.publisher"
```

## Deploy our Function to Google Cloud

Storage triggered functions can NOT be tested locally. Deploy your function using `gcloud`:

```bash
gcloud functions deploy dsadeb_airports_loader_storage_trigger \
    --runtime python37 \
    --trigger-resource gs://dsa-deb-ch8 \
    --trigger-event google.storage.object.finalize \
    --service-account=deb-01-sa@deb-01.iam.gserviceaccount.com \
    --region=us-central1
```

**NOTES:**

- `--trigger-resource`: specifies the Storage bucket that we like to trigger our function with.
- `--trigger-event`: set to trigger our function based on objects being created on our bucket. See the other available trigger events on [google documentation](https://cloud.google.com/functions/docs/calling/storage).
- `--service-account` and `--region` specify our service account and region for this function.

Read the [google documentation](https://cloud.google.com/functions/docs/calling/storage) for complete guide on triggering your function by storage events.

## Testing our Function

To test our function, we can load a airports data file to our storage bucket and view our function logs:

```bash
# load a file into our storage bucket. change your gcs bucket name and path
gsutil cp ./data/deb-airports-AK.csv gs://dsa-deb-ch8/airports/

# wait several sections and view the logs for your function. check to see if you see messages regarding the data file you just loaded
gcloud functions logs read dsadeb_airports_loader_storage_trigger
```


# Deleting Your Functions

You can delete your functions by running:

```bash
gcloud functions delete dsadeb_howdoi --quiet
gcloud functions delete dsadeb_airports_loader_storage_trigger --quiet
```
