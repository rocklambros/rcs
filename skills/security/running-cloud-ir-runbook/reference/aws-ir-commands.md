# AWS IR command reference

> AWS CLI / SDK commands organized by runbook step. Substitute the bracketed values.
> Run in the IR rotation's quarantine role, not the on-call's day-to-day role.

## Step 2: Preserve evidence

Capture CloudTrail for the alert window ± 4h into the evidence-destination account.

```bash
# Identity-keyed events from CloudTrail (90-day API; for older use the S3 archive)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=[affected-identity] \
  --start-time [window-start-minus-4h] --end-time [window-end-plus-4h] \
  --max-results 1000 \
  --region [region] \
  > evidence/cloudtrail-by-identity.json

# Resource-keyed events (when the identity touched a specific resource)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=[resource-id] \
  --start-time [window-start-minus-4h] --end-time [window-end-plus-4h] \
  > evidence/cloudtrail-by-resource.json

# Long-retention: read directly from the CloudTrail S3 bucket (gzipped JSON per file)
aws s3 cp s3://[org-cloudtrail-bucket]/AWSLogs/[account-id]/CloudTrail/[region]/[YYYY/MM/DD]/ \
  evidence/cloudtrail-archive/ --recursive
```

Snapshot the identity's IAM policies before changing anything:

```bash
aws iam list-attached-user-policies --user-name [user] > evidence/user-attached-policies.json
aws iam list-user-policies --user-name [user] > evidence/user-inline-policies.json
for p in $(aws iam list-user-policies --user-name [user] --query 'PolicyNames[]' --output text); do
  aws iam get-user-policy --user-name [user] --policy-name $p > evidence/inline-$p.json
done
aws iam list-access-keys --user-name [user] > evidence/user-access-keys.json
aws iam list-groups-for-user --user-name [user] > evidence/user-groups.json
```

VPC Flow Logs for the alert window (if delivered to CloudWatch Logs):

```bash
aws logs filter-log-events \
  --log-group-name [vpc-flow-log-group] \
  --start-time [window-start-ms] --end-time [window-end-ms] \
  --filter-pattern '[srcaddr=[suspect-ip]]' \
  > evidence/vpc-flow-filtered.json
```

S3 server-access logs (if enabled on the bucket the identity could touch):

```bash
aws s3 cp s3://[server-access-log-bucket]/[prefix]/ evidence/s3-access-logs/ --recursive \
  --exclude '*' --include '[YYYY-MM-DD]*'
```

After capture, hash and seal:

```bash
find evidence/ -type f -exec sha256sum {} \; > evidence/HASHES.txt
aws s3 sync evidence/ s3://[ir-evidence-bucket]/[engagement-id]/ \
  --metadata-directive REPLACE \
  --metadata "ir-rotation=[on-call],hashed=true"
# Object Lock should be enabled on the evidence bucket with a 1-year retention
```

## Step 3: Contain

Disable user access keys (do NOT delete):

```bash
for k in $(aws iam list-access-keys --user-name [user] --query 'AccessKeyMetadata[].AccessKeyId' --output text); do
  aws iam update-access-key --user-name [user] --access-key-id $k --status Inactive
done
```

Attach explicit deny policy to halt all actions (catches any forgotten key path):

```bash
cat > /tmp/ir-deny-all.json <<'EOF'
{"Version":"2012-10-17","Statement":[{"Effect":"Deny","Action":"*","Resource":"*"}]}
EOF
aws iam put-user-policy --user-name [user] --policy-name IR-DENY-ALL \
  --policy-document file:///tmp/ir-deny-all.json
```

Revoke active assumed-role sessions (token issued before now):

```bash
# Replace [now-iso] with the containment timestamp
cat > /tmp/ir-revoke-sessions.json <<EOF
{"Version":"2012-10-17","Statement":[{"Effect":"Deny","Action":"*","Resource":"*","Condition":{"DateLessThan":{"aws:TokenIssueTime":"[now-iso]"}}}]}
EOF
aws iam put-role-policy --role-name [role] --policy-name IR-REVOKE-SESSIONS \
  --policy-document file:///tmp/ir-revoke-sessions.json
```

For console access (if the identity has a password):

```bash
aws iam delete-login-profile --user-name [user]
```

## Step 4: Blast-radius assessment

Could-touch set (simulate the effective permission set):

```bash
# For a specific action
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::[account]:user/[user] \
  --action-names s3:GetObject ec2:RunInstances iam:CreateAccessKey \
  --resource-arns 'arn:aws:s3:::*' 'arn:aws:ec2:*:[account]:*'

# Recommended tool: policy-sentry to enumerate the full could-touch set
# https://policy-sentry.readthedocs.io/
```

Did-touch set (what actually happened):

```bash
# Group the captured CloudTrail by EventName + Resource
jq '[.Events[] | {time:.EventTime,event:.EventName,resources:[.Resources[]?.ResourceName]}]' \
  evidence/cloudtrail-by-identity.json \
  > evidence/did-touch-summary.json
```

## Step 6: Eradicate

Check for any keys / policies / roles the identity created during the window:

```bash
jq '[.Events[] | select(.EventName | IN("CreateAccessKey","CreateUser","CreateRole","AttachUserPolicy","AttachRolePolicy","PutUserPolicy","PutRolePolicy","CreatePolicyVersion","UpdateAssumeRolePolicy"))]' \
  evidence/cloudtrail-by-identity.json \
  > evidence/identity-mutations.json
```

Each entry in `identity-mutations.json` is a candidate access path. Verify and revert.

Check for Lambda / EventBridge persistence:

```bash
jq '[.Events[] | select(.EventName | IN("CreateFunction","UpdateFunctionCode","CreateEventSourceMapping","PutRule","PutTargets","CreateSchedule"))]' \
  evidence/cloudtrail-by-identity.json \
  > evidence/persistence-candidates.json
```

## Step 7: Recover

Re-enable the identity only after dual sign-off (IR lead + service owner):

```bash
aws iam delete-user-policy --user-name [user] --policy-name IR-DENY-ALL
aws iam delete-role-policy --role-name [role] --policy-name IR-REVOKE-SESSIONS
# Mint a new credential scoped per least-privilege
```

Rotate dependent secrets the identity could have read:

```bash
# Database passwords, third-party API keys, signing keys, OAuth client secrets
# Each is provider-specific — script per resource
```
