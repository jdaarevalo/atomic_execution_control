# LambdaDynamoLock

`LambdaDynamoLock` is a Python library designed to ensure atomic executions within AWS Lambda functions by leveraging DynamoDB. It provides a mechanism to prevent concurrent executions of Lambda functions that could lead to race conditions or duplicate processing. This library is particularly useful for distributed applications where Lambda functions are triggered in response to events and require coordination or state management.

## Features

- **Atomic Execution**: Ensures that only one instance of a Lambda function processes a specific task at a time.
- **Status Management**: Tracks the execution status of tasks in DynamoDB, marking them as in progress or finished.
- **Timeout Handling**: Supports time-based expiry for task locks, making it resilient to failures or stalls in execution.
- **Easy Integration**: Designed to be easily integrated into existing AWS Lambda functions with minimal configuration.

## Installation

Install `LambdaDynamoLock` using pip:

```bash
pip install lambda_dynamo_lock
```

## Prerequisites
An AWS account and AWS CLI configured with DynamoDB access.
A DynamoDB table set up for tracking execution statuses.

# Usage
Below is a quick example to help you get started:

```bash
from lambda_dynamo_lock import LambdaDynamoLock
import os

# DynamoDB table and primary key
TABLE_NAME = 'YourDynamoDBTableName'
PRIMARY_KEY = 'YourPrimaryKey'

# Initialize LambdaDynamoLock
ldl = LambdaDynamoLock(
    table_name=TABLE_NAME,
    primary_key=PRIMARY_KEY,
    region_name="eu-west-1",
    endpoint_url="http://docker.for.mac.localhost:8000/" if os.environ.get("AWS_SAM_LOCAL") else None
)

# Attempt to write a lock key for today's date
date_to_run = '2023-01-01'

# delete items in Dynamo for old executions
ldl.delete_items_finished_or_old(keys=[date_to_run], item_execution_valid_for=20)

# write in Dynamo the date_to_run and block other executions to the same key
result = ldl.write_atomically_a_key(key=date_to_run)

if result:
    # If lock is acquired, perform your task
    print("Lock acquired, proceeding with task.")
    ## run_your_etl(date_to_run)
    # Remember to update the status to 'finished' after completing your task
    ldl.update_status(key=date_to_run)
else:
    # If lock couldn't be acquired, another instance is already processing the task
    print("Task already in progress by another instance.")
    # wait until other instances with the same key finish
    ldl.wait_other_instances_finish(keys=[date_to_run])
```

## Configuration

LambdaDynamoLock can be configured with several parameters at initialization to fit your needs:

**table_name:** Name of the DynamoDB table used for tracking execution.
**primary_key:** The primary key attribute name in your DynamoDB table.
**region_name:** AWS region where your DynamoDB table is located.
**endpoint_url:** Custom endpoint URL, useful for local testing with DynamoDB Local.


### Additional method parameters:


- `delete_items_finished_or_old` method:
  - **item_execution_valid_for** (optional, default=20): Time in minutes to consider an execution old enough to be deleted.
- `wait_other_instances_finish` method:
  - **timeout** (optional): Maximum time in seconds to wait for the 'finished' status.
  - **time_to_retry** (optional): Time in seconds to wait before trying to validate the status again.


## Support and Contact

Having trouble with `LambdaDynamoLock`? Check out our [GitHub issues](https://github.com/jdaarevalo/lambda_dynamo_lock/issues) or contact support and we’ll help you sort it out. Feel free to wirte a message to jdaarevalo@gmail.com


## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request on GitHub.

## License
This project is licensed under the MIT License - see the LICENSE file for details.