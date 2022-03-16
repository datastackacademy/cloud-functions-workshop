
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

Create a directory called `/cloud_functions/howdoi` and create two files under it for `main.py` and `requirements.txt`. Edit 
your `main.py` to include the skeleton of you Cloud Function:

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

Or use Postman:

![postman example](imgs/postman_01.png)

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

## Deleting your Cloud Function

To delete your function, run:

```bash
gcloud functions list

NAME                                 STATUS  TRIGGER       REGION
dsa-howdoi-function                  ACTIVE  HTTP Trigger  us-central1


gcloud functions delete dsa-howdoi-function --region=us-central1
```


# Challenge Projects

## Wikipedia Summary Function

Create a Cloud Function that returns a 2 sentence summary for a wikipedia topic. Use the [pypi wikipedia](https://pypi.org/project/wikipedia/) package.

