#!/bin/bash
# cognora-production.sh — Production deployment script for AWS ECS
# Usage: ./cognora-production.sh [deploy|scale|status|logs]

set -euo pipefail

AWS_REGION="us-east-1"
CLUSTER="cognora-cluster"
SERVICE="cognora-backend"
TASK_DEF="cognora-backend"
ALB_TARGET_GROUP="arn:aws:elasticloadbalancing:us-east-1:ACCOUNT_ID:targetgroup/cognora-backend/abcd1234"
REPO="ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cognora"

deploy() {
    echo "=== Building and pushing Docker image ==="
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $REPO

    docker build -t $REPO:latest ./backend
    docker push $REPO:latest

    echo "=== Registering new task definition ==="
    aws ecs register-task-definition \
        --cli-input-json file://deploy/ecs-task-definition.json \
        --region $AWS_REGION

    echo "=== Updating ECS service ==="
    aws ecs update-service \
        --cluster $CLUSTER \
        --service $SERVICE \
        --task-definition $TASK_DEF \
        --force-new-deployment \
        --region $AWS_REGION

    echo "=== Waiting for deployment to stabilize ==="
    aws ecs wait services-stable \
        --cluster $CLUSTER \
        --services $SERVICE \
        --region $AWS_REGION

    echo "=== Deployment complete ==="
}

scale() {
    local count=${1:-4}
    echo "=== Scaling to $count tasks ==="
    aws ecs update-service \
        --cluster $CLUSTER \
        --service $SERVICE \
        --desired-count $count \
        --region $AWS_REGION
    echo "=== Scaled to $count ==="
}

status() {
    echo "=== ECS Service Status ==="
    aws ecs describe-services \
        --cluster $CLUSTER \
        --services $SERVICE \
        --region $AWS_REGION \
        --query 'services[0].{status:status,desired:desiredCount,running:runningCount,health:healthCheckGracePeriodSeconds}'

    echo ""
    echo "=== Target Group Health ==="
    aws elbv2 describe-target-health \
        --target-group-arn $ALB_TARGET_GROUP \
        --region $AWS_REGION \
        --query 'TargetHealthDescriptions[].{id:Target.Id,port:Target.Port,state:TargetHealth.State}'

    echo ""
    echo "=== Auto Scaling ==="
    aws application-autoscaling describe-scalable-targets \
        --service-namespace ecs \
        --resource-id "service/$CLUSTER/$SERVICE" \
        --region $AWS_REGION
}

logs() {
    aws logs tail /ecs/cognora-backend \
        --region $AWS_REGION \
        --since 1h \
        --follow
}

case ${1:-help} in
    deploy) deploy ;;
    scale) scale "${2:-4}" ;;
    status) status ;;
    logs) logs ;;
    *)
        echo "Usage: $0 {deploy|scale|status|logs}"
        echo "  deploy         Build, push, and deploy to ECS"
        echo "  scale [N]      Scale to N tasks (default: 4)"
        echo "  status         Show service health and auto-scaling status"
        echo "  logs           Stream CloudWatch logs"
        ;;
esac
