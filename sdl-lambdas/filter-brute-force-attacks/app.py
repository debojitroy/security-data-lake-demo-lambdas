title_filter = 'brute force attacks'
ipv4_path = 'ProductFields.aws/guardduty/service/action/networkConnectionAction/remoteIpDetails/ipAddressV4'


def get_result_rows(event):
    if 'ResultSet' in event and 'Rows' in event['ResultSet']:
        return event['ResultSet']['Rows']
    else:
        return None


def is_brute_force(title):
    return title_filter in title.lower()


def remove_curly_braces(input_val):
    return input_val.replace("{", "").replace("}", "")


def convert_to_dict(input_val):
    return dict(item.split("=") for item in input_val.split(", "))


def convert_to_output_list(ip_set):
    output = []
    for ip in ip_set:
        output.append({"ip_to_block": ip})

    return output


def lambda_handler(event, context):
    print(event)
    print(context)

    rows = get_result_rows(event)

    ips_to_block = set({})

    if rows is not None:
        for finding in rows:
            item = finding['Data']

            title = item[5]['VarCharValue']
            finding = item[7]['VarCharValue']
            print('Title: ', title)
            print('F: ', finding)

            if is_brute_force(title):
                new_obj = convert_to_dict(remove_curly_braces(finding))
                ipv4 = new_obj[ipv4_path]
                print('Brute Force IPv4: ', ipv4)
                ips_to_block.add(ipv4)
            else:
                print('Not Brute Force...')

    return convert_to_output_list(ips_to_block)
