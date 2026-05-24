# GCP + Azure IR command reference

> Equivalents to the AWS commands in `aws-ir-commands.md`. Run in the IR rotation's
> quarantine identity, not the on-call's day-to-day identity.

## GCP

### Step 2: Preserve evidence

Capture Cloud Audit Logs for the alert window:

```bash
gcloud logging read \
  'protoPayload.authenticationInfo.principalEmail="[affected-sa-email]"
   AND timestamp >= "[window-start-iso]" AND timestamp <= "[window-end-iso]"' \
  --project=[project-id] \
  --format=json \
  > evidence/gcp-audit-by-identity.json

# Resource-keyed
gcloud logging read \
  'resource.labels.bucket_name="[bucket]" OR resource.labels.instance_id="[instance]"
   AND timestamp >= "[window-start-iso]" AND timestamp <= "[window-end-iso]"' \
  --project=[project-id] --format=json \
  > evidence/gcp-audit-by-resource.json
```

Snapshot IAM bindings:

```bash
gcloud projects get-iam-policy [project-id] --format=json > evidence/gcp-iam-policy.json
gcloud iam service-accounts get-iam-policy [sa-email] --format=json \
  > evidence/gcp-sa-iam-policy.json
gcloud iam service-accounts keys list --iam-account=[sa-email] --format=json \
  > evidence/gcp-sa-keys.json
```

VPC Flow Logs (if exported to BigQuery):

```bash
bq query --use_legacy_sql=false --format=json \
  'SELECT * FROM `[project].vpc_flow_logs.compute_googleapis_com_vpc_flows_*`
   WHERE _TABLE_SUFFIX BETWEEN "[YYYYMMDD]" AND "[YYYYMMDD]"
   AND connection.src_ip = "[suspect-ip]"' \
  > evidence/gcp-vpc-flow.json
```

### Step 3: Contain

Disable the service account (do NOT delete):

```bash
gcloud iam service-accounts disable [sa-email] --project=[project-id]
```

Delete leaked keys (after they are captured in evidence):

```bash
for k in $(gcloud iam service-accounts keys list --iam-account=[sa-email] \
  --filter='keyType=USER_MANAGED' --format='value(name)' | awk -F/ '{print $NF}'); do
  gcloud iam service-accounts keys delete $k --iam-account=[sa-email] --quiet
done
```

Revoke project-level binding (attach an explicit deny binding):

```bash
gcloud projects add-iam-policy-binding [project-id] \
  --member='serviceAccount:[sa-email]' \
  --role='roles/iam.denyAdmin' \
  --condition='None'
# OR use IAM Deny policies (preview/GA depending on region) for explicit denies
```

For OAuth2 grants on human accounts, revoke via the Google Workspace admin console
under Security → API controls → App access control.

### Step 4: Blast-radius assessment

Could-touch set:

```bash
gcloud asset analyze-iam-policy \
  --organization=[org-id] \
  --identity=serviceAccount:[sa-email] \
  --output-resource-edges \
  > evidence/gcp-could-touch.json
```

### Step 6: Eradicate

Identity-keyed mutations:

```bash
gcloud logging read \
  'protoPayload.authenticationInfo.principalEmail="[sa-email]"
   AND protoPayload.methodName=~"^(google.iam|google.cloud.functions|google.cloud.scheduler|google.pubsub).*"' \
  --project=[project-id] --format=json \
  > evidence/gcp-identity-mutations.json
```

## Azure

### Step 2: Preserve evidence

Activity Log for the alert window:

```bash
az monitor activity-log list \
  --caller [affected-principal-id] \
  --start-time [window-start-iso] --end-time [window-end-iso] \
  --output json \
  > evidence/azure-activity-by-caller.json
```

Sign-in logs (for human users + service principals):

```bash
az rest --method get \
  --url "https://graph.microsoft.com/v1.0/auditLogs/signIns?\$filter=userPrincipalName eq '[upn]' and createdDateTime ge [iso] and createdDateTime le [iso]" \
  > evidence/azure-signin-logs.json
```

NSG Flow Logs (assuming exported to a storage account):

```bash
az storage blob download-batch \
  --account-name [storage-acct] \
  --source [container] \
  --pattern '*[YYYY/MM/DD]*' \
  --destination evidence/azure-nsg-flow/
```

Snapshot RBAC role assignments:

```bash
az role assignment list --assignee [principal-id] --all --output json \
  > evidence/azure-role-assignments.json
```

### Step 3: Contain

Disable the user / service principal:

```bash
# Human user or application identity
az ad user update --id [user-or-app-id] --account-enabled false
# Service principal
az ad sp update --id [sp-id] --set accountEnabled=false
```

Reset application credentials:

```bash
az ad app credential reset --id [app-id]
```

Revoke active sessions for a user (forces token re-issuance):

```bash
az rest --method post \
  --url "https://graph.microsoft.com/v1.0/users/[user-id]/revokeSignInSessions"
```

### Step 4: Blast-radius assessment

Could-touch set:

```bash
# Effective RBAC across all subscriptions in the tenant
az graph query -q "AuthorizationResources
  | where type =~ 'microsoft.authorization/roleassignments'
  | where properties.principalId == '[principal-id]'
  | project subscriptionId, properties" \
  > evidence/azure-could-touch.json
```

### Step 6: Eradicate

Identity-keyed mutations:

```bash
az monitor activity-log list \
  --caller [principal-id] \
  --start-time [window-start-iso] --end-time [window-end-iso] \
  --query '[?contains(operationName.value, `roleAssignments/write`) || contains(operationName.value, `microsoft.web/sites/write`) || contains(operationName.value, `Microsoft.Automation`)]' \
  > evidence/azure-identity-mutations.json
```
