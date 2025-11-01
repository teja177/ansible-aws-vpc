#!/usr/bin/env python3
"""
Cursor Ultra Plan Usage Analysis Tool

This script analyzes your Cursor usage data to determine if the Ultra plan
is cost-effective based on your actual usage patterns.

Usage:
    python analyze_ultra_plan_usage.py --data usage_data.json
    or
    python analyze_ultra_plan_usage.py --help
"""

import json
import argparse
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

# Plan pricing (update these with current Cursor pricing)
PLAN_PRICING = {
    "free": {"monthly": 0, "name": "Free"},
    "pro": {"monthly": 20, "name": "Pro"},  # Example pricing
    "ultra": {"monthly": 42, "name": "Ultra"},  # Example pricing
}

# Typical usage limits (update these with actual Cursor limits)
PLAN_LIMITS = {
    "free": {
        "requests_per_month": 500,
        "features": ["basic_ai", "limited_context"]
    },
    "pro": {
        "requests_per_month": 5000,
        "features": ["advanced_ai", "larger_context", "priority_support"]
    },
    "ultra": {
        "requests_per_month": 50000,
        "features": ["ultra_ai", "unlimited_context", "priority_support", "advanced_features"]
    }
}


def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats."""
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date: {date_str}")


def analyze_usage_data(data: Dict, months: int = 2) -> Dict:
    """Analyze usage data for the specified number of months."""
    cutoff_date = datetime.now() - timedelta(days=30 * months)
    
    results = {
        "total_requests": 0,
        "daily_average": 0,
        "monthly_average": 0,
        "peak_days": [],
        "usage_by_feature": defaultdict(int),
        "dates_analyzed": [],
        "recommendations": []
    }
    
    # Extract usage entries
    usage_entries = data.get("usage", [])
    if not usage_entries:
        usage_entries = data.get("requests", [])
    if not usage_entries:
        usage_entries = data.get("events", [])
    
    if not usage_entries:
        return {
            "error": "No usage data found. Expected keys: 'usage', 'requests', or 'events'",
            "data_structure": list(data.keys())
        }
    
    # Filter by date
    recent_usage = []
    for entry in usage_entries:
        entry_date_str = entry.get("date") or entry.get("timestamp") or entry.get("time")
        if not entry_date_str:
            continue
        
        try:
            entry_date = parse_date(entry_date_str)
            if entry_date >= cutoff_date:
                recent_usage.append(entry)
                results["total_requests"] += entry.get("count", 1)
                
                # Track feature usage
                feature = entry.get("feature") or entry.get("type") or "unknown"
                results["usage_by_feature"][feature] += entry.get("count", 1)
                
                # Track dates
                date_key = entry_date.strftime("%Y-%m-%d")
                if date_key not in results["dates_analyzed"]:
                    results["dates_analyzed"].append(date_key)
        except ValueError:
            continue
    
    # Calculate averages
    days_analyzed = len(results["dates_analyzed"])
    if days_analyzed > 0:
        results["daily_average"] = results["total_requests"] / days_analyzed
        results["monthly_average"] = results["daily_average"] * 30
    
    # Find peak days
    daily_counts = defaultdict(int)
    for entry in recent_usage:
        entry_date_str = entry.get("date") or entry.get("timestamp") or entry.get("time")
        if entry_date_str:
            try:
                entry_date = parse_date(entry_date_str)
                date_key = entry_date.strftime("%Y-%m-%d")
                daily_counts[date_key] += entry.get("count", 1)
            except ValueError:
                continue
    
    if daily_counts:
        sorted_days = sorted(daily_counts.items(), key=lambda x: x[1], reverse=True)
        results["peak_days"] = sorted_days[:5]
    
    return results


def recommend_plan(analysis: Dict) -> Dict:
    """Recommend the best plan based on usage analysis."""
    monthly_avg = analysis.get("monthly_average", 0)
    total_requests = analysis.get("total_requests", 0)
    
    recommendations = {
        "current_plan": "ultra",
        "recommended_plan": None,
        "monthly_cost": PLAN_PRICING["ultra"]["monthly"],
        "recommended_cost": None,
        "potential_savings": None,
        "reasoning": [],
        "risk_assessment": None
    }
    
    # Calculate recommendation based on usage
    ultra_limit = PLAN_LIMITS["ultra"]["requests_per_month"]
    pro_limit = PLAN_LIMITS["pro"]["requests_per_month"]
    
    if monthly_avg <= pro_limit * 0.8:  # Using less than 80% of Pro limit
        recommendations["recommended_plan"] = "pro"
        recommendations["recommended_cost"] = PLAN_PRICING["pro"]["monthly"]
        recommendations["potential_savings"] = PLAN_PRICING["ultra"]["monthly"] - PLAN_PRICING["pro"]["monthly"]
        recommendations["reasoning"].append(
            f"Average monthly usage ({monthly_avg:.0f} requests) is well below Pro plan limit ({pro_limit} requests)"
        )
        recommendations["risk_assessment"] = "low"
    elif monthly_avg <= ultra_limit * 0.6:  # Using less than 60% of Ultra limit
        recommendations["recommended_plan"] = "pro"
        recommendations["recommended_cost"] = PLAN_PRICING["pro"]["monthly"]
        recommendations["potential_savings"] = PLAN_PRICING["ultra"]["monthly"] - PLAN_PRICING["pro"]["monthly"]
        recommendations["reasoning"].append(
            f"Average monthly usage ({monthly_avg:.0f} requests) is below Pro plan limit ({pro_limit} requests)"
        )
        recommendations["risk_assessment"] = "medium"
    else:
        recommendations["recommended_plan"] = "ultra"
        recommendations["recommended_cost"] = PLAN_PRICING["ultra"]["monthly"]
        recommendations["potential_savings"] = 0
        recommendations["reasoning"].append(
            f"Average monthly usage ({monthly_avg:.0f} requests) exceeds Pro plan limit ({pro_limit} requests)"
        )
        recommendations["risk_assessment"] = "high"
    
    # Check feature usage
    features_used = list(analysis.get("usage_by_feature", {}).keys())
    ultra_features = PLAN_LIMITS["ultra"]["features"]
    pro_features = PLAN_LIMITS["pro"]["features"]
    
    ultra_only_features = set(ultra_features) - set(pro_features)
    if ultra_only_features:
        recommendations["reasoning"].append(
            f"Ultra-only features available: {', '.join(ultra_only_features)}"
        )
    
    return recommendations


def print_report(analysis: Dict, recommendations: Dict):
    """Print a formatted usage report."""
    print("\n" + "="*70)
    print("CURSOR ULTRA PLAN USAGE ANALYSIS")
    print("="*70)
    
    if "error" in analysis:
        print(f"\n? Error: {analysis['error']}")
        print(f"Data structure keys found: {', '.join(analysis.get('data_structure', []))}")
        return
    
    print(f"\n?? USAGE STATISTICS (Last 2 Months)")
    print(f"{'?'*70}")
    print(f"Total Requests:        {analysis['total_requests']:,}")
    print(f"Days Analyzed:         {len(analysis['dates_analyzed'])}")
    print(f"Daily Average:         {analysis['daily_average']:.1f} requests/day")
    print(f"Monthly Average:       {analysis['monthly_average']:.0f} requests/month")
    
    if analysis['peak_days']:
        print(f"\n?? Peak Usage Days:")
        for date, count in analysis['peak_days']:
            print(f"  {date}: {count:,} requests")
    
    if analysis['usage_by_feature']:
        print(f"\n?? Usage by Feature:")
        sorted_features = sorted(analysis['usage_by_feature'].items(), 
                                key=lambda x: x[1], reverse=True)
        for feature, count in sorted_features[:10]:
            print(f"  {feature}: {count:,} requests")
    
    print(f"\n?? COST ANALYSIS")
    print(f"{'?'*70}")
    print(f"Current Plan:          {recommendations['current_plan'].upper()}")
    print(f"Monthly Cost:          ${recommendations['monthly_cost']:.2f}")
    
    if recommendations['recommended_plan'] != recommendations['current_plan']:
        print(f"\n? RECOMMENDATION: Switch to {recommendations['recommended_plan'].upper()} plan")
        print(f"Recommended Cost:     ${recommendations['recommended_cost']:.2f}")
        print(f"Potential Savings:     ${recommendations['potential_savings']:.2f}/month")
        print(f"                      ${recommendations['potential_savings'] * 12:.2f}/year")
        print(f"Risk Assessment:       {recommendations['risk_assessment'].upper()}")
    else:
        print(f"\n? RECOMMENDATION: Keep ULTRA plan")
        print(f"Your usage justifies the Ultra plan")
    
    print(f"\n?? REASONING")
    print(f"{'?'*70}")
    for reason in recommendations['reasoning']:
        print(f"  ? {reason}")
    
    print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Cursor Ultra Plan usage to determine cost-effectiveness"
    )
    parser.add_argument(
        "--data",
        type=str,
        help="Path to JSON file containing usage data"
    )
    parser.add_argument(
        "--months",
        type=int,
        default=2,
        help="Number of months to analyze (default: 2)"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Generate sample data structure for reference"
    )
    
    args = parser.parse_args()
    
    if args.sample:
        sample_data = {
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
        print("Sample data structure:")
        print(json.dumps(sample_data, indent=2))
        return
    
    if not args.data:
        print("Error: --data argument required")
        print("\nTo get your usage data:")
        print("1. Go to Cursor Settings > Account/Billing")
        print("2. Look for 'Usage' or 'Export Usage Data' option")
        print("3. Export your usage data as JSON")
        print("\nOr use --sample to see expected data format")
        sys.exit(1)
    
    try:
        with open(args.data, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{args.data}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.data}': {e}")
        sys.exit(1)
    
    analysis = analyze_usage_data(data, args.months)
    recommendations = recommend_plan(analysis)
    print_report(analysis, recommendations)


if __name__ == "__main__":
    main()
