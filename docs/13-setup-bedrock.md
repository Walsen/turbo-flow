# TurboFlow 4.0 — Amazon Bedrock Setup

Run TurboFlow with Amazon Bedrock instead of a direct Anthropic API key. Your model calls go through your AWS account — you control billing, data residency, and access.

## Prerequisites

- AWS account with Bedrock access enabled
- Claude models enabled in Bedrock (Opus 4.6, Sonnet 4.6, Haiku 4.5)
- AWS credentials configured (IAM role, access keys, SSO, or Bedrock API key)

## Quick start

### Option A: Bootstrap with Bedrock

```bash
# Clone and copy devpods (standard pattern)
git clone https://github.com/adventurewavelabs/turbo-flow
cp -r turbo-flow/devpods .
rm -rf turbo-flow

# Set AWS credentials
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret

# Run Bedrock setup
bash devpods/bootstrap.sh setup:bedrock
```

### Option B: Docker with Bedrock

```bash
# Build
docker build -t turbo-flow:4.0 .

# Run with Bedrock
docker run -it \
  -e CLAUDE_CODE_USE_BEDROCK=1 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  turbo-flow:4.0
```

### Option C: Docker Compose with Bedrock

Create a `.env` file:

```bash
CLAUDE_CODE_USE_BEDROCK=1
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

Then:

```bash
docker compose up -d
docker compose exec turboflow bash
```

### Option D: ECS with IAM task role (production)

No access keys needed — the container assumes its IAM role automatically.

```bash
# In your ECS task definition, set:
CLAUDE_CODE_USE_BEDROCK=1
AWS_REGION=us-east-1
# IAM task role provides credentials automatically
```

## AWS credentials

Claude Code uses the standard AWS SDK credential chain. Any of these work:

| Method | Environment variables | Best for |
|---|---|---|
| Access keys | `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | Local dev, CI |
| SSO profile | `AWS_PROFILE=your-profile` | Corporate SSO |
| Bedrock API key | `AWS_BEARER_TOKEN_BEDROCK=your-key` | Simplest auth |
| IAM role | (automatic via ECS/EC2) | Production |
| Session token | `AWS_SESSION_TOKEN` (+ access keys) | Temporary creds |

## Model configuration

Default model pins (cross-region inference profiles):

```bash
ANTHROPIC_DEFAULT_OPUS_MODEL=us.anthropic.claude-opus-4-6-v1
ANTHROPIC_DEFAULT_SONNET_MODEL=us.anthropic.claude-sonnet-4-6
ANTHROPIC_DEFAULT_HAIKU_MODEL=us.anthropic.claude-haiku-4-5-20251001-v1:0
```

Override with application inference profile ARNs for per-tenant routing:

```bash
ANTHROPIC_MODEL=arn:aws:bedrock:us-east-2:123456789012:application-inference-profile/your-id
```

## IAM policy

Minimum permissions for Claude Code on Bedrock:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListInferenceProfiles"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:inference-profile/*",
        "arn:aws:bedrock:*:*:application-inference-profile/*",
        "arn:aws:bedrock:*:*:foundation-model/*"
      ]
    }
  ]
}
```

## Environment variables reference

| Variable | Required | Description |
|---|---|---|
| `CLAUDE_CODE_USE_BEDROCK` | Yes | Set to `1` to enable Bedrock |
| `AWS_REGION` | Yes | AWS region (e.g., `us-east-1`) |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | No | Opus model ID (default: cross-region profile) |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | No | Sonnet model ID |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | No | Haiku model ID |
| `ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION` | No | Override region for Haiku |
| `ANTHROPIC_BEDROCK_BASE_URL` | No | Custom Bedrock endpoint (for gateways) |
| `ENABLE_PROMPT_CACHING_1H_BEDROCK` | No | Set to `1` for 1-hour cache TTL |
| `CLAUDE_CODE_SKIP_BEDROCK_AUTH` | No | Skip AWS auth (for LLM gateways) |

## Verify

After setup, run:

```bash
claude /status
```

The provider line should show `Amazon Bedrock`.

Or use the TurboFlow status check:

```bash
turbo-status
```

## Troubleshooting

- "on-demand throughput isn't supported" → Use inference profile IDs (with `us.` prefix)
- Region errors → Check model availability: `aws bedrock list-inference-profiles --region your-region`
- 403 errors → Verify IAM policy has `bedrock:InvokeModel` permission
- Throttling → Consider provisioned throughput for production workloads

## References

- [Claude Code on Amazon Bedrock (official docs)](https://code.claude.com/docs/en/amazon-bedrock)
- [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)
- [Bedrock inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html)
