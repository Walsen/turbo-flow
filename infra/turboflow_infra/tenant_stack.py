"""
TurboFlow Tenant Stack — per-tenant infrastructure.

Creates for each tenant:
- AgentCore Runtime (Strands agent deployment)
- AgentCore Memory (short-term + long-term)
- S3 prefix isolation (IAM policy scoped to tenant prefix)
- Cost allocation tags
- CloudWatch log group
"""

from constructs import Construct
from aws_cdk import (
    Stack,
    Tags,
    RemovalPolicy,
    CfnOutput,
    aws_iam as iam,
    aws_logs as logs,
    aws_s3 as s3,
)
import aws_cdk.aws_bedrock_agentcore_alpha as agentcore


class TenantStack(Stack):
    """Per-tenant infrastructure — one stack per tenant."""

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        tenant_id: str,
        tenant_name: str,
        tenant_plan: str,  # starter, pro, enterprise
        tenant_bucket: s3.IBucket,
        agent_execution_role: iam.IRole,
        agent_code_bucket: str,
        agent_code_key: str,
        **kwargs,
    ) -> None:  # type: ignore
        super().__init__(scope, id, **kwargs)

        # Apply cost allocation tag to everything in this stack
        Tags.of(self).add("tenant", tenant_id)
        Tags.of(self).add("tenant_name", tenant_name)
        Tags.of(self).add("tenant_plan", tenant_plan)
        Tags.of(self).add("project", "turboflow")

        # ── CloudWatch Log Group ─────────────────────────────────────────
        self.log_group = logs.LogGroup(
            self,
            "TenantLogs",
            log_group_name=f"/turboflow/tenants/{tenant_id}",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # ── AgentCore Runtime ────────────────────────────────────────────
        artifact = agentcore.AgentRuntimeArtifact.from_s3(
            s3.Location(
                bucket_name=agent_code_bucket,
                object_key=agent_code_key,
            ),
            agentcore.AgentCoreRuntime.PYTHON_3_12,
            ["main.py"],
        )

        self.runtime = agentcore.Runtime(
            self,
            "AgentRuntime",
            runtime_name=f"tf_{tenant_id.replace('-', '_')}",
            agent_runtime_artifact=artifact,
            execution_role=agent_execution_role,
            description=f"TurboFlow agent for tenant {tenant_name} ({tenant_plan})",
            environment_variables={
                "TENANT_ID": tenant_id,
                "TENANT_PLAN": tenant_plan,
                "TURBOFLOW_AGENT_BACKEND": "strands",
                "CLAUDE_CODE_USE_BEDROCK": "1",
                "AWS_REGION": self.region,
                "TURBOFLOW_MEMORY_BACKEND": "agentcore",
                "S3_WORKSPACE_PREFIX": f"s3://{tenant_bucket.bucket_name}/{tenant_id}/",
            },
            tags={
                "tenant": tenant_id,
                "tenant_plan": tenant_plan,
            },
        )

        # ── Tenant-scoped IAM policy ─────────────────────────────────────
        # Restrict S3 access to only this tenant's prefix
        self.tenant_policy = iam.Policy(
            self,
            "TenantS3Policy",
            policy_name=f"turboflow-tenant-{tenant_id}-s3",
            statements=[
                iam.PolicyStatement(
                    actions=["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"],
                    resources=[
                        f"{tenant_bucket.bucket_arn}/{tenant_id}/*",
                        tenant_bucket.bucket_arn,
                    ],
                    conditions={
                        "StringLike": {
                            "s3:prefix": [f"{tenant_id}/*"],
                        }
                    },
                ),
            ],
        )

        # ── Outputs ──────────────────────────────────────────────────────
        CfnOutput(self, "TenantId", value=tenant_id)
        CfnOutput(self, "RuntimeName", value=f"tf_{tenant_id.replace('-', '_')}")
        CfnOutput(self, "RuntimeArn", value=self.runtime.agent_runtime_arn)
        CfnOutput(self, "WorkspacePrefix", value=f"s3://{tenant_bucket.bucket_name}/{tenant_id}/")
        CfnOutput(self, "LogGroup", value=self.log_group.log_group_name)
