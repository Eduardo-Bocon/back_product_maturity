import asyncio
import os
from dotenv import load_dotenv
from services.uptime_robot import get_monitor_uptime, get_product_uptime, get_product_response_times

load_dotenv()

async def test_uptime_robot_integration():
    """Test UptimeRobot integration"""
    
    print("=== Testing UptimeRobot Integration ===\n")
    
    # Check if environment variables are set
    api_key = os.getenv("UPTIMEROBOT_API_KEY")
    
    print("Environment Variables:")
    print(f"UPTIMEROBOT_API_KEY: {'[OK] Set' if api_key else '[X] Missing'}")
    print()
    
    if not api_key:
        print("[X] Missing required environment variable. Please set:")
        print("   - UPTIMEROBOT_API_KEY (your UptimeRobot API key)")
        print("   Get it from: https://uptimerobot.com/dashboard#mySettings")
        return
    
    # Test product URLs
    test_products = ["chorus"]
   
    
    print("=== Testing Product Uptime ===")
    for product_id in test_products:
        
        print(f"Testing product: {product_id}")
        
        try:
            uptime = await get_product_uptime(product_id)
            if uptime is not None:
                print(f"[OK] {product_id} uptime: {uptime}%")
                
                # Categorize uptime status
                if uptime >= 99.5:
                    status = "EXCELLENT"
                elif uptime >= 99.0:
                    status = "GOOD"
                elif uptime >= 95.0:
                    status = "FAIR"
                else:
                    status = "POOR"
                print(f"     Status: {status}")
            else:
                
                print(f"[INFO] No monitor found for {product_id} or API error")
        except Exception as e:
            print(f"[X] Error getting uptime for {product_id}: {e}")
        
        print()
    
    print("=== Testing Response Times/Latency ===")
    for product_id in test_products:
        print(f"Testing response times for: {product_id}")
        
        try:
            response_data = await get_product_response_times(product_id)
            if response_data:
                print(f"[OK] Response time data for {product_id}:")
                print(f"     Average: {response_data['average_ms']}ms")
                print(f"     Min: {response_data['min_ms']}ms")
                print(f"     Max: {response_data['max_ms']}ms")
                print(f"     P95: {response_data['p95_ms']}ms")
                print(f"     P99: {response_data['p99_ms']}ms")
                print(f"     Sample count: {response_data['sample_count']}")
                
                # Categorize latency performance
                avg_ms = response_data['average_ms']
                p95_ms = response_data['p95_ms']
                
                if avg_ms < 100:
                    perf = "EXCELLENT"
                elif avg_ms < 300:
                    perf = "GOOD"
                elif avg_ms < 1000:
                    perf = "FAIR"
                else:
                    perf = "POOR"
                    
                print(f"     Performance: {perf}")
                
                # Show potential criteria
                criteria_checks = {
                    "Fast avg (<200ms)": avg_ms < 200,
                    "Acceptable avg (<500ms)": avg_ms < 500,
                    "Fast P95 (<300ms)": p95_ms < 300,
                    "Acceptable P95 (<1000ms)": p95_ms < 1000
                }
                
                print("     Potential criteria:")
                for criteria, passed in criteria_checks.items():
                    status = "✅" if passed else "❌"
                    print(f"       {status} {criteria}")
                    
            else:
                print(f"[INFO] No response time data available for {product_id}")
        except Exception as e:
            print(f"[X] Error getting response times for {product_id}: {e}")
        
        print()
    
    print("=== Testing Direct URL Monitoring ===")
    # Test with specific URLs (you can modify these)
    test_urls = [
        "https://chorus.dooor.ai/",
    ]
    
    for url in test_urls:
        print(f"Testing URL: {url}")
        
        try:
            uptime = await get_monitor_uptime(url)
            if uptime is not None:
                print(f"[OK] Uptime: {uptime}%")
                
                # Check if uptime meets criteria
                criteria_checks = {
                    "99%+ uptime": uptime >= 99.0,
                    "95%+ uptime": uptime >= 95.0,
                    "90%+ uptime": uptime >= 90.0
                }
                
                print("     Criteria checks:")
                for criteria, passed in criteria_checks.items():
                    status = "✅" if passed else "❌"
                    print(f"       {status} {criteria}")
            else:
                print(f"[INFO] No monitor found for {url} or API error")
        except Exception as e:
            print(f"[X] Error getting uptime for {url}: {e}")
        
        print()
    
    print("=== Integration Test with Main Application ===")
    print("Testing how uptime and latency data would integrate with product evaluation...")
    
    for product_id in test_products:  # Test all products
        print(f"Product: {product_id}")
        
        try:
            # Get both uptime and response time data
            uptime = await get_product_uptime(product_id)
            response_data = await get_product_response_times(product_id)
            
            if uptime is not None:
                # Simulate integration with main.py criteria
                uptime_criteria = {
                    "uptime_excellent": uptime >= 99.5,  # ✅ if >= 99.5%
                    "uptime_good": uptime >= 99.0,       # ✅ if >= 99.0%
                    "uptime_acceptable": uptime >= 95.0   # ✅ if >= 95.0%
                }
                
                print(f"  Uptime: {uptime}%")
                print("  Uptime criteria:")
                for criteria, passed in uptime_criteria.items():
                    emoji = "✅" if passed else "❌"
                    print(f"    {emoji} {criteria}")
            else:
                print(f"  [INFO] No uptime data available")
            
            if response_data:
                # Simulate latency criteria
                avg_ms = response_data['average_ms']
                p95_ms = response_data['p95_ms']
                
                latency_criteria = {
                    "latency_fast_avg": avg_ms < 200,     # ✅ if avg < 200ms
                    "latency_good_avg": avg_ms < 500,     # ✅ if avg < 500ms
                    "latency_fast_p95": p95_ms < 300,     # ✅ if P95 < 300ms
                    "latency_good_p95": p95_ms < 1000     # ✅ if P95 < 1000ms
                }
                
                print(f"  Response times: Avg={avg_ms}ms, P95={p95_ms}ms")
                print("  Latency criteria:")
                for criteria, passed in latency_criteria.items():
                    emoji = "✅" if passed else "❌"
                    print(f"    {emoji} {criteria}")
                    
                # Suggest which criteria to use
                if avg_ms < 200 and p95_ms < 300:
                    suggestion = "latency_fast (avg<200ms, P95<300ms)"
                elif avg_ms < 500 and p95_ms < 1000:
                    suggestion = "latency_good (avg<500ms, P95<1000ms)"
                else:
                    suggestion = "latency_acceptable (needs improvement)"
                
                print(f"  💡 Suggested latency criteria: {suggestion}")
            else:
                print(f"  [INFO] No latency data available")
                
        except Exception as e:
            print(f"  [X] Error: {e}")
        
        print()
    
    print("=== Test Complete ===")
    print("\n💡 Next Steps:")
    print("1. Add UPTIMEROBOT_API_KEY to your .env file")
    print("2. Ensure your products are monitored in UptimeRobot with friendly names")
    print("3. Import and integrate uptime/latency checks in main.py")
    print("   Example: from services.uptime_robot import get_product_uptime, get_product_response_times")
    print("4. Add latency criteria to your product maturity evaluation")
    print("   Example: 'latency_fast': response_times and response_times['p95_ms'] < 300")

if __name__ == "__main__":
    asyncio.run(test_uptime_robot_integration())