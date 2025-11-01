# Cursor Ultra Plan Usage Analysis

This tool helps you determine if your Cursor Ultra plan is cost-effective based on your actual usage patterns.

## Quick Start

1. **Export your usage data from Cursor:**
   - Go to Cursor Settings ? Account/Billing
   - Look for "Usage" or "Export Usage Data" option
   - Export data for the last 2 months as JSON

2. **Run the analysis:**
   ```bash
   python analyze_ultra_plan_usage.py --data your_usage_data.json
   ```

3. **View the sample data structure:**
   ```bash
   python analyze_ultra_plan_usage.py --sample
   ```

## What the Analysis Shows

- **Total Requests**: Count of all requests made in the analysis period
- **Daily/Monthly Averages**: Your average usage patterns
- **Peak Usage Days**: Days with highest usage
- **Usage by Feature**: Breakdown of which features you use most
- **Cost Recommendation**: Whether Ultra plan is worth it or if you should downgrade
- **Potential Savings**: How much you could save by switching plans

## How to Get Your Usage Data

### Option 1: Cursor Dashboard
1. Log into your Cursor account at cursor.sh
2. Navigate to Settings ? Billing
3. Look for "Usage Statistics" or "Export Data"
4. Download your usage data as JSON

### Option 2: Cursor API (if available)
```bash
# Example API call (endpoint may vary)
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.cursor.sh/v1/usage?months=2 > usage_data.json
```

### Option 3: Manual Data Collection
If you have access to usage logs, format them as:
```json
{
  "usage": [
    {
      "date": "2024-01-15",
      "count": 150,
      "feature": "code_completion"
    },
    {
      "date": "2024-01-16",
      "count": 200,
      "feature": "chat"
    }
  ]
}
```

## Plan Comparison

The script compares your usage against typical plan limits:

- **Free Plan**: ~500 requests/month
- **Pro Plan**: ~5,000 requests/month  
- **Ultra Plan**: ~50,000 requests/month

**Note**: Update the pricing and limits in `analyze_ultra_plan_usage.py` if they differ from Cursor's current offerings.

## Recommendations

The script will recommend:
- **Keep Ultra**: If your usage exceeds Pro limits or you use Ultra-only features
- **Switch to Pro**: If your usage is within Pro limits, saving you money
- **Risk Assessment**: Low/Medium/High risk of hitting limits if downgrading

## Troubleshooting

If you get an error about data structure:
1. Check the sample format: `python analyze_ultra_plan_usage.py --sample`
2. Ensure your JSON has one of these keys: `usage`, `requests`, or `events`
3. Each entry should have a `date`/`timestamp` field and a `count` field
