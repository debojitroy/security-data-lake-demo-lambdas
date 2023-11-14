import json
import os
import boto3
from urllib.parse import unquote
import base64
import requests

slack_message_template = '''
{
    "replace_original": "true",
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":saluting_face: Accepted your request - *[Action]* - *[Resource]*"
			}
		}
	]
}
'''


def extract_details_from_payload(payload):
    print(payload)
    ip = None
    action = None
    callback_url = None

    if 'actions' in payload:
        action_string = payload['actions'][0]["value"]
        print(action_string)

        action_details = action_string.split("#")
        ip = action_details[0]
        action = action_details[1]
    if 'response_url' in payload:
        callback_url = payload['response_url']
    return {
        'ip': ip,
        'action': action,
        'callback_url': callback_url
    }


def process_nacl_action(sqs_url, details):
    print('nacl_action: ', details)

    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl=sqs_url,
        MessageBody=json.dumps(
            {
                'ip': details['ip'],
                'action': details['action']
            }
        )
    )


def process_callback(details):
    message_body_str = slack_message_template.replace("[Action]", details['action'] + ' Block').replace("[Resource]",
                                                                                                        details['ip'])

    message_body = json.loads(message_body_str)
    print(message_body)

    response = requests.post(details['callback_url'], json=message_body)
    print(response)


def extract_payload(event):
    if 'body' in event:
        body = event['body']
        if body:
            decoded_body = base64.b64decode(body).decode('utf-8')
            print("decoded_body: ", decoded_body)
            url_parsed_body = unquote(decoded_body)
            print("url_parsed_body: ", url_parsed_body)
            payload = url_parsed_body.split("=")[1]
            print("payload: ", payload)

            return json.loads(payload)
    return None


def lambda_handler(event, context):
    print('Incoming Event: ', event)
    print('Incoming Context: ', context)

    sqs_url = os.environ["sqs_url"]
    payload = extract_payload(event)

    details = extract_details_from_payload(payload)

    process_nacl_action(sqs_url, details)
    process_callback(details)

    return {}
