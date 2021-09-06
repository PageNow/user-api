[
    {
        "name": "pagenow-user-api",
        "image": "${docker_image_url_pagenow_user_api}",
        "essential": true,
        "cpu": 10,
        "memory": 512,
        "links": [],
        "portMappings": [
            {
                "containerPort": 8000,
                "hostPort": 0,
                "protocol": "tcp"
            }
        ],
        "command": ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        "environment": [
            {
                "name": "RDS_DB_NAME",
                "value": "${rds_db_name}"
            },
            {
                "name": "RDS_USERNAME",
                "value": "${rds_username}"
            },
            {
                "name": "RDS_PASSWORD",
                "value": "${rds_password}"
            },
            {
                "name": "RDS_HOSTNAME",
                "value": "${rds_hostname}"
            },
            {
                "name": "RDS_PORT",
                "value": "5432"
            }
        ],
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": "/ecs/pagenow-user-api",
                "awslogs-region": "${region}",
                "awslogs-stream-prefix": "pagenow-user-api-log-stream"
            }
        }
    }
]