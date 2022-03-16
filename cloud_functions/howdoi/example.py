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
    # first try to get the question from the URL params
    question = request.args.get('question', None)
    # if question is not in URL params then try other options
    if question is None:
        content_type = request.headers['content-type']
        if content_type == 'application/json':
            # part of json request body
            request_json = request.get_json(silent=True)
            if request_json and 'question' in request_json:
                question = request_json['question']
            else:
                raise ValueError("JSON is invalid, or missing a 'question' tag")
        elif content_type == 'text/plain':
            # as plain text in request data
            name = request.data
        elif content_type == 'application/x-www-form-urlencoded':
            # as a form parameter
            name = request.form.get('question')
        else:
            # couldn't find the question anywhere! return http error response
            return "Unknown content type: {}".format(content_type), 400, { 'content-type': 'text/plain'}
    
    logger.info(f"new question: '{question}'")
    # send back the answer to the question
    answer = howdoi.howdoi(question)
    # response rest header options
    response_headers = {
        'content-type': 'text/plain',
        'server-time': str(datetime.now()),
    }
    # the return is a regular flask return tuple: (data, http resp code, headers)
    return answer, 200, response_headers
