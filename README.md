Python scripts to retrieve a list of images deployed in OCP\OKD pulled from a specific AWS ECR Registry. The list can be matched with the images on AWS ECR Registry to retrieve their storage size.
JSON file produced by ocp-list-images-2-file.py is compliant with the definition from the AWS cli command
*aws ecr describe-images --generate-cli-skeleton*

## ocp-list-images-2-file.py
The script queries OpenShift/OKD API server and retrieves the list of all projects accessible by the user. For every project retrieves all pods container images link and filters only the ones from the selected AWS ECR Registry.

*Input*
- API Server address
- API Server authentication token
- AWS ECR Registry address
- Output JSON file name

*Output*
- JSON file

## ecr-list-images-size-2-file.py
The script queries AWS ECR Registry API and retrieves the size of the images.

*Input*
- JSON file name produced by ocp-list-images-2-file.py
- Output JSON file name
- Output txt file name
- AWS access key ID
- AWS secret access key
- AWS session token

*Output*
- JSON file
- TXT file
