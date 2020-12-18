#!/usr/bin/env python

import os
import sys
import json
import requests
import base64

COMPLETION_STATUS = [
    'In Progress',
    'Testing',
    'Done'
]


def dump_summary(sprint_name, ds):
    sprint_dir = './data/' + sprint_name.lower().replace(' ', '_')
    output_file = os.path.join(sprint_dir, 'summary.json')

    if os.path.exists(output_file):
        print('STATUS: Skipping summary dump')
        return output_file

    with open(os.path.join(sprint_dir, 'summary.json'), 'w') as fd:
        fd.write(json.dumps(ds, indent=2, default=str))


def get_summary(jira_url, output_ds):
    ds = {'meta': {'tag_order': []}, 'users': {}}
    for page in output_ds:
        for issue in page['issues']:
            if issue['fields']['assignee'] is None:
                continue
            status = issue['fields']['status']['name']

            if status not in COMPLETION_STATUS:
                continue

            jira_id = issue['key']
            jira_user = issue['fields']['assignee']['displayName']
            jira_summary = issue['fields']['summary']
            jira_description = issue['fields']['description']

            if status == 'In Progress':
                jira_summary = 'In Progress - ' + jira_summary

            if jira_user not in ds['users']:
                ds['users'][jira_user] = []

            ds['users'][jira_user].append(
                {
                    'url': jira_url + '/browse/' + jira_id,
                    'summary': jira_summary,
                    'description': jira_description,
                    'tags': [],
                    'demo': {},
                }
            )
    return ds


def load_output_file(file_name):
    return json.loads(open(file_name).read())


def dump_sprint_info(jira_url, jira_sprint_name, jira_user_name, jira_password):
    sprint_dir = './data/' + jira_sprint_name.lower().replace(' ', '_')
    output_file = os.path.join(sprint_dir, 'output.json')

    if os.path.exists(output_file):
        print('STATUS: Skipping collection')
        return output_file

    if not os.path.exists(sprint_dir):
        os.makedirs(sprint_dir)

    url = jira_url + '/rest/api/2/search'
    payload = {
        'startAt': 0,
        'jql': 'Sprint = "{}"'.format(jira_sprint_name),
    }
    print('STATUS: Getting details startAt - 0')

    auth_str = jira_user_name + ':' + jira_password
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(auth_str.encode()).decode('utf-8'),
        'Content-Type': 'application/json',
    }
    resp = requests.get(url, headers=headers, params=payload)

    if resp.status_code != 200:
        print('ERROR: Failed to fetch sprint details')
        print(resp.text)
        sys.exit(1)

    output = []
    curr_output = resp.json()
    output.append(curr_output)

    if curr_output['total'] > curr_output['maxResults']:
        pending = curr_output['total'] - curr_output['maxResults']
        remaining_iterations = pending / curr_output['maxResults']

        if remaining_iterations == 0:
            remaining_iterations = 1

        totalResults = curr_output['maxResults']

        while remaining_iterations > 0:
            payload['startAt'] = totalResults
            print('STATUS: Getting details startAt - ' + str(payload['startAt']))
            resp = requests.get(url, headers=headers, params=payload)
            curr_output = resp.json()
            totalResults += len(curr_output['issues'])
            remaining_iterations -= 1
            output.append(curr_output)

    with open(os.path.join(sprint_dir, 'output.json'), 'w') as fd:
        fd.write(json.dumps(output, indent=2, default=str))
    return output_file


def main():

    jira_url = os.environ.get('JIRA_URL')
    if not jira_url or jira_url == '':
        sys.stderr.write('ERROR: env var JIRA_URL not set\n')
        sys.exit(1)

    jira_sprint_name = os.environ.get('JIRA_SPRINT_NAME')
    if not jira_sprint_name or jira_sprint_name == '':
        sys.stderr.write('ERROR: env var JIRA_SPRINT_NAME not set\n')
        sys.exit(1)

    jira_user_name = os.environ.get('JIRA_USER_NAME')
    if not jira_user_name or jira_user_name == '':
        sys.stderr.write('ERROR: env var JIRA_USER_NAME not set\n')
        sys.exit(1)

    jira_password = os.environ.get('JIRA_PASSWORD')
    if not jira_password or jira_password == '':
        sys.stderr.write('ERROR: env var JIRA_PASSWORD not set\n')
        sys.exit(1)

    output_file = dump_sprint_info(jira_url, jira_sprint_name, jira_user_name, jira_password)
    output_ds = load_output_file(output_file)
    summary_ds = get_summary(jira_url, output_ds)
    dump_summary(jira_sprint_name, summary_ds)


if __name__ == '__main__':
    main()
