# Lab 04: Serverless Computing

## 🎯 Lab Scenario
**FoodDelivery Express** is a food delivery startup that went from 100 to 50,000 restaurants overnight after a viral TikTok video. Their monolithic application on EC2 instances is costing $30,000/month and still crashing during dinner rush hours (6-9 PM). The CEO demands: "We need to handle 1 million orders per day, scale instantly, and cut costs by 80%!"

## 🍕 The Serverless Journey
**Day 1**: "Server crashed during Super Bowl - lost $500K in orders!"  
**Day 7**: "We're paying for servers 24/7 but only busy 3 hours/day"  
**Day 14**: "New feature deployment takes 3 days and breaks everything"  
**Day 21**: "Competitor launches in 10 new cities instantly - we need 2 months!"  
**Day 30**: "AWS bill is $30,000 but we only made $25,000!"

## 🎓 What You'll Learn
1. **Serverless Fundamentals**: Lambda, API Gateway, DynamoDB, S3
2. **Event-Driven Architecture**: SNS, SQS, EventBridge, Step Functions
3. **Serverless Patterns**: Request-Response, Async Processing, Fan-out/Fan-in
4. **Multi-Cloud Serverless**: AWS Lambda, Azure Functions, Google Cloud Functions
5. **Edge Computing**: CloudFront Functions, Lambda@Edge
6. **Observability**: X-Ray, CloudWatch Insights, Distributed Tracing

## 🌟 Real-World Skills
After this lab, you'll be able to:
- Migrate monolithic apps to serverless
- Build event-driven microservices
- Reduce infrastructure costs by 90%
- Deploy globally in minutes
- Handle millions of requests with zero servers
- Implement complex workflows with Step Functions

## ⏱️ Duration: 75 minutes

## 💰 Cost Comparison
- **Monolithic on EC2**: $30,000/month
- **Containerized on ECS**: $15,000/month
- **Serverless Architecture**: $3,000/month
- **Actual Usage Cost**: Pay only for dinner rush!

## 🏗️ Architecture Evolution

### Before: Monolithic Nightmare
```
Users → Load Balancer → EC2 Instances (Always Running)
                         - Web Server
                         - App Server
                         - Database
                         Problems:
                         ❌ Paying 24/7
                         ❌ Can't scale parts
                         ❌ 30-minute deploys
                         ❌ Single point of failure
```

### After: Serverless Microservices
```
     Mobile App / Web
            │
      CloudFront CDN
            │
       API Gateway
            │
    ┌───────┴───────────────────────┐
    │                               │
Lambda:         Lambda:         Lambda:
Order Service   Restaurant      Delivery
    │           Service         Service
    │               │               │
DynamoDB        DynamoDB        DynamoDB
Orders          Restaurants     Drivers
    │               │               │
    └───────┬───────┘───────────────┘
            │
        EventBridge
            │
    ┌───────┴───────────────────────┐
    │               │               │
SNS:            SQS:            Step Functions:
Notifications   Analytics       Order Workflow
    │               │               │
Lambda:         Lambda:         Lambda:
Send Email      Process         State Machine
Send SMS        BigData         Orchestration
```

## 📝 Part 1: Foundation - Serverless Infrastructure

### Business Need
Replace $30,000/month infrastructure with pay-per-use serverless.

### Step 1.1: Serverless Backend Infrastructure

Create `infrastructure/serverless-backend.yaml` (AWS SAM):
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: FoodDelivery Express - Serverless Backend

Globals:
  Function:
    Runtime: python3.9
    Timeout: 30
    MemorySize: 512
    Environment:
      Variables:
        ENVIRONMENT: !Ref Environment
        LOG_LEVEL: INFO
    Tracing: Active
    Layers:
      - !Ref SharedLibrariesLayer

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

Resources:
  # Shared Lambda Layer
  SharedLibrariesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: food-delivery-shared
      Description: Shared libraries for all functions
      ContentUri: layers/shared/
      CompatibleRuntimes:
        - python3.9
      RetentionPolicy: Delete

  # API Gateway
  FoodDeliveryApi:
    Type: AWS::Serverless::Api
    Properties:
      Name: !Sub food-delivery-api-${Environment}
      StageName: !Ref Environment
      TracingEnabled: true
      Cors:
        AllowMethods: "'*'"
        AllowHeaders: "'*'"
        AllowOrigin: "'*'"
      Auth:
        DefaultAuthorizer: CognitoAuthorizer
        Authorizers:
          CognitoAuthorizer:
            UserPoolArn: !GetAtt UserPool.Arn
      GatewayResponses:
        DEFAULT_4XX:
          ResponseParameters:
            Headers:
              Access-Control-Allow-Origin: "'*'"
        DEFAULT_5XX:
          ResponseParameters:
            Headers:
              Access-Control-Allow-Origin: "'*'"

  # Cognito User Pool for Authentication
  UserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: !Sub food-delivery-users-${Environment}
      AutoVerifiedAttributes:
        - email
      Schema:
        - Name: email
          Required: true
          Mutable: false
        - Name: name
          Required: true
          Mutable: true
        - Name: phone_number
          Required: false
          Mutable: true
      Policies:
        PasswordPolicy:
          MinimumLength: 8
          RequireUppercase: true
          RequireLowercase: true
          RequireNumbers: true
          RequireSymbols: true
      MfaConfiguration: OPTIONAL
      EnabledMfas:
        - SMS_MFA
        - SOFTWARE_TOKEN_MFA

  UserPoolClient:
    Type: AWS::Cognito::UserPoolClient
    Properties:
      ClientName: food-delivery-app
      UserPoolId: !Ref UserPool
      GenerateSecret: false
      AllowedOAuthFlowsUserPoolClient: true
      AllowedOAuthFlows:
        - code
        - implicit
      AllowedOAuthScopes:
        - email
        - openid
        - profile
      CallbackURLs:
        - http://localhost:3000
        - https://app.fooddelivery.com

  # DynamoDB Tables
  OrdersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub food-delivery-orders-${Environment}
      BillingMode: PAY_PER_REQUEST
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      AttributeDefinitions:
        - AttributeName: orderId
          AttributeType: S
        - AttributeName: userId
          AttributeType: S
        - AttributeName: restaurantId
          AttributeType: S
        - AttributeName: status
          AttributeType: S
        - AttributeName: createdAt
          AttributeType: N
      KeySchema:
        - AttributeName: orderId
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: UserOrdersIndex
          KeySchema:
            - AttributeName: userId
              KeyType: HASH
            - AttributeName: createdAt
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
        - IndexName: RestaurantOrdersIndex
          KeySchema:
            - AttributeName: restaurantId
              KeyType: HASH
            - AttributeName: status
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      SSESpecification:
        SSEEnabled: true
      Tags:
        - Key: Environment
          Value: !Ref Environment

  RestaurantsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub food-delivery-restaurants-${Environment}
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: restaurantId
          AttributeType: S
        - AttributeName: cuisineType
          AttributeType: S
        - AttributeName: rating
          AttributeType: N
      KeySchema:
        - AttributeName: restaurantId
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: CuisineRatingIndex
          KeySchema:
            - AttributeName: cuisineType
              KeyType: HASH
            - AttributeName: rating
              KeyType: RANGE
          Projection:
            ProjectionType: ALL

  DriversTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub food-delivery-drivers-${Environment}
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: driverId
          AttributeType: S
        - AttributeName: status
          AttributeType: S
        - AttributeName: location
          AttributeType: S
      KeySchema:
        - AttributeName: driverId
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: AvailableDriversIndex
          KeySchema:
            - AttributeName: status
              KeyType: HASH
            - AttributeName: location
              KeyType: RANGE
          Projection:
            ProjectionType: ALL

  # Lambda Functions
  OrderServiceFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub food-delivery-order-service-${Environment}
      CodeUri: functions/order-service/
      Handler: app.lambda_handler
      Events:
        CreateOrder:
          Type: Api
          Properties:
            RestApiId: !Ref FoodDeliveryApi
            Path: /orders
            Method: POST
        GetOrder:
          Type: Api
          Properties:
            RestApiId: !Ref FoodDeliveryApi
            Path: /orders/{orderId}
            Method: GET
        UpdateOrder:
          Type: Api
          Properties:
            RestApiId: !Ref FoodDeliveryApi
            Path: /orders/{orderId}
            Method: PUT
      Environment:
        Variables:
          ORDERS_TABLE: !Ref OrdersTable
          RESTAURANTS_TABLE: !Ref RestaurantsTable
          EVENT_BUS: !Ref OrderEventBus
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref OrdersTable
        - DynamoDBReadPolicy:
            TableName: !Ref RestaurantsTable
        - EventBridgePutEventsPolicy:
            EventBusName: !Ref OrderEventBus

  RestaurantServiceFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub food-delivery-restaurant-service-${Environment}
      CodeUri: functions/restaurant-service/
      Handler: app.lambda_handler
      Events:
        GetRestaurants:
          Type: Api
          Properties:
            RestApiId: !Ref FoodDeliveryApi
            Path: /restaurants
            Method: GET
        GetRestaurant:
          Type: Api
          Properties:
            RestApiId: !Ref FoodDeliveryApi
            Path: /restaurants/{restaurantId}
            Method: GET
        SearchRestaurants:
          Type: Api
          Properties:
            RestApiId: !Ref FoodDeliveryApi
            Path: /restaurants/search
            Method: POST
      Environment:
        Variables:
          RESTAURANTS_TABLE: !Ref RestaurantsTable
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref RestaurantsTable

  DeliveryServiceFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub food-delivery-delivery-service-${Environment}
      CodeUri: functions/delivery-service/
      Handler: app.lambda_handler
      ReservedConcurrentExecutions: 100
      Events:
        AssignDriver:
          Type: Api
          Properties:
            RestApiId: !Ref FoodDeliveryApi
            Path: /deliveries/assign
            Method: POST
        TrackDelivery:
          Type: Api
          Properties:
            RestApiId: !Ref FoodDeliveryApi
            Path: /deliveries/{orderId}/track
            Method: GET
        UpdateLocation:
          Type: Api
          Properties:
            RestApiId: !Ref FoodDeliveryApi
            Path: /deliveries/{orderId}/location
            Method: PUT
      Environment:
        Variables:
          DRIVERS_TABLE: !Ref DriversTable
          ORDERS_TABLE: !Ref OrdersTable
          LOCATION_STREAM: !Ref LocationStream
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref DriversTable
        - DynamoDBCrudPolicy:
            TableName: !Ref OrdersTable
        - KinesisCrudPolicy:
            StreamName: !Ref LocationStream

  # Event-Driven Architecture
  OrderEventBus:
    Type: AWS::Events::EventBus
    Properties:
      Name: !Sub food-delivery-events-${Environment}

  OrderEventRule:
    Type: AWS::Events::Rule
    Properties:
      Name: !Sub order-processing-rule-${Environment}
      EventBusName: !Ref OrderEventBus
      EventPattern:
        source:
          - food.delivery.orders
        detail-type:
          - Order Created
          - Order Updated
          - Order Cancelled
      State: ENABLED
      Targets:
        - Arn: !GetAtt OrderProcessingQueue.Arn
          Id: order-queue-target
          SqsParameters:
            MessageGroupId: orders

  # SQS Queues
  OrderProcessingQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub food-delivery-orders-queue-${Environment}.fifo
      FifoQueue: true
      ContentBasedDeduplication: true
      VisibilityTimeout: 300
      MessageRetentionPeriod: 1209600
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt OrderDeadLetterQueue.Arn
        maxReceiveCount: 3

  OrderDeadLetterQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub food-delivery-orders-dlq-${Environment}.fifo
      FifoQueue: true
      MessageRetentionPeriod: 1209600

  NotificationQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub food-delivery-notifications-${Environment}
      VisibilityTimeout: 60

  # SNS Topics
  NotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub food-delivery-notifications-${Environment}
      DisplayName: Food Delivery Notifications
      Subscriptions:
        - Endpoint: !GetAtt NotificationQueue.Arn
          Protocol: sqs

  # Kinesis for real-time location tracking
  LocationStream:
    Type: AWS::Kinesis::Stream
    Properties:
      Name: !Sub food-delivery-location-stream-${Environment}
      ShardCount: 1
      RetentionPeriodHours: 24
      ShardLevelMetrics:
        - IncomingRecords
        - OutgoingRecords

  # Step Functions for Order Workflow
  OrderWorkflow:
    Type: AWS::Serverless::StateMachine
    Properties:
      Name: !Sub food-delivery-order-workflow-${Environment}
      DefinitionUri: statemachine/order-workflow.asl.json
      DefinitionSubstitutions:
        ValidateOrderArn: !GetAtt ValidateOrderFunction.Arn
        ProcessPaymentArn: !GetAtt ProcessPaymentFunction.Arn
        NotifyRestaurantArn: !GetAtt NotifyRestaurantFunction.Arn
        AssignDriverArn: !GetAtt AssignDriverFunction.Arn
        NotifyCustomerArn: !GetAtt NotifyCustomerFunction.Arn
      Role: !GetAtt StepFunctionsRole.Arn
      Tracing:
        Enabled: true

  # Supporting Lambda Functions for Step Functions
  ValidateOrderFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub food-delivery-validate-order-${Environment}
      CodeUri: functions/validate-order/
      Handler: app.lambda_handler

  ProcessPaymentFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub food-delivery-process-payment-${Environment}
      CodeUri: functions/process-payment/
      Handler: app.lambda_handler
      Environment:
        Variables:
          STRIPE_SECRET_KEY: !Sub '{{resolve:secretsmanager:stripe-keys-${Environment}:SecretString:secret_key}}'

  NotifyRestaurantFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub food-delivery-notify-restaurant-${Environment}
      CodeUri: functions/notify-restaurant/
      Handler: app.lambda_handler

  AssignDriverFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub food-delivery-assign-driver-${Environment}
      CodeUri: functions/assign-driver/
      Handler: app.lambda_handler

  NotifyCustomerFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub food-delivery-notify-customer-${Environment}
      CodeUri: functions/notify-customer/
      Handler: app.lambda_handler

  # IAM Roles
  StepFunctionsRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: states.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaRole
        - arn:aws:iam::aws:policy/CloudWatchLogsFullAccess

  # CloudWatch Dashboard
  OperationalDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub food-delivery-dashboard-${Environment}
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "properties": {
                "metrics": [
                  [ "AWS/Lambda", "Invocations", { "stat": "Sum" } ],
                  [ ".", "Errors", { "stat": "Sum" } ],
                  [ ".", "Duration", { "stat": "Average" } ],
                  [ ".", "ConcurrentExecutions", { "stat": "Maximum" } ]
                ],
                "period": 300,
                "stat": "Average",
                "region": "${AWS::Region}",
                "title": "Lambda Metrics"
              }
            },
            {
              "type": "metric",
              "properties": {
                "metrics": [
                  [ "AWS/DynamoDB", "ConsumedReadCapacityUnits", { "stat": "Sum" } ],
                  [ ".", "ConsumedWriteCapacityUnits", { "stat": "Sum" } ],
                  [ ".", "ThrottledRequests", { "stat": "Sum" } ]
                ],
                "period": 300,
                "stat": "Sum",
                "region": "${AWS::Region}",
                "title": "DynamoDB Metrics"
              }
            }
          ]
        }

Outputs:
  ApiUrl:
    Description: API Gateway URL
    Value: !Sub https://${FoodDeliveryApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}

  UserPoolId:
    Description: Cognito User Pool ID
    Value: !Ref UserPool

  UserPoolClientId:
    Description: Cognito User Pool Client ID
    Value: !Ref UserPoolClient
```

## 📝 Part 2: Lambda Functions Implementation

### Order Service Function

Create `functions/order-service/app.py`:
```python
import json
import os
import boto3
import uuid
from datetime import datetime
from decimal import Decimal
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths

logger = Logger()
tracer = Tracer()
metrics = Metrics()
app = APIGatewayRestResolver()

dynamodb = boto3.resource('dynamodb')
events = boto3.client('events')

ORDERS_TABLE = os.environ['ORDERS_TABLE']
RESTAURANTS_TABLE = os.environ['RESTAURANTS_TABLE']
EVENT_BUS = os.environ['EVENT_BUS']

orders_table = dynamodb.Table(ORDERS_TABLE)
restaurants_table = dynamodb.Table(RESTAURANTS_TABLE)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

@app.post("/orders")
@tracer.capture_method
def create_order():
    """Create a new food delivery order"""
    try:
        request_body = app.current_event.json_body
        
        # Validate restaurant exists
        restaurant = restaurants_table.get_item(
            Key={'restaurantId': request_body['restaurantId']}
        )
        
        if 'Item' not in restaurant:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Restaurant not found'})
            }
        
        # Create order
        order_id = str(uuid.uuid4())
        timestamp = int(datetime.utcnow().timestamp())
        
        order = {
            'orderId': order_id,
            'userId': request_body['userId'],
            'restaurantId': request_body['restaurantId'],
            'items': request_body['items'],
            'totalAmount': calculate_total(request_body['items']),
            'status': 'PENDING',
            'createdAt': timestamp,
            'updatedAt': timestamp,
            'deliveryAddress': request_body['deliveryAddress'],
            'paymentMethod': request_body['paymentMethod']
        }
        
        # Save to DynamoDB
        orders_table.put_item(Item=order)
        
        # Emit event
        events.put_events(
            Entries=[
                {
                    'Source': 'food.delivery.orders',
                    'DetailType': 'Order Created',
                    'Detail': json.dumps(order, cls=DecimalEncoder),
                    'EventBusName': EVENT_BUS
                }
            ]
        )
        
        # Record metrics
        metrics.add_metric(name="OrdersCreated", unit=MetricUnit.Count, value=1)
        metrics.add_metric(name="OrderValue", unit=MetricUnit.None, value=float(order['totalAmount']))
        
        logger.info(f"Order created: {order_id}")
        
        return {
            'statusCode': 201,
            'body': json.dumps(order, cls=DecimalEncoder)
        }
        
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        metrics.add_metric(name="OrderCreationErrors", unit=MetricUnit.Count, value=1)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to create order'})
        }

@app.get("/orders/<orderId>")
@tracer.capture_method
def get_order(orderId: str):
    """Get order details"""
    try:
        response = orders_table.get_item(Key={'orderId': orderId})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Order not found'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(response['Item'], cls=DecimalEncoder)
        }
        
    except Exception as e:
        logger.error(f"Error getting order: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to get order'})
        }

@app.put("/orders/<orderId>")
@tracer.capture_method
def update_order(orderId: str):
    """Update order status"""
    try:
        request_body = app.current_event.json_body
        new_status = request_body['status']
        
        # Update order
        response = orders_table.update_item(
            Key={'orderId': orderId},
            UpdateExpression='SET #status = :status, updatedAt = :timestamp',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': new_status,
                ':timestamp': int(datetime.utcnow().timestamp())
            },
            ReturnValues='ALL_NEW'
        )
        
        # Emit event
        events.put_events(
            Entries=[
                {
                    'Source': 'food.delivery.orders',
                    'DetailType': 'Order Updated',
                    'Detail': json.dumps({
                        'orderId': orderId,
                        'status': new_status
                    }),
                    'EventBusName': EVENT_BUS
                }
            ]
        )
        
        logger.info(f"Order {orderId} updated to status: {new_status}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(response['Attributes'], cls=DecimalEncoder)
        }
        
    except Exception as e:
        logger.error(f"Error updating order: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to update order'})
        }

def calculate_total(items):
    """Calculate total order amount"""
    total = Decimal(0)
    for item in items:
        total += Decimal(str(item['price'])) * Decimal(str(item['quantity']))
    return total

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    return app.resolve(event, context)
```

## 📝 Part 3: Step Functions Workflow

Create `statemachine/order-workflow.asl.json`:
```json
{
  "Comment": "Food Delivery Order Processing Workflow",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "${ValidateOrderArn}",
      "Retry": [
        {
          "ErrorEquals": ["Lambda.ServiceException", "Lambda.AWSLambdaException"],
          "IntervalSeconds": 2,
          "MaxAttempts": 6,
          "BackoffRate": 2
        }
      ],
      "Next": "ProcessPayment",
      "Catch": [
        {
          "ErrorEquals": ["ValidationError"],
          "Next": "OrderFailed"
        }
      ]
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "${ProcessPaymentArn}",
      "Retry": [
        {
          "ErrorEquals": ["PaymentRetryableError"],
          "IntervalSeconds": 5,
          "MaxAttempts": 3,
          "BackoffRate": 2
        }
      ],
      "Next": "PaymentSuccessful?",
      "Catch": [
        {
          "ErrorEquals": ["PaymentError"],
          "Next": "RefundPayment"
        }
      ]
    },
    "PaymentSuccessful?": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.paymentStatus",
          "StringEquals": "SUCCESS",
          "Next": "ParallelProcessing"
        }
      ],
      "Default": "RefundPayment"
    },
    "ParallelProcessing": {
      "Type": "Parallel",
      "Next": "WaitForRestaurantConfirmation",
      "Branches": [
        {
          "StartAt": "NotifyRestaurant",
          "States": {
            "NotifyRestaurant": {
              "Type": "Task",
              "Resource": "${NotifyRestaurantArn}",
              "End": true
            }
          }
        },
        {
          "StartAt": "AssignDriver",
          "States": {
            "AssignDriver": {
              "Type": "Task",
              "Resource": "${AssignDriverArn}",
              "End": true
            }
          }
        },
        {
          "StartAt": "NotifyCustomer",
          "States": {
            "NotifyCustomer": {
              "Type": "Task",
              "Resource": "${NotifyCustomerArn}",
              "End": true
            }
          }
        }
      ]
    },
    "WaitForRestaurantConfirmation": {
      "Type": "Wait",
      "Seconds": 300,
      "Next": "CheckRestaurantConfirmation"
    },
    "CheckRestaurantConfirmation": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.restaurantConfirmed",
          "BooleanEquals": true,
          "Next": "OrderSuccessful"
        }
      ],
      "Default": "RestaurantTimeout"
    },
    "RestaurantTimeout": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:${AWS::Region}:${AWS::AccountId}:food-delivery-alerts",
        "Message": "Restaurant did not confirm order in time"
      },
      "Next": "RefundPayment"
    },
    "RefundPayment": {
      "Type": "Task",
      "Resource": "${ProcessPaymentArn}",
      "Parameters": {
        "action": "REFUND",
        "orderId.$": "$.orderId",
        "amount.$": "$.totalAmount"
      },
      "Next": "OrderFailed"
    },
    "OrderSuccessful": {
      "Type": "Succeed"
    },
    "OrderFailed": {
      "Type": "Fail",
      "Error": "OrderProcessingFailed",
      "Cause": "Order could not be processed successfully"
    }
  }
}
```

## 📝 Part 4: Multi-Cloud Serverless

### Azure Functions Implementation

Create `functions-azure/OrderProcessor/index.js`:
```javascript
const { CosmosClient } = require("@azure/cosmos");
const { ServiceBusClient } = require("@azure/service-bus");

const endpoint = process.env.COSMOS_ENDPOINT;
const key = process.env.COSMOS_KEY;
const databaseId = "FoodDelivery";
const containerId = "Orders";

const client = new CosmosClient({ endpoint, key });
const database = client.database(databaseId);
const container = database.container(containerId);

const serviceBusConnectionString = process.env.SERVICE_BUS_CONNECTION;
const queueName = "order-processing";

module.exports = async function (context, req) {
    context.log('Processing order request');

    try {
        const order = req.body;
        order.id = generateOrderId();
        order.timestamp = new Date().toISOString();
        order.status = 'PENDING';

        // Save to Cosmos DB
        const { resource: createdOrder } = await container.items.create(order);

        // Send to Service Bus for async processing
        const sbClient = new ServiceBusClient(serviceBusConnectionString);
        const sender = sbClient.createSender(queueName);

        await sender.sendMessages({
            body: createdOrder,
            contentType: "application/json",
        });

        await sender.close();
        await sbClient.close();

        context.res = {
            status: 201,
            body: createdOrder
        };
    } catch (error) {
        context.log.error('Error processing order:', error);
        context.res = {
            status: 500,
            body: { error: 'Failed to process order' }
        };
    }
};

function generateOrderId() {
    return 'ORD-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
}
```

### Google Cloud Functions Implementation

Create `functions-gcp/order_processor/main.py`:
```python
import json
import os
from datetime import datetime
from google.cloud import firestore
from google.cloud import pubsub_v1
from google.cloud import tasks_v2
import functions_framework

# Initialize clients
db = firestore.Client()
publisher = pubsub_v1.PublisherClient()
tasks_client = tasks_v2.CloudTasksClient()

PROJECT_ID = os.environ.get('GCP_PROJECT')
TOPIC_NAME = f"projects/{PROJECT_ID}/topics/order-events"
QUEUE_PATH = tasks_client.queue_path(PROJECT_ID, 'us-central1', 'order-processing')

@functions_framework.http
def process_order(request):
    """HTTP Cloud Function for processing orders"""
    
    try:
        request_json = request.get_json(silent=True)
        
        if not request_json:
            return json.dumps({'error': 'Invalid request'}), 400
        
        # Create order document
        order_ref = db.collection('orders').document()
        order_data = {
            'orderId': order_ref.id,
            'userId': request_json.get('userId'),
            'restaurantId': request_json.get('restaurantId'),
            'items': request_json.get('items'),
            'totalAmount': calculate_total(request_json.get('items', [])),
            'status': 'PENDING',
            'createdAt': firestore.SERVER_TIMESTAMP,
            'deliveryAddress': request_json.get('deliveryAddress')
        }
        
        # Save to Firestore
        order_ref.set(order_data)
        
        # Publish event to Pub/Sub
        message_data = json.dumps(order_data, default=str).encode('utf-8')
        future = publisher.publish(TOPIC_NAME, message_data)
        future.result()  # Wait for publish to complete
        
        # Create Cloud Task for async processing
        task = {
            'http_request': {
                'http_method': tasks_v2.HttpMethod.POST,
                'url': f"https://us-central1-{PROJECT_ID}.cloudfunctions.net/process-payment",
                'headers': {'Content-Type': 'application/json'},
                'body': message_data
            }
        }
        
        response = tasks_client.create_task(parent=QUEUE_PATH, task=task)
        
        return json.dumps({
            'orderId': order_ref.id,
            'status': 'CREATED',
            'message': 'Order is being processed'
        }), 201
        
    except Exception as e:
        print(f"Error processing order: {e}")
        return json.dumps({'error': str(e)}), 500

def calculate_total(items):
    """Calculate order total"""
    return sum(item.get('price', 0) * item.get('quantity', 1) for item in items)

@functions_framework.cloud_event
def handle_order_event(cloud_event):
    """Pub/Sub triggered function for order events"""
    
    try:
        # Parse the Pub/Sub message
        message_data = base64.b64decode(cloud_event.data["message"]["data"])
        order_data = json.loads(message_data)
        
        # Process based on order status
        if order_data.get('status') == 'PENDING':
            # Notify restaurant
            notify_restaurant(order_data)
        elif order_data.get('status') == 'CONFIRMED':
            # Assign driver
            assign_driver(order_data)
        elif order_data.get('status') == 'DELIVERED':
            # Complete order
            complete_order(order_data)
            
    except Exception as e:
        print(f"Error handling order event: {e}")
        raise e

def notify_restaurant(order_data):
    """Send notification to restaurant"""
    # Implementation here
    pass

def assign_driver(order_data):
    """Assign driver to order"""
    # Implementation here
    pass

def complete_order(order_data):
    """Mark order as complete"""
    # Implementation here
    pass
```

## 📝 Part 5: Deployment and Monitoring

Create `scripts/deploy-serverless.sh`:
```bash
#!/bin/bash

set -e

ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}

echo "🚀 Deploying FoodDelivery Serverless Architecture..."

# 1. Package Lambda functions
echo "1️⃣ Packaging Lambda functions..."
cd functions
for dir in */; do
    echo "Packaging $dir..."
    cd $dir
    pip install -r requirements.txt -t .
    zip -r9 ../${dir%/}.zip .
    cd ..
done
cd ..

# 2. Deploy SAM application
echo "2️⃣ Deploying SAM application..."
sam build --template infrastructure/serverless-backend.yaml
sam deploy \
    --stack-name food-delivery-${ENVIRONMENT} \
    --s3-bucket food-delivery-sam-artifacts \
    --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
    --parameter-overrides Environment=${ENVIRONMENT} \
    --region ${REGION}

# 3. Deploy Step Functions
echo "3️⃣ Deploying Step Functions workflow..."
aws stepfunctions create-state-machine \
    --name food-delivery-order-workflow-${ENVIRONMENT} \
    --definition file://statemachine/order-workflow.asl.json \
    --role-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/StepFunctionsRole

# 4. Setup CloudWatch Alarms
echo "4️⃣ Setting up CloudWatch alarms..."
aws cloudwatch put-metric-alarm \
    --alarm-name food-delivery-high-errors \
    --alarm-description "Alert when Lambda errors are high" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1

# 5. Enable X-Ray tracing
echo "5️⃣ Enabling X-Ray tracing..."
aws lambda update-function-configuration \
    --function-name food-delivery-order-service-${ENVIRONMENT} \
    --tracing-config Mode=Active

# Get outputs
API_URL=$(aws cloudformation describe-stacks \
    --stack-name food-delivery-${ENVIRONMENT} \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

echo "✅ Deployment complete!"
echo ""
echo "📊 Serverless Architecture Ready!"
echo "API Endpoint: $API_URL"
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo ""
echo "💰 Cost Savings:"
echo "Before: $30,000/month (EC2)"
echo "After: ~$3,000/month (Serverless)"
echo "Savings: 90% reduction!"
```

## 📝 Part 6: Performance Testing

Create `scripts/load-test.js`:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
    stages: [
        { duration: '2m', target: 100 },  // Ramp up to 100 users
        { duration: '5m', target: 100 },  // Stay at 100 users
        { duration: '2m', target: 1000 }, // Spike to 1000 users
        { duration: '5m', target: 1000 }, // Stay at 1000 users
        { duration: '2m', target: 0 },    // Ramp down to 0 users
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
        errors: ['rate<0.01'],            // Error rate under 1%
    },
};

const API_URL = 'https://api.fooddelivery.com';

export default function () {
    // Create order
    const orderPayload = JSON.stringify({
        userId: `user-${Math.random()}`,
        restaurantId: `rest-${Math.floor(Math.random() * 100)}`,
        items: [
            { name: 'Pizza', price: 15.99, quantity: 1 },
            { name: 'Soda', price: 2.99, quantity: 2 }
        ],
        deliveryAddress: '123 Main St',
        paymentMethod: 'card'
    });

    const headers = { 'Content-Type': 'application/json' };
    
    const createResponse = http.post(`${API_URL}/orders`, orderPayload, { headers });
    
    check(createResponse, {
        'order created': (r) => r.status === 201,
        'has order ID': (r) => JSON.parse(r.body).orderId !== undefined,
    });
    
    errorRate.add(createResponse.status !== 201);
    
    if (createResponse.status === 201) {
        const orderId = JSON.parse(createResponse.body).orderId;
        
        // Get order status
        const getResponse = http.get(`${API_URL}/orders/${orderId}`);
        
        check(getResponse, {
            'order retrieved': (r) => r.status === 200,
            'correct order ID': (r) => JSON.parse(r.body).orderId === orderId,
        });
    }
    
    sleep(1);
}
```

## ✅ Verification and Results

After completing this lab, you've achieved:
- ✅ Migrated from $30,000/month monolithic to $3,000/month serverless
- ✅ Scaled from 100 to 50,000 restaurants instantly
- ✅ Handle 1 million orders/day with zero servers
- ✅ Deploy new features in seconds instead of days
- ✅ 99.99% availability with multi-region failover
- ✅ Pay only for actual usage during dinner rush

## 📚 Additional Resources
- [AWS Serverless Application Model](https://aws.amazon.com/serverless/sam/)
- [Azure Functions Best Practices](https://docs.microsoft.com/azure/azure-functions/functions-best-practices)
- [Google Cloud Functions Patterns](https://cloud.google.com/functions/docs/bestpractices)