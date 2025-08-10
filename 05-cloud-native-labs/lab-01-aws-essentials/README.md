# Lab 01: AWS Essentials

## 🎯 Lab Scenario
**PhotoShare Inc.** is a startup building the next Instagram. They have 10,000 users and growing fast. Currently running on a single server that crashes during peak hours. The CEO says: "We need to scale to 1 million users in 6 months, but we only have $5,000/month budget. Can AWS help?"

Your mission: Migrate PhotoShare from a single server to a scalable, highly available AWS architecture while staying within budget.

## 📸 The PhotoShare Story
**Week 1**: "Our server crashed during a viral moment - lost 1000 new users!"  
**Week 2**: "Storage full! Where do we put user photos?"  
**Week 3**: "Database is slow, queries taking 30 seconds"  
**Week 4**: "We're trending! Traffic increased 10x overnight"  
**Week 5**: "Security breach - user data exposed!"  
**Week 6**: "AWS bill is $15,000! We're going bankrupt!"

## 🎓 What You'll Learn
1. **Core AWS Services**: EC2, S3, RDS, VPC, IAM
2. **High Availability**: Multi-AZ deployments, load balancing
3. **Storage Solutions**: Object storage, block storage, databases
4. **Security Fundamentals**: IAM roles, security groups, encryption
5. **Cost Management**: Right-sizing, reserved instances, cost alerts
6. **Monitoring**: CloudWatch metrics, alarms, logs

## 🌟 Real-World Skills
After this lab, you'll be able to:
- Migrate applications to AWS
- Design for 99.99% availability
- Handle 1000x traffic spikes
- Reduce costs by 70%
- Implement security best practices
- Set up monitoring and alerting

## ⏱️ Duration: 60 minutes

## 💰 Cost Estimate
- **During Lab**: ~$2 (using free tier mostly)
- **If Left Running**: ~$150/month
- **After Optimization**: ~$50/month

## 🏗️ Architecture Evolution

### Current State: Single Server Chaos
```
Internet → Single Server (Everything)
         - Web Server
         - Database
         - File Storage
         - No Backups 😱
```

### Target State: Cloud-Native Architecture
```
                     Route 53 (DNS)
                           │
                      CloudFront
                           │
                    ELB (Load Balancer)
                     /            \
                EC2-1              EC2-2
              (Auto Scaling)    (Auto Scaling)
                     \            /
                      RDS MySQL
                    (Multi-AZ)
                          │
                     S3 (Photos)
                          │
                CloudWatch (Monitoring)
```

## 📝 Part 1: Foundation - VPC and Networking

### Understanding the Business Need
PhotoShare needs network isolation for security compliance and future growth.

### Step 1.1: Create VPC with Public/Private Subnets

Create `infrastructure/vpc.yaml` (CloudFormation):
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'PhotoShare VPC - Network Foundation'

Parameters:
  EnvironmentName:
    Description: Environment name prefix
    Type: String
    Default: PhotoShare-Dev

Mappings:
  SubnetConfig:
    VPC:
      CIDR: 10.0.0.0/16
    PublicSubnet1:
      CIDR: 10.0.1.0/24
    PublicSubnet2:
      CIDR: 10.0.2.0/24
    PrivateSubnet1:
      CIDR: 10.0.10.0/24
    PrivateSubnet2:
      CIDR: 10.0.11.0/24

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !FindInMap [SubnetConfig, VPC, CIDR]
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-VPC
        - Key: Purpose
          Value: PhotoShare Application Network

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-IGW

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # Public Subnets
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: !FindInMap [SubnetConfig, PublicSubnet1, CIDR]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-Public-Subnet-1
        - Key: Type
          Value: Public

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: !FindInMap [SubnetConfig, PublicSubnet2, CIDR]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-Public-Subnet-2
        - Key: Type
          Value: Public

  # Private Subnets
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: !FindInMap [SubnetConfig, PrivateSubnet1, CIDR]
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-Private-Subnet-1
        - Key: Type
          Value: Private

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: !FindInMap [SubnetConfig, PrivateSubnet2, CIDR]
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-Private-Subnet-2
        - Key: Type
          Value: Private

  # NAT Gateways
  NatGateway1EIP:
    Type: AWS::EC2::EIP
    DependsOn: AttachGateway
    Properties:
      Domain: vpc

  NatGateway1:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatGateway1EIP.AllocationId
      SubnetId: !Ref PublicSubnet1

  # Route Tables
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-Public-Routes

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet1
      RouteTableId: !Ref PublicRouteTable

  PublicSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet2
      RouteTableId: !Ref PublicRouteTable

  PrivateRouteTable1:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-Private-Routes-1

  PrivateRoute1:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway1

  PrivateSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet1
      RouteTableId: !Ref PrivateRouteTable1

  PrivateSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet2
      RouteTableId: !Ref PrivateRouteTable1

Outputs:
  VPC:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub ${EnvironmentName}-VPC

  PublicSubnets:
    Description: Public subnet IDs
    Value: !Join [",", [!Ref PublicSubnet1, !Ref PublicSubnet2]]
    Export:
      Name: !Sub ${EnvironmentName}-PublicSubnets

  PrivateSubnets:
    Description: Private subnet IDs
    Value: !Join [",", [!Ref PrivateSubnet1, !Ref PrivateSubnet2]]
    Export:
      Name: !Sub ${EnvironmentName}-PrivateSubnets
```

### Step 1.2: Deploy the VPC

Create `scripts/deploy-vpc.sh`:
```bash
#!/bin/bash

STACK_NAME="photoshare-vpc"
TEMPLATE_FILE="infrastructure/vpc.yaml"
REGION="us-east-1"

echo "🚀 Deploying PhotoShare VPC..."

# Validate template
aws cloudformation validate-template \
    --template-body file://$TEMPLATE_FILE \
    --region $REGION

# Deploy stack
aws cloudformation deploy \
    --template-file $TEMPLATE_FILE \
    --stack-name $STACK_NAME \
    --parameter-overrides EnvironmentName=PhotoShare-Dev \
    --region $REGION \
    --capabilities CAPABILITY_IAM

# Get outputs
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs' \
    --region $REGION \
    --output table

echo "✅ VPC deployment complete!"
```

## 📝 Part 2: Compute - EC2 and Auto Scaling

### Business Need
PhotoShare needs servers that automatically scale based on traffic.

### Step 2.1: Create Launch Template and Auto Scaling

Create `infrastructure/compute.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'PhotoShare Compute - EC2 Auto Scaling'

Parameters:
  EnvironmentName:
    Type: String
    Default: PhotoShare-Dev
  
  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
    Description: EC2 instance type (t3.micro = free tier)

  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 Key Pair for SSH access

Resources:
  # Security Group
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for PhotoShare web servers
      VpcId: 
        Fn::ImportValue: !Sub ${EnvironmentName}-VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/16  # Only from VPC
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-WebServer-SG

  # IAM Role for EC2
  EC2Role:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
      Policies:
        - PolicyName: S3Access
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:DeleteObject
                Resource: !Sub 'arn:aws:s3:::photoshare-uploads-${AWS::AccountId}/*'
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-EC2-Role

  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref EC2Role

  # Launch Template
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: !Sub ${EnvironmentName}-LaunchTemplate
      LaunchTemplateData:
        ImageId: ami-0c02fb55731490381  # Amazon Linux 2
        InstanceType: !Ref InstanceType
        KeyName: !Ref KeyName
        IamInstanceProfile:
          Arn: !GetAtt EC2InstanceProfile.Arn
        SecurityGroupIds:
          - !Ref WebServerSecurityGroup
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash
            yum update -y
            yum install -y httpd
            
            # Install Node.js
            curl -sL https://rpm.nodesource.com/setup_16.x | sudo bash -
            yum install -y nodejs
            
            # Install PhotoShare application
            mkdir -p /var/www/photoshare
            cd /var/www/photoshare
            
            # Create simple Node.js app
            cat > app.js << 'EOF'
            const express = require('express');
            const app = express();
            const port = 3000;
            
            app.get('/', (req, res) => {
              res.send(`
                <h1>PhotoShare</h1>
                <p>Instance ID: ${require('os').hostname()}</p>
                <p>Region: ${AWS::Region}</p>
                <p>Environment: ${EnvironmentName}</p>
              `);
            });
            
            app.get('/health', (req, res) => {
              res.status(200).send('OK');
            });
            
            app.listen(port, () => {
              console.log(`PhotoShare running on port ${port}`);
            });
            EOF
            
            npm install express
            
            # Setup systemd service
            cat > /etc/systemd/system/photoshare.service << EOF
            [Unit]
            Description=PhotoShare Application
            After=network.target
            
            [Service]
            Type=simple
            User=ec2-user
            WorkingDirectory=/var/www/photoshare
            ExecStart=/usr/bin/node app.js
            Restart=on-failure
            
            [Install]
            WantedBy=multi-user.target
            EOF
            
            systemctl enable photoshare
            systemctl start photoshare
            
            # Setup Apache as reverse proxy
            cat > /etc/httpd/conf.d/photoshare.conf << EOF
            <VirtualHost *:80>
                ProxyPreserveHost On
                ProxyPass / http://localhost:3000/
                ProxyPassReverse / http://localhost:3000/
            </VirtualHost>
            EOF
            
            systemctl enable httpd
            systemctl start httpd
            
            # CloudWatch agent
            wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
            rpm -U ./amazon-cloudwatch-agent.rpm
        TagSpecifications:
          - ResourceType: instance
            Tags:
              - Key: Name
                Value: !Sub ${EnvironmentName}-Instance
              - Key: Environment
                Value: !Ref EnvironmentName

  # Application Load Balancer
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub ${EnvironmentName}-ALB
      Subnets: !Split
        - ','
        - Fn::ImportValue: !Sub ${EnvironmentName}-PublicSubnets
      SecurityGroups:
        - !Ref WebServerSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-ALB

  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub ${EnvironmentName}-TG
      Port: 80
      Protocol: HTTP
      VpcId:
        Fn::ImportValue: !Sub ${EnvironmentName}-VPC
      HealthCheckPath: /health
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-TG

  ALBListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup

  # Auto Scaling Group
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub ${EnvironmentName}-ASG
      VPCZoneIdentifier: !Split
        - ','
        - Fn::ImportValue: !Sub ${EnvironmentName}-PrivateSubnets
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      MinSize: 2
      MaxSize: 10
      DesiredCapacity: 2
      TargetGroupARNs:
        - !Ref TargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-ASG-Instance
          PropagateAtLaunch: true

  # Auto Scaling Policies
  ScaleUpPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref AutoScalingGroup
      PolicyType: SimpleScaling
      AdjustmentType: ChangeInCapacity
      ScalingAdjustment: 1
      Cooldown: 300

  ScaleDownPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref AutoScalingGroup
      PolicyType: SimpleScaling
      AdjustmentType: ChangeInCapacity
      ScalingAdjustment: -1
      Cooldown: 300

  # CloudWatch Alarms
  CPUAlarmHigh:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${EnvironmentName}-CPU-High
      AlarmDescription: Scale up when CPU exceeds 70%
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Statistic: Average
      Period: 300
      EvaluationPeriods: 1
      Threshold: 70
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref AutoScalingGroup
      AlarmActions:
        - !Ref ScaleUpPolicy

  CPUAlarmLow:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${EnvironmentName}-CPU-Low
      AlarmDescription: Scale down when CPU is below 30%
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 30
      ComparisonOperator: LessThanThreshold
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref AutoScalingGroup
      AlarmActions:
        - !Ref ScaleDownPolicy

Outputs:
  LoadBalancerURL:
    Description: URL of the Application Load Balancer
    Value: !Sub http://${ApplicationLoadBalancer.DNSName}
    Export:
      Name: !Sub ${EnvironmentName}-ALB-URL

  AutoScalingGroup:
    Description: Auto Scaling Group Name
    Value: !Ref AutoScalingGroup
    Export:
      Name: !Sub ${EnvironmentName}-ASG
```

## 📝 Part 3: Storage - S3 for Photos

### Business Need
PhotoShare needs unlimited storage for millions of user photos.

Create `infrastructure/storage.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'PhotoShare Storage - S3 and CloudFront'

Parameters:
  EnvironmentName:
    Type: String
    Default: PhotoShare-Dev

Resources:
  # S3 Bucket for uploads
  PhotoBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub photoshare-uploads-${AWS::AccountId}
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Id: MoveToIA
            Status: Enabled
            Transitions:
              - StorageClass: STANDARD_IA
                TransitionInDays: 30
              - StorageClass: GLACIER
                TransitionInDays: 90
          - Id: DeleteOldVersions
            Status: Enabled
            NoncurrentVersionExpirationInDays: 30
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-Photos
        - Key: Purpose
          Value: User uploaded photos

  # CloudFront Distribution
  CloudFrontOriginAccessIdentity:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: !Sub OAI for ${EnvironmentName}

  PhotoBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref PhotoBucket
      PolicyDocument:
        Statement:
          - Sid: AllowCloudFrontAccess
            Effect: Allow
            Principal:
              Service: cloudfront.amazonaws.com
            Action: s3:GetObject
            Resource: !Sub ${PhotoBucket.Arn}/*
            Condition:
              StringEquals:
                AWS:SourceArn: !Sub arn:aws:cloudfront::${AWS::AccountId}:distribution/${CloudFrontDistribution}

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Enabled: true
        Comment: !Sub ${EnvironmentName} Photo CDN
        DefaultRootObject: index.html
        Origins:
          - Id: S3Origin
            DomainName: !GetAtt PhotoBucket.RegionalDomainName
            S3OriginConfig:
              OriginAccessIdentity: !Sub origin-access-identity/cloudfront/${CloudFrontOriginAccessIdentity}
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
          CachedMethods:
            - GET
            - HEAD
          Compress: true
          ForwardedValues:
            QueryString: false
            Cookies:
              Forward: none
        PriceClass: PriceClass_100
        ViewerCertificate:
          CloudFrontDefaultCertificate: true
        Tags:
          - Key: Name
            Value: !Sub ${EnvironmentName}-CDN

Outputs:
  BucketName:
    Description: S3 Bucket Name
    Value: !Ref PhotoBucket
    Export:
      Name: !Sub ${EnvironmentName}-PhotoBucket

  CloudFrontURL:
    Description: CloudFront Distribution URL
    Value: !GetAtt CloudFrontDistribution.DomainName
    Export:
      Name: !Sub ${EnvironmentName}-CDN-URL
```

## 📝 Part 4: Database - RDS MySQL

### Business Need
PhotoShare needs a managed database that handles backups and scaling automatically.

Create `infrastructure/database.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'PhotoShare Database - RDS MySQL'

Parameters:
  EnvironmentName:
    Type: String
    Default: PhotoShare-Dev
  
  DBInstanceClass:
    Type: String
    Default: db.t3.micro
    Description: RDS instance type (db.t3.micro = free tier)
  
  MasterUsername:
    Type: String
    Default: admin
    Description: Database master username
  
  MasterPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    Description: Database master password (min 8 characters)

Resources:
  # DB Subnet Group
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupName: !Sub ${EnvironmentName}-db-subnet-group
      DBSubnetGroupDescription: Subnet group for PhotoShare database
      SubnetIds: !Split
        - ','
        - Fn::ImportValue: !Sub ${EnvironmentName}-PrivateSubnets
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-DBSubnetGroup

  # Security Group for Database
  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for PhotoShare database
      VpcId:
        Fn::ImportValue: !Sub ${EnvironmentName}-VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref WebServerSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-Database-SG

  # RDS MySQL Instance
  Database:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    Properties:
      DBInstanceIdentifier: !Sub ${EnvironmentName}-mysql
      Engine: mysql
      EngineVersion: '8.0.28'
      DBInstanceClass: !Ref DBInstanceClass
      AllocatedStorage: 20
      StorageType: gp2
      StorageEncrypted: true
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterPassword
      DBName: photoshare
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      DBSubnetGroupName: !Ref DBSubnetGroup
      BackupRetentionPeriod: 7
      PreferredBackupWindow: "03:00-04:00"
      PreferredMaintenanceWindow: "sun:04:00-sun:05:00"
      MultiAZ: false  # Set to true for production
      EnableCloudwatchLogsExports:
        - error
        - general
        - slowquery
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-MySQL

  # Read Replica (for production)
  # DatabaseReadReplica:
  #   Type: AWS::RDS::DBInstance
  #   Properties:
  #     SourceDBInstanceIdentifier: !Ref Database
  #     DBInstanceClass: !Ref DBInstanceClass

Outputs:
  DatabaseEndpoint:
    Description: Database endpoint
    Value: !GetAtt Database.Endpoint.Address
    Export:
      Name: !Sub ${EnvironmentName}-DatabaseEndpoint

  DatabasePort:
    Description: Database port
    Value: !GetAtt Database.Endpoint.Port
    Export:
      Name: !Sub ${EnvironmentName}-DatabasePort
```

## 📝 Part 5: Monitoring and Alerts

Create `infrastructure/monitoring.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'PhotoShare Monitoring - CloudWatch Dashboards and Alarms'

Parameters:
  EnvironmentName:
    Type: String
    Default: PhotoShare-Dev
  
  EmailAddress:
    Type: String
    Description: Email for notifications

Resources:
  # SNS Topic for Alerts
  AlertTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub ${EnvironmentName}-Alerts
      DisplayName: PhotoShare Alerts
      Subscription:
        - Endpoint: !Ref EmailAddress
          Protocol: email

  # CloudWatch Dashboard
  Dashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub ${EnvironmentName}-Dashboard
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "properties": {
                "metrics": [
                  [ "AWS/EC2", "CPUUtilization", { "stat": "Average" } ],
                  [ ".", "NetworkIn", { "stat": "Sum" } ],
                  [ ".", "NetworkOut", { "stat": "Sum" } ]
                ],
                "period": 300,
                "stat": "Average",
                "region": "${AWS::Region}",
                "title": "EC2 Metrics"
              }
            },
            {
              "type": "metric",
              "properties": {
                "metrics": [
                  [ "AWS/RDS", "DatabaseConnections" ],
                  [ ".", "CPUUtilization" ],
                  [ ".", "FreeableMemory" ]
                ],
                "period": 300,
                "stat": "Average",
                "region": "${AWS::Region}",
                "title": "RDS Metrics"
              }
            }
          ]
        }

  # High CPU Alarm
  HighCPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${EnvironmentName}-HighCPU
      AlarmDescription: Alert when CPU exceeds 80%
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic

  # Database Connection Alarm
  DatabaseConnectionAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${EnvironmentName}-HighDBConnections
      AlarmDescription: Alert when database connections exceed 80
      MetricName: DatabaseConnections
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 1
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic

  # Billing Alarm
  BillingAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${EnvironmentName}-BillingAlert
      AlarmDescription: Alert when estimated charges exceed $100
      MetricName: EstimatedCharges
      Namespace: AWS/Billing
      Statistic: Maximum
      Period: 86400
      EvaluationPeriods: 1
      Threshold: 100
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic
      Dimensions:
        - Name: Currency
          Value: USD
```

## 🚀 Deployment Scripts

Create `scripts/deploy-all.sh`:
```bash
#!/bin/bash

echo "🚀 Deploying PhotoShare Infrastructure..."

# Set variables
REGION="us-east-1"
KEY_NAME="photoshare-key"
EMAIL="your-email@example.com"

# Create SSH key if it doesn't exist
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME --region $REGION 2>/dev/null; then
    echo "Creating SSH key pair..."
    aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > $KEY_NAME.pem
    chmod 400 $KEY_NAME.pem
fi

# Deploy VPC
echo "1️⃣ Deploying VPC..."
aws cloudformation deploy \
    --template-file infrastructure/vpc.yaml \
    --stack-name photoshare-vpc \
    --parameter-overrides EnvironmentName=PhotoShare-Dev \
    --region $REGION

# Deploy Storage
echo "2️⃣ Deploying Storage..."
aws cloudformation deploy \
    --template-file infrastructure/storage.yaml \
    --stack-name photoshare-storage \
    --parameter-overrides EnvironmentName=PhotoShare-Dev \
    --region $REGION

# Deploy Database
echo "3️⃣ Deploying Database..."
read -s -p "Enter database password: " DB_PASSWORD
echo
aws cloudformation deploy \
    --template-file infrastructure/database.yaml \
    --stack-name photoshare-database \
    --parameter-overrides \
        EnvironmentName=PhotoShare-Dev \
        MasterPassword=$DB_PASSWORD \
    --region $REGION

# Deploy Compute
echo "4️⃣ Deploying Compute..."
aws cloudformation deploy \
    --template-file infrastructure/compute.yaml \
    --stack-name photoshare-compute \
    --parameter-overrides \
        EnvironmentName=PhotoShare-Dev \
        KeyName=$KEY_NAME \
    --capabilities CAPABILITY_IAM \
    --region $REGION

# Deploy Monitoring
echo "5️⃣ Deploying Monitoring..."
aws cloudformation deploy \
    --template-file infrastructure/monitoring.yaml \
    --stack-name photoshare-monitoring \
    --parameter-overrides \
        EnvironmentName=PhotoShare-Dev \
        EmailAddress=$EMAIL \
    --region $REGION

# Get outputs
echo "✅ Deployment Complete!"
echo ""
echo "📊 Infrastructure Summary:"
ALB_URL=$(aws cloudformation describe-stacks \
    --stack-name photoshare-compute \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
    --output text \
    --region $REGION)

echo "🌐 Application URL: $ALB_URL"
echo "📦 Check your email to confirm SNS subscription for alerts"
```

## 💰 Cost Optimization

Create `scripts/cost-optimize.sh`:
```bash
#!/bin/bash

echo "💰 Analyzing PhotoShare costs..."

# Get current costs
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics "UnblendedCost" \
    --group-by Type=DIMENSION,Key=SERVICE

echo ""
echo "💡 Cost Optimization Recommendations:"
echo "1. Switch to t3.micro instances (save $50/month)"
echo "2. Use S3 Intelligent-Tiering (save $100/month)"
echo "3. Enable RDS auto-stop for dev (save $30/month)"
echo "4. Use Spot instances for batch jobs (save 70%)"
echo "5. Purchase Reserved Instances (save 40%)"

echo ""
echo "🎯 Implementing Quick Wins..."

# Enable S3 Intelligent-Tiering
aws s3api put-bucket-intelligent-tiering-configuration \
    --bucket photoshare-uploads-$(aws sts get-caller-identity --query Account --output text) \
    --id archive-old-photos \
    --intelligent-tiering-configuration '{
        "Id": "archive-old-photos",
        "Status": "Enabled",
        "Tierings": [{
            "Days": 90,
            "AccessTier": "ARCHIVE_ACCESS"
        }]
    }'

echo "✅ Cost optimizations applied!"
```

## 🧹 Cleanup

Create `scripts/cleanup.sh`:
```bash
#!/bin/bash

echo "🧹 Cleaning up PhotoShare infrastructure..."

REGION="us-east-1"

# Delete stacks in reverse order
for stack in photoshare-monitoring photoshare-compute photoshare-database photoshare-storage photoshare-vpc; do
    echo "Deleting $stack..."
    aws cloudformation delete-stack --stack-name $stack --region $REGION
done

# Wait for deletion
echo "Waiting for cleanup to complete..."
aws cloudformation wait stack-delete-complete --stack-name photoshare-vpc --region $REGION

echo "✅ Cleanup complete!"
```

## ✅ Verification Steps

1. **Check VPC Creation**:
```bash
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=PhotoShare-Dev-VPC"
```

2. **Verify Auto Scaling**:
```bash
aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names PhotoShare-Dev-ASG
```

3. **Test Application**:
```bash
curl http://<ALB-DNS-Name>
```

4. **Check CloudWatch Metrics**:
```bash
aws cloudwatch get-metric-statistics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-02T00:00:00Z \
    --period 3600 \
    --statistics Average
```

## 🎓 Learning Outcomes

After completing this lab, you can:
- ✅ Build production-ready AWS infrastructure
- ✅ Implement auto-scaling for cost efficiency
- ✅ Set up monitoring and alerting
- ✅ Use Infrastructure as Code (CloudFormation)
- ✅ Optimize costs (reduced from $15,000 to $50/month!)
- ✅ Handle 1 million users on PhotoShare

## 📚 Additional Resources
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Cost Optimization](https://aws.amazon.com/aws-cost-management/aws-cost-optimization/)
- [CloudFormation Best Practices](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html)