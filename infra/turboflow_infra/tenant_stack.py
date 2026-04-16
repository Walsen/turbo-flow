"""
TurboFlow Tenant Stack — per-tenant infrastructure.

Creates for each tenant:
- AgentCore Runtime (Strands agent deployment)
- AgentCore Memory (short-term + long-term with semantic, summarization, user preference)
- AgentCore Gateway (managed MCP server for tenant tools)
- S3 prefix isolation (IAM policy scoped to tenant prefix)
- Cost allocation tags
- CloudWatch log group
"""

from constructs import Construct
from aws_cdk import (
    Duration,
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

        safe_id = tenant_id.replace("-", "_")

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

        # ── AgentCore Memory ─────────────────────────────────────────────
        # Replaces local SQLite AgentDB with managed memory.
        # Short-term: in-session context (90 days retention).
        # Long-term: semantic facts, session summaries, user preferences.
        self.memory = agentcore.Memory(
            self,
            "TenantMemory",
            memory_name=f"tf_{safe_id}_memory",
            description=f"TurboFlow memory for tenant {tenant_name}",
            expiration_duration=Duration.days(90),
            memory_strategies=[
                agentcore.MemoryStrategy.using_built_in_semantic(),
                agentcore.MemoryStrategy.using_built_in_summarization(),
                agentcore.MemoryStrategy.using_built_in_user_preference(),
            ],
            tags={"tenant": tenant_id, "tenant_plan": tenant_plan},
        )

        # ── AgentCore Gateway ────────────────────────────────────────────
        # Managed MCP server hosting for tenant tools.
        self.gateway = agentcore.Gateway(
            self,
            "TenantGateway",
            gateway_name=f"tf-{tenant_id}-gw",
            description=f"TurboFlow MCP gateway for tenant {tenant_name}",
            tags={"tenant": tenant_id, "tenant_plan": tenant_plan},
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
            runtime_name=f"tf_{safe_id}",
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
                "TURBOFLOW_MEMORY_ID": self.memory.memory_id,
                "TURBOFLOW_GATEWAY_ID": self.gateway.gateway_id,
                "S3_WORKSPACE_PREFIX": f"s3://{tenant_bucket.bucket_name}/{tenant_id}/",
            },
            tags={
                "tenant": tenant_id,
                "tenant_plan": tenant_plan,
            },
        )

        # ── Tenant-scoped IAM policy ─────────────────────────────────────
        self.tenant_policy = iam.Policy(
            self,
            "TenantS3Policy",
            policy_name=f"turboflow-tenant-{tenant_id}-s3",
            statements=[
                # S3 access scoped to tenant prefix
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
        CfnOutput(self, "RuntimeName", value=f"tf_{safe_id}")
        CfnOutput(self, "RuntimeArn", value=self.runtime.agent_runtime_arn)
        CfnOutput(self, "MemoryId", value=self.memory.memory_id)
        CfnOutput(self, "MemoryArn", value=self.memory.memory_arn)
        CfnOutput(self, "GatewayId", value=self.gateway.gateway_id)
        CfnOutput(self, "GatewayArn", value=self.gateway.gateway_arn)
        CfnOutput(self, "WorkspacePrefix", value=f"s3://{tenant_bucket.bucket_name}/{tenant_id}/")
        CfnOutput(self, "LogGroup", value=self.log_group.log_group_name)
