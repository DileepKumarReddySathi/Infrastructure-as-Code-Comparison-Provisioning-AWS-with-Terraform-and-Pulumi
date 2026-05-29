import pulumi
import pulumi_aws as aws
import json

# Create the VPC
vpc = aws.ec2.Vpc("app-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    tags={"Name": "app-vpc-pulumi"}
)

# Create the public subnet
subnet = aws.ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    tags={"Name": "public-subnet-pulumi"}
)

# Internet Gateway
igw = aws.ec2.InternetGateway("app-igw",
    vpc_id=vpc.id,
    tags={"Name": "app-igw-pulumi"}
)

# Route Table
route_table = aws.ec2.RouteTable("public-rt",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id,
        )
    ],
    tags={"Name": "public-rt-pulumi"}
)

# Route Table Association
rta = aws.ec2.RouteTableAssociation("public-rta",
    subnet_id=subnet.id,
    route_table_id=route_table.id
)

# Primary S3 bucket with versioning
main_bucket = aws.s3.Bucket("app-bucket-pulumi",
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    )
)

# IAM Role for EC2 to access S3
ec2_role = aws.iam.Role("ec2-s3-access-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            }
        }]
    })
)

# IAM Policy for S3 PutObject
s3_policy = aws.iam.RolePolicy("s3-put-policy",
    role=ec2_role.id,
    policy=main_bucket.arn.apply(lambda arn: json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["s3:PutObject"],
            "Effect": "Allow",
            "Resource": f"{arn}/*"
        }]
    }))
)

# IAM Instance Profile
instance_profile = aws.iam.InstanceProfile("ec2-s3-profile",
    role=ec2_role.name
)

# Security Group
web_sg = aws.ec2.SecurityGroup("web-sg",
    vpc_id=vpc.id,
    description="Allow HTTP and SSH",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp', from_port=80, to_port=80, cidr_blocks=['0.0.0.0/0']
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp', from_port=22, to_port=22, cidr_blocks=['0.0.0.0/0']
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol='-1', from_port=0, to_port=0, cidr_blocks=['0.0.0.0/0']
        )
    ],
    tags={"Name": "web-sg-pulumi"}
)

# EC2 Instance
user_data_script = """#!/bin/bash
yum update -y
yum install -y docker
service docker start
usermod -a -G docker ec2-user
"""

app_server = aws.ec2.Instance("app-server",
    instance_type="t2.micro",
    ami="ami-0c55b159cbfafe1f0", # Amazon Linux 2023 AMI
    subnet_id=subnet.id,
    vpc_security_group_ids=[web_sg.id],
    iam_instance_profile=instance_profile.name,
    user_data=user_data_script,
    tags={"Name": "app-server-pulumi"}
)

# Dynamic Resource Creation for logging buckets
environments = ["dev", "staging", "prod"]
buckets = {}
for env in environments:
    bucket_name = f"myapp-logs-{env}"
    buckets[env] = aws.s3.Bucket(f"logs-{env}",
        bucket=bucket_name,
        tags={"Environment": env}
    )

# Exports
pulumi.export('instance_public_ip', app_server.public_ip)
