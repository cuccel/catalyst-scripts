#!/usr/bin/env python3

import json
import argparse
import urllib.request

parser = argparse.ArgumentParser(description="Create an alert to Catalyst")
parser.add_argument("-u", "--url", type=str, help="API url", required=True)
parser.add_argument("-t", "--token", type=str, help="API key", required=True)
parser.add_argument("-d", "--description", type=str, help="Description", required=True)
parser.add_argument("-n", "--name", type=str, help="Ticket name", required=True)

parser.add_argument("--schema", type=str, help="Schema name", default="default")
parser.add_argument("--tlp", type=str, help="TLP Level", default="Green")
parser.add_argument("-s", "--severity", type=str, help="Severity", default="Low")
parser.add_argument("--type", type=str, help="Ticket Type", default="alert")
parser.add_argument("--customfields", type=str, help="Custom Fields. Format: field1:value1;field2:value2")

args = parser.parse_args()

def create_alert(api_url, api_key, ticket_type, ticket_schema, description, name, tlp="Green", severity="Low", customfields=None):
    headers = {'private-token': api_key}

    try:
        schema_url = f"{api_url}/templates/{ticket_schema}"
        schema_request = urllib.request.Request(schema_url, headers=headers)
        with urllib.request.urlopen(schema_request) as response:
            schema_response = json.loads(response.read().decode())

        alert = {
            "details": {
                "description": description,
                "severity": severity,
                "tlp": tlp
            },
            "status": "open",
            "type": ticket_type,
            "name": name,
            "schema": schema_response['schema']
        }

        if customfields:
            for field in customfields.split(";"):
                name, value = field.split(":")
                alert["details"][name] = value

        alert_json = json.dumps(alert).encode()
        alert_request = urllib.request.Request(f"{api_url}/tickets", alert_json, headers=headers)

        with urllib.request.urlopen(alert_request) as response:
            response_body = response.read().decode()
            if response.status != 200:
                return(f"Error submitting alert. Status code: {response.status}, Response body: {response_body}")
            else:
                response_json = json.loads(response_body)
                return(response_json['id'])

    except urllib.error.URLError as e:
        return(f"Error submitting alert: {e}")

print(create_alert(args.url, args.token, args.type, args.schema, args.description, args.name, args.tlp, args.severity, args.customfields))