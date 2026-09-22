import os
import boto3
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


# AWS CloudWatch
cloudwatch = boto3.client(
    "cloudwatch",
    region_name="us-east-1"
)

# UAE timezone
DUBAI = ZoneInfo("Asia/Dubai")


def monitor_traffic(period):
    """
    Check CloudFront traffic for either:

    afternoon = 1 PM - 2 PM UAE
    evening   = 6 PM - 7 PM UAE
    """

    # Get today's date in UAE
    now_local = datetime.now(timezone.utc).astimezone(DUBAI)

    # Decide which one-hour window to check
    if period == "afternoon":
        end_local = now_local.replace(
            hour=14,
            minute=0,
            second=0,
            microsecond=0
        )

        window_name = "1 PM - 2 PM"

    elif period == "evening":
        end_local = now_local.replace(
            hour=19,
            minute=0,
            second=0,
            microsecond=0
        )

        window_name = "6 PM - 7 PM"

    else:
        raise ValueError(
            "PERIOD must be 'afternoon' or 'evening'"
        )

    # One hour before the ending time
    start_local = end_local - timedelta(hours=1)

    # Convert UAE time → UTC
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)

    distribution_id = os.environ["DISTRIBUTION_ID"]

    print("========================================")
    print("CarryAura Traffic Monitor")
    print("========================================")
    print(f"Window: {window_name} UAE time")
    print(f"Distribution: {distribution_id}")
    print(f"Start: {start_local}")
    print(f"End:   {end_local}")
    print("========================================")

    # Ask CloudWatch for CloudFront requests
    response = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                "Id": "requests",

                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/CloudFront",
                        "MetricName": "Requests",

                        "Dimensions": [
                            {
                                "Name": "DistributionId",
                                "Value": distribution_id
                            },
                            {
                                "Name": "Region",
                                "Value": "Global"
                            }
                        ]
                    },

                    # 5 minutes
                    "Period": 300,

                    "Stat": "Sum"
                },

                "ReturnData": True
            }
        ],

        StartTime=start_utc,
        EndTime=end_utc,

        ScanBy="TimestampAscending"
    )

    results = response["MetricDataResults"][0]

    timestamps = results.get("Timestamps", [])
    values = results.get("Values", [])

    points = sorted(
        zip(timestamps, values),
        key=lambda x: x[0]
    )

    if not points:
        print("")
        print("⚠️ No CloudFront request data was returned.")
        print("CloudFront data may have a short delay.")
        print("")

        return {
            "status": "no_data"
        }

    # Variables for our report
    busiest_time = None
    busiest_requests = -1
    total_requests = 0

    print("")
    print("5-MINUTE TRAFFIC")
    print("----------------------------------------")

    for timestamp, value in points:

        local_time = timestamp.astimezone(DUBAI)

        value = value or 0

        total_requests += value

        period_end = local_time + timedelta(minutes=5)

        print(
            f"{local_time.strftime('%H:%M')} - "
            f"{period_end.strftime('%H:%M')}: "
            f"{int(value)} requests"
        )

        # Find busiest 5-minute period
        if value > busiest_requests:
            busiest_requests = value
            busiest_time = local_time

    print("")
    print("----------------------------------------")
    print(f"Total requests: {int(total_requests)}")

    if busiest_time is not None:

        busiest_end = busiest_time + timedelta(minutes=5)

        print(
            "BUSIEST 5-MINUTE PERIOD: "
            f"{busiest_time.strftime('%H:%M')} - "
            f"{busiest_end.strftime('%H:%M')} UAE"
        )

        print(
            f"Requests in busiest period: "
            f"{int(busiest_requests)}"
        )

    print("----------------------------------------")
    print(
        "NOTE: CloudFront Requests are requests, "
        "not unique visitors."
    )
    print("========================================")

    return {
        "status": "ok",
        "window": window_name,
        "total_requests": int(total_requests),
        "busiest_5_minute_requests": int(busiest_requests),
        "busiest_5_minute_start": (
            busiest_time.isoformat()
            if busiest_time
            else None
        )
    }


if __name__ == "__main__":

    period = os.environ.get(
        "PERIOD",
        "afternoon"
    )

    monitor_traffic(period)
