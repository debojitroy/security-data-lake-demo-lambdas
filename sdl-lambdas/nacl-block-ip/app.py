import boto3
import json
import os

import requests

slack_message_template = '''
{
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":white_check_mark: Completed your request - *[Action]* - *[IP]*"
			}
		}
	]
}
'''


def should_block(action):
    return action == 'approve'


def get_lowest_ingress_rule_number(nacl_response):
    entries = nacl_response['NetworkAcls'][0]['Entries']

    lowest_rule_number = 32767

    for entry in entries:
        if entry['Egress'] is False and entry['RuleNumber'] < lowest_rule_number:
            lowest_rule_number = entry['RuleNumber']

    return lowest_rule_number


def make_nacl_block_entry(nacl_id, ip, rule_number):
    ec2 = boto3.client('ec2')
    ec2.create_network_acl_entry(
        NetworkAclId=nacl_id,
        RuleNumber=rule_number,
        Protocol='-1',
        RuleAction='deny',
        Egress=False,
        CidrBlock=ip + "/32",
        PortRange={
            'From': -1,
            'To': -1
        })


def prepare_slack_message(ip_to_block, action):
    return slack_message_template.replace("[Action]", action).replace("[IP]", ip_to_block)


def send_slack_message(slack_url, ip_to_block, action):
    slack_message = prepare_slack_message(ip_to_block, action)
    message_body = json.loads(slack_message)
    response = requests.post(slack_url, json=message_body)
    print(response)


def lambda_handler(event, context):
    records = event["Records"]
    nacl_id = os.environ["nacl_id"]
    slack_url = os.environ["slack_url"]

    print('NACL ID: ', nacl_id)
    print('Slack URL: ', slack_url)

    ec2 = boto3.client('ec2')

    response = ec2.describe_network_acls(
        Filters=[
            {
                'Name': 'network-acl-id',
                'Values': [
                    os.environ["nacl_id"]
                ]
            },
        ]
    )

    print('NACL Search Response: ', response)

    lowest_rule = get_lowest_ingress_rule_number(response)
    new_rule = lowest_rule - 10

    for record in records:
        payload = record["body"]
        print('Payload: ', payload)

        action_details = json.loads(payload)

        ip_to_block = action_details["ip"]
        action = action_details["action"]

        print('IP to Block: ', ip_to_block)
        print('Action: ', action)
        print('New Rule: ', new_rule)

        if should_block(action):
            rule = new_rule
            make_nacl_block_entry(nacl_id, ip_to_block, rule)
            new_rule = new_rule - 10

        send_slack_message(slack_url, ip_to_block, action)
