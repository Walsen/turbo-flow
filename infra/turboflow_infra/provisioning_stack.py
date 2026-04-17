"""
TurboFlow Provisioning Stack — tenant lifecycle automation.

Creates:
- Lambda function that provisions/deprovisions tenant stacks via CloudFormation
- API Gateway HTTP API for tenant CRUD
- DynamoDB table for tenant metadata
- IAM role for the provisioning Lambda

API:
  POST   /tenants          — create a new tenant
  GET    /tenants           — list all tenants
  GET    /tenants/{id}      — get tenant details
  DELETE /tenants/{id}      — tear down a tenant
"""

from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_apigatewayv2 as apigwv2,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
)


class ProvisioningStack(Stack):
    """Tenant provisioning automation — API + Lambda + DynamoDB."""

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        tenant_bucket_name: str,
        agent_execution_role_arn: str,
        agent_code_bucket: str,
        agent_code_key: str,
        **kwargs,
    ) -> None:  # type: ignore
        super().__init__(scope, id, **kwargs)

        # ── DynamoDB table for tenant metadata ───────────────────────────
        self.tenant_table = dynamodb.Table(
            self,
            "TenantTable",
            table_name="turboflow-tenants",
            partition_key=dynamodb.Attribute(
                name="tenant_id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # ── Lambda execution role ────────────────────────────────────────
        self.lambda_role = iam.Role(
            self,
            "ProvisioningRole",
            role_name="turboflow-provisioning",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
        )

        # CloudFormation permissions for stack CRUD
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "cloudformation:CreateStack",
                    "cloudformation:UpdateStack",
                    "cloudformation:DeleteStack",
                    "cloudformation:DescribeStacks",
                    "cloudformation:DescribeStackEvents",
                    "cloudformation:GetTemplate",
                ],
                resources=[
                    f"arn:aws:cloudformation:{self.region}:{self.account}:stack/TurboFlowTenant-*/*"
                ],
            )
        )

        # AgentCore permissions
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["bedrock-agentcore:*"],
                resources=["*"],
            )
        )

        # S3 permissions for agent code
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject"],
                resources=[
                    f"arn:aws:s3:::{tenant_bucket_name}/*",
                    f"arn:aws:s3:::{agent_code_bucket}/*",
                ],
            )
        )

        # IAM pass role (for AgentCore Runtime)
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["iam:PassRole"],
                resources=[agent_execution_role_arn],
            )
        )

        # DynamoDB permissions
        self.tenant_table.grant_read_write_data(self.lambda_role)

        # ── Provisioning Lambda ──────────────────────────────────────────
        self.provisioning_fn = lambda_.Function(
            self,
            "ProvisioningFunction",
            function_name="turboflow-provision-tenant",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._lambda_code()),
            role=self.lambda_role,
            timeout=Duration.minutes(5),
            memory_size=256,
            environment={
                "TENANT_TABLE": self.tenant_table.table_name,
                "TENANT_BUCKET": tenant_bucket_name,
                "AGENT_CODE_BUCKET": agent_code_bucket,
                "AGENT_CODE_KEY": agent_code_key,
                "AGENT_EXECUTION_ROLE_ARN": agent_execution_role_arn,
                "AWS_ACCOUNT_ID": self.account,
                "STACK_REGION": self.region,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # ── API Gateway HTTP API ─────────────────────────────────────────
        self.api = apigwv2.CfnApi(
            self,
            "TenantApi",
            name="turboflow-tenants",
            protocol_type="HTTP",
        )

        # Lambda integration
        integration = apigwv2.CfnIntegration(
            self,
            "LambdaIntegration",
            api_id=self.api.ref,
            integration_type="AWS_PROXY",
            integration_uri=self.provisioning_fn.function_arn,
            payload_format_version="2.0",
        )

        # Routes
        for route_key in [
            "POST /tenants",
            "GET /tenants",
            "GET /tenants/{id}",
            "DELETE /tenants/{id}",
        ]:
            safe_name = route_key.replace(" ", "").replace("/", "").replace("{", "").replace("}", "")
            apigwv2.CfnRoute(
                self,
                f"Route{safe_name}",
                api_id=self.api.ref,
                route_key=route_key,
                target=f"integrations/{integration.ref}",
            )

        # Default stage with auto-deploy
        apigwv2.CfnStage(
            self,
            "DefaultStage",
            api_id=self.api.ref,
            stage_name="$default",
            auto_deploy=True,
        )

        # Grant API Gateway permission to invoke Lambda
        self.provisioning_fn.add_permission(
            "ApiGatewayInvoke",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            source_arn=f"arn:aws:execute-api:{self.region}:{self.account}:{self.api.ref}/*",
        )

        # ── Outputs ──────────────────────────────────────────────────────
        CfnOutput(
            self,
            "ApiUrl",
            value=f"https://{self.api.ref}.execute-api.{self.region}.amazonaws.com",
        )
        CfnOutput(self, "TenantTableName", value=self.tenant_table.table_name)
        CfnOutput(
            self, "ProvisioningFunctionArn", value=self.provisioning_fn.function_arn
        )

    def _lambda_code(self) -> str:
        return '''
import json
import os
import time
import boto3

cfn = boto3.client("cloudformation")
ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ["TENANT_TABLE"])

TENANT_BUCKET = os.environ["TENANT_BUCKET"]
AGENT_CODE_BUCKET = os.environ["AGENT_CODE_BUCKET"]
AGENT_CODE_KEY = os.environ["AGENT_CODE_KEY"]
AGENT_ROLE_ARN = os.environ["AGENT_EXECUTION_ROLE_ARN"]
ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID"]
REGION = os.environ["STACK_REGION"]


def handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("rawPath", "")
    body = json.loads(event.get("body", "{}")) if event.get("body") else {}

    try:
        if method == "POST" and path == "/tenants":
            return create_tenant(body)
        elif method == "GET" and path == "/tenants":
            return list_tenants()
        elif method == "GET" and "/tenants/" in path:
            tenant_id = path.split("/tenants/")[1]
            return get_tenant(tenant_id)
        elif method == "DELETE" and "/tenants/" in path:
            tenant_id = path.split("/tenants/")[1]
            return delete_tenant(tenant_id)
        else:
            return response(404, {"error": "Not found"})
    except Exception as e:
        return response(500, {"error": str(e)})


def create_tenant(body):
    tenant_id = body.get("tenant_id", f"tenant-{int(time.time())}")
    tenant_name = body.get("name", tenant_id)
    tenant_plan = body.get("plan", "starter")
    safe_id = tenant_id.replace("-", "_")
    stack_name = f"TurboFlowTenant-{tenant_id}"

    # Check if exists
    existing = table.get_item(Key={"tenant_id": tenant_id}).get("Item")
    if existing:
        return response(409, {"error": f"Tenant {tenant_id} already exists"})

    # Create CloudFormation stack using the tenant template
    # This is a simplified inline template — in production, use the CDK-generated template
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": f"TurboFlow tenant: {tenant_name} ({tenant_plan})",
        "Resources": {
            "TenantLogs": {
                "Type": "AWS::Logs::LogGroup",
                "Properties": {
                    "LogGroupName": f"/turboflow/tenants/{tenant_id}",
                    "RetentionInDays": 30,
                },
            },
        },
        "Outputs": {
            "TenantId": {"Value": tenant_id},
            "WorkspacePrefix": {"Value": f"s3://{TENANT_BUCKET}/{tenant_id}/"},
        },
    }

    cfn.create_stack(
        StackName=stack_name,
        TemplateBody=json.dumps(template),
        Tags=[
            {"Key": "tenant", "Value": tenant_id},
            {"Key": "tenant_plan", "Value": tenant_plan},
            {"Key": "project", "Value": "turboflow"},
        ],
    )

    # Store in DynamoDB
    table.put_item(
        Item={
            "tenant_id": tenant_id,
            "name": tenant_name,
            "plan": tenant_plan,
            "stack_name": stack_name,
            "status": "provisioning",
            "created_at": int(time.time()),
            "workspace": f"s3://{TENANT_BUCKET}/{tenant_id}/",
        }
    )

    return response(201, {
        "tenant_id": tenant_id,
        "name": tenant_name,
        "plan": tenant_plan,
        "status": "provisioning",
        "stack_name": stack_name,
    })


def list_tenants():
    items = table.scan().get("Items", [])
    return response(200, {"tenants": items})


def get_tenant(tenant_id):
    item = table.get_item(Key={"tenant_id": tenant_id}).get("Item")
    if not item:
        return response(404, {"error": f"Tenant {tenant_id} not found"})

    # Check stack status
    stack_name = item.get("stack_name", "")
    if stack_name:
        try:
            stacks = cfn.describe_stacks(StackName=stack_name)["Stacks"]
            if stacks:
                item["stack_status"] = stacks[0]["StackStatus"]
        except Exception:
            item["stack_status"] = "NOT_FOUND"

    return response(200, item)


def delete_tenant(tenant_id):
    item = table.get_item(Key={"tenant_id": tenant_id}).get("Item")
    if not item:
        return response(404, {"error": f"Tenant {tenant_id} not found"})

    stack_name = item.get("stack_name", "")
    if stack_name:
        try:
            cfn.delete_stack(StackName=stack_name)
        except Exception:
            pass

    table.update_item(
        Key={"tenant_id": tenant_id},
        UpdateExpression="SET #s = :s, deleted_at = :d",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": "deleting", ":d": int(time.time())},
    )

    return response(200, {"tenant_id": tenant_id, "status": "deleting"})


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }
'''
