import boto3
import datetime
from collections import defaultdict

# --- Configuration ---
AWS_REGION = 'us-east-1' # Change to your desired region
IDLE_CPU_THRESHOLD = 5.0 # Percentage for EC2/RDS idle check
IDLE_DAYS_THRESHOLD = 7 # Number of days for idle check
S3_LARGE_BUCKET_THRESHOLD_GB = 100 # GB to consider an S3 bucket "large"

# --- Boto3 Clients ---
ec2_client = boto3.client('ec2', region_name=AWS_REGION)
cloudwatch_client = boto3.client('cloudwatch', region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)
rds_client = boto3.client('rds', region_name=AWS_REGION)

# --- Helper Functions ---

def get_metric_statistics(namespace, metric_name, dimensions, period_seconds, start_time, end_time, statistic='Average'):
    """
    Retrieves CloudWatch metric statistics.
    """
    response = cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'm1',
                'MetricStat': {
                    'Metric': {
                        'Namespace': namespace,
                        'MetricName': metric_name,
                        'Dimensions': dimensions
                    },
                    'Period': period_seconds,
                    'Stat': statistic
                },
                'ReturnData': True
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
    )
    # Check if there's any data
    if response['MetricDataResults'] and response['MetricDataResults'][0]['Values']:
        return response['MetricDataResults'][0]['Values']
    return []

def get_average_metric(namespace, metric_name, dimensions, days_ago, period_seconds=3600):
    """
    Calculates the average metric over a specified number of days.
    """
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(days=days_ago)

    metric_values = get_metric_statistics(
        namespace=namespace,
        metric_name=metric_name,
        dimensions=dimensions,
        period_seconds=period_seconds, # 1 hour period
        start_time=start_time,
        end_time=end_time
    )
    if metric_values:
        return sum(metric_values) / len(metric_values)
    return None

# --- Cost Vector Functions ---

def analyze_idle_ec2_instances():
    """
    Identifies idle EC2 instances based on CPU utilization.
    """
    print(f"\n--- Analyzing Idle EC2 Instances ({AWS_REGION}) ---")
    idle_instances = []
    
    response = ec2_client.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            launch_time = instance['LaunchTime']
            instance_name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')

            # Only check instances running for at least our idle threshold days
            if (datetime.datetime.utcnow().replace(tzinfo=None) - launch_time.replace(tzinfo=None)).days < IDLE_DAYS_THRESHOLD:
                # print(f"Skipping {instance_id} (not running long enough)")
                continue

            avg_cpu = get_average_metric(
                namespace='AWS/EC2',
                metric_name='CPUUtilization',
                dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                days_ago=IDLE_DAYS_THRESHOLD
            )

            if avg_cpu is not None and avg_cpu < IDLE_CPU_THRESHOLD:
                idle_instances.append({
                    'ResourceID': instance_id,
                    'Name': instance_name,
                    'Service': 'EC2',
                    'Region': AWS_REGION,
                    'Reason': f"Average CPU utilization over {IDLE_DAYS_THRESHOLD} days: {avg_cpu:.2f}% (below {IDLE_CPU_THRESHOLD}%)",
                    'Action': f"Consider stopping or terminating instance '{instance_name}' ({instance_id}).",
                    'PotentialSavings': 'Estimate required' # Placeholder for actual cost calculation
                })
                print(f"  - IDLE EC2: {instance_name} ({instance_id}) - Avg CPU: {avg_cpu:.2f}%")
            # else:
            #     print(f"  - EC2 {instance_id} - Avg CPU: {avg_cpu:.2f}% (OK)")

    return idle_instances

def analyze_unattached_ebs_volumes():
    """
    Identifies unattached EBS volumes.
    """
    print(f"\n--- Analyzing Unattached EBS Volumes ({AWS_REGION}) ---")
    unattached_volumes = []

    response = ec2_client.describe_volumes(
        Filters=[
            {'Name': 'status', 'Values': ['available']} # 'available' means not attached
        ]
    )

    for volume in response['Volumes']:
        volume_id = volume['VolumeId']
        volume_size = volume['Size'] # GB
        volume_type = volume['VolumeType']
        create_time = volume['CreateTime']

        # Ensure it's truly unattached (sometimes 'available' can briefly appear during transitions)
        if not volume.get('Attachments'):
            unattached_volumes.append({
                'ResourceID': volume_id,
                'Name': 'N/A', # EBS volumes don't have a 'Name' tag by default
                'Service': 'EBS',
                'Region': AWS_REGION,
                'Reason': f"Volume is unattached. Size: {volume_size} GB, Type: {volume_type}",
                'Action': f"Consider deleting volume '{volume_id}'.",
                'PotentialSavings': 'Estimate required'
            })
            print(f"  - UNATTACHED EBS: {volume_id} - {volume_size}GB {volume_type}")
    return unattached_volumes

def analyze_large_s3_buckets():
    """
    Identifies large S3 buckets that might warrant review.
    Note: Getting accurate size of S3 buckets can be complex without S3 Inventory or CloudWatch metrics for S3.
    This simplified version just lists buckets and assumes you'd investigate.
    """
    print(f"\n--- Analyzing Large S3 Buckets ({AWS_REGION}) ---")
    large_buckets = []
    
    response = s3_client.list_buckets()
    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        # This is a highly simplified way to get size, and can be slow/expensive for many objects.
        # For a more accurate size, you'd typically use S3 Inventory reports or CloudWatch metrics for S3.
        # This example just demonstrates iterating over objects.
        total_size_bytes = 0
        try:
            list_objects_response = s3_client.list_objects_v2(Bucket=bucket_name)
            while True:
                for obj in list_objects_response.get('Contents', []):
                    total_size_bytes += obj['Size']
                if not list_objects_response.get('IsTruncated'):
                    break
                list_objects_response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    ContinuationToken=list_objects_response['NextContinuationToken']
                )
            
            total_size_gb = total_size_bytes / (1024**3)
            if total_size_gb >= S3_LARGE_BUCKET_THRESHOLD_GB:
                large_buckets.append({
                    'ResourceID': bucket_name,
                    'Name': bucket_name,
                    'Service': 'S3',
                    'Region': AWS_REGION,
                    'Reason': f"Bucket size: {total_size_gb:.2f} GB (above {S3_LARGE_BUCKET_THRESHOLD_GB} GB threshold). Potential for old versions or incomplete uploads.",
                    'Action': f"Review S3 bucket '{bucket_name}' for lifecycle policies, old versions, or incomplete multipart uploads.",
                    'PotentialSavings': 'Estimate required'
                })
                print(f"  - LARGE S3: {bucket_name} - {total_size_gb:.2f} GB")

        except Exception as e:
            # S3 operations can fail due to permissions or bucket region mismatches
            print(f"  - WARNING: Could not access S3 bucket '{bucket_name}': {e}")
            pass # Skip if we can't access it

    return large_buckets

def analyze_idle_rds_instances():
    """
    Identifies idle RDS instances based on CPU utilization and connections.
    """
    print(f"\n--- Analyzing Idle RDS Instances ({AWS_REGION}) ---")
    idle_rds_instances = []

    response = rds_client.describe_db_instances()

    for db_instance in response['DBInstances']:
        db_instance_id = db_instance['DBInstanceIdentifier']
        db_instance_status = db_instance['DBInstanceStatus']
        
        # Only check instances that are available (running)
        if db_instance_status != 'available':
            continue

        # Get average CPU utilization
        avg_cpu = get_average_metric(
            namespace='AWS/RDS',
            metric_name='CPUUtilization',
            dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}],
            days_ago=IDLE_DAYS_THRESHOLD
        )
        
        # Get average database connections
        avg_connections = get_average_metric(
            namespace='AWS/RDS',
            metric_name='DatabaseConnections',
            dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}],
            days_ago=IDLE_DAYS_THRESHOLD,
            period_seconds=3600 # 1 hour period
        )

        is_idle_cpu = (avg_cpu is not None and avg_cpu < IDLE_CPU_THRESHOLD)
        is_idle_connections = (avg_connections is not None and avg_connections == 0)

        if is_idle_cpu and is_idle_connections:
            idle_rds_instances.append({
                'ResourceID': db_instance_id,
                'Name': db_instance_id,
                'Service': 'RDS',
                'Region': AWS_REGION,
                'Reason': f"Average CPU: {avg_cpu:.2f}% and Average Connections: {avg_connections:.0f} over {IDLE_DAYS_THRESHOLD} days.",
                'Action': f"Consider stopping or deleting RDS instance '{db_instance_id}'.",
                'PotentialSavings': 'Estimate required'
            })
            print(f"  - IDLE RDS: {db_instance_id} - Avg CPU: {avg_cpu:.2f}%, Avg Connections: {avg_connections:.0f}")
        # else:
        #     print(f"  - RDS {db_instance_id} - Avg CPU: {avg_cpu:.2f}%, Avg Connections: {avg_connections:.0f} (OK)")
    
    return idle_rds_instances


def analyze_underutilized_ec2_instances():
    """
    Identifies potentially underutilized EC2 instances that could be downsized.
    This is a more complex analysis. For a beginner, we'll focus on instances
    with consistently low-to-moderate CPU that are still running.
    """
    print(f"\n--- Analyzing Underutilized EC2 Instances ({AWS_REGION}) ---")
    underutilized_instances = []

    response = ec2_client.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            instance_name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
            
            # Skip if it's already flagged as idle
            # (A proper system would combine these checks better)
            # For simplicity, if CPU is very low, it's idle. If it's low-to-moderate, it's underutilized.
            
            avg_cpu = get_average_metric(
                namespace='AWS/EC2',
                metric_name='CPUUtilization',
                dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                days_ago=IDLE_DAYS_THRESHOLD
            )

            # Define a range for underutilization that's above idle but below optimal
            UNDERUTILIZED_CPU_LOW = IDLE_CPU_THRESHOLD
            UNDERUTILIZED_CPU_HIGH = 25.0 # Example: if CPU is consistently below 25%

            if avg_cpu is not None and UNDERUTILIZED_CPU_LOW < avg_cpu < UNDERUTILIZED_CPU_HIGH:
                underutilized_instances.append({
                    'ResourceID': instance_id,
                    'Name': instance_name,
                    'Service': 'EC2',
                    'Region': AWS_REGION,
                    'Reason': f"Average CPU utilization over {IDLE_DAYS_THRESHOLD} days: {avg_cpu:.2f}% (suggests downsizing from {instance_type}).",
                    'Action': f"Consider rightsizing instance '{instance_name}' ({instance_id}) from {instance_type} to a smaller type (e.g., from m5.large to m5.medium).",
                    'PotentialSavings': 'Estimate required'
                })
                print(f"  - UNDERUTILIZED EC2: {instance_name} ({instance_id}) - Avg CPU: {avg_cpu:.2f}% on {instance_type}")
    return underutilized_instances


def generate_report(findings):
    """
    Generates a human-readable report from the findings.
    """
    report_lines = ["# AWS Cost Optimization Report\n"]
    report_lines.append(f"**Generated On:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    report_lines.append(f"**Region:** {AWS_REGION}\n")
    
    if not findings:
        report_lines.append("## No cost-saving opportunities identified at this time. Great job!\n")
        return "\n".join(report_lines)

    report_lines.append("## Potential Cost-Saving Opportunities\n")
    report_lines.append("---")

    for finding in findings:
        report_lines.append(f"\n### {finding['Service']} - {finding['ResourceID']}")
        if finding['Name'] != 'N/A' and finding['Name'] != finding['ResourceID']:
            report_lines.append(f"**Name:** {finding['Name']}")
        report_lines.append(f"**Region:** {finding['Region']}")
        report_lines.append(f"**Reason:** {finding['Reason']}")
        report_lines.append(f"**Recommended Action:** {finding['Action']}")
        report_lines.append(f"**Estimated Savings:** {finding['PotentialSavings']}") # You'll replace this
        report_lines.append("---")
    
    report_lines.append("\n**Note:** Potential savings are placeholders and require a more sophisticated cost estimation model.")
    return "\n".join(report_lines)

def main():
    all_findings = []
    
    all_findings.extend(analyze_idle_ec2_instances())
    all_findings.extend(analyze_unattached_ebs_volumes())
    all_findings.extend(analyze_large_s3_buckets())
    all_findings.extend(analyze_idle_rds_instances())
    all_findings.extend(analyze_underutilized_ec2_instances())

    report_content = generate_report(all_findings)
    print("\n" + report_content)

    # Save report to a file
    with open('cost_optimization_report.md', 'w') as f:
        f.write(report_content)
    print("\nReport saved to cost_optimization_report.md")

if __name__ == "__main__":
    main()