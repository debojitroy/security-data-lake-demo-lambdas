import boto3
import os


def check_has_entries(nacl_response):
    if nacl_response['NetworkAcls'] is not None and len(nacl_response['NetworkAcls']) > 0 and \
            nacl_response['NetworkAcls'][0]['Entries'] is not None and len(
        nacl_response['NetworkAcls'][0]['Entries']) > 0:
        return True

    return False


def check_ip_already_blocked(nacl_response, ip_to_block):
    if check_has_entries(nacl_response):
        entries = nacl_response['NetworkAcls'][0]['Entries']
        return any(entry['CidrBlock'] == ip_to_block + "/32" and entry['RuleAction'] == "deny" for entry in entries)

    return False


def lambda_handler(event, context):
    incoming_ip = event["ip_to_block"]
    print('Incoming IP: ', incoming_ip)
    print('NACL ID: ', os.environ["nacl_id"])

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

    print('Response: ', response)

    return {
        'incoming_ip': incoming_ip,
        'already_blocked': check_ip_already_blocked(response, incoming_ip),
    }
