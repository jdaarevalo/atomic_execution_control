from setuptools import setup, find_packages

setup(
    name='atomic_execution_control',
    version='0.1.3',
    author='Jose David Arevalo',
    author_email='jdaarevalo@gmail.com',
    description='A utility for atomic DynamoDB operations in AWS Lambda, Fargate, EC2 ... functions',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jdaarevalo/atomic_execution_control',
    packages=find_packages(),
    install_requires=[
        'boto3'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
