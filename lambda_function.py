"""
Alexa skill for learning nifty words.
"""

from __future__ import print_function
import logging
import random
import psycopg2
import secrets

from words import WORDS

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

DEFAULT_COLLECTION = "hungry-tuber"

# --------------- Helpers that build all of the responses ----------------------

def spellout(s):
    return "<say-as interpret-as='spell-out'>{}</say-as>".format(s)

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>{}</speak>".format(output),
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Ask me for a word. I've got binders full of words."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Still there? Ask me for a word."

    return build_response(
        session_attributes,
        build_speechlet_response(
            card_title,
            speech_output,
            reprompt_text,
            should_end_session=False))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "See yaw."

    # Setting this to true ends the session and exits the skill.
    should_end_session = True

    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def intent_GetWord(intent, session):
    session_attributes = {}

    # Get a random word from the DB
    conn = psycopg2.connect(secrets.POSTGRES_URL)
    cursor = conn.cursor()

    cursor.execute("""
        select word, definition
        from words
        where collection = %s
        and deleted = false
        order by RANDOM()
        limit 1""", (DEFAULT_COLLECTION,))
    qres = cursor.fetchall()
    if len(qres) == 0:
        raise RuntimeError("db returned no words")

    word, definition = qres[0]

    # Create the response
    card_title = intent["name"]
    speech_output = "{}. {}. {}. {}".format(word, spellout(word), word, definition)
    reprompt_text = None

    return build_response(
        session_attributes,
        build_speechlet_response(
            card_title,
            speech_output,
            reprompt_text,
            should_end_session=True))

def intent_AddWord(intent, session):
    session_attributes = {}

    card_title = intent["name"]
    speech_output = "not implemented"
    reprompt_text = None

    return build_response(
        session_attributes,
        build_speechlet_response(
            card_title,
            speech_output,
            reprompt_text,
            should_end_session=True))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetWord":
        return intent_GetWord(intent, session)
    elif intent_name == "AddWord":
        return intent_AddWord(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    app_id = "amzn1.ask.skill.832a2dd9-563a-4d0f-aa21-cbf0844dc3b6"

    req_app_id = event['session']['application']['applicationId']
    if req_app_id != app_id:
        logger.error("Wrong Application ID: %s", req_app_id)
        raise ValueError("Wrong Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
