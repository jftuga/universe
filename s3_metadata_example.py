
import boto3
import sys

bucket="example-bucket"
key="example-key"

include = [ '_', '.', '/', '=', '+', '-', ' ', '@', ':']

s = ""
for i in range(0,127):
    if chr(i).isalnum():
        s += chr(i)
        continue
    if chr(i) in include:
        s += chr(i)
        continue

print(s, len(s))
print()

client = boto3.client("s3")
response = client.put_object_tagging(Bucket=bucket, Key=key,
                Tagging={ "TagSet": [{"Key": "testing", "Value": s}]})
print(response)
