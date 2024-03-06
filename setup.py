from setuptools import setup, find_packages

setup(
    name='lambda_dynamo_lock',
    version='0.1.1',
    author='Jose David Arevalo',
    author_email='jdaarevalo@gmail.com',
    description='A utility for atomic DynamoDB operations in AWS Lambda functions',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jdaarevalo/lambda_dynamo_lock',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'aws-lambda-powertools'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
