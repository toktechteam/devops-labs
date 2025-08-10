# Lab 01: Terraform Basics

## 🎯 Lab Scenario
**You've just joined TechStartup Inc. as a DevOps Engineer. The company has been managing infrastructure manually through cloud consoles, leading to configuration drift and deployment errors. Your first task is to introduce Infrastructure as Code using Terraform. You'll start by creating a proof-of-concept that demonstrates Terraform's core capabilities to convince the team to adopt IaC practices.**

## 🎓 What You'll Learn
By completing this lab, you will:
1. **Understand why Terraform**: Learn how IaC solves real infrastructure problems
2. **Master HCL syntax**: Write your first Terraform configurations
3. **Work with state**: Understand how Terraform tracks resources
4. **Use variables**: Make configurations reusable across environments
5. **Apply functions**: Transform and manipulate data in Terraform
6. **Handle dependencies**: Control resource creation order

## 🌟 Real-World Application
After this lab, you'll be able to:
- Convert manual infrastructure deployments to code
- Create reusable infrastructure templates
- Version control your infrastructure
- Implement consistent environments (dev/staging/prod)
- Reduce deployment time from hours to minutes

## ⏱️ Duration: 45 minutes

## 📋 Prerequisites
- Terraform installed (1.5+)
- Text editor (VS Code recommended with Terraform extension)
- Basic command line knowledge
- AWS/Azure/GCP account (free tier sufficient)

## 🏗️ Architecture
```
Your Journey: Manual → Infrastructure as Code
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Before (Manual):                After (Terraform):
┌─────────────┐                 ┌─────────────┐
│   Console   │                 │    Code     │
│   Clicks    │      →          │    (HCL)    │
│   No Track  │                 │   Tracked   │
└─────────────┘                 └─────────────┘
      ↓                               ↓
┌─────────────┐                 ┌─────────────┐
│   Random    │                 │   State     │
│   Config    │      →          │    File     │
│   Drift     │                 │   Managed   │
└─────────────┘                 └─────────────┘
```

## 🎬 Lab Story
**Scenario**: Your manager asks: "We need to deploy 10 identical environments for our new project. Last time it took 3 days and each environment was slightly different. Can you help?"

**Your Mission**: Build a Terraform configuration that can:
1. Deploy consistent infrastructure in minutes
2. Track all changes in version control
3. Allow easy updates and rollbacks
4. Support multiple environments with minimal changes

## 📝 Instructions

### Part 1: Your First Infrastructure as Code
**Goal**: Replace manual S3 bucket creation with Terraform

#### The Manual Way (What We're Replacing):
```
1. Log into AWS Console
2. Navigate to S3
3. Click "Create Bucket"
4. Enter name, select region
5. Configure settings (versioning, encryption)
6. Set permissions
7. Add tags
8. Click "Create"
9. Repeat for each environment... 😫
```

#### The Terraform Way:
Create `main.tf`:
```hcl
# Configure Terraform settings
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

# Generate random ID for unique naming
resource "random_id" "project" {
  byte_length = 4
}

# Create local file
resource "local_file" "config" {
  filename = "${path.module}/output/app-config-${random_id.project.hex}.json"
  content = jsonencode({
    project_id = random_id.project.hex
    timestamp  = timestamp()
    environment = var.environment
    settings = {
      debug_mode = var.enable_debug
      max_connections = var.max_connections
      features = var.features
    }
  })
  
  file_permission = "0644"
}

# Create sensitive file with proper permissions
resource "local_sensitive_file" "secrets" {
  filename = "${path.module}/output/secrets-${random_id.project.hex}.env"
  content = <<-EOT
    DATABASE_PASSWORD=${random_password.db_password.result}
    API_KEY=${random_password.api_key.result}
    JWT_SECRET=${random_password.jwt_secret.result}
    ENCRYPTION_KEY=${random_password.encryption_key.result}
  EOT
  
  file_permission = "0600"
}

# Generate random passwords
resource "random_password" "db_password" {
  length  = 32
  special = true
  override_special = "!@#$%^&*"
}

resource "random_password" "api_key" {
  length  = 48
  special = false
  upper   = true
  lower   = true
  numeric = true
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

resource "random_password" "encryption_key" {
  length  = 32
  special = false
}
```

### Step 2: Variables Configuration

Create `variables.tf`:
```hcl
# Environment variable with validation
variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "development"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

# Boolean variable
variable "enable_debug" {
  description = "Enable debug mode"
  type        = bool
  default     = false
}

# Number variable with validation
variable "max_connections" {
  description = "Maximum number of database connections"
  type        = number
  default     = 100
  
  validation {
    condition     = var.max_connections >= 10 && var.max_connections <= 1000
    error_message = "Max connections must be between 10 and 1000."
  }
}

# List variable
variable "features" {
  description = "List of enabled features"
  type        = list(string)
  default     = ["logging", "metrics", "tracing"]
}

# Map variable
variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    Project     = "terraform-basics"
    ManagedBy   = "terraform"
    Environment = "lab"
  }
}

# Complex object variable
variable "database_config" {
  description = "Database configuration"
  type = object({
    engine   = string
    version  = string
    port     = number
    replicas = number
    backup = object({
      enabled   = bool
      retention = number
    })
  })
  default = {
    engine   = "postgres"
    version  = "14.7"
    port     = 5432
    replicas = 2
    backup = {
      enabled   = true
      retention = 7
    }
  }
}

# Optional variable with default null
variable "custom_domain" {
  description = "Custom domain name"
  type        = string
  default     = null
}

# Sensitive variable
variable "api_token" {
  description = "API authentication token"
  type        = string
  sensitive   = true
  default     = ""
}
```

### Step 3: Outputs Configuration

Create `outputs.tf`:
```hcl
# Simple output
output "project_id" {
  description = "Unique project identifier"
  value       = random_id.project.hex
}

# Sensitive output
output "database_password" {
  description = "Generated database password"
  value       = random_password.db_password.result
  sensitive   = true
}

# Complex output with formatting
output "configuration_summary" {
  description = "Configuration summary"
  value = {
    environment = var.environment
    debug_enabled = var.enable_debug
    config_file = local_file.config.filename
    secrets_file = local_sensitive_file.secrets.filename
    features_enabled = length(var.features)
    database = {
      engine = var.database_config.engine
      version = var.database_config.version
      replicas = var.database_config.replicas
    }
  }
}

# Conditional output
output "custom_domain_info" {
  description = "Custom domain information"
  value = var.custom_domain != null ? {
    domain = var.custom_domain
    url    = "https://${var.custom_domain}"
  } : null
}

# Output with depends_on
output "deployment_complete" {
  description = "Deployment completion status"
  value       = "All resources created successfully at ${timestamp()}"
  depends_on  = [
    local_file.config,
    local_sensitive_file.secrets
  ]
}
```

### Step 4: Advanced Resources

Create `advanced.tf`:
```hcl
# Local variables
locals {
  common_tags = merge(
    var.tags,
    {
      Environment = var.environment
      Timestamp   = timestamp()
      ProjectID   = random_id.project.hex
    }
  )
  
  is_production = var.environment == "production"
  
  # Dynamic configuration based on environment
  instance_config = {
    development = {
      instance_type = "t2.micro"
      volume_size   = 10
      monitoring    = false
    }
    staging = {
      instance_type = "t2.small"
      volume_size   = 20
      monitoring    = true
    }
    production = {
      instance_type = "t2.medium"
      volume_size   = 50
      monitoring    = true
    }
  }
  
  selected_config = local.instance_config[var.environment]
}

# Data source - read existing file
data "local_file" "readme" {
  filename = "${path.module}/README.md"
}

# Null resource with provisioners
resource "null_resource" "setup" {
  # Triggers cause resource recreation
  triggers = {
    project_id = random_id.project.hex
    timestamp  = timestamp()
  }
  
  # Local exec provisioner
  provisioner "local-exec" {
    command = <<-EOT
      echo "Setting up project ${random_id.project.hex}"
      mkdir -p ${path.module}/output
      echo "Project initialized at $(date)" > ${path.module}/output/setup.log
    EOT
    
    interpreter = ["bash", "-c"]
  }
  
  # Another provisioner that runs on destroy
  provisioner "local-exec" {
    when    = destroy
    command = "echo 'Cleanup completed at $(date)' >> ${path.module}/output/cleanup.log"
    interpreter = ["bash", "-c"]
  }
}

# Dynamic blocks example
resource "local_file" "dynamic_config" {
  filename = "${path.module}/output/dynamic-config.yaml"
  content = yamlencode({
    features = [
      for feature in var.features : {
        name    = feature
        enabled = true
        config  = {
          level = local.is_production ? "production" : "development"
        }
      }
    ]
    
    databases = {
      for i in range(var.database_config.replicas) : 
      "replica-${i}" => {
        host = "db-${i}.example.com"
        port = var.database_config.port + i
        role = i == 0 ? "primary" : "replica"
      }
    }
  })
}

# Count example
resource "local_file" "logs" {
  count = local.is_production ? 3 : 1
  
  filename = "${path.module}/output/log-${count.index}.txt"
  content  = "Log file ${count.index + 1} for ${var.environment}"
}

# For_each example with map
resource "local_file" "config_files" {
  for_each = {
    app     = "application.conf"
    db      = "database.conf"
    cache   = "cache.conf"
    queue   = "queue.conf"
  }
  
  filename = "${path.module}/output/${each.value}"
  content = jsonencode({
    service = each.key
    config  = "Configuration for ${each.key}"
    environment = var.environment
    tags = local.common_tags
  })
}

# For_each with set
resource "random_uuid" "feature_ids" {
  for_each = toset(var.features)
}

# Conditional resource creation
resource "local_file" "production_only" {
  count = local.is_production ? 1 : 0
  
  filename = "${path.module}/output/production-config.json"
  content = jsonencode({
    high_availability = true
    backup_enabled    = true
    monitoring_level  = "enhanced"
  })
}
```

### Step 5: Functions and Expressions

Create `functions.tf`:
```hcl
# Demonstrate Terraform functions
locals {
  # String functions
  upper_env = upper(var.environment)
  lower_env = lower(var.environment)
  title_env = title(var.environment)
  
  # Format and replace
  formatted_string = format("Project %s in %s", random_id.project.hex, var.environment)
  replaced_string  = replace(var.environment, "development", "dev")
  
  # Collection functions
  feature_list   = join(", ", var.features)
  first_feature  = element(var.features, 0)
  feature_count  = length(var.features)
  unique_features = distinct(concat(var.features, ["logging", "custom"]))
  
  # Map functions
  tag_keys   = keys(var.tags)
  tag_values = values(var.tags)
  merged_tags = merge(
    var.tags,
    {
      "ExtraTag" = "ExtraValue"
    }
  )
  
  # Numeric functions
  min_value = min(10, 20, 30)
  max_value = max(10, 20, 30)
  ceil_value = ceil(10.3)
  floor_value = floor(10.7)
  
  # Date and time
  current_time = timestamp()
  formatted_date = formatdate("YYYY-MM-DD", timestamp())
  
  # Encoding functions
  base64_encoded = base64encode("Hello Terraform")
  json_encoded = jsonencode({
    key = "value"
    list = [1, 2, 3]
  })
  yaml_encoded = yamlencode({
    key = "value"
    list = [1, 2, 3]
  })
  
  # Filesystem functions
  file_exists = fileexists("${path.module}/README.md")
  path_module = path.module
  path_root   = path.root
  path_cwd    = path.cwd
  
  # Type conversion
  string_to_number = tonumber("42")
  number_to_string = tostring(42)
  to_list = tolist(["a", "b", "c"])
  to_set  = toset(["a", "b", "b", "c"])
  to_map  = tomap({
    key1 = "value1"
    key2 = "value2"
  })
  
  # Conditional expressions
  instance_type = var.environment == "production" ? "t2.large" : "t2.micro"
  
  # Complex expressions
  filtered_features = [
    for feature in var.features : 
    upper(feature) 
    if feature != "logging"
  ]
  
  # Map transformation
  upper_tags = {
    for key, value in var.tags :
    upper(key) => upper(value)
  }
  
  # Try function for error handling
  safe_conversion = try(
    tonumber(var.custom_domain),
    0
  )
  
  # Lookup with default
  default_value = lookup(var.tags, "Missing", "default-value")
  
  # Contains check
  has_logging = contains(var.features, "logging")
  
  # Range generation
  number_list = range(1, 5)
  
  # Flatten nested lists
  nested_list = [[1, 2], [3, 4], [5]]
  flat_list = flatten(local.nested_list)
  
  # Regex
  regex_match = regex("^[a-z]+", var.environment)
  regex_replace = regexreplace(var.environment, "[aeiou]", "*")
}

# Output to demonstrate functions
resource "local_file" "functions_demo" {
  filename = "${path.module}/output/functions-demo.json"
  content = jsonencode({
    string_functions = {
      upper = local.upper_env
      lower = local.lower_env
      title = local.title_env
      formatted = local.formatted_string
      replaced = local.replaced_string
    }
    collection_functions = {
      joined = local.feature_list
      first = local.first_feature
      count = local.feature_count
      unique = local.unique_features
    }
    map_functions = {
      keys = local.tag_keys
      values = local.tag_values
      merged = local.merged_tags
    }
    numeric_functions = {
      min = local.min_value
      max = local.max_value
      ceil = local.ceil_value
      floor = local.floor_value
    }
    datetime = {
      current = local.current_time
      formatted = local.formatted_date
    }
    encoding = {
      base64 = local.base64_encoded
      json = local.json_encoded
    }
    filesystem = {
      file_exists = local.file_exists
      module_path = local.path_module
    }
    conditionals = {
      instance_type = local.instance_type
      has_logging = local.has_logging
    }
    transformations = {
      filtered_features = local.filtered_features
      upper_tags = local.upper_tags
    }
    regex = {
      match = local.regex_match
      replace = local.regex_replace
    }
  })
}
```

### Step 6: Terraform Configuration

Create `terraform.tfvars.example`:
```hcl
environment = "development"
enable_debug = true
max_connections = 150

features = [
  "logging",
  "metrics", 
  "tracing",
  "analytics"
]

tags = {
  Project     = "terraform-basics-lab"
  Owner       = "devops-team"
  CostCenter  = "engineering"
  Environment = "lab"
}

database_config = {
  engine   = "postgres"
  version  = "14.7"
  port     = 5432
  replicas = 3
  backup = {
    enabled   = true
    retention = 30
  }
}

# Uncomment to set custom domain
# custom_domain = "example.com"

# Sensitive variable - set via environment variable
# export TF_VAR_api_token="your-secret-token"
```

### Step 7: Validation and Testing

Create `validation.tf`:
```hcl
# Check resource creation conditions
check "environment_resources" {
  assert {
    condition = (
      var.environment == "production" 
      ? var.database_config.replicas >= 2 
      : true
    )
    error_message = "Production environment requires at least 2 database replicas"
  }
}

check "backup_configuration" {
  assert {
    condition = (
      var.environment == "production"
      ? var.database_config.backup.enabled == true
      : true
    )
    error_message = "Backup must be enabled in production"
  }
}

# Moved blocks for refactoring
moved {
  from = local_file.old_config
  to   = local_file.config
}

# Import blocks for existing resources
import {
  id = "/tmp/existing-file.txt"
  to = local_file.imported_file
}

resource "local_file" "imported_file" {
  filename = "/tmp/existing-file.txt"
  content  = "This file was imported"
}
```

### Step 8: Scripts

Create `scripts/init.sh`:
```bash
#!/bin/bash

echo "🚀 Initializing Terraform Lab 01..."

# Create necessary directories
mkdir -p output

# Initialize Terraform
terraform init

# Format code
terraform fmt -recursive

# Validate configuration
terraform validate

echo "✅ Initialization complete!"
echo ""
echo "Next steps:"
echo "1. Review the plan: terraform plan"
echo "2. Apply changes: terraform apply"
echo "3. Explore outputs: terraform output"
echo "4. Clean up: terraform destroy"
```

Create `scripts/demo.sh`:
```bash
#!/bin/bash

set -e

echo "🎯 Terraform Basics Lab Demo"
echo "============================"

# Clean previous state
rm -rf .terraform terraform.tfstate* output/

# Initialize
echo -e "\n📦 Initializing Terraform..."
terraform init

# Format check
echo -e "\n🎨 Checking formatting..."
terraform fmt -check -recursive

# Validate
echo -e "\n✔️ Validating configuration..."
terraform validate

# Plan
echo -e "\n📋 Creating execution plan..."
terraform plan -out=tfplan

# Show plan details
echo -e "\n🔍 Plan summary:"
terraform show -json tfplan | jq '.resource_changes | length' | xargs echo "Resources to create:"

# Apply
echo -e "\n🚀 Applying configuration..."
terraform apply tfplan

# Show outputs
echo -e "\n📊 Outputs:"
terraform output -json | jq

# Show state
echo -e "\n📁 State file resources:"
terraform state list

# Show specific resource
echo -e "\n🔍 Random ID details:"
terraform state show random_id.project

# Refresh state
echo -e "\n🔄 Refreshing state..."
terraform refresh

# Create workspace
echo -e "\n🏗️ Creating new workspace..."
terraform workspace new demo
terraform workspace list

# Back to default
terraform workspace select default

echo -e "\n✅ Demo complete! Run 'terraform destroy' to clean up."
```

## ✅ Verification Steps

Run `scripts/verify.sh`:
```bash
#!/bin/bash

echo "🔍 Verifying Lab 01..."

# Check Terraform version
echo "Terraform version:"
terraform version

# Check initialization
if [ -d ".terraform" ]; then
    echo "✅ Terraform initialized"
else
    echo "❌ Terraform not initialized. Run: terraform init"
    exit 1
fi

# Validate configuration
echo -e "\nValidating configuration:"
terraform validate

# Check formatting
echo -e "\nChecking formatting:"
terraform fmt -check -recursive

# List resources in state
if [ -f "terraform.tfstate" ]; then
    echo -e "\nResources in state:"
    terraform state list
    
    echo -e "\nOutputs:"
    terraform output
fi

# Check created files
echo -e "\nCreated files:"
ls -la output/ 2>/dev/null || echo "No output files yet"

echo -e "\n✅ Lab 01 verification complete!"
```

## 🧹 Cleanup

Run `scripts/cleanup.sh`:
```bash
#!/bin/bash

echo "🧹 Cleaning up Lab 01..."

# Destroy resources
terraform destroy -auto-approve

# Remove Terraform files
rm -rf .terraform
rm -f terraform.tfstate*
rm -f tfplan
rm -rf output/

# Remove workspaces
terraform workspace select default 2>/dev/null
terraform workspace delete demo 2>/dev/null || true

echo "✅ Cleanup complete!"
```

## 🐛 Troubleshooting

### State Lock Issues
```bash
# Force unlock (use with caution)
terraform force-unlock <lock-id>

# Remove state lock
rm .terraform.lock.hcl
terraform init
```

### Resource Already Exists
```bash
# Import existing resource
terraform import local_file.config /path/to/file

# Or remove from state
terraform state rm local_file.config
```

### Variable Issues
```bash
# Set via environment
export TF_VAR_environment="production"

# Or use var file
terraform apply -var-file="production.tfvars"

# Or inline
terraform apply -var="environment=production"
```

## 📚 Additional Resources
- [Terraform Language Documentation](https://www.terraform.io/language)
- [Built-in Functions](https://www.terraform.io/language/functions)
- [State Management](https://www.terraform.io/language/state)