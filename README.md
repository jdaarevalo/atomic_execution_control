# AtomicExecutionControl

`AtomicExecutionControl` is a Python library crafted to address the complexities of ensuring atomic operations across distributed applications, particularly those deployed on AWS services like Lambda, Fargate, and EC2. By leveraging DynamoDB, this library offers a robust mechanism to prevent concurrent executions, thus mitigating race conditions and duplicate processing risks. Whether you're handling event-driven workflows, orchestrating microservices, or ensuring data integrity across distributed systems, `AtomicExecutionControl` simplifies state management and execution coordination, making your applications more reliable, efficient and most important 'atomic'.



## Features

- **Atomic Execution**: Ensures that only one instance of a the function processes a specific task at a time.
- **Status Management**: Tracks the execution status of tasks in DynamoDB, marking them as in progress or finished.
- **Timeout Handling**: Supports time-based expiry for task locks, making it resilient to failures or stalls in execution.
- **Easy Integration**: Designed to be easily integrated into existing AWS Lambda, Fargate or EC2 functions with minimal configuration.

## Installation

Install `AtomicExecutionControl` using pip:

```bash
pip install atomic_execution_control
```

## Prerequisites
An AWS account and AWS CLI configured with DynamoDB access.
A DynamoDB table set up for tracking execution statuses.

# Usage
Below is a quick example to help you get started:

```python
from atomic_execution_control import AtomicExecutionControl
import os

# DynamoDB table and primary key
TABLE_NAME = 'YourDynamoDBTableName'
PRIMARY_KEY = 'YourPrimaryKey'

# Initialize AtomicExecutionControl
aec = AtomicExecutionControl(
    table_name=TABLE_NAME,
    primary_key=PRIMARY_KEY,
    region_name="eu-west-1",
    endpoint_url="http://docker.for.mac.localhost:8000/" if os.environ.get("AWS_SAM_LOCAL") else None
)

# Attempt to write a lock key for today's date
date_to_run = '2023-01-01'

# delete items in Dynamo for old executions
aec.delete_items_finished_or_old(keys=[date_to_run], item_execution_valid_for=20)

# write in Dynamo the date_to_run and block other executions to the same key
result = aec.write_atomically_a_key(key=date_to_run)

if result:
    # If lock is acquired, perform your task
    
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


## Support and Contact

If you encounter any issues or have questions about `AtomicExecutionControl`, don't hesitate to reach out. You can [file an issue](https://github.com/jdaarevalo/atomic_execution_control/issues) on our GitHub repository or email us directly at jdaarevalo@gmail.com. We're also open to feedback and suggestions to make `AtomicExecutionControl` even better!


## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request on GitHub.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
