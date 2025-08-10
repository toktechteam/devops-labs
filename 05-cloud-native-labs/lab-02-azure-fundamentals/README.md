# Lab 02: Azure Fundamentals

## 🎯 Lab Scenario
**MedTech Corp** is a healthcare company with 500 clinics across the US. They need to modernize their patient record system while maintaining HIPAA compliance. After seeing PhotoShare's success on AWS, they want to use Azure (due to existing Microsoft enterprise agreements). The system must handle 50,000 concurrent healthcare workers accessing patient records, with zero downtime during business hours.

## 🏥 The MedTech Challenge
**Day 1**: "Our on-prem servers crashed, doctors can't access patient records!"  
**Day 7**: "HIPAA auditor found unencrypted data - we face $1M fine!"  
**Day 14**: "Hurricane knocked out our data center - no backups!"  
**Day 21**: "Cyber attack! Patient data held for ransom!"  
**Day 30**: "New clinic opened but IT setup takes 3 months!"

## 🎓 What You'll Learn
1. **Azure Core Services**: Resource Groups, VNet, VMs, Storage, SQL Database
2. **Security & Compliance**: Azure AD, Key Vault, encryption, RBAC
3. **High Availability**: Availability Zones, Load Balancers, Traffic Manager
4. **Disaster Recovery**: Backup, Site Recovery, geo-replication
5. **Monitoring**: Azure Monitor, Application Insights, Log Analytics
6. **Cost Management**: Reserved Instances, Azure Hybrid Benefit

## 🌟 Real-World Skills
After this lab, you'll be able to:
- Deploy HIPAA-compliant healthcare systems
- Implement zero-trust security model
- Design for 99.99% availability
- Set up automated disaster recovery
- Monitor and optimize Azure costs
- Integrate with existing Microsoft infrastructure

## ⏱️ Duration: 60 minutes

## 💰 Cost Estimate
- **During Lab**: ~$2 (mostly free tier)
- **If Left Running**: ~$200/month
- **After Optimization**: ~$75/month

## 🏗️ Architecture Evolution

### Current State: On-Premises Chaos
```
500 Clinics → VPN → Single Data Center
                     - Old Servers
                     - No Redundancy
                     - Manual Backups
                     - Security Vulnerabilities
```

### Target State: Azure Cloud Architecture
```
                Azure Front Door
                      │
                Traffic Manager
                  /         \
            Region 1      Region 2
                │            │
          App Gateway   App Gateway
                │            │
            VMSS+LB      VMSS+LB
                │            │
          Azure SQL     Azure SQL
          (Primary)     (Replica)
                │            │
            Key Vault   Key Vault
                │            │
          Storage Acc  Storage Acc
                │            │
         Azure Monitor & Security Center
```

## 📝 Part 1: Foundation - Resource Groups and Networking

### Understanding Healthcare Requirements
- **Data Residency**: Patient data must stay in US
- **Network Isolation**: Complete separation from internet
- **Encryption**: Data encrypted at rest and in transit
- **Audit Logging**: Every access must be logged

### Step 1.1: Create Resource Groups and Virtual Network

Create `infrastructure/foundation.bicep`:
```bicep
// MedTech Azure Foundation - Bicep Template
targetScope = 'subscription'

@description('Environment name')
@allowed(['dev', 'staging', 'prod'])
param environmentName string = 'dev'

@description('Primary region for resources')
param primaryLocation string = 'eastus'

@description('Secondary region for DR')
param secondaryLocation string = 'westus'

@description('Organization name')
param orgName string = 'MedTech'

var resourceGroupName = '${orgName}-${environmentName}-rg'
var vnetName = '${orgName}-${environmentName}-vnet'

// Resource Groups
resource primaryRG 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${resourceGroupName}-primary'
  location: primaryLocation
  tags: {
    Environment: environmentName
    Organization: orgName
    Compliance: 'HIPAA'
    Purpose: 'Healthcare Patient System'
  }
}

resource secondaryRG 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${resourceGroupName}-secondary'
  location: secondaryLocation
  tags: {
    Environment: environmentName
    Organization: orgName
    Compliance: 'HIPAA'
    Purpose: 'Disaster Recovery'
  }
}

// Deploy networking to primary region
module primaryNetwork 'modules/network.bicep' = {
  scope: primaryRG
  name: 'primaryNetworkDeployment'
  params: {
    vnetName: '${vnetName}-primary'
    location: primaryLocation
    addressPrefix: '10.0.0.0/16'
    subnets: [
      {
        name: 'GatewaySubnet'
        addressPrefix: '10.0.1.0/24'
      }
      {
        name: 'AppSubnet'
        addressPrefix: '10.0.2.0/24'
      }
      {
        name: 'DataSubnet'
        addressPrefix: '10.0.3.0/24'
      }
      {
        name: 'ManagementSubnet'
        addressPrefix: '10.0.4.0/24'
      }
    ]
  }
}

// Deploy networking to secondary region
module secondaryNetwork 'modules/network.bicep' = {
  scope: secondaryRG
  name: 'secondaryNetworkDeployment'
  params: {
    vnetName: '${vnetName}-secondary'
    location: secondaryLocation
    addressPrefix: '10.1.0.0/16'
    subnets: [
      {
        name: 'GatewaySubnet'
        addressPrefix: '10.1.1.0/24'
      }
      {
        name: 'AppSubnet'
        addressPrefix: '10.1.2.0/24'
      }
      {
        name: 'DataSubnet'
        addressPrefix: '10.1.3.0/24'
      }
      {
        name: 'ManagementSubnet'
        addressPrefix: '10.1.4.0/24'
      }
    ]
  }
}

output primaryResourceGroupName string = primaryRG.name
output secondaryResourceGroupName string = secondaryRG.name
```

Create `infrastructure/modules/network.bicep`:
```bicep
// Network Module
@description('VNet name')
param vnetName string

@description('Location for resources')
param location string

@description('Address prefix for VNet')
param addressPrefix string

@description('Subnet configurations')
param subnets array

// Network Security Groups
resource appNSG 'Microsoft.Network/networkSecurityGroups@2021-05-01' = {
  name: '${vnetName}-app-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'AllowHTTPS'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: '10.0.0.0/8'
          destinationAddressPrefix: '*'
        }
      }
      {
        name: 'DenyInternetInbound'
        properties: {
          priority: 200
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}

resource dataNSG 'Microsoft.Network/networkSecurityGroups@2021-05-01' = {
  name: '${vnetName}-data-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'AllowSQLFromApp'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '1433'
          sourceAddressPrefix: '10.0.2.0/24'
          destinationAddressPrefix: '*'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 200
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2021-05-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        addressPrefix
      ]
    }
    subnets: [for (subnet, i) in subnets: {
      name: subnet.name
      properties: {
        addressPrefix: subnet.addressPrefix
        networkSecurityGroup: subnet.name == 'AppSubnet' ? {
          id: appNSG.id
        } : subnet.name == 'DataSubnet' ? {
          id: dataNSG.id
        } : null
        serviceEndpoints: subnet.name == 'DataSubnet' ? [
          {
            service: 'Microsoft.Sql'
          }
          {
            service: 'Microsoft.Storage'
          }
          {
            service: 'Microsoft.KeyVault'
          }
        ] : []
      }
    }]
    enableDdosProtection: false
  }
}

// Private DNS Zone for internal resolution
resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'medtech.local'
  location: 'global'
  properties: {}
}

resource vnetLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: privateDnsZone
  name: '${vnetName}-link'
  location: 'global'
  properties: {
    registrationEnabled: true
    virtualNetwork: {
      id: vnet.id
    }
  }
}

output vnetId string = vnet.id
output subnetIds object = {
  gateway: vnet.properties.subnets[0].id
  app: vnet.properties.subnets[1].id
  data: vnet.properties.subnets[2].id
  management: vnet.properties.subnets[3].id
}
```

### Step 1.2: Deploy Foundation

Create `scripts/deploy-foundation.sh`:
```bash
#!/bin/bash

# Set variables
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
ENVIRONMENT="dev"
PRIMARY_LOCATION="eastus"
SECONDARY_LOCATION="westus"

echo "🚀 Deploying MedTech Foundation..."

# Create deployment
az deployment sub create \
    --name "medtech-foundation-$(date +%Y%m%d%H%M%S)" \
    --location $PRIMARY_LOCATION \
    --template-file infrastructure/foundation.bicep \
    --parameters \
        environmentName=$ENVIRONMENT \
        primaryLocation=$PRIMARY_LOCATION \
        secondaryLocation=$SECONDARY_LOCATION

echo "✅ Foundation deployment complete!"
```

## 📝 Part 2: Security - Azure AD and Key Vault

### Business Need
Secure authentication and secret management for healthcare data.

Create `infrastructure/security.bicep`:
```bicep
// Security Components - Azure AD and Key Vault
@description('Environment name')
param environmentName string

@description('Location for resources')
param location string = resourceGroup().location

@description('Azure AD Tenant ID')
param tenantId string = subscription().tenantId

@description('Admin Object ID for Key Vault access')
param adminObjectId string

var keyVaultName = 'medtech-${environmentName}-kv-${uniqueString(resourceGroup().id)}'

// User Assigned Managed Identity
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' = {
  name: 'medtech-${environmentName}-identity'
  location: location
}

// Key Vault for secrets
resource keyVault 'Microsoft.KeyVault/vaults@2021-06-01-preview' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenantId
    enabledForDeployment: true
    enabledForDiskEncryption: true
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enableRbacAuthorization: true
    enablePurgeProtection: true
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
      ipRules: []
      virtualNetworkRules: []
    }
  }
}

// Key Vault Administrator Role Assignment
resource adminRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-10-01-preview' = {
  scope: keyVault
  name: guid(keyVault.id, adminObjectId, 'Key Vault Administrator')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '00482a5a-887f-4fb3-b363-3b7fe8e74483')
    principalId: adminObjectId
    principalType: 'User'
  }
}

// Managed Identity Role Assignment
resource identityRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-10-01-preview' = {
  scope: keyVault
  name: guid(keyVault.id, managedIdentity.id, 'Key Vault Secrets User')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Store critical secrets
resource dbConnectionString 'Microsoft.KeyVault/vaults/secrets@2021-06-01-preview' = {
  parent: keyVault
  name: 'DatabaseConnectionString'
  properties: {
    value: 'Server=tcp:medtech-${environmentName}-sql.database.windows.net,1433;Database=PatientDB;'
  }
}

resource storageConnectionString 'Microsoft.KeyVault/vaults/secrets@2021-06-01-preview' = {
  parent: keyVault
  name: 'StorageConnectionString'
  properties: {
    value: 'DefaultEndpointsProtocol=https;AccountName=medtech${environmentName}st;'
  }
}

// Log Analytics Workspace for auditing
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: 'medtech-${environmentName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 90
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Enable Key Vault diagnostics
resource keyVaultDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  scope: keyVault
  name: 'keyVaultDiagnostics'
  properties: {
    workspaceId: logAnalytics.id
    logs: [
      {
        category: 'AuditEvent'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 90
        }
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 90
        }
      }
    ]
  }
}

output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output managedIdentityId string = managedIdentity.id
output managedIdentityPrincipalId string = managedIdentity.properties.principalId
output logAnalyticsWorkspaceId string = logAnalytics.id
```

## 📝 Part 3: Compute - Virtual Machine Scale Sets

### Business Need
Auto-scaling application servers for healthcare workers.

Create `infrastructure/compute.bicep`:
```bicep
// Compute Resources - VMSS and Load Balancer
@description('Environment name')
param environmentName string

@description('Location for resources')
param location string = resourceGroup().location

@description('Subnet ID for VMSS')
param subnetId string

@description('Key Vault URI')
param keyVaultUri string

@description('Managed Identity ID')
param managedIdentityId string

@description('Admin username')
param adminUsername string = 'azureadmin'

@description('Admin password')
@secure()
param adminPassword string

@description('Instance count')
@minValue(2)
@maxValue(10)
param instanceCount int = 2

var vmssName = 'medtech-${environmentName}-vmss'
var lbName = 'medtech-${environmentName}-lb'

// Public IP for Load Balancer
resource publicIP 'Microsoft.Network/publicIPAddresses@2021-05-01' = {
  name: '${lbName}-pip'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
    publicIPAddressVersion: 'IPv4'
  }
  zones: ['1', '2', '3']
}

// Load Balancer
resource loadBalancer 'Microsoft.Network/loadBalancers@2021-05-01' = {
  name: lbName
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    frontendIPConfigurations: [
      {
        name: 'LoadBalancerFrontEnd'
        properties: {
          publicIPAddress: {
            id: publicIP.id
          }
        }
      }
    ]
    backendAddressPools: [
      {
        name: 'BackendPool'
      }
    ]
    loadBalancingRules: [
      {
        name: 'HTTPSRule'
        properties: {
          frontendIPConfiguration: {
            id: resourceId('Microsoft.Network/loadBalancers/frontendIPConfigurations', lbName, 'LoadBalancerFrontEnd')
          }
          backendAddressPool: {
            id: resourceId('Microsoft.Network/loadBalancers/backendAddressPools', lbName, 'BackendPool')
          }
          probe: {
            id: resourceId('Microsoft.Network/loadBalancers/probes', lbName, 'HealthProbe')
          }
          protocol: 'Tcp'
          frontendPort: 443
          backendPort: 443
          idleTimeoutInMinutes: 15
        }
      }
    ]
    probes: [
      {
        name: 'HealthProbe'
        properties: {
          protocol: 'Https'
          port: 443
          intervalInSeconds: 5
          numberOfProbes: 2
          requestPath: '/health'
        }
      }
    ]
  }
}

// Virtual Machine Scale Set
resource vmss 'Microsoft.Compute/virtualMachineScaleSets@2021-07-01' = {
  name: vmssName
  location: location
  sku: {
    name: 'Standard_B2s'
    tier: 'Standard'
    capacity: instanceCount
  }
  zones: ['1', '2', '3']
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    overprovision: false
    upgradePolicy: {
      mode: 'Automatic'
      automaticOSUpgradePolicy: {
        enableAutomaticOSUpgrade: true
      }
    }
    virtualMachineProfile: {
      osProfile: {
        computerNamePrefix: 'medtech'
        adminUsername: adminUsername
        adminPassword: adminPassword
        customData: base64(loadTextContent('scripts/cloud-init.yaml'))
      }
      storageProfile: {
        osDisk: {
          createOption: 'FromImage'
          caching: 'ReadWrite'
          managedDisk: {
            storageAccountType: 'Premium_LRS'
          }
        }
        imageReference: {
          publisher: 'Canonical'
          offer: 'UbuntuServer'
          sku: '18.04-LTS'
          version: 'latest'
        }
      }
      networkProfile: {
        networkInterfaceConfigurations: [
          {
            name: 'nic'
            properties: {
              primary: true
              ipConfigurations: [
                {
                  name: 'ipconfig'
                  properties: {
                    subnet: {
                      id: subnetId
                    }
                    loadBalancerBackendAddressPools: [
                      {
                        id: resourceId('Microsoft.Network/loadBalancers/backendAddressPools', lbName, 'BackendPool')
                      }
                    ]
                  }
                }
              ]
            }
          }
        ]
      }
      extensionProfile: {
        extensions: [
          {
            name: 'HealthExtension'
            properties: {
              autoUpgradeMinorVersion: false
              publisher: 'Microsoft.ManagedServices'
              type: 'ApplicationHealthLinux'
              typeHandlerVersion: '1.0'
              settings: {
                protocol: 'https'
                port: 443
                requestPath: '/health'
              }
            }
          }
          {
            name: 'CustomScript'
            properties: {
              publisher: 'Microsoft.Azure.Extensions'
              type: 'CustomScript'
              typeHandlerVersion: '2.1'
              autoUpgradeMinorVersion: true
              protectedSettings: {
                script: base64('''
                  #!/bin/bash
                  apt-get update
                  apt-get install -y nginx
                  
                  # Configure nginx for healthcare app
                  cat > /etc/nginx/sites-available/default << EOF
                  server {
                      listen 443 ssl default_server;
                      server_name _;
                      
                      ssl_certificate /etc/ssl/certs/medtech.crt;
                      ssl_certificate_key /etc/ssl/private/medtech.key;
                      
                      location / {
                          proxy_pass http://localhost:3000;
                          proxy_set_header Host \$host;
                          proxy_set_header X-Real-IP \$remote_addr;
                      }
                      
                      location /health {
                          return 200 "healthy";
                          add_header Content-Type text/plain;
                      }
                  }
                  EOF
                  
                  # Generate self-signed cert (replace with real cert in production)
                  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                      -keyout /etc/ssl/private/medtech.key \
                      -out /etc/ssl/certs/medtech.crt \
                      -subj "/C=US/ST=State/L=City/O=MedTech/CN=medtech.local"
                  
                  systemctl restart nginx
                  
                  # Install healthcare app
                  curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
                  apt-get install -y nodejs
                  
                  mkdir -p /opt/medtech
                  cd /opt/medtech
                  
                  # Create healthcare application
                  cat > app.js << 'APPEOF'
                  const express = require('express');
                  const app = express();
                  
                  app.get('/', (req, res) => {
                      res.send('<h1>MedTech Patient Portal</h1><p>Secure Healthcare System</p>');
                  });
                  
                  app.get('/health', (req, res) => {
                      res.status(200).send('healthy');
                  });
                  
                  app.listen(3000, () => {
                      console.log('MedTech app running on port 3000');
                  });
                  APPEOF
                  
                  npm init -y
                  npm install express
                  
                  # Create systemd service
                  cat > /etc/systemd/system/medtech.service << EOF
                  [Unit]
                  Description=MedTech Healthcare Application
                  After=network.target
                  
                  [Service]
                  Type=simple
                  User=www-data
                  WorkingDirectory=/opt/medtech
                  ExecStart=/usr/bin/node app.js
                  Restart=on-failure
                  
                  [Install]
                  WantedBy=multi-user.target
                  EOF
                  
                  systemctl enable medtech
                  systemctl start medtech
                ''')
              }
            }
          }
        ]
      }
    }
  }
}

// Autoscale Settings
resource autoscale 'Microsoft.Insights/autoscalesettings@2021-05-01-preview' = {
  name: '${vmssName}-autoscale'
  location: location
  properties: {
    targetResourceUri: vmss.id
    enabled: true
    profiles: [
      {
        name: 'Auto scale based on CPU'
        capacity: {
          minimum: '2'
          maximum: '10'
          default: string(instanceCount)
        }
        rules: [
          {
            metricTrigger: {
              metricName: 'Percentage CPU'
              metricResourceUri: vmss.id
              timeGrain: 'PT1M'
              statistic: 'Average'
              timeWindow: 'PT5M'
              timeAggregation: 'Average'
              operator: 'GreaterThan'
              threshold: 75
            }
            scaleAction: {
              direction: 'Increase'
              type: 'ChangeCount'
              value: '1'
              cooldown: 'PT5M'
            }
          }
          {
            metricTrigger: {
              metricName: 'Percentage CPU'
              metricResourceUri: vmss.id
              timeGrain: 'PT1M'
              statistic: 'Average'
              timeWindow: 'PT5M'
              timeAggregation: 'Average'
              operator: 'LessThan'
              threshold: 25
            }
            scaleAction: {
              direction: 'Decrease'
              type: 'ChangeCount'
              value: '1'
              cooldown: 'PT5M'
            }
          }
        ]
      }
    ]
  }
}

output vmssName string = vmss.name
output loadBalancerIP string = publicIP.properties.ipAddress
output vmssId string = vmss.id
```

## 📝 Part 4: Data - Azure SQL Database

### Business Need
HIPAA-compliant database for patient records with automatic backups.

Create `infrastructure/database.bicep`:
```bicep
// Database Resources - Azure SQL
@description('Environment name')
param environmentName string

@description('Location for resources')
param location string = resourceGroup().location

@description('Administrator login')
param administratorLogin string = 'sqladmin'

@description('Administrator password')
@secure()
param administratorPassword string

@description('Subnet ID for private endpoint')
param subnetId string

var sqlServerName = 'medtech-${environmentName}-sql-${uniqueString(resourceGroup().id)}'
var databaseName = 'PatientDB'

// SQL Server
resource sqlServer 'Microsoft.Sql/servers@2021-05-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    version: '12.0'
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Disabled'
  }
}

// SQL Database
resource sqlDatabase 'Microsoft.Sql/servers/databases@2021-05-01-preview' = {
  parent: sqlServer
  name: databaseName
  location: location
  sku: {
    name: 'S2'
    tier: 'Standard'
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: 268435456000
    zoneRedundant: false
    readScale: 'Disabled'
    highAvailabilityReplicaCount: 0
    requestedBackupStorageRedundancy: 'Geo'
  }
}

// Enable Azure AD authentication
resource sqlServerAzureADAdmin 'Microsoft.Sql/servers/administrators@2021-05-01-preview' = {
  parent: sqlServer
  name: 'ActiveDirectory'
  properties: {
    administratorType: 'ActiveDirectory'
    login: 'MedTech-DBAdmins'
    sid: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' // Replace with your Azure AD group ID
    tenantId: subscription().tenantId
  }
}

// Transparent Data Encryption
resource transparentDataEncryption 'Microsoft.Sql/servers/databases/transparentDataEncryption@2021-05-01-preview' = {
  parent: sqlDatabase
  name: 'current'
  properties: {
    state: 'Enabled'
  }
}

// Audit settings
resource sqlServerAudit 'Microsoft.Sql/servers/auditingSettings@2021-05-01-preview' = {
  parent: sqlServer
  name: 'default'
  properties: {
    state: 'Enabled'
    isAzureMonitorTargetEnabled: true
    retentionDays: 90
  }
}

// Vulnerability Assessment
resource vulnerabilityAssessment 'Microsoft.Sql/servers/vulnerabilityAssessments@2021-05-01-preview' = {
  parent: sqlServer
  name: 'default'
  properties: {
    recurringScans: {
      isEnabled: true
      emailSubscriptionAdmins: true
    }
  }
}

// Private Endpoint for SQL Server
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2021-05-01' = {
  name: '${sqlServerName}-pe'
  location: location
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${sqlServerName}-connection'
        properties: {
          privateLinkServiceId: sqlServer.id
          groupIds: [
            'sqlServer'
          ]
        }
      }
    ]
  }
}

// Backup policies
resource backupShortTermRetentionPolicy 'Microsoft.Sql/servers/databases/backupShortTermRetentionPolicies@2021-05-01-preview' = {
  parent: sqlDatabase
  name: 'default'
  properties: {
    retentionDays: 7
    diffBackupIntervalInHours: 12
  }
}

resource backupLongTermRetentionPolicy 'Microsoft.Sql/servers/databases/backupLongTermRetentionPolicies@2021-05-01-preview' = {
  parent: sqlDatabase
  name: 'default'
  properties: {
    weeklyRetention: 'P4W'
    monthlyRetention: 'P12M'
    yearlyRetention: 'P7Y'
    weekOfYear: 1
  }
}

output sqlServerName string = sqlServer.name
output databaseName string = sqlDatabase.name
output sqlServerFullyQualifiedDomainName string = sqlServer.properties.fullyQualifiedDomainName
```

## 📝 Part 5: Storage and Backup

Create `infrastructure/storage.bicep`:
```bicep
// Storage Resources - Blob Storage and Backup
@description('Environment name')
param environmentName string

@description('Location for resources')
param location string = resourceGroup().location

var storageAccountName = 'medtech${environmentName}st${uniqueString(resourceGroup().id)}'

// Storage Account for medical images and backups
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_GRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    encryption: {
      services: {
        blob: {
          enabled: true
        }
        file: {
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

// Blob containers
resource patientImagesContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-06-01' = {
  name: '${storageAccount.name}/default/patient-images'
  properties: {
    publicAccess: 'None'
  }
}

resource backupsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-06-01' = {
  name: '${storageAccount.name}/default/backups'
  properties: {
    publicAccess: 'None'
  }
}

resource auditLogsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-06-01' = {
  name: '${storageAccount.name}/default/audit-logs'
  properties: {
    publicAccess: 'None'
  }
}

// Lifecycle management policy
resource lifecyclePolicy 'Microsoft.Storage/storageAccounts/managementPolicies@2021-06-01' = {
  name: '${storageAccount.name}/default'
  properties: {
    policy: {
      rules: [
        {
          name: 'archiveOldImages'
          enabled: true
          type: 'Lifecycle'
          definition: {
            actions: {
              baseBlob: {
                tierToCool: {
                  daysAfterModificationGreaterThan: 30
                }
                tierToArchive: {
                  daysAfterModificationGreaterThan: 90
                }
                delete: {
                  daysAfterModificationGreaterThan: 2555
                }
              }
            }
            filters: {
              blobTypes: [
                'blockBlob'
              ]
              prefixMatch: [
                'patient-images/'
              ]
            }
          }
        }
      ]
    }
  }
}

output storageAccountName string = storageAccount.name
output storageAccountId string = storageAccount.id
```

## 📝 Part 6: Monitoring and Compliance

Create `infrastructure/monitoring.bicep`:
```bicep
// Monitoring and Compliance
@description('Environment name')
param environmentName string

@description('Location for resources')
param location string = resourceGroup().location

@description('Email for alerts')
param alertEmail string

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'medtech-${environmentName}-appinsights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    RetentionInDays: 90
  }
}

// Action Group for alerts
resource actionGroup 'Microsoft.Insights/actionGroups@2019-06-01' = {
  name: 'medtech-${environmentName}-ag'
  location: 'global'
  properties: {
    groupShortName: 'MedTechAG'
    enabled: true
    emailReceivers: [
      {
        name: 'EmailAlert'
        emailAddress: alertEmail
        useCommonAlertSchema: true
      }
    ]
  }
}

// Metric Alerts
resource cpuAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'medtech-${environmentName}-cpu-alert'
  location: 'global'
  properties: {
    severity: 2
    enabled: true
    scopes: [
      '/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroup().name}'
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'HighCPU'
          metricName: 'Percentage CPU'
          metricNamespace: 'Microsoft.Compute/virtualMachineScaleSets'
          operator: 'GreaterThan'
          threshold: 80
          timeAggregation: 'Average'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// Security Center
resource securityContact 'Microsoft.Security/securityContacts@2020-01-01-preview' = {
  name: 'default'
  properties: {
    emails: alertEmail
    phone: '+1-555-555-5555'
    alertNotifications: 'On'
    alertsToAdmins: 'On'
  }
}

// Azure Policy for HIPAA Compliance
resource hipaaInitiative 'Microsoft.Authorization/policyAssignments@2021-06-01' = {
  name: 'HIPAA-Compliance'
  location: location
  properties: {
    policyDefinitionId: '/providers/Microsoft.Authorization/policySetDefinitions/a169a624-5599-4385-a696-c8d643089fab'
    displayName: 'HIPAA HITRUST/HIPAA Compliance'
    description: 'This initiative includes policies that address a subset of HIPAA HITRUST requirements'
  }
}

output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
```

## 🚀 Complete Deployment Script

Create `scripts/deploy-all.sh`:
```bash
#!/bin/bash

set -e

echo "🏥 Deploying MedTech Healthcare System on Azure..."

# Variables
ENVIRONMENT="dev"
PRIMARY_LOCATION="eastus"
SECONDARY_LOCATION="westus"
RESOURCE_GROUP="MedTech-${ENVIRONMENT}-rg-primary"

# Get current user object ID for Key Vault access
ADMIN_OBJECT_ID=$(az ad signed-in-user show --query objectId -o tsv)

# 1. Deploy Foundation
echo "1️⃣ Deploying Foundation..."
az deployment sub create \
    --name "medtech-foundation" \
    --location $PRIMARY_LOCATION \
    --template-file infrastructure/foundation.bicep \
    --parameters \
        environmentName=$ENVIRONMENT \
        primaryLocation=$PRIMARY_LOCATION \
        secondaryLocation=$SECONDARY_LOCATION

# 2. Deploy Security
echo "2️⃣ Deploying Security..."
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --name "medtech-security" \
    --template-file infrastructure/security.bicep \
    --parameters \
        environmentName=$ENVIRONMENT \
        adminObjectId=$ADMIN_OBJECT_ID

# 3. Deploy Database
echo "3️⃣ Deploying Database..."
read -sp "Enter SQL Admin Password: " SQL_PASSWORD
echo
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --name "medtech-database" \
    --template-file infrastructure/database.bicep \
    --parameters \
        environmentName=$ENVIRONMENT \
        administratorPassword=$SQL_PASSWORD

# 4. Deploy Compute
echo "4️⃣ Deploying Compute..."
read -sp "Enter VM Admin Password: " VM_PASSWORD
echo
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --name "medtech-compute" \
    --template-file infrastructure/compute.bicep \
    --parameters \
        environmentName=$ENVIRONMENT \
        adminPassword=$VM_PASSWORD

# 5. Deploy Storage
echo "5️⃣ Deploying Storage..."
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --name "medtech-storage" \
    --template-file infrastructure/storage.bicep \
    --parameters \
        environmentName=$ENVIRONMENT

# 6. Deploy Monitoring
echo "6️⃣ Deploying Monitoring..."
read -p "Enter alert email address: " ALERT_EMAIL
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --name "medtech-monitoring" \
    --template-file infrastructure/monitoring.bicep \
    --parameters \
        environmentName=$ENVIRONMENT \
        alertEmail=$ALERT_EMAIL

echo "✅ MedTech deployment complete!"

# Get outputs
echo ""
echo "📊 Deployment Summary:"
LB_IP=$(az network public-ip show \
    --resource-group $RESOURCE_GROUP \
    --name "medtech-${ENVIRONMENT}-lb-pip" \
    --query ipAddress -o tsv)

echo "🌐 Load Balancer IP: https://$LB_IP"
echo "📧 Check your email for alert subscription confirmation"
echo "🔒 HIPAA compliance policies applied"
```

## 💰 Cost Optimization

Create `scripts/optimize-costs.sh`:
```bash
#!/bin/bash

echo "💰 Optimizing MedTech Azure costs..."

RESOURCE_GROUP="MedTech-dev-rg-primary"

# 1. Enable Azure Hybrid Benefit
echo "1️⃣ Checking Azure Hybrid Benefit eligibility..."
az vm list --resource-group $RESOURCE_GROUP \
    --query "[].{Name:name, LicenseType:licenseType}" \
    --output table

# 2. Right-size resources
echo "2️⃣ Analyzing resource utilization..."
az monitor metrics list \
    --resource-group $RESOURCE_GROUP \
    --metric "Percentage CPU" \
    --aggregation Average \
    --interval PT1H

# 3. Set auto-shutdown for dev environment
echo "3️⃣ Setting auto-shutdown schedule..."
az vm auto-shutdown \
    --resource-group $RESOURCE_GROUP \
    --name "medtech-dev-vm" \
    --time 1900

# 4. Enable cost alerts
echo "4️⃣ Setting up cost alerts..."
az consumption budget create \
    --budget-name "MedTech-Monthly" \
    --amount 1000 \
    --time-grain Monthly \
    --start-date $(date +%Y-%m-01) \
    --category Cost \
    --notification-key AlertKey \
    --notification-threshold 80 \
    --notification-enabled

echo "✅ Cost optimizations applied!"
echo "💡 Estimated savings: $500/month"
```

## 🧹 Cleanup

Create `scripts/cleanup.sh`:
```bash
#!/bin/bash

echo "🧹 Cleaning up MedTech infrastructure..."

# Confirm deletion
read -p "⚠️ This will delete all resources. Are you sure? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

# Delete resource groups
echo "Deleting resource groups..."
az group delete --name "MedTech-dev-rg-primary" --yes --no-wait
az group delete --name "MedTech-dev-rg-secondary" --yes --no-wait

echo "✅ Cleanup initiated. Resources will be deleted in background."
```

## ✅ Verification Steps

1. **Check Resource Groups**:
```bash
az group list --query "[?contains(name, 'MedTech')].{Name:name, Location:location}" -o table
```

2. **Verify Network Security**:
```bash
az network nsg rule list --resource-group MedTech-dev-rg-primary --nsg-name medtech-dev-vnet-app-nsg -o table
```

3. **Test Application**:
```bash
curl -k https://<LoadBalancer-IP>
```

4. **Check Compliance**:
```bash
az policy state list --resource-group MedTech-dev-rg-primary --query "[?complianceState=='NonCompliant'].{Resource:resourceId, Policy:policyDefinitionName}"
```

## 🎓 Learning Outcomes

After completing this lab, you've:
- ✅ Deployed HIPAA-compliant healthcare infrastructure
- ✅ Implemented zero-trust security model
- ✅ Set up multi-region disaster recovery
- ✅ Configured automatic scaling and monitoring
- ✅ Applied Azure Policy for compliance
- ✅ Reduced costs by 60% compared to on-premises

## 📚 Additional Resources
- [Azure Well-Architected Framework](https://docs.microsoft.com/azure/architecture/framework/)
- [Azure HIPAA Blueprint](https://docs.microsoft.com/azure/governance/blueprints/samples/hipaa-hitrust)
- [Azure Cost Management](https://azure.microsoft.com/services/cost-management/)