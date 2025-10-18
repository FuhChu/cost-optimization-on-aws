# cost-optimization-on-aws
This project helps identify idle resources and propose cost saving steps.
# AWS Cost Optimization and Reporting Tool

## Project Objective
This project aims to help organizations optimize their AWS cloud spending by identifying idle, underutilized, or unattached resources across various AWS services. It leverages AWS APIs with Python's `boto3` library to analyze resource usage, generate actionable reports, and deliver these insights to relevant stakeholders via email and/or Slack/Teams notifications.

The goal is to provide a clear, automated overview of potential cost-saving opportunities, empowering teams to make informed decisions about their cloud infrastructure.

## Features
*   **Identifies Idle EC2 Instances:** Flags running EC2 instances with consistently low CPU utilization over a defined period.
*   **Detects Unattached EBS Volumes:** Lists EBS volumes that are not connected to any EC2 instance.
*   **Highlights Large S3 Buckets:** Pinpoints S3 buckets with significant storage, prompting review for old versions, incomplete multipart uploads, or unneeded data.
*   **Finds Idle RDS Instances:** Identifies running RDS databases with low CPU utilization and few (or zero) active connections.
*   **Suggests Underutilized EC2 Instances:** Points out EC2 instances that might be oversized based on consistently moderate CPU usage, suggesting potential rightsizing opportunities.
*   **Generates Comprehensive Reports:** Creates a human-readable Markdown report detailing findings, reasons, recommended actions, and placeholder for estimated savings.
*   **Notification Integration:** Sends reports or summaries via email and/or Slack/Teams webhooks.

## Technologies Used
*   **Python 3:** Core scripting language.
*   **boto3:** AWS SDK for Python, used to interact with AWS services (EC2, CloudWatch, S3, RDS).
*   **`requests`:** For sending notifications to webhooks (e.g., Slack, Microsoft Teams).
*   **`smtplib`:** Python's built-in library for sending email notifications.
*   **AWS CLI:** For configuring AWS credentials locally.

## Getting Started

### Prerequisites
*   An active AWS account with permissions to read EC2, RDS, S3, and CloudWatch metrics.
*   Python 3.x installed.
*   AWS CLI installed and configured with your AWS credentials.
    ```bash
    aws configure
    ```
*   (Optional) SMTP server details for email notifications (e.g., Gmail account settings).
*   (Optional) Slack or Microsoft Teams incoming webhook URL for notifications.

### Installation

1.  **Clone the Repository (or create the project structure):**
    ```bash
    git clone https://github.com/your-username/aws-cost-optimizer.git
    cd aws-cost-optimizer
    ```
    (If not using Git, just create a directory `aws_cost_optimizer` and navigate into it.)

2.  **Create and Activate a Python Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    ```

3.  **Install Required Python Packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

All configurable parameters are defined at the top of the `cost_optimizer.py` script.

### AWS Settings
*   `AWS_REGION`: The AWS region to analyze (e.g., `'us-east-1'`).
*   `IDLE_CPU_THRESHOLD`: Percentage CPU utilization below which an instance is considered idle (e.g., `5.0`).
*   `IDLE_DAYS_THRESHOLD`: Number of days for which metrics are analyzed to determine idleness (e.g., `7`).
*   `S3_LARGE_BUCKET_THRESHOLD_GB`: Size in GB above which an S3 bucket is flagged for review (e.g., `100`).

### Notification Settings (Uncomment and fill as needed)
*   **Email:**
    *   `EMAIL_SENDER`: Your sending email address.
    *   `EMAIL_RECIPIENT`: Recipient email address.
    *   `EMAIL_PASSWORD`: Your email password (for Gmail, consider an App Password or environment variable for security).
    *   `SMTP_SERVER`: Your SMTP server (e.g., `'smtp.gmail.com'`).
    *   `SMTP_PORT`: Your SMTP port (e.g., `587` for TLS).
*   **Slack/Teams Webhook:**
    *   `SLACK_WEBHOOK_URL`: Your Slack Incoming Webhook URL.
    *   `TEAMS_WEBHOOK_URL`: Your Microsoft Teams Incoming Webhook URL.

**SECURITY NOTE:** For production environments, it is *highly recommended* to manage sensitive credentials (email passwords, webhook URLs) using AWS Secrets Manager, AWS Parameter Store, or environment variables instead of hardcoding them in the script.

## How to Run

1.  **Activate your virtual environment:**
    ```bash
    source venv/bin/activate
    ```
2.  **Execute the Python script:**
    ```bash
    python cost_optimizer.py
    ```

The script will print the report to the console and save it as `cost_optimization_report.md` in the project directory. If configured, it will also send notifications.

## Output
*   A detailed report will be generated and saved as `cost_optimization_report.md`.
*   A summary or the full report can be sent via email.
*   A summary can be posted to a configured Slack or Microsoft Teams channel.

## Future Enhancements (Production-Grade Improvements)
*   **Advanced Cost Estimation:** Integrate with AWS Price List API or Cost Explorer API for accurate potential savings.
*   **Multi-Region/Multi-Account Support:** Extend to scan multiple AWS regions or accounts (using AWS Organizations).
*   **Robust Logging:** Implement Python's `logging` module for better debuggability and monitoring.
*   **Error Handling & Retries:** Implement comprehensive error handling and retry mechanisms for AWS API calls.
*   **Configuration Management:** Externalize all configurations (e.g., using environment variables, AWS Parameter Store).
*   **Serverless Deployment:** Deploy as an AWS Lambda function triggered by CloudWatch Events for fully managed, cost-effective execution.
*   **Idempotency & State Management:** Track identified issues to avoid duplicate notifications and support automated remediation workflows.
*   **Automated Remediation (with caution):** Implement safe, approval-based mechanisms to stop/terminate resources. Include a `--dry-run` option.
*   **Dashboarding:** Store findings in a database (e.g., DynamoDB) and visualize trends using tools like Amazon QuickSight or Grafana.
*   **Unit and Integration Testing:** Implement tests to ensure reliability and correctness.

## Contributing
Feel free to fork this repository, open issues, and submit pull requests to improve this tool!

## License
This project is open-source and available under the [MIT License](LICENSE).
