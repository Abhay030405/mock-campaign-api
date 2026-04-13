import json
from datetime import datetime, timedelta, timezone

import requests

# Configuration
BASE_URL = "http://localhost:8000"  # Change to Render URL when deployed


def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())


def test_get_customers():
    """Test getting customer cohort"""
    response = requests.get(f"{BASE_URL}/api/customers", params={"limit": 5})
    customers = response.json()
    print(f"\nFetched {len(customers)} customers (sample)")
    if customers:
        print("First customer:", json.dumps(customers[0], indent=2))
    return [c["customer_id"] for c in customers[:10]]


def test_customer_count():
    """Test customer count endpoint"""
    response = requests.get(f"{BASE_URL}/api/customers/count")
    print("\nCustomer Count:", response.json())


def test_validate_ids(customer_ids):
    """Test customer ID validation"""
    payload = {"customer_ids": customer_ids + ["FAKE_ID_999"]}
    response = requests.post(f"{BASE_URL}/api/customers/validate", json=payload)
    print("\nValidation:", response.json())


def test_schedule_campaign(customer_ids):
    """Test scheduling a campaign"""
    payload = {
        "customer_ids": customer_ids,
        "subject": "\U0001f389 Exclusive Offer: XDeposit - Higher Returns Await!",
        "body": (
            "Dear Valued Customer,\n\n"
            "Discover <b>XDeposit</b>, our flagship term deposit product offering "
            "<b>1% higher returns</b> than competitors!\n\n"
            "\U0001f31f Special Bonus: Female senior citizens get an additional 0.25% boost!\n\n"
            "Click here to explore: https://superbfsi.com/xdeposit/explore/\n\n"
            "Limited time offer - Act now! \U0001f4b0\n\n"
            "Best regards,\nSuperBFSI Team"
        ),
        "scheduled_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "segment_name": "test_segment",
        "variant_id": "var_test_1",
    }

    response = requests.post(f"{BASE_URL}/api/campaigns/schedule", json=payload)
    result = response.json()
    print("\nCampaign Scheduled:", json.dumps(result, indent=2))
    return result["campaign_id"]


def test_get_metrics(campaign_id):
    """Test getting campaign metrics"""
    response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}/metrics")
    metrics = response.json()
    print("\nCampaign Metrics:", json.dumps(metrics, indent=2))
    print(f"\n  Performance Summary:")
    print(f"   Open Rate: {metrics['open_rate']*100:.2f}%")
    print(f"   Click Rate: {metrics['click_rate']*100:.2f}%")
    print(f"   Click-Through Rate: {metrics['click_through_rate']*100:.2f}%")
    print(f"   Total Sent: {metrics['total_sent']}")


def test_get_campaign_details(campaign_id):
    """Test getting campaign details"""
    response = requests.get(f"{BASE_URL}/api/campaigns/{campaign_id}")
    details = response.json()
    print("\nCampaign Details:", json.dumps(details, indent=2))


def test_get_results(campaign_id):
    """Test getting individual results"""
    response = requests.get(
        f"{BASE_URL}/api/campaigns/{campaign_id}/results", params={"limit": 5}
    )
    results = response.json()
    print(f"\nIndividual Results (first {len(results)}):")
    for r in results:
        status = "opened" if r["opened"] else "not opened"
        click = " + clicked" if r["clicked"] else ""
        print(f"   {r['customer_id']}: {status}{click} (open_prob={r['open_probability']:.2f})")


if __name__ == "__main__":
    print("Testing Mock Campaign API\n")
    print("=" * 50)

    test_health()
    customer_ids = test_get_customers()
    test_customer_count()

    if customer_ids:
        test_validate_ids(customer_ids)
        campaign_id = test_schedule_campaign(customer_ids)
        test_get_metrics(campaign_id)
        test_get_campaign_details(campaign_id)
        test_get_results(campaign_id)
    else:
        print("\nNo customers loaded — skipping campaign tests.")
        print("Make sure customers.csv is in app/database/")

    print("\n" + "=" * 50)
    print("All tests completed!")
