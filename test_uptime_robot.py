import asyncio
import os
from dotenv import load_dotenv
from services.uptime_robot import get_monitor_uptime, get_product_uptime

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
    print("Testing how uptime data would integrate with product evaluation...")
    
    for product_id in test_products[:2]:  # Test first 2 products
        print(f"Product: {product_id}")
        
        try:
            uptime = await get_product_uptime(product_id)
            
            if uptime is not None:
                # Simulate integration with main.py criteria
                uptime_criteria = {
                    "uptime_excellent": uptime >= 99.5,  # ✅ if >= 99.5%
                    "uptime_good": uptime >= 99.0,       # ✅ if >= 99.0%
                    "uptime_acceptable": uptime >= 95.0   # ✅ if >= 95.0%
                }
                
                print(f"  Uptime: {uptime}%")
                print("  Potential criteria:")
                for criteria, passed in uptime_criteria.items():
                    emoji = "✅" if passed else "❌"
                    print(f"    {emoji} {criteria}")
                
                # Suggest which criteria to use in main.py
                if uptime >= 99.5:
                    suggestion = "uptime_excellent (99.5%+)"
                elif uptime >= 99.0:
                    suggestion = "uptime_good (99.0%+)"
                else:
                    suggestion = "uptime_acceptable (95.0%+)"
                
                print(f"  💡 Suggested criteria for main.py: {suggestion}")
            else:
                print(f"  [INFO] No uptime data available")
        except Exception as e:
            print(f"  [X] Error: {e}")
        
        print()
    
    print("=== Test Complete ===")
    print("\n💡 Next Steps:")
    print("1. Add UPTIMEROBOT_API_KEY to your .env file")
    print("2. Ensure your staging URLs are monitored in UptimeRobot")
    print("3. Import and integrate uptime checks in main.py")
    print("   Example: from services.uptime_robot import get_product_uptime")

if __name__ == "__main__":
    asyncio.run(test_uptime_robot_integration())