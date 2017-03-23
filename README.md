# Jama and Automated Testing

Jama Software is the definitive system of record and action for product development. The company’s modern requirements and test management solution helps enterprises accelerate development time, mitigate risk, slash complexity and verify regulatory compliance. More than 600 product-centric organizations, including NASA, Boeing and Caterpillar use Jama to modernize their process for bringing complex products to market. The venture-backed company is headquartered in Portland, Oregon. For more information, visit [jamasoftware.com](http://jamasoftware.com).

Please visit [dev.jamasoftware.com](http://dev.jamasoftware.com) for additional resources and join the discussion in our community [community.jamasoftware.com](http://community.jamasoftware.com).

## Why Connect Jama to your Automated Testing Tool?
Jama is used for managing requirements and the manual test cases that validate and verify those requirements.  Jama provides traceability between the various layers of requirements down to manual test cases so teams can ensure test coverage and show the results of those manual tests.  However, many teams also validate/verify their requirements through automated testing via a separate Automation Test Tool (ATT).  If you want to demonstrate traceability from your requirements to both manual AND automated testing results in Jama, you can leverage Jama’s API to bring automated test results into Jama.

For more information about which of the approaches below is better for your team see [this article](https://community.jamasoftware.com/blogs/iman-bilal/2017/01/25/connecting-jama-to-your-automated-testing-tool).

### Jama Initiated Tests
Jama’s manual test center offers functionality for your team to manually create Test Cases and Test Plans for executing those tests.  It also offers some out of the box reporting via Test Plan summary and Test Plan detail reports.  Teams familiar with using Jama’s test center to execute manual test cases can use a similar approach to initiate automated tests directly from Jama.

You’ll need some information from your Jama configuration to configure the scripts:

1. __The API ID of the automated test user.__  When test runs are assigned to this user the script will run whatever command(s) appear in the “action” column of the test run.

2. __The API ID of test runs in your Jama instance.__

3. __Credentials for an account to access and update the test run results.__  This can be the automated test user or any user with appropriate permissions.

### Automated Testing Tool Initiated Tests
For teams not using Jama’s Test Center for manual testing or who don’t want to interact with Jama in order to initiate the automated test scripts we recommend not leveraging the Jama test center at all.

You’ll need some information from your Jama configuration to configure the script:

1. __The API ID of the set item type.__  This is a system-defined item type.

2. __The API ID of the test results item type.__  This is the new item type created for this approach.

3. __The API ID of the project that will hold the test results.__

4. __The unique name of the field containing the Pass/Fail picklist in the test results item type.__

5. __The API IDs of the ‘pass’ and ‘fail’ options in the above picklist.__

### Interested in having someone guide you through this process?
Jama's Professional Services team can assist you with practical guidance on both the desired cross-team processes and the supporting technical workflow.  Contact your Customer Success manager for more information.
