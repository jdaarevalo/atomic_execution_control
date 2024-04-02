# AtomicExecutionControl

[![PyPI](https://img.shields.io/pypi/v/atomic-execution-control)](https://pypi.org/project/atomic-execution-control/)
[![Downloads](https://pepy.tech/badge/atomic-execution-control)](https://pepy.tech/badge/atomic-execution-control)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/gouline/dbt-metabase/blob/master/LICENSE)


`AtomicExecutionControl` is a Python library crafted to address the complexities of ensuring atomic operations across distributed applications, particularly those deployed on AWS services like Lambda, Fargate, and EC2. By leveraging DynamoDB, this library offers a robust mechanism to prevent concurrent executions, thus mitigating race conditions and duplicate processing risks. Whether you're handling event-driven workflows, orchestrating microservices, or ensuring data integrity across distributed systems, `AtomicExecutionControl` simplifies state management and execution coordination, making your applications more reliable, efficient and most important 'atomic'.


## Features

- **Atomic Execution**: Ensures that only one instance of a the function processes a specific task at a time.
- **Status Management**: Tracks the execution status of tasks in DynamoDB, marking them as in progress or finished.
- **Timeout Handling**: Supports time-based expiry for task locks, making it resilient to failures or stalls in execution.
- **Easy Integration**: Designed to be easily integrated into existing AWS Lambda, Fargate or EC2 functions with minimal configuration.


## Quick Start

Get up and running with `AtomicExecutionControl` in just a few steps:

1. Install the package:

```bash
pip install atomic_execution_control
```

2. Set up a DynamoDB table in AWS with a primary key.


3. Use the following snippet to ensure atomic execution in your project:

```python

from atomic_execution_control import AtomicExecutionControl

# Initialize with your DynamoDB table details
aec = AtomicExecutionControl(table_name="YourTable", primary_key="YourKey")

# Start controlling execution atomically
```


## Prerequisites

A DynamoDB table set up for tracking execution statuses.


## Configuration

`AtomicExecutionControl` can be configured with the following parameters during initialization:

- **`table_name`** (required): The name of the DynamoDB table used for tracking execution.
- **`primary_key`** (required): The primary key attribute name in your DynamoDB table.
- **`region_name`** (optional, default=`"eu-west-1"`): The AWS region where your DynamoDB table is located.
- **`endpoint_url`** (optional): Custom endpoint URL, useful for local testing with DynamoDB Local.


### Additional method parameters:


- `delete_items_finished_or_old` method:
  - **item_execution_valid_for** (optional, default=20): Time in minutes to consider an execution old enough to be deleted.
- `wait_other_instances_finish` method:
  - **timeout** (optional): Maximum time in seconds to wait for the 'finished' status.
  - **time_to_retry** (optional): Time in seconds to wait before trying to validate the status again.


## Examples

### Preventing Duplicate Processing

Below is a quick example to help you get started:

```python
from atomic_execution_control import AtomicExecutionControl
import os

# DynamoDB table and primary key
TABLE_NAME = 'YourDynamoDBTableName'
PRIMARY_KEY = 'YourPrimaryKey'

# Test also in your local environment 
# verify the endpoint_url, this url "http://localhost:8000" is also valid.
endpoint_url = "http://docker.for.mac.localhost:8000/" if os.environ.get("AWS_SAM_LOCAL") else None
 
# Initialize AtomicExecutionControl
aec = AtomicExecutionControl(
    table_name=TABLE_NAME,
    primary_key=PRIMARY_KEY,
    region_name="eu-west-1",
    endpoint_url=endpoint_url
)

# In case you already log into an specific AWS account via AWS Single Sign-On (SSO)
# you can send the profile_name parameter as follow.
profile_name =  'AwsProfileName'
aec = AtomicExecutionControl(
    table_name=TABLE_NAME,
    primary_key=PRIMARY_KEY,
    region_name="eu-west-1",
    endpoint_url=endpoint_url,
    profile_name=profile_name
)

# Assume you have an event-driven architecture where multiple events 
# could trigger the same task
date_to_run = '2024-01-01'


# delete items in Dynamo for old executions
aec.delete_items_finished_or_old(keys=[date_to_run], item_execution_valid_for=20)

# write in Dynamo the date_to_run and block other executions to the same key
result = aec.write_atomically_a_key(key=date_to_run)

if result:
    # Process the event
    
    print("Lock acquired, proceeding with task.")
    
    ## run_your_etl(date_to_run)
    
    # Remember to update the status to 'finished' after completing your task
    aec.update_status(key=date_to_run)
else:
    # If lock couldn't be acquired, another instance is already processing the task
    print("Task already in progress by another instance.")
    # wait until other instances with the same key finish
    aec.wait_other_instances_finish(keys=[date_to_run])

```

## Support and Contact

Encountering issues or have questions about integrating `AtomicExecutionControl`? We're here to help!

- **Ask a Question or Report an Issue**: For technical issues or questions, please [open an issue](https://github.com/jdaarevalo/atomic_execution_control/issues) on our GitHub repository.
- **Email Us**: For direct support or inquiries, email us at jdaarevalo@gmail.com - we aim to respond as quickly as possible.
- **Suggestions**: Your feedback and suggestions are invaluable in making `AtomicExecutionControl` better. Don't hesitate to reach out with ideas for improvements or new features!


## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request on GitHub.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
