#!/bin/bash
set -e

# ==== CONFIG ====
PROFILE="CAB432-STUDENT-901444280953"
REGION="ap-southeast-2"
INSTANCE_ID="i-00ef57baf827d039c"
HOSTED_ZONE_ID="Z02680423BHWEVRU2JZDQ"
SUBDOMAIN="n11326158.cab432.com"

# ==== SCRIPT ====
echo "Fetching current EC2 Public DNS..."
EC2_DNS=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query "Reservations[0].Instances[0].PublicDnsName" \
  --output text \
  --region $REGION \
  --profile $PROFILE)

if [ -z "$EC2_DNS" ]; then
  echo "Could not fetch EC2 DNS. Is the instance running?"
  exit 1
fi

echo "Current EC2 DNS: $EC2_DNS"

TMPFILE=$(mktemp)

cat > $TMPFILE <<EOF
{
  "Comment": "Update record to new EC2 public DNS",
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "$SUBDOMAIN",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [
          {
            "Value": "$EC2_DNS"
          }
        ]
      }
    }
  ]
}
EOF

echo "Updating Route53 record for $SUBDOMAIN..."
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://$TMPFILE \
  --region $REGION \
  --profile $PROFILE

rm $TMPFILE
echo "Route53 updated successfully!"
