# --- S3 bucket ---
resource "aws_s3_bucket" "app_bucket" {
  bucket = "n11326158-assessment2"

  tags = {
    qut-username = "n11326158@qut.edu.au"
    purpose      = "assessment-2"
  }

  lifecycle {
    ignore_changes = all
  }
}

# --- Cognito user pool ---
resource "aws_cognito_user_pool" "userpool" {
  name = "cab432-userpool-n11326158"

  tags = {
    qut-username = "n11326158@qut.edu.au"
    purpose      = "assessment-2"
  }

  lifecycle {
    ignore_changes = all
  }
}

# --- Cognito app client ---
resource "aws_cognito_user_pool_client" "app_client" {
  name         = "cab432-userpool-n11326158"
  user_pool_id = aws_cognito_user_pool.userpool.id

  lifecycle {
    ignore_changes = all
  }
}

# --- Cognito group ---
resource "aws_cognito_user_group" "admin" {
  name         = "admin"
  user_pool_id = aws_cognito_user_pool.userpool.id

  lifecycle {
    ignore_changes = all
  }
}

# --- Route53 record ---
resource "aws_route53_record" "app" {
  zone_id = "Z02680423BHWEVRU2JZDQ"
  name    = "n11326158.cab432.com"
  type    = "CNAME"
  ttl     = 300
  records = ["ec2-54-252-136-209.ap-southeast-2.compute.amazonaws.com"]

  lifecycle {
    ignore_changes = all
  }
}
