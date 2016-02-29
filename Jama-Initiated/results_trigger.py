import requests
import json
import time
import os

# The base_url of your Jama instance
# For hosted: "https://{Org Base}.jamacloud.com/rest/{version or 'latest'}/"
base_url = '{base_url}/rest/latest/'  # TODO: Change this to match your configuration

# Username and password should be stored somewhere other than in the
# source code according to your organization's security policies
auth = ('api_user', 'password')  # TODO: Change this to match your configuration

# The frequency to check for results.
polling_interval = 600  # In seconds


# This function will need to be tailored to parse the output of your particular
# automated test framework
def parse_results():
    filename = next((f for f in os.listdir('.') if "results---" in f), None)
    timestamp = filename.split('---')[1]
    parsed_name = "parsed---{}".format(timestamp)
    os.rename(filename, parsed_name)
    with open(parsed_name, 'r') as results_file:
        item_id = results_file.readline().split(':')[1].strip()
        step_number = results_file.readline().split(':')[1].strip()
        result = results_file.readline().split(':')[1].strip()
        print "Found results for run {}.".format(item_id)

        # After parsing results we end up with the Jama item ID, the test run step number
        # and the results of the test execution
        update_results(item_id, int(step_number), result)


def update_results(item_id, step_number, result):
    run_url = base_url + "testruns/{}".format(item_id)
    run_to_update = json.loads(requests.get(run_url, auth=auth).text)['data']
    print "Retrieved run {} from Jama.".format(run_to_update['id'])
    fields = run_to_update['fields']
    remove_field(fields, 'testRunStatus')
    remove_field(fields, 'executionDate')
    step = fields['testRunSteps'][step_number - 1]

    # Setting the step's status depends on the previous results parsing
    if result == 'Pass':
        step['status'] = 'PASSED'
    else:
        step['status'] = 'FAILED'

    print "Updating: \n\tItem ID: {}\n\tStep Number: {}\n\tResult: {}.".format(item_id, step_number, result)
    requests.put(run_url, auth=auth, json={'fields': fields})
    print "Attempting to unlock test run {}.".format(item_id)
    attempt_unlock(item_id, fields)


def attempt_unlock(item_id, fields):
    for step in fields['testRunSteps']:
        if step['status'] == 'NOT_RUN':
            print "Some steps not yet run.  Leaving test run {} locked.".format(item_id)
            return
    print "All steps have been run.  Unlocking test run {}.".format(item_id)
    lock_url = base_url + "testruns/{}/lock".format(item_id)
    requests.put(lock_url, json={'locked': False}, auth=auth)


# Convenience function to safely remove read-only fields from the test run
# before updating it
def remove_field(item, field):
    try:
        del item[field]
    except KeyError:
        pass


if __name__ == "__main__":
    while True:
        print "==========Polling Results=========="
        try:
            parse_results()
        except AttributeError:
            time.sleep(polling_interval)
