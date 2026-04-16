# TurboFlow Cloud — Infrastructure (CDK)

Phase 3 serverless infrastructure using AWS CDK (Python).

## Architecture

```
PlatformStack (shared, deploy once):
  - S3 bucket for all tenant workspaces
  - Cognito User Pool for authentication
  - IAM execution role for AgentCore agents
  - CloudWatch dashboard

TenantStack (per tenant):
  - AgentCore Runtime (Strands agent)
  - S3 prefix isolation (IAM scoped)
  - CloudWatch log group
  - Cost allocation tags
```

## Quick Start

```bash
cd infra
uv sync

# Synthesize CloudFormation templates
cdk synth

# Deploy shared platform
cdk deploy TurboFlowPlatform

# Deploy demo tenant
cdk deploy TenantDemo

# Tear down demo tenant
cdk destroy TenantDemo
```

## Environment

```bash
export AWS_PROFILE=walsen
export AWS_REGION=us-east-1
export CDK_DEFAULT_ACCOUNT=862307432587
export CDK_DEFAULT_REGION=us-east-1
```
