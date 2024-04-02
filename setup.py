from setuptools import setup, find_packages

# Dynamic loading of the long description
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='atomic_execution_control',
    version='0.1.5',
    author='Jose David Arevalo',
    author_email='jdaarevalo@gmail.com',
    description='Ensures atomic executions across AWS services using DynamoDB to prevent race conditions in distributed applications.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jdaarevalo/atomic_execution_control',
    packages=find_packages(),
    install_requires=[
        'boto3>=1.14.0'
    ],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='atomic execution, DynamoDB, AWS Lambda, AWS Fargate, EC2, distributed systems, concurrency control, race condition prevention, cloud computing, AWS services, state management',
)
