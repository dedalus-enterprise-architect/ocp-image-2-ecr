import json
import configparser
import os
import requests

# Get the directory containing the script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Load parameters from config.ini
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, 'config.ini'))
api_server = config.get("openshift", "api_server")
bearer_token = config.get("openshift", "bearer_token")
desired_registry = config.get("openshift", "registry")
desired_registry_short = config.get("openshift", "registry_short")
image_file = config.get("openshift", "image_file")

# Connect to the OpenShift API server
headers = {
    'Authorization': f'Bearer {bearer_token}'
}
response = requests.get(f"{api_server}/apis/project.openshift.io/v1/projects", headers=headers, verify=False)

# Initialize an empty list to store image information
images = []

# Get all projects the user has access to
if response.status_code == 200:
    projects = json.loads(response.text)["items"]

    # Iterate through all projects
    for project in projects:
        try:
            # Get all pods in the project
            response = requests.get(f"{api_server}/api/v1/namespaces/{project['metadata']['name']}/pods", headers=headers, verify=False)
            if response.status_code == 200:
                pods = json.loads(response.text)["items"]
            # Iterate through all pods
            for pod in pods:
                for container in pod["spec"]["containers"]:
                    container_image = container["image"]
                    # Get the container image information
                    # container_image = pod["spec"]["containers"][0]["image"]
                    # Split the image information into registry, repository, and tag/digest
                    registry = container_image.split("/")[0]
                    #repository = "/".join(container_image.split("/")[1:-1])
                    repository = container_image.split("/", 1)[1].split(":")[0].split("@")[0]
                    if "@" in container_image:
                        digest = container_image.split("@")[-1]
                        tag = ""
                    else:
                        tag = container_image.split(":")[-1]
                        digest = ""
                    # Append the image information to the list
                    # Check if the registry matches the desired registry
                    if registry == desired_registry:
                        if digest == "":
                            images.append({
                                "registryId": desired_registry_short,
                                "repositoryName": repository,
                                "imageIds": [
                                    {
                                        "imageTag": tag
                                    }
                                ],
                                "filter": {
                                    "tagStatus": "ANY"
                                }
                            })
                        else:
                            images.append({
                                "registryId": desired_registry_short,
                                "repositoryName": repository,
                                "imageIds": [
                                    {
                                        "imageDigest": digest
                                    }
                                ],
                                "filter": {
                                    "tagStatus": "ANY"
                                }
                            })
        except Exception as e:
        # Handle the exception if the user does not have access to the project
          print(f"Error getting pods for project {project['metadata']['name']}: {e}")

# Strip duplicates from list
seen = []
for i, image in enumerate(images):
    if any(image == other for j, other in enumerate(seen)):
        continue
    seen.append(image)
images = seen


# Save the image list to a JSON file
json_to_file=json.dumps(images)
with open(image_file, "w") as f:
    f.write(json_to_file)


