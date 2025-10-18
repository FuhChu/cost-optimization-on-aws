# AWS Cost Optimization and Reporting Tool 🚀

!Python
!License
!Built with

This project helps organizations optimize their AWS cloud spending by identifying idle, underutilized, or unattached resources. It leverages AWS APIs with Python's `boto3` library to analyze resource usage, generate actionable reports, and deliver these insights to relevant stakeholders.

## ✨ Key Features

| Feature                        | Description                                                                                             | AWS Service(s)      |
| ------------------------------ | ------------------------------------------------------------------------------------------------------- | ------------------- |
| **Idle Instance Detection**    | Flags running EC2 & RDS instances with consistently low CPU utilization.                                | `EC2`, `RDS`, `CloudWatch` |
| **Unattached Volume Detection**| Lists EBS volumes that are not connected to any EC2 instance ("zombie" volumes).                        | `EC2` (EBS)         |
| **Large S3 Bucket Analysis**   | Pinpoints S3 buckets with significant storage, prompting review for cleanup or lifecycle policies.      | `S3`                |
| **Comprehensive Reporting**    | Generates a human-readable Markdown report with findings, reasons, and recommended actions.             | -                   |
| **Multi-Channel Notifications**| Sends reports or summaries via Email, Slack, and Microsoft Teams.                                       | -                   |

## 🛠️ Technologies Used

*   **Python 3:** Core scripting language.
*   **boto3:** AWS SDK for Python to interact with AWS services.
*   **`requests`:** For sending notifications to webhooks (Slack, Teams).
*   **`smtplib`:** Python's built-in library for sending email notifications.
*   **AWS CLI:** For local credential configuration.

---

## ⚙️ Getting Started

### Prerequisites

*   An active AWS account with permissions to read `EC2`, `RDS`, `S3`, and `CloudWatch` metrics.
*   Python 3.x installed.
*   AWS CLI installed and configured with your credentials:
    ```bash
    aws configure
    ```

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/aws-cost-optimizer.git
    cd aws-cost-optimizer
    ```

2.  **Create and Activate a Python Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🔧 Configuration

All configurable parameters are defined at the top of the `cost_optimizer.py` script.

*   **AWS Settings:** `AWS_REGION`, `IDLE_CPU_THRESHOLD`, `IDLE_DAYS_THRESHOLD`, etc.
*   **Notification Settings:** `EMAIL_SENDER`, `SLACK_WEBHOOK_URL`, etc.

> **🔒 Security Note**
> For production environments, it is **highly recommended** to manage sensitive credentials (email passwords, webhook URLs) using AWS Secrets Manager, AWS Parameter Store, or environment variables instead of hardcoding them in the script.

## ▶️ How to Run

1.  Ensure your virtual environment is activated.
2.  Execute the script from your terminal:
    ```bash
    python cost_optimizer.py
    ```

The script will print the report to the console and save it as `cost_optimization_report.md`. If configured, it will also send notifications.

## 📊 Sample Output

A detailed report will be generated and saved as `cost_optimization_report.md`.

*(A screenshot of the generated Markdown report would look great here!)*

---

## 🔮 Future Enhancements

*   **Advanced Cost Estimation:** Integrate with AWS Price List or Cost Explorer APIs.
*   **Multi-Region/Multi-Account Support:** Scan multiple AWS regions or accounts.
*   **Robust Logging & Error Handling:** Implement the `logging` module and comprehensive retries.
*   **External Configuration:** Move all configurations to environment variables or AWS Parameter Store.
*   **Serverless Deployment:** Deploy as an AWS Lambda function for automated, scheduled execution.
*   **State Management:** Use DynamoDB to track findings and avoid duplicate notifications.
*   **Automated Remediation:** Implement safe, approval-based mechanisms to stop/terminate resources.
*   **Dashboarding:** Visualize findings and trends with Amazon QuickSight or Grafana.

## 🤝 Contributing

Feel free to fork this repository, open issues, and submit pull requests to improve this tool!

## 📄 License

This project is open-source and available under the MIT License.
