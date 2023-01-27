import configparser
import os
import json
import boto3
from botocore.exceptions import ClientError

# Get the directory containing the script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Load parameters from config.ini
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, 'config.ini'))
in_file = config.get("openshift", "image_file")
out_file = config.get("ecr", "output_json_file")
sum_file = config.get("ecr", "output_sum_file")
aws_access_key_id = config.get('ecr', 'aws_access_key_id')
aws_secret_access_key = config.get('ecr', 'aws_secret_access_key')
aws_session_token= config.get('ecr', 'aws_session_token')
aws_region = config.get('ecr', 'aws_region')

# Create an ECR client
ecr_client = boto3.client('ecr', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token, region_name=aws_region)

# Load the JSON file
with open(in_file, 'r') as f:
    data = json.load(f)

results = []
# Iterate over the JSON blocks
for block in data:
    try:
        # Pass the block to the `describe_images` method
        response = ecr_client.describe_images(**block)
        for item in response['imageDetails']:
            results.append({
                'registryId': item['registryId'],
                'repositoryName': item['repositoryName'],
                'imageDigest': item['imageDigest'],
                'imageTags': item['imageTags'],
                'imageSizeInBytes': item['imageSizeInBytes']
            })
        total_size_bytes = sum(single_image['imageSizeInBytes'] for single_image in results)
        total_size_gb = total_size_bytes / (1024 ** 3)
    except ClientError as e:
        if e.response['Error']['Code'] == 'RepositoryNotFoundException':
            print(f"Error: {block['repositoryName']} not found.")
        elif e.response['Error']['Code'] == 'ImageNotFoundException':
            print(f"Error: {block['imageIds'][0]['imageTag']} not found.")
        else:
            raise
    
#save the image report to a json file
json_to_file=json.dumps(results)
with open(out_file, "w") as jsonf:
    jsonf.write(json_to_file)

#save the image total size to a text file
with open(sum_file, "w") as textf:
    textf.write(f"Total image size in bytes: {total_size_bytes}")
    textf.write(f"Total image size in GB: {total_size_gb:.2f}")