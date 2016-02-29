import os
import random
import sys

import jama_proxy

doc_key = "TEST-DOC-15"  # TODO: Change this to match your configuration
test_result = random.choice(["Pass", "Fail"])
test_result_body = "This test {}ed.".format(test_result)

# The test invokes the code that updates Jama with the results
# You can add markup to your test results for formatting
results_body = sys.argv[0].split(os.sep)[-1] + ':<br>' + test_result_body
jama_proxy.update_results(doc_key, results_body, test_result)
