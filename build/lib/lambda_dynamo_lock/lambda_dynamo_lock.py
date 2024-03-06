# dynamodb operations to ensure atomic executions
import boto3
import logging
import time
import json

from botocore.exceptions import ClientError
from datetime import datetime, timedelta

# Import Logger from aws_lambda_powertools if available, else define a dummy Logger
try:
    from aws_lambda_powertools import Logger
except ImportError:
    class Logger:
        def __init__(self, *args, **kwargs):
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        def info(self, message):
            self.logger.info(message)

        def warning(self, message):
            self.logger.warning(message)

        def error(self, message):
            self.logger.error(message)

class LambdaDynamoLock:
    def __init__(self, table_name:str, primary_key:str, region_name:str='eu-west-1', endpoint_url:str=None, logger=None):
        self.table_name = table_name
        self.primary_key = primary_key
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.dynamodb_resource = boto3.resource('dynamodb', region_name=self.region_name, endpoint_url=self.endpoint_url)
        self.dynamodb_client = boto3.client('dynamodb', region_name=self.region_name, endpoint_url=self.endpoint_url)
        self.table = self.dynamodb_resource.Table(self.table_name)
        self.ITEM_EXECUTION_VALID_FOR = 20 # minutes
        self.TIME_TO_RETRY_CHECK_STATUS = 20 # seconds
        self.MAX_TIME_TO_CHECK_STATUS = 840 # seconds
        self.STATUS_EXECUTION_FINISHED = "FINISHED"
        self.STATUS_EXECUTION_IN_PROGRESS = "IN_PROGRESS"
        # Initialize or use the provided logger
        self.logger = logger if logger else Logger()

    def _log(self, level, message, **kwargs):
        if hasattr(self.logger, 'structure_logs'):  # Check if aws_lambda_powertools.Logger
            structured_message = {**message, **kwargs}
            getattr(self.logger, level)(structured_message)
        else:  # Fallback to standard logging
            log_message = json.dumps({"message": message, **kwargs})
            getattr(logging, level)(log_message)

    # method to write atomically a primary_key
    def write_atomically_a_key(self, key:str, status:str = None) -> bool:
        timestamp_now = datetime.now().isoformat()
        status = status if status else self.STATUS_EXECUTION_IN_PROGRESS
        item = {
                f"{self.primary_key}": key,
                "status_execution": status,
                'created_at': timestamp_now,
                'updated_at': timestamp_now
            }

        try:
            self.table.put_item(
                Item=item,
                ConditionExpression=f'attribute_not_exists({self.primary_key})'
            )
        except ClientError as exception:
            if exception.response['Error']['Code'] == 'ConditionalCheckFailedException':
                self.logger.warning({
                    "message": "Conditional check failed, item already exists",
                    "key": key,
                    "status": status,
                    "action": "conditional_check_failed_exception"
                })
                return False
            else:
                self.logger.error({
                    "message": "Error writing atomically to DynamoDB",
                    "error": exception.response['Error']['Message'],
                    "key": key,
                    "status": status,
                    "action": "write_atomically_a_key"
                })
                raise
        else:
            self.logger.info({
                "message": "Successfully wrote key atomically",
                "key": key,
                "status": status,
                "action": "write_atomically_a_key"
            })
            return True

    #method to delete items based on their status_execution and updated_at values
    def delete_items_finished_or_old(self, keys: list[str], item_execution_valid_for:int=None) -> None:
        item_execution_valid_for = item_execution_valid_for if item_execution_valid_for else self.ITEM_EXECUTION_VALID_FOR
        self.logger.info({"action": "delete_items_finished_or_old", "keys": keys, "message":"start items deletion"})
        
        items = self.get_items(keys)   
        items_to_delete = [item[f'{self.primary_key}'] for item in items if self.is_item_deletable(item, item_execution_valid_for)]
        self.logger.info({"action": "items_to_delete", "items": items_to_delete})
        self.delete_items(items_to_delete)

    # method to get batch items based on a list of keys
    def get_items(self, keys: list[str]) -> list[dict]:
        keys = [{f'{self.primary_key}': {'S': key}} for key in keys]
        self.logger.info({"action": "get_items", "keys":keys})
        try:
            response = self.dynamodb_client.batch_get_item(
                RequestItems={
                    self.table_name: {
                        'Keys': keys
                    }
                }
            )
            # Extract item from the response
            items = response['Responses'][self.table_name]
            # Format and return items
            return [{k: list(v.values())[0] for k, v in item.items()} for item in items]
            
        except Exception as e:
            self.logger.error({"action": "get_items_error", "error": e, "keys": keys})
            raise

    # method to check if an item is deletable based on its status_execution and updated_at values
    def is_item_deletable(self, item:str, item_execution_valid_for:int) -> bool:
        self.logger.info({"action": "is_item_deletable", "item": item})
        status_execution = item.get('status_execution')
        updated_at_str = item.get('updated_at')
        updated_at = datetime.strptime(updated_at_str, "%Y-%m-%dT%H:%M:%S.%f")
        time_limit = datetime.now() - timedelta(minutes=item_execution_valid_for)
        #an item could be deleted after item_execution_valid_for min or if the status is STATUS_EXECUTION_FINISHED
        return status_execution == self.STATUS_EXECUTION_FINISHED or updated_at < time_limit

    # method to delete keys
    def delete_items(self, keys: list[str]) -> None:
        self.logger.info({"action": "delete_items", "primary_keys": keys})
        if not keys:
            return
        # delete items one by one to avoid exceeding the provisioned throughput of the table
        for key in keys:
            self.table.delete_item(
                Key={f'{self.primary_key}': key}
            )

    # method to update the status_execution of a primary_key
    def update_status(self, key:str, new_status:str = None) -> None:
        self.logger.info({"action": "update_status", "key": key, "new_status": new_status})
        new_status = new_status if new_status else self.STATUS_EXECUTION_FINISHED
        timestamp_now = datetime.now().isoformat()
        
        self.table.update_item(
            Key={f"{self.primary_key}": key},
            UpdateExpression='SET updated_at = :updateVal, status_execution = :statusVal',
            ExpressionAttributeValues={
                ':updateVal': timestamp_now,
                ':statusVal': new_status
            }
        )

    # method to wait for all instances to finish
    def wait_other_instances_finish(self, keys: list[str], timeout:int=None, time_to_retry:int=None):
        start_time = time.time()
        remaining_ids = keys.copy()
        timeout = timeout if timeout else self.MAX_TIME_TO_CHECK_STATUS
        time_to_retry = time_to_retry if time_to_retry else self.TIME_TO_RETRY_CHECK_STATUS
        
        while remaining_ids and (time.time() - start_time) < timeout:
            for key in remaining_ids.copy():
                try:
                    response = self.table.get_item(Key={f'{self.primary_key}': key})
                    if 'Item' in response and response['Item']['status_execution'] == self.STATUS_EXECUTION_FINISHED:
                        remaining_ids.remove(key)
                except Exception as e:
                    self.logger.error({"action": "wait_for_all_executions_to_finish_error", "error": e, "key":key})
                    raise
            if remaining_ids:
                self.logger.info({"action": "wait_for_all_executions_to_finish", "remaining_ids": remaining_ids})
                time.sleep(time_to_retry)

        if not remaining_ids:
            self.logger.info({"action": "all_executions_finished"})
            return True
        else:
            self.logger.error({"action": "all_executions_not_finished", "remaining_ids": remaining_ids})
            return False
