import boto3
from botocore.exceptions import ClientError

from app.application.id_generator.id_incremental_generator import id_generator
from app.application.unit_of_work import UnitOfWork
from app.config import settings
from app.infraestructure.dynamodb_repository import DynamoDBMovieRepository


class DynamoDBUnitOfWork(UnitOfWork):
    def __init__(self):
        self.session = boto3.Session(region_name=settings.AWS_REGION)

        if settings.DDB_ENDPOINT_URL:
            self.dynamodb = self.session.resource('dynamodb', endpoint_url=settings.DDB_ENDPOINT_URL)
        else:
            self.dynamodb = self.session.resource('dynamodb')

        self.table_name = settings.DDB_TABLE_NAME
        self._initialize_table()
        self.table = self.dynamodb.Table(self.table_name)
        self._initialize_id_generator()

    def _initialize_table(self):
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load()
            print(f"Table '{self.table_name}' already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"Creating DynamoDB table '{self.table_name}'...")
                table = self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'id',
                            'KeyType': 'HASH'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'id',
                            'AttributeType': 'N'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )

                table.wait_until_exists()
                print(f"Table '{self.table_name}' created successfully")
            else:
                raise

    def _initialize_id_generator(self):
        try:
            repo = DynamoDBMovieRepository(self.table)
            max_id = repo.get_max_id()
            id_generator.set_current(max_id)
            print(f"ID generator initialized. Starting from: {max_id + 1}")
        except Exception as e:
            print(f"Warning: Could not initialize ID generator: {e}")
            id_generator.set_current(0)

    def __enter__(self):
        self.movies = DynamoDBMovieRepository(self.table)
        return self

    def __exit__(self, *args):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass