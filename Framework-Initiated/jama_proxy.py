import requests
import urllib
import json
import sys


# The base_url of your Jama instance
# For hosted: "https://{Org Base}.jamacloud.com/rest/{version or 'latest'}/"
base_url = '{base_url}/rest/latest/'  # TODO: Change this to match your configuration

# Username and password should be stored somewhere other than in the
# source code according to your organization's security policies
auth = ('username', 'password')  # TODO: Change this to match your configuration

# The following configuration information is all available in the admin section
# of your Jama instance, or by REST calls.  This is easiest from your swagger
# documentation at {Jama Base URL}/api-docs

# Much of this information could be retrieved in this script, but it would all
# need to be retrieved each time the script runs.  It's much quicker (and simpler)
# to gather it once and enter it manually

# The item type ID of sets
set_type_id = 89029  # TODO: Change this to match your configuration

# The item type ID of your new Test Results item type
test_result_type_id = 89057  # TODO: Change this to match your configuration

# The project to store test results in
test_result_project_id = 20462  # TODO: Change this to match your configuration

# The name of the unique name of the field with the results picklist
results_pick_list = 'result'  # TODO: Change this to match your configuration

# The picklist option API ID of 'Pass'
pass_api_id = 156757  # TODO: Change this to match your configuration

# The picklist option API ID of 'Fail'
fail_api_id = 156758  # TODO: Change this to match your configuration


def update_results(document_key, results_text, test_result):

    # You'll need to figure out how to parse your test results here
    test_passed = test_result == 'Pass'

    satisfied_item = get_item_by_document_key(document_key)
    if satisfied_item is None:
        print "Item with document key {} wasn't found.".format(document_key)
        return

    downstream_item = get_downstream_result_item(satisfied_item)
    project_name = get_project_name(satisfied_item)
    set_id = get_set_id_for_name(project_name)
    updated_item = create_payload(set_id, satisfied_item, results_text, test_passed)

    if downstream_item is None:
        print "Posting new results item."
        post_and_relate(updated_item, satisfied_item)
    else:
        print "Updating existing results item."
        requests.put(base_url + 'items/{}'.format(downstream_item['id']), auth=auth, json=updated_item)


def post_and_relate(results_item, upstream_item):
    print "Posting new results item."
    json_response = json.loads(requests.post(base_url + 'items', auth=auth, json=results_item).text)

    results_item_id = json_response['meta']['location'].split('/')[-1]
    print "New results item's ID: {}".format(results_item_id)

    print "Relating items {} and {}.".format(results_item_id, upstream_item['id'])
    relationship = {'fromItem': upstream_item['id'], 'toItem': results_item_id}
    requests.post(base_url + 'relationships', auth=auth, json=relationship)


def create_payload(set_id, item, results_text, test_passed):
    if test_passed:
        result_api_id = pass_api_id
    else:
        result_api_id = fail_api_id
    return {
        'project': test_result_project_id,
        'itemType': test_result_type_id,
        'fields': {
            'name': "Results: {}".format(item['fields']['name']),
            'description': results_text,
            results_pick_list: result_api_id
        },
        'location': {
            'parent': {
                'item': set_id
            }
        }
    }


def get_project_name(item):
    url = base_url + 'projects/{}'.format(item['project'])
    return json.loads(requests.get(url, auth=auth).text)['data']['fields']['name']


def get_set_id_for_name(project_name):
    escaped_project_name = urllib.quote_plus(project_name)
    url = base_url + 'abstractitems?project={}&contains={}'.format(test_result_project_id, escaped_project_name)
    json_response = json.loads(requests.get(url, auth=auth).text)
    result_count = json_response['meta']['pageInfo']['totalResults']
    if result_count == 1:
        print "Adding to existing set."
        return json_response['data'][0]['id']
    if result_count == 0:
        print "Creating new set."
        return create_set(project_name)


def create_set(project_name):
    url = base_url + 'itemtypes/{}'.format(test_result_type_id)
    type_key = json.loads(requests.get(url, auth=auth).text)['data']['typeKey']

    payload = {
        'project': test_result_project_id,
        'itemType': set_type_id,
        'childItemType': test_result_type_id,
        'fields': {
            'name': project_name,
            'setKey': type_key
        }
    }

    url = base_url + 'items/'
    json_response = json.loads(requests.post(url, auth=auth, json=payload).text)
    location = json_response['meta']['location']
    return location.split('/')[-1]


def get_item_by_document_key(doc_key):
    remaining_results = -1
    start_index = 0

    url = base_url + 'abstractitems?contains={}'.format(urllib.quote_plus(doc_key))
    print "Retrieving resource: {}".format(url)

    while remaining_results != 0:
        start_at = '&startAt={}'.format(start_index)

        current_url = url + start_at
        response = requests.get(current_url, auth=auth)
        json_response = json.loads(response.text)

        for item in json_response['data']:
            if item['documentKey'].lower() == doc_key.lower():
                return item

        page_info = json_response['meta']['pageInfo']
        total_results = page_info['totalResults']
        result_count = page_info['resultCount']
        remaining_results = total_results - (start_index + result_count)
        start_index += 20

    return None


def get_downstream_result_item(item):
    remaining_results = -1
    start_index = 0

    url = base_url + 'items/{}/downstreamrelated'.format(item['id'])
    print "Retrieving resource: {}".format(url)

    while remaining_results != 0:
        start_at = '?startAt={}'.format(start_index)

        current_url = url + start_at
        response = requests.get(current_url, auth=auth)
        json_response = json.loads(response.text)

        if json_response['meta']['pageInfo']['totalResults'] == 0:
            return None

        for downstream_item in json_response['data']:
            if downstream_item['itemType'] == test_result_type_id:
                return downstream_item

        page_info = json_response['meta']['pageInfo']
        total_results = page_info['totalResults']
        result_count = page_info['resultCount']
        remaining_results = total_results - (start_index + result_count)
        start_index += 20


if __name__ == '__main__':
    # sys.argv[1] is Document Key
    #
    # sys.argv[2] is the Results Body.
    # This will be used as the test result item's description
    #
    # sys.argv[3] is the Test Result.
    # This will be parsed and used to determine which picklist option to assign
    update_results(sys.argv[1], sys.argv[2], sys.argv[3])
