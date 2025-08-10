# Lab 04: Modules & Workspaces

## 🎯 Lab Scenario
**Your company "GlobalTech Corp" has grown from 1 to 50 development teams. Each team needs identical infrastructure (VPC, compute, database) but with different configurations. The current approach of copy-pasting Terraform files has led to 500,000 lines of duplicated code, inconsistencies, and maintenance nightmares. You've been asked to lead the infrastructure standardization initiative.**

## 🏢 The Business Problem
Current situation at GlobalTech:
- **50 development teams** each maintaining separate Terraform code
- **3 environments per team** (dev, staging, prod) = 150 deployments
- **Every update** requires changing 150 different files
- **Last security patch** took 3 weeks to roll out
- **Configuration drift** causing production incidents
- **New team onboarding** takes 2 weeks

## 🎓 What You'll Learn
By completing this lab, you will master:
1. **Module Creation**: Build reusable infrastructure components
2. **Module Composition**: Combine modules for complete solutions
3. **Workspace Management**: Handle multiple environments efficiently
4. **Module Versioning**: Control module updates and rollbacks
5. **Testing Strategies**: Validate modules before production
6. **Module Registry**: Share modules across teams
7. **Environment Parity**: Ensure dev matches production

## 🌟 Real-World Skills You'll Gain
After this lab, you'll be able to:
- Reduce infrastructure code by 80% using modules
- Onboard new teams in hours instead of weeks
- Roll out updates to all environments simultaneously
- Maintain consistency across 100+ deployments
- Create company-wide infrastructure standards
- Build a private module registry
- Implement infrastructure testing pipelines

## ⏱️ Duration: 75 minutes

## 📋 Prerequisites
- Completed Labs 01-03
- Understanding of Terraform basics
- Git knowledge helpful
- AWS/Azure credentials

## 🏗️ Architecture
```
From Chaos to Order: The Module Journey
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEFORE (The Problem):
┌──────────────────────────────────────┐
│  Team 1    Team 2    Team 3   ...50  │
│  ↓         ↓         ↓         ↓     │
│  Copy      Copy      Copy      Copy  │
│  Paste     Paste     Paste     Paste │
│  Edit      Edit      Edit      Edit  │
│  ↓         ↓         ↓         ↓     │
│  Drift     Bugs      Errors    Chaos │
└──────────────────────────────────────┘

AFTER (The Solution):
┌──────────────────────────────────────┐
│        Shared Module Registry        │
│  ┌────────────────────────────────┐  │
│  │   terraform-aws-vpc (v2.1.0)   │  │
│  │   terraform-aws-compute (v1.5) │  │
│  │   terraform-aws-rds (v3.0.1)   │  │
│  └────────────────────────────────┘  │
│              ↓                       │
│     Module Composition               │
│  ┌────────────────────────────────┐  │
│  │  Team 1  Team 2  Team 3  ...50 │  │
│  │    ↓       ↓       ↓       ↓   │  │
│  │   dev    dev     dev     dev   │  │
│  │  stage  stage   stage   stage  │  │
│  │   prod   prod    prod    prod  │  │
│  └────────────────────────────────┘  │
│                                      │
│  Benefits:                           │
│  ✓ Single source of truth           │
│  ✓ Version controlled               │
│  ✓ Tested and validated             │
│  ✓ Consistent across teams          │
└──────────────────────────────────────┘

Module Structure:
modules/
├── networking/          # VPC, Subnets, Routes
│   ├── main.tf         # Core logic
│   ├── variables.tf    # Input parameters
│   ├── outputs.tf      # Return values
│   ├── versions.tf     # Provider requirements
│   ├── README.md       # Documentation
│   └── examples/       # Usage examples
├── compute/            # EC2, Auto Scaling
├── database/           # RDS, DynamoDB
├── security/           # IAM, Security Groups
└── monitoring/         # CloudWatch, Alarms
```

## 🎬 The Module Evolution Story

**Week 1**: "Why is Team A's VPC different from Team B's?"  
**Week 2**: "The security fix needs to be applied to 150 configs!"  
**Week 3**: "New team needs infrastructure... copying Team C's code"  
**Week 4**: "Production down! Dev had different settings"  
**Week 5**: "We need infrastructure standards NOW!"

**Your Mission**: Transform chaos into order using Terraform modules and workspaces!

## 📝 Instructions

### Part 1: Understanding the Problem
**The Copy-Paste Nightmare**

Before modules, every team did this:
```hcl
# team1/vpc.tf (5000 lines)
resource "aws_vpc" "main" {
  cidr_block = "10.1.0.0/16"  # Team 1 specific
  # ... 100 more settings
}

# team2/vpc.tf (5000 lines) 
resource "aws_vpc" "main" {
  cidr_block = "10.2.0.0/16"  # Team 2 specific
  # ... 100 more settings (slightly different)
}

# team3/vpc.tf (5000 lines)
# ... and so on for 50 teams
```

**Problems**:
- 250,000 lines of VPC code alone!
- Security update? Edit 50 files
- Bug fix? Good luck finding all instances
- New best practice? 6-month rollout

### Part 2: The Module Solution
**Creating Your First Reusable Module**

#### What Makes a Good Module?
1. **Single Purpose**: Does one thing well (networking OR compute, not both)
2. **Configurable**: Flexible via variables
3. **Predictable**: Consistent outputs
4. **Documented**: Clear usage examples
5. **Versioned**: Controlled releases

Create `modules/networking/variables.tf`:
```hcl
variable "environment" {
  description = "Environment name"
  type        = string
  
  validation {
    condition     = can(regex("^(dev|staging|prod)$", var.environment))
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "public_subnet_count" {
  description = "Number of public subnets"
  type        = number
  default     = 2
  
  validation {
    condition     = var.public_subnet_count >= 1 && var.public_subnet_count <= 3
    error_message = "Public subnet count must be between 1 and 3."
  }
}

variable "private_subnet_count" {
  description = "Number of private subnets"
  type        = number
  default     = 2
}

variable "database_subnet_count" {
  description = "Number of database subnets"
  type        = number
  default     = 2
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use a single NAT Gateway for all private subnets"
  type        = bool
  default     = false
}

variable "enable_vpn_gateway" {
  description = "Enable VPN Gateway"
  type        = bool
  default     = false
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}
```

Create `modules/networking/main.tf`:
```hcl
# Data source for AZs
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs = var.availability_zones != null ? var.availability_zones : data.aws_availability_zones.available.names
  
  # Calculate subnet CIDR blocks
  vpc_cidr_block = var.vpc_cidr
  subnet_bits    = 4
  
  public_subnet_cidrs = [
    for i in range(var.public_subnet_count) :
    cidrsubnet(local.vpc_cidr_block, local.subnet_bits, i)
  ]
  
  private_subnet_cidrs = [
    for i in range(var.private_subnet_count) :
    cidrsubnet(local.vpc_cidr_block, local.subnet_bits, i + var.public_subnet_count)
  ]
  
  database_subnet_cidrs = [
    for i in range(var.database_subnet_count) :
    cidrsubnet(local.vpc_cidr_block, local.subnet_bits, i + var.public_subnet_count + var.private_subnet_count)
  ]
  
  common_tags = merge(
    var.tags,
    {
      Module      = "networking"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-vpc"
    }
  )
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-igw"
    }
  )
}

# Public Subnets
resource "aws_subnet" "public" {
  count = var.public_subnet_count
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_subnet_cidrs[count.index]
  availability_zone       = element(local.azs, count.index)
  map_public_ip_on_launch = true
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-public-subnet-${count.index + 1}"
      Type = "Public"
    }
  )
}

# Private Subnets
resource "aws_subnet" "private" {
  count = var.private_subnet_count
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_subnet_cidrs[count.index]
  availability_zone = element(local.azs, count.index)
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-private-subnet-${count.index + 1}"
      Type = "Private"
    }
  )
}

# Database Subnets
resource "aws_subnet" "database" {
  count = var.database_subnet_count
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.database_subnet_cidrs[count.index]
  availability_zone = element(local.azs, count.index)
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-database-subnet-${count.index + 1}"
      Type = "Database"
    }
  )
}

# Elastic IPs for NAT Gateways
resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : var.public_subnet_count) : 0
  domain = "vpc"
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-eip-${count.index + 1}"
    }
  )
  
  depends_on = [aws_internet_gateway.main]
}

# NAT Gateways
resource "aws_nat_gateway" "main" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : var.public_subnet_count) : 0
  
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-nat-${count.index + 1}"
    }
  )
  
  depends_on = [aws_internet_gateway.main]
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-public-rt"
    }
  )
}

resource "aws_route_table" "private" {
  count  = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : var.private_subnet_count) : 0
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = var.single_nat_gateway ? aws_nat_gateway.main[0].id : aws_nat_gateway.main[count.index].id
  }
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-private-rt-${count.index + 1}"
    }
  )
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count = var.public_subnet_count
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count = var.private_subnet_count
  
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = var.enable_nat_gateway ? (var.single_nat_gateway ? aws_route_table.private[0].id : aws_route_table.private[count.index].id) : aws_route_table.public.id
}

resource "aws_route_table_association" "database" {
  count = var.database_subnet_count
  
  subnet_id      = aws_subnet.database[count.index].id
  route_table_id = var.enable_nat_gateway ? (var.single_nat_gateway ? aws_route_table.private[0].id : aws_route_table.private[0].id) : aws_route_table.public.id
}

# VPC Flow Logs
resource "aws_flow_log" "main" {
  count = var.enable_flow_logs ? 1 : 0
  
  iam_role_arn    = aws_iam_role.flow_logs[0].arn
  log_destination_arn = aws_cloudwatch_log_group.flow_logs[0].arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-flow-logs"
    }
  )
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0
  
  name              = "/aws/vpc/${var.project_name}-${var.environment}"
  retention_in_days = 30
  
  tags = local.common_tags
}

resource "aws_iam_role" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0
  
  name = "${var.project_name}-${var.environment}-flow-logs-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_tags
}

resource "aws_iam_role_policy" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0
  
  name = "${var.project_name}-${var.environment}-flow-logs-policy"
  role = aws_iam_role.flow_logs[0].id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect = "Allow"
        Resource = "*"
      }
    ]
  })
}
```

Create `modules/networking/outputs.tf`:
```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "List of database subnet IDs"
  value       = aws_subnet.database[*].id
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs"
  value       = aws_nat_gateway.main[*].id
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "availability_zones" {
  description = "List of availability zones used"
  value       = local.azs
}

output "public_route_table_id" {
  description = "ID of the public route table"
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "List of private route table IDs"
  value       = aws_route_table.private[*].id
}
```

Create `modules/networking/versions.tf`:
```hcl
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}
```

### Step 2: Create Compute Module

Create `modules/compute/main.tf`:
```hcl
locals {
  common_tags = merge(
    var.tags,
    {
      Module      = "compute"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

# Data source for AMI
data "aws_ami" "app" {
  most_recent = true
  owners      = var.ami_owners
  
  filter {
    name   = "name"
    values = var.ami_name_filter
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Launch Template
resource "aws_launch_template" "app" {
  name_prefix   = "${var.project_name}-${var.environment}-"
  image_id      = var.ami_id != null ? var.ami_id : data.aws_ami.app.id
  instance_type = var.instance_type
  key_name      = var.key_name
  
  vpc_security_group_ids = var.security_group_ids
  
  iam_instance_profile {
    arn = var.iam_instance_profile_arn
  }
  
  user_data = var.user_data_base64
  
  block_device_mappings {
    device_name = "/dev/xvda"
    
    ebs {
      volume_size           = var.root_volume_size
      volume_type           = var.root_volume_type
      delete_on_termination = true
      encrypted             = var.enable_ebs_encryption
      kms_key_id           = var.kms_key_id
    }
  }
  
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }
  
  monitoring {
    enabled = var.enable_monitoring
  }
  
  tag_specifications {
    resource_type = "instance"
    tags = merge(
      local.common_tags,
      {
        Name = "${var.project_name}-${var.environment}-instance"
      }
    )
  }
  
  tag_specifications {
    resource_type = "volume"
    tags = merge(
      local.common_tags,
      {
        Name = "${var.project_name}-${var.environment}-volume"
      }
    )
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "app" {
  name                      = "${var.project_name}-${var.environment}-asg"
  vpc_zone_identifier       = var.subnet_ids
  target_group_arns         = var.target_group_arns
  health_check_type         = var.health_check_type
  health_check_grace_period = var.health_check_grace_period
  min_size                  = var.min_size
  max_size                  = var.max_size
  desired_capacity          = var.desired_capacity
  
  launch_template {
    id      = aws_launch_template.app.id
    version = var.launch_template_version
  }
  
  enabled_metrics = var.enabled_metrics
  
  dynamic "tag" {
    for_each = local.common_tags
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }
  
  lifecycle {
    create_before_destroy = true
    ignore_changes        = [desired_capacity]
  }
  
  depends_on = [aws_launch_template.app]
}

# Auto Scaling Policies
resource "aws_autoscaling_policy" "scale_up" {
  count = var.enable_autoscaling ? 1 : 0
  
  name                   = "${var.project_name}-${var.environment}-scale-up"
  scaling_adjustment     = var.scale_up_adjustment
  adjustment_type        = "ChangeInCapacity"
  cooldown              = var.scale_up_cooldown
  autoscaling_group_name = aws_autoscaling_group.app.name
}

resource "aws_autoscaling_policy" "scale_down" {
  count = var.enable_autoscaling ? 1 : 0
  
  name                   = "${var.project_name}-${var.environment}-scale-down"
  scaling_adjustment     = var.scale_down_adjustment
  adjustment_type        = "ChangeInCapacity"
  cooldown              = var.scale_down_cooldown
  autoscaling_group_name = aws_autoscaling_group.app.name
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  count = var.enable_autoscaling ? 1 : 0
  
  alarm_name          = "${var.project_name}-${var.environment}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.cpu_high_evaluation_periods
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = var.cpu_high_period
  statistic           = "Average"
  threshold           = var.cpu_high_threshold
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_up[0].arn]
  
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }
  
  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "cpu_low" {
  count = var.enable_autoscaling ? 1 : 0
  
  alarm_name          = "${var.project_name}-${var.environment}-cpu-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = var.cpu_low_evaluation_periods
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = var.cpu_low_period
  statistic           = "Average"
  threshold           = var.cpu_low_threshold
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_down[0].arn]
  
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }
  
  tags = local.common_tags
}
```

Create `modules/compute/variables.tf`:
```hcl
variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for instances"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security group IDs"
  type        = list(string)
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "AMI ID (optional, will use data source if not provided)"
  type        = string
  default     = null
}

variable "ami_owners" {
  description = "AMI owners for data source"
  type        = list(string)
  default     = ["amazon"]
}

variable "ami_name_filter" {
  description = "AMI name filter for data source"
  type        = list(string)
  default     = ["amzn2-ami-hvm-*-x86_64-gp2"]
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
  default     = null
}

variable "user_data_base64" {
  description = "Base64 encoded user data"
  type        = string
  default     = null
}

variable "iam_instance_profile_arn" {
  description = "IAM instance profile ARN"
  type        = string
  default     = null
}

variable "min_size" {
  description = "Minimum number of instances"
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum number of instances"
  type        = number
  default     = 3
}

variable "desired_capacity" {
  description = "Desired number of instances"
  type        = number
  default     = 2
}

variable "target_group_arns" {
  description = "Target group ARNs for load balancer"
  type        = list(string)
  default     = []
}

variable "health_check_type" {
  description = "Type of health check"
  type        = string
  default     = "EC2"
}

variable "health_check_grace_period" {
  description = "Health check grace period in seconds"
  type        = number
  default     = 300
}

variable "enable_autoscaling" {
  description = "Enable autoscaling policies"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# Additional variables...
variable "root_volume_size" {
  default = 20
}

variable "root_volume_type" {
  default = "gp3"
}

variable "enable_ebs_encryption" {
  default = true
}

variable "kms_key_id" {
  default = null
}

variable "enable_monitoring" {
  default = true
}

variable "launch_template_version" {
  default = "$Latest"
}

variable "enabled_metrics" {
  type = list(string)
  default = [
    "GroupMinSize",
    "GroupMaxSize",
    "GroupDesiredCapacity",
    "GroupInServiceInstances"
  ]
}

variable "scale_up_adjustment" {
  default = 1
}

variable "scale_up_cooldown" {
  default = 300
}

variable "scale_down_adjustment" {
  default = -1
}

variable "scale_down_cooldown" {
  default = 300
}

variable "cpu_high_threshold" {
  default = 70
}

variable "cpu_high_evaluation_periods" {
  default = 2
}

variable "cpu_high_period" {
  default = 120
}

variable "cpu_low_threshold" {
  default = 30
}

variable "cpu_low_evaluation_periods" {
  default = 2
}

variable "cpu_low_period" {
  default = 120
}
```

### Step 3: Create Database Module

Create `modules/database/main.tf`:
```hcl
locals {
  common_tags = merge(
    var.tags,
    {
      Module      = "database"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

# Random password for database
resource "random_password" "db" {
  length  = 32
  special = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.subnet_ids
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-db-subnet-group"
    }
  )
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}-db"
  
  engine         = var.engine
  engine_version = var.engine_version
  instance_class = var.instance_class
  
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = var.storage_type
  storage_encrypted     = var.storage_encrypted
  kms_key_id           = var.kms_key_id
  
  db_name  = var.database_name
  username = var.master_username
  password = var.master_password != null ? var.master_password : random_password.db.result
  port     = var.port
  
  vpc_security_group_ids = var.security_group_ids
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  maintenance_window     = var.maintenance_window
  
  multi_az               = var.multi_az
  publicly_accessible    = var.publicly_accessible
  deletion_protection    = var.deletion_protection
  skip_final_snapshot    = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.project_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  
  enabled_cloudwatch_logs_exports = var.enabled_cloudwatch_logs_exports
  
  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_retention_period
  
  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-db"
    }
  )
  
  lifecycle {
    ignore_changes = [password]
  }
}

# Store credentials in Secrets Manager
resource "aws_secretsmanager_secret" "db" {
  name = "${var.project_name}-${var.environment}-db-credentials"
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id = aws_secretsmanager_secret.db.id
  
  secret_string = jsonencode({
    username = aws_db_instance.main.username
    password = var.master_password != null ? var.master_password : random_password.db.result
    endpoint = aws_db_instance.main.endpoint
    address  = aws_db_instance.main.address
    port     = aws_db_instance.main.port
    database = aws_db_instance.main.db_name
  })
}

# Read Replica (optional)
resource "aws_db_instance" "read_replica" {
  count = var.create_read_replica ? 1 : 0
  
  identifier = "${var.project_name}-${var.environment}-db-replica"
  
  replicate_source_db = aws_db_instance.main.identifier
  instance_class      = var.replica_instance_class != null ? var.replica_instance_class : var.instance_class
  
  publicly_accessible = false
  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  
  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_retention_period
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-db-replica"
    }
  )
}
```

### Step 4: Create Main Configuration Using Modules

Create `environments/dev/main.tf`:
```hcl
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend configuration for workspace
  backend "s3" {
    bucket         = "terraform-state-bucket"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
    
    # Workspace key prefix
    workspace_key_prefix = "workspaces"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = local.common_tags
  }
}

locals {
  environment = terraform.workspace == "default" ? "dev" : terraform.workspace
  
  # Environment-specific configurations
  env_config = {
    dev = {
      vpc_cidr              = "10.0.0.0/16"
      instance_type         = "t3.micro"
      db_instance_class     = "db.t3.micro"
      min_size             = 1
      max_size             = 3
      enable_nat_gateway   = false
      single_nat_gateway   = true
      enable_flow_logs     = false
      multi_az             = false
      backup_retention     = 1
    }
    staging = {
      vpc_cidr              = "10.1.0.0/16"
      instance_type         = "t3.small"
      db_instance_class     = "db.t3.small"
      min_size             = 2
      max_size             = 5
      enable_nat_gateway   = true
      single_nat_gateway   = true
      enable_flow_logs     = true
      multi_az             = false
      backup_retention     = 7
    }
    prod = {
      vpc_cidr              = "10.2.0.0/16"
      instance_type         = "t3.medium"
      db_instance_class     = "db.t3.medium"
      min_size             = 3
      max_size             = 10
      enable_nat_gateway   = true
      single_nat_gateway   = false
      enable_flow_logs     = true
      multi_az             = true
      backup_retention     = 30
    }
  }
  
  config = local.env_config[local.environment]
  
  common_tags = {
    Project     = var.project_name
    Environment = local.environment
    Workspace   = terraform.workspace
    ManagedBy   = "Terraform"
  }
}

# Networking Module
module "networking" {
  source = "../../modules/networking"
  
  project_name          = var.project_name
  environment           = local.environment
  vpc_cidr             = local.config.vpc_cidr
  availability_zones   = data.aws_availability_zones.available.names
  public_subnet_count  = 2
  private_subnet_count = 2
  database_subnet_count = 2
  enable_nat_gateway   = local.config.enable_nat_gateway
  single_nat_gateway   = local.config.single_nat_gateway
  enable_flow_logs     = local.config.enable_flow_logs
  tags                 = local.common_tags
}

# Security Module
module "security" {
  source = "../../modules/security"
  
  project_name = var.project_name
  environment  = local.environment
  vpc_id       = module.networking.vpc_id
  vpc_cidr     = module.networking.vpc_cidr
  tags         = local.common_tags
}

# Compute Module
module "compute" {
  source = "../../modules/compute"
  
  project_name       = var.project_name
  environment        = local.environment
  subnet_ids         = module.networking.private_subnet_ids
  security_group_ids = [module.security.app_security_group_id]
  instance_type      = local.config.instance_type
  min_size          = local.config.min_size
  max_size          = local.config.max_size
  desired_capacity   = local.config.min_size
  target_group_arns  = [module.load_balancer.target_group_arn]
  tags              = local.common_tags
  
  depends_on = [module.networking]
}

# Database Module
module "database" {
  source = "../../modules/database"
  
  project_name     = var.project_name
  environment      = local.environment
  subnet_ids       = module.networking.database_subnet_ids
  security_group_ids = [module.security.db_security_group_id]
  instance_class   = local.config.db_instance_class
  multi_az         = local.config.multi_az
  backup_retention_period = local.config.backup_retention
  tags             = local.common_tags
  
  depends_on = [module.networking]
}

# Load Balancer Module
module "load_balancer" {
  source = "../../modules/load_balancer"
  
  project_name       = var.project_name
  environment        = local.environment
  vpc_id            = module.networking.vpc_id
  subnet_ids        = module.networking.public_subnet_ids
  security_group_id = module.security.alb_security_group_id
  tags              = local.common_tags
  
  depends_on = [module.networking]
}

# Data source for AZs
data "aws_availability_zones" "available" {
  state = "available"
}
```

### Step 5: Workspace Management Script

Create `scripts/workspace-manager.sh`:
```bash
#!/bin/bash

# Workspace management script

set -e

ENVIRONMENTS=("dev" "staging" "prod")

# Function to create workspace
create_workspace() {
    local env=$1
    echo "Creating workspace: $env"
    terraform workspace new $env || echo "Workspace $env already exists"
}

# Function to switch workspace
switch_workspace() {
    local env=$1
    echo "Switching to workspace: $env"
    terraform workspace select $env
}

# Function to plan for workspace
plan_workspace() {
    local env=$1
    switch_workspace $env
    echo "Planning for $env environment"
    terraform plan -var-file="environments/$env/terraform.tfvars" -out="$env.tfplan"
}

# Function to apply for workspace
apply_workspace() {
    local env=$1
    switch_workspace $env
    echo "Applying for $env environment"
    terraform apply -var-file="environments/$env/terraform.tfvars" -auto-approve
}

# Function to destroy workspace resources
destroy_workspace() {
    local env=$1
    switch_workspace $env
    echo "Destroying $env environment"
    terraform destroy -var-file="environments/$env/terraform.tfvars" -auto-approve
}

# Main menu
case "$1" in
    init)
        terraform init
        for env in "${ENVIRONMENTS[@]}"; do
            create_workspace $env
        done
        ;;
    plan)
        if [ -z "$2" ]; then
            echo "Usage: $0 plan <environment>"
            exit 1
        fi
        plan_workspace $2
        ;;
    apply)
        if [ -z "$2" ]; then
            echo "Usage: $0 apply <environment>"
            exit 1
        fi
        apply_workspace $2
        ;;
    destroy)
        if [ -z "$2" ]; then
            echo "Usage: $0 destroy <environment>"
            exit 1
        fi
        destroy_workspace $2
        ;;
    list)
        terraform workspace list
        ;;
    show)
        terraform workspace show
        ;;
    *)
        echo "Usage: $0 {init|plan|apply|destroy|list|show} [environment]"
        echo "Environments: ${ENVIRONMENTS[@]}"
        exit 1
        ;;
esac
```

### Step 6: Module Testing

Create `modules/networking/tests/networking_test.go`:
```go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestNetworkingModule(t *testing.T) {
    t.Parallel()

    terraformOptions := &terraform.Options{
        TerraformDir: "../",
        Vars: map[string]interface{}{
            "project_name": "test",
            "environment": "test",
            "vpc_cidr": "10.0.0.0/16",
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    // Validate outputs
    vpcId := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcId)

    publicSubnets := terraform.OutputList(t, terraformOptions, "public_subnet_ids")
    assert.Equal(t, 2, len(publicSubnets))
}
```

Create `modules/networking/examples/basic/main.tf`:
```hcl
module "networking" {
  source = "../../"
  
  project_name = "example"
  environment  = "test"
  vpc_cidr     = "10.0.0.0/16"
  
  availability_zones = ["us-east-1a", "us-east-1b"]
  
  public_subnet_count   = 2
  private_subnet_count  = 2
  database_subnet_count = 2
  
  enable_nat_gateway = true
  single_nat_gateway = true
  enable_flow_logs   = false
  
  tags = {
    Example = "true"
  }
}

output "vpc_id" {
  value = module.networking.vpc_id
}

output "public_subnet_ids" {
  value = module.networking.public_subnet_ids
}
```

## ✅ Verification Steps

Run `scripts/verify.sh`:
```bash
#!/bin/bash

echo "🔍 Verifying Lab 04 - Modules & Workspaces..."

# Check module structure
echo "Module Structure:"
find modules -type f -name "*.tf" | head -20

# List workspaces
echo -e "\nWorkspaces:"
terraform workspace list

# Show current workspace
echo -e "\nCurrent Workspace:"
terraform workspace show

# Validate modules
echo -e "\nValidating Modules:"
for module in modules/*/; do
    echo "Validating $module"
    terraform -chdir="$module" init -backend=false
    terraform -chdir="$module" validate
done

# Check module outputs
echo -e "\nModule Outputs:"
terraform output -json | jq 'keys'

echo -e "\n✅ Lab 04 verification complete!"
```

## 🧹 Cleanup

Run `scripts/cleanup.sh`:
```bash
#!/bin/bash

echo "🧹 Cleaning up Lab 04..."

# Destroy all workspace resources
for workspace in $(terraform workspace list | grep -v default | sed 's/\*//g'); do
    echo "Cleaning workspace: $workspace"
    terraform workspace select $workspace
    terraform destroy -auto-approve || true
done

# Switch to default
terraform workspace select default

# Delete workspaces
for workspace in $(terraform workspace list | grep -v default | sed 's/\*//g'); do
    terraform workspace delete $workspace
done

# Clean up files
rm -rf .terraform terraform.tfstate* *.tfplan

echo "✅ Cleanup complete!"
```

## 📚 Additional Resources
- [Terraform Modules](https://www.terraform.io/docs/language/modules)
- [Workspaces](https://www.terraform.io/docs/language/state/workspaces.html)
- [Module Registry](https://registry.terraform.io/)