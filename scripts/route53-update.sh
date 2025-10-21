#!/bin/bash
set -e

# ==== CONFIG ====
PROFILE="CAB432-STUDENT-901444280953"
REGION="ap-southeast-2"
HOSTED_ZONE_ID="Z02680423BHWEVRU2JZDQ"
SUBDOMAIN="n11326158.cab432.com"
ALB_NAME="n11326158-imgproc-main"

# ==== FETCH ALB DNS ====
echo "[INFO] Fetching DNS name for ALB ($ALB_NAME)..."
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names "$ALB_NAME" \
  --query "LoadBalancers[0].DNSName" \
  --output text \
  --region "$REGION" \
  --profile "$PROFILE")

if [ -z "$ALB_DNS" ] || [ "$ALB_DNS" == "None" ]; then
  echo "[ERROR] Could not fetch ALB DNS name. Check ALB name or permissions."
  exit 1
fi

echo "[SUCCESS] Found ALB DNS: $ALB_DNS"

# ==== CREATE ROUTE53 UPDATE FILE ====
TMPFILE=$(mktemp)

cat > "$TMPFILE" <<EOF
{
  "Comment": "Update record to point to ALB DNS",
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "$SUBDOMAIN",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [
          {
            "Value": "$ALB_DNS"
          }
        ]
      }
    }
  ]
}
EOF

# ==== UPDATE ROUTE53 ====
echo "[INFO] Updating Route53 record for $SUBDOMAIN..."
aws route53 change-resource-record-sets \
  --hosted-zone-id "$HOSTED_ZONE_ID" \
  --change-batch "file://$TMPFILE" \
  --region "$REGION" \
  --profile "$PROFILE"

rm "$TMPFILE"
echo "[SUCCESS] Route53 updated successfully to ALB ($ALB_DNS)"
