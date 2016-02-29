import subprocess
import datetime
import requests
import urllib
import json
import time
import os

# The base_url of your Jama instance
# For hosted: "https://{Org Base}.jamacloud.com/rest/{version or 'latest'}/"
base_url = "{base_url}/rest/latest/"  # TODO: Change this to match your configuration

# Username and password should be stored somewhere other than in the
# source code according to your organization's security policies
auth = ('username', 'password')  # TODO: Change this to match your configuration

# The API ID of a Jama user.  When tests are assigned to this user this script
# will run the tests
automation_user_id = 18364  # TODO: Change this to match your configuration

# The item type ID of test runs in your Jama instance
runs_type_id = 89035  # TODO: Change this to match your configuration

# The frequency to poll Jama.  Frequent polling can impact system performance
polling_interval = 600  # In seconds


def run_test(test_run):
    test_run_id = test_run['id']
    print "Evaluating run {}.".format(test_run_id)
    lock_url = base_url + "testruns/{}/lock".format(test_run_id)
    run_is_locked = json.loads(requests.get(lock_url, auth=auth).text)['data']['locked']
    if not run_is_locked:
        print "Test run {} not locked.  Running.".format(test_run_id)
        step_successfully_run = False

        print "Locking test run {}.".format(test_run_id)
        requests.put(lock_url, json={'locked': True}, auth=auth)

        run_url = base_url + "testruns/{}".format(test_run_id)
        test_run = json.loads(requests.get(run_url, auth=auth).text)['data']

        steps = test_run['fields']['testRunSteps']
        for step_index in range(0, len(steps)):
            test_step = steps[step_index]
            if test_step['status'] == 'NOT_RUN':
                print "Step {} status == 'NOT_RUN'.".format(step_index)
                try:
                    test_script_name = test_step['action']

                    print "Starting subprocess."
                    print os.system('pwd')
                    print os.system('ls')
                    # This subprocess call can be used to initiate any kind of action.
                    # Make sure that this kind of action conforms to your organization's security policies.
                    subprocess.Popen(['python', test_script_name.strip(), str(test_run_id), str(step_index + 1)])

                    step_successfully_run = True
                except:
                    print "Error: Problem running step {} with action: {}.".format(step_index, test_step['action'])
            else:
                print "Not running step with status {}.".format(test_step['status'])
        if not step_successfully_run:
            print "Unlocking test run {}.".format(test_run_id)
            requests.put(lock_url, json={'locked': False}, auth=auth)
    else:
        print "Run {} is locked.  Skipping.".format(test_run_id)


def get_automation_runs():
    last_run_time = get_last_run_time()
    if last_run_time is not None:
        last_run = datetime.datetime.fromtimestamp(last_run_time)
        last_activity_date = last_run.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    else:
        last_activity_date = None

    runs = get_all_tests(last_activity_date)
    print "Runs evaluated: {}.".format(len(runs))

    to_remove = []
    for run in runs:
        if not valid_run(run):
            to_remove.append(run)
    for run in to_remove:
        runs.remove(run)

    return runs


def get_all_tests(last_activity_date):
    remaining_results = -1
    start_index = 0

    all_runs = []

    contains = urllib.quote_plus('"assignedTo":{}'.format(automation_user_id))
    item_type_segment = "abstractitems?itemType={}".format(runs_type_id)
    if last_activity_date is not None:
        last_activity_date_segment = "&lastActivityDate={}".format(last_activity_date)
    else:
        last_activity_date_segment = ""
    contains_segment = "&contains={}".format(contains)
    sort_by_segment = "&sortBy=modifiedDate.asc"
    url = ''.join([
        base_url,
        item_type_segment,
        last_activity_date_segment,
        contains_segment,
        sort_by_segment
    ])

    print "Requesting resource: {}.".format(url)

    while remaining_results != 0:
        start_at = "&startAt={}".format(start_index)

        current_url = url + start_at
        response = requests.get(current_url, auth=auth)
        json_response = json.loads(response.text)

        page_info = json_response['meta']['pageInfo']
        total_results = page_info['totalResults']
        result_count = page_info['resultCount']
        remaining_results = total_results - (start_index + result_count)
        start_index += 20

        all_runs.extend(json_response['data'])

    return all_runs


def valid_run(run):
    print "Validating run {}.".format(run['id'])
    if run['type'] != 'testruns':
        print "Item {} is not a test run.  Skipping.".format(run['id'])
        return False
    if run['fields']['testRunStatus'] != 'NOT_RUN':
        print "Run {} status must be NOT_RUN to evaluate.  Skipping.".format(run['id'])
        return False
    print "Run {} is valid.".format(run['id'])
    return True


def get_last_run_time():
    try:
        with open('last_run_time.dat', 'r+') as f:
            old_time = f.readline()
    except IOError:
        old_time = None

    with open('last_run_time.dat', 'w') as f:
        f.write(str(time.time() - 5))

    return float(old_time) if old_time is not None else None


if __name__ == "__main__":
    while True:
        print "==========Polling Jama=========="
        tests_to_evaluate = get_automation_runs()
        for test in tests_to_evaluate:
            run_test(test)
        time.sleep(polling_interval)
