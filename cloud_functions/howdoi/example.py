"""
This is a simple example of a Google Cloud Functions.

This function responses to HTTP Cloud Function requests; which is basically a mini-flask REST server.
This function uses the very cool `howdoi` pypi package which answers various coding question.

To test, send a REST request to the function with a question and see your response.
"""

from flask import Request
from datetime import datetime
from howdoi import howdoi

# local package imports
from utils import logger


# howdoi module setup not to use SSL, this breaks sometimes!
howdoi.VERIFY_SSL_CERTIFICATE = False
howdoi.SCHEME = 'http://'


def simple_function(request: Request):
    name = request.args.get("name", "Anonymous")
    return f"hello {name}", 200


def howdoi_function(request: Request):
    """
    Our Google Cloud Function to answer programming question

    send a REST request with your programming question as the GET URL param
    """
    
    question = request.args.get('question', None)
    if question is None:
        answer = "You forgot to provide a question!"
    else:
        # use the howdoi lib for an answer
        answer = howdoi.howdoi(question)
    
    # send back response
    logger.info(f"new question: '{question}'")
    response_headers = {
        'content-type': 'text/plain',
        'server-time': str(datetime.now()),
    }
    # the return is a regular flask return tuple: (data, http resp code, headers)
    return answer, 200, response_headers

