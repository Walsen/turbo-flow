#!/usr/bin/env python3
"""
TurboFlow Cloud — CDK App Entry Point

Deploys:
1. PlatformStack — shared infrastructure (S3, Cognito, IAM, CloudWatch)
2. ProvisioningStack — tenant lifecycle API (Lambda + API Gateway + DynamoDB)
3. TenantStack(s) — per-tenant AgentCore Runtime, Memory, Gateway

Usage:
  cd infra
  uv sync
  cdk synth                         # Generate CloudFormation templates
  cdk deploy TurboFlowPlatform      # Deploy shared infrastructure
  cdk deploy TurboFlowProvisioning  # Deploy tenant provisioning API
  cdk deploy TenantDemo             # Deploy a demo tenant
  cdk destroy TenantDemo            # Tear down a tenant
"""

import os

import aws_cdk as cdk

from turboflow_infra.platform_stack import PlatformStack
from turboflow_infra.provisioning_stack import ProvisioningStack
from turboflow_infra.tenant_stack import TenantStack

app = cdk.App()

env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT", os.environ.get("AWS_ACCOUNT_ID")),
    region=os.environ.get("CDK_DEFAULT_REGION", os.environ.get("AWS_REGION", "us-east-1")),
)

agent_code_bucket = f"turboflow-tenants-{env.account}-{env.region}"

# ── Platform Stack (deploy once) ─────────────────────────────────────────
platform = PlatformStack(app, "TurboFlowPlatform", env=env)

# ── Provisioning Stack (tenant lifecycle API) ────────────────────────────
ProvisioningStack(
    app,
    "TurboFlowProvisioning",
    env=env,
    tenant_bucket_name=platform.tenant_bucket.bucket_name,
    agent_execution_role_arn=platform.agent_execution_role.role_arn,
    agent_code_bucket=agent_code_bucket,
    agent_code_key="agent-code/deployment_package.zip",
)

# ── Demo Tenant (for testing) ────────────────────────────────────────────
TenantStack(
    app,
    "TenantDemo",
    env=env,
    tenant_id="demo-001",
    tenant_name="Demo Tenant",
    tenant_plan="starter",
    tenant_bucket=platform.tenant_bucket,
    agent_execution_role=platform.agent_execution_role,
    agent_code_bucket=agent_code_bucket,
    agent_code_key="agent-code/deployment_package.zip",
)

app.synth()
