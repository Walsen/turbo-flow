"""
TurboFlow Platform Stack — shared infrastructure for all tenants.

Creates:
- S3 bucket for tenant workspaces
- Cognito User Pool for tenant authentication
- AgentCore Gateway for managed MCP tools
- CloudWatch dashboard for platform metrics
"""

from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    Duration,
    aws_s3 as s3,
    aws_cognito as cognito,
    aws_iam as iam,
    aws_cloudwatch as cw,
)


class PlatformStack(Stack):
    """Shared platform infrastructure — deployed once, used by all tenants."""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:  # type: ignore
        super().__init__(scope, id, **kwargs)

        # ── S3 bucket for all tenant workspaces ──────────────────────────
        self.tenant_bucket = s3.Bucket(
            self,
            "TenantWorkspaces",
            bucket_name=f"turboflow-tenants-{self.account}-{self.region}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="transition-to-ia",
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30),
                        )
                    ],
                ),
                s3.LifecycleRule(
                    id="expire-deleted-tenants",
                    prefix="deleted/",
                    expiration=Duration.days(30),
                ),
            ],
        )

        # ── Cognito User Pool for tenant authentication ──────────────────
        self.user_pool = cognito.UserPool(
            self,
            "TenantUserPool",
            user_pool_name="turboflow-tenants",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True,
            ),
            removal_policy=RemovalPolicy.RETAIN,
        )

        self.user_pool_client = self.user_pool.add_client(
            "TenantAppClient",
            user_pool_client_name="turboflow-app",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[cognito.OAuthScope.OPENID, cognito.OAuthScope.EMAIL, cognito.OAuthScope.PROFILE],
            ),
        )

        # ── IAM role for AgentCore Runtime agents ────────────────────────
        self.agent_execution_role = iam.Role(
            self,
            "AgentExecutionRole",
            role_name="turboflow-agent-execution",
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            description="Execution role for TurboFlow Strands agents on AgentCore Runtime",
        )

        # Bedrock model invocation
        self.agent_execution_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=[
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.*",
                    f"arn:aws:bedrock:{self.region}::foundation-model/us.anthropic.*",
                    f"arn:aws:bedrock:{self.region}::foundation-model/amazon.*",
                ],
            )
        )

        # S3 access for tenant workspaces
        self.tenant_bucket.grant_read_write(self.agent_execution_role)

        # CloudWatch logs
        self.agent_execution_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                resources=["*"],
            )
        )

        # AgentCore Memory access
        self.agent_execution_role.add_to_policy(
            iam.PolicyStatement(
                actions=["bedrock-agentcore:*"],
                resources=["*"],
            )
        )

        # ── CloudWatch Dashboard ─────────────────────────────────────────
        self.dashboard = cw.Dashboard(
            self,
            "PlatformDashboard",
            dashboard_name="turboflow-platform",
        )

        # ── Outputs ──────────────────────────────────────────────────────
        CfnOutput(self, "TenantBucketName", value=self.tenant_bucket.bucket_name)
        CfnOutput(self, "TenantBucketArn", value=self.tenant_bucket.bucket_arn)
        CfnOutput(self, "UserPoolId", value=self.user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=self.user_pool_client.user_pool_client_id)
        CfnOutput(self, "AgentExecutionRoleArn", value=self.agent_execution_role.role_arn)
