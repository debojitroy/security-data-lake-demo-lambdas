import json
import os
import requests

slack_message = '''
{
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*New IP Blocking Request - [IP]*"
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*Type:*\\nNACL Block"
				},
				{
					"type": "mrkdwn",
					"text": "*Source:*\\nGuard Duty"
				},
				{
					"type": "mrkdwn",
					"text": "*Reason:*\\nBrute Force Attack"
				},
				{
					"type": "mrkdwn",
					"text": "*IPv4:*\\n*[IP]*"
				}
			]
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"emoji": true,
						"text": "Approve"
					},
					"style": "primary",
					"value": "[IP]#approve"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"emoji": true,
						"text": "Deny"
					},
					"style": "danger",
					"value": "[IP]#deny"
				}
			]
		}
	]
}
'''


def lambda_handler(event, context):
    ip = event["ip_to_block"]
    slack_url = os.environ["slack_url"]

    message_body_str = slack_message.replace("[IP]", ip)

    message_body = json.loads(message_body_str)
    print(message_body)

    response = requests.post(slack_url, json=message_body)
    print(response)

    return {
        'statusCode': 200
    }
