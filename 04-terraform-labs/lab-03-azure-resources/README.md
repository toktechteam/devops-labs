# Lab 03: Azure Resources

## 🎯 Lab Scenario
**Your company "HealthTech Solutions" is expanding to Azure for their patient management system. After the successful AWS deployment, management wants a multi-cloud strategy for risk mitigation. You're tasked with deploying a HIPAA-compliant healthcare application on Azure that processes sensitive patient data and must meet strict security and availability requirements.**

## 🏥 Business Context
HealthTech Solutions needs:
- **HIPAA Compliance**: Encryption, audit logs, access controls
- **24/7 Availability**: Hospitals don't close
- **Data Residency**: Patient data must stay in specific regions
- **Scalability**: Handle 10,000 concurrent users during emergencies
- **Disaster Recovery**: 15-minute RTO for critical systems
- **Cost Control**: Healthcare margins are tight

## 🎓 What You'll Learn
By completing this lab, you will master:
1. **Azure Networking**: VNETs, subnets, and network security
2. **Compute at Scale**: Virtual Machine Scale Sets
3. **Managed Identity**: Passwordless authentication
4. **Azure SQL**: Managed database with threat detection
5. **Key Vault**: Secure secrets management
6. **Application Gateway**: Layer 7 load balancing with WAF
7. **Storage & CDN**: Global content delivery
8. **Compliance**: Healthcare industry requirements

## 🌟 Real-World Skills You'll Gain
After this lab, you'll be able to:
- Deploy production workloads on Azure
- Implement zero-trust security model
- Configure auto-scaling for cost optimization
- Set up geo-redundant disaster recovery
- Manage compliance requirements (HIPAA, GDPR)
- Integrate Azure services using managed identities
- Monitor and optimize Azure costs

## ⏱️ Duration: 60 minutes

## 💰 Cost Estimate
- **During Lab**: ~$1.00 (if destroyed within 1 hour)
- **If Left Running**: ~$150/month
- **⚠️ IMPORTANT**: Run cleanup script immediately after lab

## 📋 Prerequisites
- Azure subscription with credits
- Azure CLI configured (`az login`)
- Terraform 1.5+
- Understanding from Labs 01-02

## 🏗️ Architecture
```
HealthTech Solutions - Azure Architecture
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
              Internet Users
                    │
            Azure Front Door
                    │
            WAF Protection
                    │
┌───────────────────┼────────────────────┐
│          Application Gateway           │
│          (Layer 7 LB + WAF)           │
├────────────────────────────────────────┤
│   Virtual Network (10.0.0.0/16)       │
│                                        │
│  ┌─────────────────────────────────┐  │
│  │   Gateway Subnet                │  │
│  │   (10.0.1.0/24)                │  │
│  └─────────────────────────────────┘  │
│                                        │
│  ┌─────────────────────────────────┐  │
│  │   App Tier - VMSS               │  │
│  │   Zone 1 │ Zone 2 │ Zone 3     │  │
│  │   ┌─────┐ ┌─────┐ ┌─────┐     │  │
│  │   │ VM1 │ │ VM2 │ │ VM3 │     │  │
│  │   └─────┘ └─────┘ └─────┘     │  │
│  └─────────────────────────────────┘  │
│                                        │
│  ┌─────────────────────────────────┐  │
│  │   Data Tier - Azure SQL         │  │
│  │   Primary │ Geo-Replica         │  │
│  │   Transparent Encryption        │  │
│  └─────────────────────────────────┘  │
│                                        │
│  ┌─────────────────────────────────┐  │
│  │   Security Services             │  │
│  │   - Key Vault (Secrets)         │  │
│  │   - Managed Identity            │  │
│  │   - NSGs (Network Security)     │  │
│  └─────────────────────────────────┘  │
│                                        │
│  ┌─────────────────────────────────┐  │
│  │   Storage & CDN                 │  │
│  │   - Blob Storage (Files)        │  │
│  │   - CDN (Global Distribution)   │  │
│  └─────────────────────────────────┘  │
└────────────────────────────────────────┘

Compliance & Security:
✓ HIPAA: Encryption, Audit Logs, Access Control
✓ Data Residency: Region-locked resources
✓ Zero Trust: Managed Identity, No passwords
✓ Defense in Depth: Multiple security layers
```

## 🎬 The Healthcare Challenge
**Day 1**: "We need to store patient records securely"  
**Day 7**: "A hospital in Europe needs access"  
**Day 14**: "Ransomware attacked our competitor!"  
**Day 21**: "Emergency! System must handle pandemic-level traffic"  
**Day 30**: "Auditors are coming for HIPAA compliance check"

**Your Mission**: Build a secure, compliant, scalable healthcare platform on Azure!

## 📝 Instructions

### Part 1: Foundation - Secure Network Setup
**Compliance Need**: "Patient data must be isolated and encrypted"

#### Why This Architecture?
- **Virtual Network**: Complete network isolation for HIPAA
- **Multiple Subnets**: Separation of concerns (DMZ, App, Data)
- **Network Security Groups**: Firewall rules at subnet level
- **Private Endpoints**: Database never exposed to internet

Create `providers.tf`:
```hcl
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
  
  # Uncomment for remote backend
  # backend "azurerm" {
  #   resource_group_name  = "terraform-state-rg"
  #   storage_account_name = "tfstatestore"
  #   container_name       = "tfstate"
  #   key                  = "azure-infrastructure/terraform.tfstate"
  # }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    
    key_vault {
      purge_soft_delete_on_destroy = true
      recover_soft_deleted_key_vaults = true
    }
    
    virtual_machine {
      delete_os_disk_on_deletion = true
      graceful_shutdown = false
    }
  }
  
  skip_provider_registration = false
}

# Data source for current subscription
data "azurerm_client_config" "current" {}

# Data source for current user
data "azuread_client_config" "current" {}
```

### Step 2: Variables

Create `variables.tf`:
```hcl
variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "terraform-azure-lab"
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
  default     = "terraform-azure-lab-rg"
}

variable "vnet_address_space" {
  description = "VNET address space"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_prefixes" {
  description = "Subnet address prefixes"
  type = object({
    gateway = list(string)
    app     = list(string)
    db      = list(string)
  })
  default = {
    gateway = ["10.0.1.0/24", "10.0.2.0/24"]
    app     = ["10.0.10.0/24", "10.0.11.0/24"]
    db      = ["10.0.20.0/24", "10.0.21.0/24"]
  }
}

variable "vm_size" {
  description = "Virtual machine size"
  type        = string
  default     = "Standard_B2s"
}

variable "vmss_instance_count" {
  description = "Number of VMSS instances"
  type        = number
  default     = 2
}

variable "admin_username" {
  description = "VM admin username"
  type        = string
  default     = "azureadmin"
}

variable "sql_admin_username" {
  description = "SQL admin username"
  type        = string
  default     = "sqladmin"
  sensitive   = true
}

variable "sql_database_edition" {
  description = "SQL database edition"
  type        = string
  default     = "Basic"
}

variable "enable_zone_redundancy" {
  description = "Enable zone redundancy"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    Environment = "Lab"
    ManagedBy   = "Terraform"
    Project     = "Azure-Infrastructure"
  }
}
```

### Step 3: Resource Group and Networking

Create `network.tf`:
```hcl
# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "${var.project_name}-vnet"
  address_space       = var.vnet_address_space
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.tags
}

# Gateway Subnets
resource "azurerm_subnet" "gateway" {
  count = length(var.subnet_prefixes.gateway)
  
  name                 = "gateway-subnet-${count.index + 1}"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_prefixes.gateway[count.index]]
}

# Application Subnets
resource "azurerm_subnet" "app" {
  count = length(var.subnet_prefixes.app)
  
  name                 = "app-subnet-${count.index + 1}"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_prefixes.app[count.index]]
  
  service_endpoints = [
    "Microsoft.Sql",
    "Microsoft.Storage",
    "Microsoft.KeyVault"
  ]
}

# Database Subnets
resource "azurerm_subnet" "db" {
  count = length(var.subnet_prefixes.db)
  
  name                 = "db-subnet-${count.index + 1}"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_prefixes.db[count.index]]
  
  delegation {
    name = "sql-delegation"
    
    service_delegation {
      name = "Microsoft.Sql/managedInstances"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
        "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action",
        "Microsoft.Network/virtualNetworks/subnets/unprepareNetworkPolicies/action"
      ]
    }
  }
  
  service_endpoints = [
    "Microsoft.Sql"
  ]
}

# NAT Gateway
resource "azurerm_public_ip" "nat" {
  count = length(var.subnet_prefixes.app)
  
  name                = "${var.project_name}-nat-pip-${count.index + 1}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
  zones               = var.enable_zone_redundancy ? ["1", "2", "3"] : []
  tags                = var.tags
}

resource "azurerm_nat_gateway" "main" {
  count = length(var.subnet_prefixes.app)
  
  name                    = "${var.project_name}-nat-${count.index + 1}"
  location                = azurerm_resource_group.main.location
  resource_group_name     = azurerm_resource_group.main.name
  sku_name                = "Standard"
  idle_timeout_in_minutes = 10
  zones                   = var.enable_zone_redundancy ? [tostring(count.index + 1)] : []
  tags                    = var.tags
}

resource "azurerm_nat_gateway_public_ip_association" "main" {
  count = length(azurerm_nat_gateway.main)
  
  nat_gateway_id       = azurerm_nat_gateway.main[count.index].id
  public_ip_address_id = azurerm_public_ip.nat[count.index].id
}

resource "azurerm_subnet_nat_gateway_association" "app" {
  count = length(azurerm_subnet.app)
  
  subnet_id      = azurerm_subnet.app[count.index].id
  nat_gateway_id = azurerm_nat_gateway.main[count.index].id
}
```

### Step 4: Network Security Groups

Create `security.tf`:
```hcl
# NSG for Application Gateway
resource "azurerm_network_security_group" "gateway" {
  name                = "${var.project_name}-gateway-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.tags
  
  security_rule {
    name                       = "AllowHTTP"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  
  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  
  security_rule {
    name                       = "AllowGatewayManager"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "65200-65535"
    source_address_prefix      = "GatewayManager"
    destination_address_prefix = "*"
  }
}

# NSG for Application Subnet
resource "azurerm_network_security_group" "app" {
  name                = "${var.project_name}-app-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.tags
  
  security_rule {
    name                       = "AllowHTTPFromGateway"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefixes    = var.subnet_prefixes.gateway
    destination_address_prefix = "*"
  }
  
  security_rule {
    name                       = "AllowSSH"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.vnet_address_space[0]
    destination_address_prefix = "*"
  }
  
  security_rule {
    name                       = "AllowRDP"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = var.vnet_address_space[0]
    destination_address_prefix = "*"
  }
}

# NSG for Database Subnet
resource "azurerm_network_security_group" "db" {
  name                = "${var.project_name}-db-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.tags
  
  security_rule {
    name                       = "AllowSQLFromApp"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "1433"
    source_address_prefixes    = var.subnet_prefixes.app
    destination_address_prefix = "*"
  }
}

# Associate NSGs with Subnets
resource "azurerm_subnet_network_security_group_association" "gateway" {
  count = length(azurerm_subnet.gateway)
  
  subnet_id                 = azurerm_subnet.gateway[count.index].id
  network_security_group_id = azurerm_network_security_group.gateway.id
}

resource "azurerm_subnet_network_security_group_association" "app" {
  count = length(azurerm_subnet.app)
  
  subnet_id                 = azurerm_subnet.app[count.index].id
  network_security_group_id = azurerm_network_security_group.app.id
}

resource "azurerm_subnet_network_security_group_association" "db" {
  count = length(azurerm_subnet.db)
  
  subnet_id                 = azurerm_subnet.db[count.index].id
  network_security_group_id = azurerm_network_security_group.db.id
}
```

### Step 5: Managed Identity and Key Vault

Create `identity.tf`:
```hcl
# User Assigned Managed Identity
resource "azurerm_user_assigned_identity" "main" {
  name                = "${var.project_name}-identity"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.tags
}

# Key Vault
resource "azurerm_key_vault" "main" {
  name                = "${var.project_name}-kv-${random_string.kv_suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
  
  enabled_for_deployment          = true
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
  enable_rbac_authorization       = true
  purge_protection_enabled        = false
  soft_delete_retention_days      = 7
  
  network_acls {
    bypass         = "AzureServices"
    default_action = "Allow"
  }
  
  tags = var.tags
}

resource "random_string" "kv_suffix" {
  length  = 6
  special = false
  upper   = false
}

# Role assignments for Key Vault
resource "azurerm_role_assignment" "kv_admin" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "identity_kv_reader" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.main.principal_id
}

# Store secrets in Key Vault
resource "random_password" "vm_password" {
  length  = 32
  special = true
}

resource "azurerm_key_vault_secret" "vm_password" {
  name         = "vm-admin-password"
  value        = random_password.vm_password.result
  key_vault_id = azurerm_key_vault.main.id
  
  depends_on = [azurerm_role_assignment.kv_admin]
}

resource "random_password" "sql_password" {
  length  = 32
  special = true
}

resource "azurerm_key_vault_secret" "sql_password" {
  name         = "sql-admin-password"
  value        = random_password.sql_password.result
  key_vault_id = azurerm_key_vault.main.id
  
  depends_on = [azurerm_role_assignment.kv_admin]
}
```

### Step 6: Virtual Machine Scale Set

Create `vmss.tf`:
```hcl
# SSH Key
resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Store SSH key locally
resource "local_sensitive_file" "ssh_key" {
  content         = tls_private_key.ssh.private_key_pem
  filename        = "${path.module}/ssh-key.pem"
  file_permission = "0600"
}

# Virtual Machine Scale Set
resource "azurerm_linux_virtual_machine_scale_set" "main" {
  name                = "${var.project_name}-vmss"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = var.vm_size
  instances           = var.vmss_instance_count
  admin_username      = var.admin_username
  
  admin_ssh_key {
    username   = var.admin_username
    public_key = tls_private_key.ssh.public_key_openssh
  }
  
  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }
  
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }
  
  network_interface {
    name    = "primary"
    primary = true
    
    ip_configuration {
      name      = "internal"
      primary   = true
      subnet_id = azurerm_subnet.app[0].id
      
      application_gateway_backend_address_pool_ids = [
        azurerm_application_gateway.main.backend_address_pool[0].id
      ]
    }
  }
  
  identity {
    type = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.main.id]
  }
  
  custom_data = base64encode(templatefile("${path.module}/cloud-init.yaml", {
    project_name = var.project_name
    environment  = var.environment
    db_server    = azurerm_mssql_server.main.fully_qualified_domain_name
    db_name      = azurerm_mssql_database.main.name
    storage_account = azurerm_storage_account.main.primary_blob_endpoint
    key_vault_name = azurerm_key_vault.main.name
  }))
  
  boot_diagnostics {
    storage_account_uri = azurerm_storage_account.main.primary_blob_endpoint
  }
  
  automatic_instance_repair {
    enabled      = true
    grace_period = "PT30M"
  }
  
  automatic_os_upgrade_policy {
    disable_automatic_rollback = false
    enable_automatic_os_upgrade = true
  }
  
  rolling_upgrade_policy {
    max_batch_instance_percent              = 20
    max_unhealthy_instance_percent           = 20
    max_unhealthy_upgraded_instance_percent = 20
    pause_time_between_batches              = "PT5M"
  }
  
  health_probe_id = azurerm_lb_probe.vmss.id
  
  tags = var.tags
  
  depends_on = [
    azurerm_application_gateway.main
  ]
}

# Autoscale Settings
resource "azurerm_monitor_autoscale_setting" "vmss" {
  name                = "${var.project_name}-vmss-autoscale"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  target_resource_id  = azurerm_linux_virtual_machine_scale_set.main.id
  
  profile {
    name = "default"
    
    capacity {
      default = var.vmss_instance_count
      minimum = 2
      maximum = 10
    }
    
    rule {
      metric_trigger {
        metric_name        = "Percentage CPU"
        metric_resource_id = azurerm_linux_virtual_machine_scale_set.main.id
        time_grain         = "PT1M"
        statistic          = "Average"
        time_window        = "PT5M"
        time_aggregation   = "Average"
        operator           = "GreaterThan"
        threshold          = 70
      }
      
      scale_action {
        direction = "Increase"
        type      = "ChangeCount"
        value     = "1"
        cooldown  = "PT5M"
      }
    }
    
    rule {
      metric_trigger {
        metric_name        = "Percentage CPU"
        metric_resource_id = azurerm_linux_virtual_machine_scale_set.main.id
        time_grain         = "PT1M"
        statistic          = "Average"
        time_window        = "PT5M"
        time_aggregation   = "Average"
        operator           = "LessThan"
        threshold          = 30
      }
      
      scale_action {
        direction = "Decrease"
        type      = "ChangeCount"
        value     = "1"
        cooldown  = "PT5M"
      }
    }
  }
  
  notification {
    operation = "Scale"
    
    email {
      send_to_subscription_administrator    = false
      send_to_subscription_co_administrators = false
      custom_emails                          = ["devops@example.com"]
    }
  }
}
```

### Step 7: Load Balancer and Application Gateway

Create `load_balancer.tf`:
```hcl
# Public IP for Load Balancer
resource "azurerm_public_ip" "lb" {
  name                = "${var.project_name}-lb-pip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
  zones               = var.enable_zone_redundancy ? ["1", "2", "3"] : []
  tags                = var.tags
}

# Load Balancer for health probes
resource "azurerm_lb" "vmss" {
  name                = "${var.project_name}-lb"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"
  
  frontend_ip_configuration {
    name                 = "PublicIPAddress"
    public_ip_address_id = azurerm_public_ip.lb.id
  }
  
  tags = var.tags
}

resource "azurerm_lb_probe" "vmss" {
  loadbalancer_id = azurerm_lb.vmss.id
  name            = "health-probe"
  port            = 80
  protocol        = "Http"
  request_path    = "/health"
}

# Public IP for Application Gateway
resource "azurerm_public_ip" "appgw" {
  name                = "${var.project_name}-appgw-pip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
  zones               = var.enable_zone_redundancy ? ["1", "2", "3"] : []
  tags                = var.tags
}

# Application Gateway
resource "azurerm_application_gateway" "main" {
  name                = "${var.project_name}-appgw"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  sku {
    name     = "Standard_v2"
    tier     = "Standard_v2"
    capacity = 2
  }
  
  gateway_ip_configuration {
    name      = "gateway-ip-config"
    subnet_id = azurerm_subnet.gateway[0].id
  }
  
  frontend_port {
    name = "http-port"
    port = 80
  }
  
  frontend_port {
    name = "https-port"
    port = 443
  }
  
  frontend_ip_configuration {
    name                 = "public-ip"
    public_ip_address_id = azurerm_public_ip.appgw.id
  }
  
  backend_address_pool {
    name = "vmss-backend-pool"
  }
  
  backend_http_settings {
    name                  = "http-settings"
    cookie_based_affinity = "Enabled"
    port                  = 80
    protocol              = "Http"
    request_timeout       = 30
    
    probe_name = "health-probe"
  }
  
  http_listener {
    name                           = "http-listener"
    frontend_ip_configuration_name = "public-ip"
    frontend_port_name             = "http-port"
    protocol                       = "Http"
  }
  
  request_routing_rule {
    name                       = "http-rule"
    rule_type                  = "Basic"
    http_listener_name         = "http-listener"
    backend_address_pool_name  = "vmss-backend-pool"
    backend_http_settings_name = "http-settings"
    priority                   = 100
  }
  
  probe {
    name                = "health-probe"
    protocol            = "Http"
    path                = "/health"
    host                = "127.0.0.1"
    interval            = 30
    timeout             = 30
    unhealthy_threshold = 3
  }
  
  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
  }
  
  autoscale_configuration {
    min_capacity = 2
    max_capacity = 10
  }
  
  tags = var.tags
}
```

### Step 8: Azure SQL Database

Create `database.tf`:
```hcl
# SQL Server
resource "azurerm_mssql_server" "main" {
  name                         = "${var.project_name}-sqlserver-${random_string.sql_suffix.result}"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_username
  administrator_login_password = random_password.sql_password.result
  
  azuread_administrator {
    login_username = "AzureAD Admin"
    object_id      = data.azurerm_client_config.current.object_id
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  tags = var.tags
}

resource "random_string" "sql_suffix" {
  length  = 6
  special = false
  upper   = false
}

# SQL Database
resource "azurerm_mssql_database" "main" {
  name      = "${var.project_name}-db"
  server_id = azurerm_mssql_server.main.id
  
  sku_name                    = var.sql_database_edition
  zone_redundant              = var.enable_zone_redundancy
  auto_pause_delay_in_minutes = var.environment != "prod" ? 60 : -1
  min_capacity                = var.environment != "prod" ? 0.5 : 1
  
  threat_detection_policy {
    state                      = "Enabled"
    email_account_admins       = true
    retention_days             = 30
    disabled_alerts            = []
    email_addresses            = ["security@example.com"]
    storage_account_access_key = azurerm_storage_account.main.primary_access_key
    storage_endpoint           = azurerm_storage_account.main.primary_blob_endpoint
  }
  
  tags = var.tags
}

# Firewall Rules
resource "azurerm_mssql_firewall_rule" "allow_azure" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

resource "azurerm_mssql_virtual_network_rule" "app" {
  count = length(azurerm_subnet.app)
  
  name      = "app-subnet-${count.index + 1}"
  server_id = azurerm_mssql_server.main.id
  subnet_id = azurerm_subnet.app[count.index].id
}

# Database Backup Policy
resource "azurerm_mssql_database_extended_auditing_policy" "main" {
  database_id                             = azurerm_mssql_database.main.id
  storage_endpoint                        = azurerm_storage_account.main.primary_blob_endpoint
  storage_account_access_key              = azurerm_storage_account.main.primary_access_key
  storage_account_access_key_is_secondary = false
  retention_in_days                       = 30
}
```

### Step 9: Storage and CDN

Create `storage.tf`:
```hcl
# Storage Account
resource "azurerm_storage_account" "main" {
  name                     = "${lower(replace(var.project_name, "-", ""))}st${random_string.storage_suffix.result}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = var.environment == "prod" ? "GRS" : "LRS"
  
  blob_properties {
    versioning_enabled = true
    
    delete_retention_policy {
      days = 7
    }
    
    container_delete_retention_policy {
      days = 7
    }
  }
  
  network_rules {
    default_action             = "Allow"
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = azurerm_subnet.app[*].id
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  tags = var.tags
}

resource "random_string" "storage_suffix" {
  length  = 6
  special = false
  upper   = false
}

# Storage Containers
resource "azurerm_storage_container" "assets" {
  name                  = "assets"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "backups" {
  name                  = "backups"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# CDN Profile
resource "azurerm_cdn_profile" "main" {
  name                = "${var.project_name}-cdn"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard_Microsoft"
  tags                = var.tags
}

# CDN Endpoint
resource "azurerm_cdn_endpoint" "assets" {
  name                = "${var.project_name}-assets"
  profile_name        = azurerm_cdn_profile.main.name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  origin {
    name      = "storage"
    host_name = azurerm_storage_account.main.primary_blob_endpoint
  }
  
  is_compression_enabled = true
  content_types_to_compress = [
    "text/html",
    "text/css",
    "text/javascript",
    "application/javascript",
    "application/json"
  ]
  
  global_delivery_rule {
    cache_expiration_action {
      behavior = "Override"
      duration = "365.00:00:00"
    }
  }
  
  delivery_rule {
    name  = "EnforceHTTPS"
    order = 1
    
    request_scheme_condition {
      operator     = "Equal"
      match_values = ["HTTP"]
    }
    
    url_redirect_action {
      redirect_type = "PermanentRedirect"
      protocol      = "Https"
    }
  }
  
  tags = var.tags
}
```

### Step 10: Cloud Init Configuration

Create `cloud-init.yaml`:
```yaml
#cloud-config
package_update: true
package_upgrade: true

packages:
  - nginx
  - docker.io
  - azure-cli
  - jq

write_files:
  - path: /etc/nginx/sites-available/default
    content: |
      server {
        listen 80 default_server;
        listen [::]:80 default_server;
        
        root /var/www/html;
        index index.html;
        
        server_name _;
        
        location / {
          try_files $uri $uri/ =404;
        }
        
        location /health {
          access_log off;
          return 200 "healthy\n";
          add_header Content-Type text/plain;
        }
      }
  
  - path: /var/www/html/index.html
    content: |
      <!DOCTYPE html>
      <html>
      <head>
          <title>${project_name} - ${environment}</title>
      </head>
      <body>
          <h1>Azure Virtual Machine Scale Set</h1>
          <p>Project: ${project_name}</p>
          <p>Environment: ${environment}</p>
          <p>Instance: $(hostname)</p>
          <p>Database: ${db_server}/${db_name}</p>
      </body>
      </html>

runcmd:
  - systemctl restart nginx
  - systemctl enable nginx
  - az login --identity
  - |
    # Get secrets from Key Vault
    DB_PASSWORD=$(az keyvault secret show --vault-name ${key_vault_name} --name sql-admin-password --query value -o tsv)
    echo "Database password retrieved from Key Vault"
  - |
    # Docker setup
    systemctl enable docker
    systemctl start docker
    usermod -aG docker azureadmin
```

### Step 11: Outputs

Create `outputs.tf`:
```hcl
output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "vnet_id" {
  description = "Virtual Network ID"
  value       = azurerm_virtual_network.main.id
}

output "application_gateway_url" {
  description = "Application Gateway URL"
  value       = "http://${azurerm_public_ip.appgw.ip_address}"
}

output "sql_server_fqdn" {
  description = "SQL Server FQDN"
  value       = azurerm_mssql_server.main.fully_qualified_domain_name
}

output "storage_account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.main.name
}

output "cdn_endpoint_url" {
  description = "CDN endpoint URL"
  value       = "https://${azurerm_cdn_endpoint.assets.host_name}"
}

output "key_vault_uri" {
  description = "Key Vault URI"
  value       = azurerm_key_vault.main.vault_uri
}

output "ssh_private_key_path" {
  description = "Path to SSH private key"
  value       = local_sensitive_file.ssh_key.filename
}

output "vmss_instances" {
  description = "VMSS instance count"
  value       = azurerm_linux_virtual_machine_scale_set.main.instances
}
```

## ✅ Verification Steps

Run `scripts/verify.sh`:
```bash
#!/bin/bash

echo "🔍 Verifying Lab 03 - Azure Infrastructure..."

# Check Azure CLI
echo "Azure Account:"
az account show --query "{Name:name, ID:id}" -o table

# Initialize Terraform
echo -e "\n📦 Initializing Terraform..."
terraform init

# Validate configuration
echo -e "\n✔️ Validating configuration..."
terraform validate

# After apply, verify resources
if [ -f "terraform.tfstate" ]; then
    echo -e "\n🏗️ Deployed resources:"
    
    # Resource Group
    RG=$(terraform output -raw resource_group_name 2>/dev/null)
    if [ ! -z "$RG" ]; then
        echo "✅ Resource Group: $RG"
        az group show -n $RG --query "location" -o tsv
    fi
    
    # Application Gateway
    APPGW_URL=$(terraform output -raw application_gateway_url 2>/dev/null)
    if [ ! -z "$APPGW_URL" ]; then
        echo "✅ Application Gateway: $APPGW_URL"
        curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" $APPGW_URL/health || true
    fi
    
    # VMSS
    echo "✅ VMSS Instances:"
    az vmss list-instances -g $RG -n ${var.project_name}-vmss --query "[].{Name:name, ProvisioningState:provisioningState}" -o table
    
    # SQL Database
    SQL_FQDN=$(terraform output -raw sql_server_fqdn 2>/dev/null)
    if [ ! -z "$SQL_FQDN" ]; then
        echo "✅ SQL Server: $SQL_FQDN"
    fi
    
    # Storage Account
    STORAGE=$(terraform output -raw storage_account_name 2>/dev/null)
    if [ ! -z "$STORAGE" ]; then
        echo "✅ Storage Account: $STORAGE"
        az storage account show -n $STORAGE -g $RG --query "primaryEndpoints" -o table
    fi
fi

echo -e "\n✅ Lab 03 verification complete!"
```

## 🧹 Cleanup

Run `scripts/cleanup.sh`:
```bash
#!/bin/bash

echo "🧹 Cleaning up Lab 03 - Azure Infrastructure..."

# Confirm destruction
read -p "Are you sure you want to destroy all resources? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

# Destroy resources
terraform destroy -auto-approve

# Clean up local files
rm -f ssh-key.pem
rm -f terraform.tfstate*
rm -f tfplan
rm -rf .terraform

echo "✅ Cleanup complete!"
```

## 🐛 Troubleshooting

### Authentication Issues
```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-id"

# Create service principal
az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/your-subscription-id"
```

### VMSS Connection
```bash
# Connect to VMSS instance
az vmss list-instance-connection-info \
  -g terraform-azure-lab-rg \
  -n terraform-azure-lab-vmss

# SSH to instance
ssh -i ssh-key.pem azureadmin@<instance-ip>
```

### Cost Management
```bash
# Deallocate VMSS instances
az vmss deallocate -g terraform-azure-lab-rg -n terraform-azure-lab-vmss

# Stop SQL Database
az sql db update -g terraform-azure-lab-rg \
  -s terraform-azure-lab-sqlserver \
  -n terraform-azure-lab-db \
  --compute-model Serverless \
  --auto-pause-delay 60
```

## 📚 Additional Resources
- [Azure Provider Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Architecture Center](https://docs.microsoft.com/en-us/azure/architecture/)
- [Azure Terraform Modules](https://github.com/Azure/terraform-azurerm-modules)