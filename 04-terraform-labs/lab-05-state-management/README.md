# Lab 05: State Management

## 🎯 Lab Scenario
**Disaster struck GlobalTech Corp! A junior developer accidentally deleted the Terraform state file for production, causing a 4-hour outage and $2M in losses. Another team's concurrent terraform apply corrupted the staging environment. The CEO demands: "This can never happen again!" You're now the State Management Expert tasked with implementing bulletproof state management, locking, versioning, and disaster recovery.**

## 💥 The State Crisis at GlobalTech
Real incidents that happened:
- **The Delete Disaster**: `rm terraform.tfstate` → Production orphaned
- **The Concurrent Catastrophe**: Two applies → State corrupted
- **The Laptop Loss**: Developer's laptop stolen → State gone
- **The Migration Mess**: Moving to S3 → Lost half the resources
- **The Import Impossibility**: 500 manually created resources → No state

## 🎓 What You'll Learn
By completing this lab, you will master:
1. **Remote State Backends**: S3, Azure Storage, Terraform Cloud
2. **State Locking**: Prevent concurrent modifications
3. **State Encryption**: Protect sensitive data
4. **State Migration**: Move between backends safely
5. **Disaster Recovery**: Backup and restore strategies
6. **Import Operations**: Bring existing resources under management
7. **State Surgery**: Fix corrupted or incorrect state

## 🌟 Real-World Skills You'll Gain
After this lab, you'll be able to:
- Implement enterprise-grade state management
- Recover from state disasters in minutes
- Migrate state between backends with zero downtime
- Import existing infrastructure into Terraform
- Set up automated state backups
- Implement break-glass procedures
- Handle state for 1000+ resource deployments

## ⏱️ Duration: 90 minutes

## ⚠️ Critical Importance
**Why State Management Matters**:
- State is the **source of truth** for your infrastructure
- Lost state = Lost control of resources
- Corrupted state = Potential data loss
- Exposed state = Security breach (contains secrets)
- Locked state = Team blocked from deployments

## 📋 Prerequisites
- Completed Labs 01-04
- AWS account with S3 and DynamoDB permissions
- Understanding of Terraform state concept
- Backup of any existing state files

## 🏗️ Architecture
```
State Management: From Chaos to Control
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE NIGHTMARES (What We're Preventing):
┌─────────────────────────────────────┐
│  😱 Local State Problems:           │
│  • Lost laptop = Lost infrastructure│
│  • No collaboration possible        │
│  • No versioning or backup          │
│  • Secrets exposed in Git           │
└─────────────────────────────────────┘

THE SOLUTION (What We're Building):
┌─────────────────────────────────────┐
│       Bulletproof State Setup       │
├─────────────────────────────────────┤
│         Developer Machines          │
│         ┌───┐  ┌───┐  ┌───┐        │
│         │D1 │  │D2 │  │D3 │        │
│         └─┬─┘  └─┬─┘  └─┬─┘        │
│           └──────┼──────┘           │
│                  ↓                   │
│      DynamoDB (Lock Table)          │
│      "Only one apply at a time"     │
│                  ↓                   │
│         S3 (State Storage)          │
│      ┌──────────────────┐           │
│      │ ✓ Versioning     │           │
│      │ ✓ Encryption     │           │
│      │ ✓ Access Logging │           │
│      └────────┬─────────┘           │
│               ↓                      │
│    Cross-Region Replication         │
│      ┌──────────────────┐           │
│      │  DR State Backup │           │
│      │   (us-west-2)    │           │
│      └──────────────────┘           │
│                                      │
│         Safety Features:            │
│  ✓ Point-in-time recovery          │
│  ✓ 90-day version history          │
│  ✓ Automated hourly backups        │
│  ✓ Break-glass procedures          │
└─────────────────────────────────────┘

State Operations Hierarchy:
1. terraform state list     → View resources
2. terraform state show     → Inspect details  
3. terraform state mv       → Rename resources
4. terraform state rm       → Remove from state
5. terraform state pull     → Download state
6. terraform state push     → Upload state
7. terraform import         → Add existing resources
```

## 🎬 The State Disaster Timeline

**Day 0**: Everything works with local state  
**Day 30**: "Hey, can you apply this while I'm on vacation?"  
**Day 31**: "Why are there two VPCs now?"  
**Day 45**: Laptop stolen at coffee shop  
**Day 46**: "Where's our infrastructure?!"  
**Day 60**: Attempt to recover... manually recreating resources  
**Day 90**: Audit finds untracked resources costing $50K/month

**Your Mission**: Implement state management that prevents ALL of these disasters!

## 📝 Instructions

### Part 1: The State Foundation
**Understanding What State Actually Does**

#### What's in a State File?
```json
{
  "version": 4,
  "terraform_version": "1.5.0",
  "serial": 42,
  "lineage": "unique-id-here",
  "resources": [
    {
      "type": "aws_instance",
      "name": "web",
      "instances": [
        {
          "attributes": {
            "id": "i-1234567890abcdef0",
            "private_ip": "10.0.1.50",
            "public_ip": "54.1.2.3",
            // Sensitive data like passwords!
          }
        }
      ]
    }
  ]
}
```

**Why This Matters**:
- `serial`: Increments with each change (conflict detection)
- `lineage`: Unique ID (prevents mixing states)
- `resources`: Maps config to real resources
- Contains **sensitive data** (passwords, keys)

### Part 2: Setting Up Bulletproof Remote State
**Goal**: Never lose state, never have conflicts, always recoverable

Create `backend-setup/main.tf`:
```hcl
# This creates the infrastructure needed for remote state
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# KMS Key for encryption
resource "aws_kms_key" "terraform_state" {
  description             = "KMS key for Terraform state encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  
  tags = merge(
    local.tags,
    {
      Name = "Terraform State KMS Key"
    }
  )
}

resource "aws_kms_alias" "terraform_state" {
  name          = "alias/${var.project_name}-terraform-state"
  target_key_id = aws_kms_key.terraform_state.key_id
}

# DynamoDB Table for State Locking
resource "aws_dynamodb_table" "terraform_locks" {
  name           = "${var.project_name}-${var.environment}-locks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
  
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.terraform_state.arn
  }
  
  point_in_time_recovery {
    enabled = true
  }
  
  tags = merge(
    local.tags,
    {
      Name = "Terraform State Lock Table"
    }
  )
  
  lifecycle {
    prevent_destroy = true
  }
}

# IAM Policy for State Access
resource "aws_iam_policy" "terraform_state" {
  name        = "${var.project_name}-terraform-state-policy"
  description = "Policy for Terraform state access"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketVersioning"
        ]
        Resource = aws_s3_bucket.terraform_state.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.terraform_state.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:DescribeTable",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem"
        ]
        Resource = aws_dynamodb_table.terraform_locks.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.terraform_state.arn
      }
    ]
  })
  
  tags = local.tags
}

# Outputs for backend configuration
output "s3_bucket_name" {
  description = "S3 bucket name for Terraform state"
  value       = aws_s3_bucket.terraform_state.id
}

output "dynamodb_table_name" {
  description = "DynamoDB table name for state locking"
  value       = aws_dynamodb_table.terraform_locks.name
}

output "kms_key_id" {
  description = "KMS key ID for state encryption"
  value       = aws_kms_key.terraform_state.id
}

output "backend_config" {
  description = "Backend configuration for Terraform"
  value = <<-EOT
    backend "s3" {
      bucket         = "${aws_s3_bucket.terraform_state.id}"
      key            = "path/to/terraform.tfstate"
      region         = "${var.aws_region}"
      dynamodb_table = "${aws_dynamodb_table.terraform_locks.name}"
      encrypt        = true
      kms_key_id     = "${aws_kms_key.terraform_state.id}"
    }
  EOT
}

# Create backup bucket
resource "aws_s3_bucket" "terraform_state_backup" {
  bucket = "${local.bucket_name}-backup"
  
  tags = merge(
    local.tags,
    {
      Name = "Terraform State Backup Bucket"
    }
  )
}

resource "aws_s3_bucket_versioning" "terraform_state_backup" {
  bucket = aws_s3_bucket.terraform_state_backup.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_replication_configuration" "terraform_state" {
  role   = aws_iam_role.replication.arn
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    id     = "backup-state"
    status = "Enabled"
    
    destination {
      bucket        = aws_s3_bucket.terraform_state_backup.arn
      storage_class = "STANDARD_IA"
      
      encryption_configuration {
        replica_kms_key_id = aws_kms_key.terraform_state.arn
      }
    }
  }
  
  depends_on = [aws_s3_bucket_versioning.terraform_state]
}

# IAM role for replication
resource "aws_iam_role" "replication" {
  name = "${var.project_name}-state-replication-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.tags
}

resource "aws_iam_role_policy" "replication" {
  name = "${var.project_name}-state-replication-policy"
  role = aws_iam_role.replication.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetReplicationConfiguration",
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.terraform_state.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl"
        ]
        Resource = "${aws_s3_bucket.terraform_state.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete"
        ]
        Resource = "${aws_s3_bucket.terraform_state_backup.arn}/*"
      }
    ]
  })
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "terraform-state"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "shared"
}

locals {
  bucket_name = "${var.project_name}-${var.environment}-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "Terraform State Management"
    ManagedBy   = "Terraform"
  }
}

data "aws_caller_identity" "current" {}

# S3 Bucket for State Storage
resource "aws_s3_bucket" "terraform_state" {
  bucket = local.bucket_name
  
  tags = merge(
    local.tags,
    {
      Name = "Terraform State Bucket"
    }
  )
  
  lifecycle {
    prevent_destroy = true
  }
}

# Enable versioning for state history
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.terraform_state.arn
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle rule for old versions
resource "aws_s3_bucket_lifecycle_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    id     = "expire-old-versions"
    status = "Enabled"
    
    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
  
  rule {
    id     = "transition-old-versions"
    status = "Enabled"
    
    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }
    
    noncurrent_version_transition {
      noncurrent_days = 60
      storage_class   = "GLACIER"
    } 