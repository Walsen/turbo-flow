#!/usr/bin/env python3
"""
TurboFlow Cloud — CDK App Entry Point

Deploys:
1. PlatformStack — shared infrastructure (S3, Cognito, IAM, CloudWatch)
2. TenantStack(s) — per-tenant AgentCore Runtime, Memory, S3 prefix isolation

Usage:
  cd infra
  uv sync
  cdk synth                    # Generate CloudFormation templates
  cdk deploy TurboFlowPlatform # Deploy shared infrastructure
  cdk deploy TenantDemo        # Deploy a demo tenant
  cdk destroy TenantDemo       # Tear down a tenant
"""

import os

import aws_cdk as cdk

from turboflow_infra.platform_stack import PlatformStack
from turboflow_infra.tenant_stack import TenantStack

app = cdk.App()

env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT", os.environ.get("AWS_ACCOUNT_ID")),
    region=os.environ.get("CDK_DEFAULT_REGION", os.environ.get("AWS_REGION", "us-east-1")),
)

# ── Platform Stack (deploy once) ─────────────────────────────────────────
platform = PlatformStack(app, "TurboFlowPlatform", env=env)

# ── Demo Tenant (for testing) ────────────────────────────────────────────
# In production, tenants are provisioned dynamically via the control plane API.
# This demo tenant is for development and testing.
agent_code_bucket = f"turboflow-tenants-{env.account}-{env.region}"

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
