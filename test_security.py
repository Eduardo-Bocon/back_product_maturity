import asyncio
import os
from services.security import (
    check_security_headers, 
    check_security_headers_detailed, 
    check_product_security, 
    check_product_security_detailed
)

async def test_security_integration():
    """Test Security Headers integration"""
    
    print("=== Testing Security Headers Integration ===\n")
    
    # Test products
    test_products = ["chorus"]
    
    print("=== Testing Product Security (Basic) ===")
    for product_id in test_products:
        print(f"Testing security for: {product_id}")
        
        try:
            security_passed = await check_product_security(product_id)
            if security_passed:
                print(f"[OK] {product_id} has all essential security headers ✅")
            else:
                print(f"[WARNING] {product_id} is missing essential security headers ❌")
        except Exception as e:
            print(f"[X] Error checking security for {product_id}: {e}")
        
        print()
    
    print("=== Testing Product Security (Detailed) ===")
    for product_id in test_products:
        print(f"Detailed security analysis for: {product_id}")
        
        try:
            security_data = await check_product_security_detailed(product_id)
            if security_data:
                summary = security_data['summary']
                print(f"[OK] Security report for {product_id}:")
                print(f"     URL: {security_data['url']}")
                print(f"     Status Code: {security_data['status_code']}")
                print(f"     Security Score: {summary['security_score']}%")
                print(f"     Headers Present: {summary['headers_present']}/{summary['total_headers_checked']}")
                print(f"     Essential Headers: {summary['essential_headers_present']}/{summary['essential_headers_total']}")
                print(f"     Essential Security Passed: {'✅' if summary['essential_security_passed'] else '❌'}")
                
                print("     Header Details:")
                for header_name, header_info in security_data['headers'].items():
                    status = "✅" if header_info['present'] else "❌"
                    if header_info['present']:
                        print(f"       {status} {header_name}: {header_info['value']}")
                    else:
                        print(f"       {status} {header_name}: MISSING")
                
                # Categorize security level
                score = summary['security_score']
                if score >= 90:
                    level = "EXCELLENT"
                elif score >= 70:
                    level = "GOOD"
                elif score >= 50:
                    level = "FAIR"
                else:
                    level = "POOR"
                
                print(f"     Security Level: {level}")
                
            else:
                print(f"[INFO] Could not retrieve security data for {product_id}")
        except Exception as e:
            print(f"[X] Error getting detailed security for {product_id}: {e}")
        
        print()
    
    print("=== Testing Direct URL Security ===")
    # Test with direct URLs
    test_urls = [
        "https://chorus.dooor.ai/",
        "https://google.com",  # For comparison - should have good security
        "https://httpbin.org/get"  # For comparison - might have basic security
    ]
    
    for url in test_urls:
        print(f"Testing URL: {url}")
        
        try:
            # Basic check
            basic_result = await check_security_headers(url)
            print(f"  Basic security check: {'✅ PASS' if basic_result else '❌ FAIL'}")
            
            # Detailed check
            detailed_result = await check_security_headers_detailed(url)
            if detailed_result:
                summary = detailed_result['summary']
                print(f"  Security score: {summary['security_score']}%")
                print(f"  Essential headers: {'✅ PASS' if summary['essential_security_passed'] else '❌ FAIL'}")
                
                # Show which essential headers are missing
                essential_headers = ["Strict-Transport-Security", "X-Content-Type-Options", "X-Frame-Options"]
                missing_essential = []
                for header in essential_headers:
                    if not detailed_result['headers'][header]['present']:
                        missing_essential.append(header)
                
                if missing_essential:
                    print(f"  Missing essential: {', '.join(missing_essential)}")
                else:
                    print(f"  All essential headers present!")
                    
        except Exception as e:
            print(f"  [X] Error: {e}")
        
        print()
    
    print("=== Integration Test with Main Application ===")
    print("Testing how security data would integrate with product evaluation...")
    
    for product_id in test_products:
        print(f"Product: {product_id}")
        
        try:
            # Get security data (same as main.py)
            security_headers = await check_product_security(product_id)
            detailed_security = await check_product_security_detailed(product_id)
            
            print(f"  Security headers check: {'✅' if security_headers else '❌'}")
            
            if detailed_security:
                summary = detailed_security['summary']
                
                # Simulate potential criteria for main.py
                security_criteria = {
                    "security_essential": summary['essential_security_passed'],
                    "security_good": summary['security_score'] >= 70,
                    "security_excellent": summary['security_score'] >= 90
                }
                
                print("  Potential security criteria:")
                for criteria, passed in security_criteria.items():
                    emoji = "✅" if passed else "❌"
                    print(f"    {emoji} {criteria}")
                
                # Current main.py criteria
                print(f"  Current main.py criteria (security_headers): {'✅' if security_headers else '❌'}")
                
                # Recommendations
                if not summary['essential_security_passed']:
                    missing = []
                    essential = ["Strict-Transport-Security", "X-Content-Type-Options", "X-Frame-Options"]
                    for header in essential:
                        if not detailed_security['headers'][header]['present']:
                            missing.append(header)
                    print(f"  💡 Recommendation: Add missing headers: {', '.join(missing)}")
                else:
                    print(f"  💡 Security looks good! Consider adding CSP for extra protection.")
                    
        except Exception as e:
            print(f"  [X] Error: {e}")
        
        print()
    
    print("=== Test Complete ===")
    print("\n💡 Next Steps:")
    print("1. Review security headers for products that failed")
    print("2. Configure missing security headers on your web servers")
    print("3. Common security headers to add:")
    print("   - Strict-Transport-Security: max-age=31536000; includeSubDomains")
    print("   - X-Content-Type-Options: nosniff")
    print("   - X-Frame-Options: DENY")
    print("   - Content-Security-Policy: default-src 'self'")
    print("4. Security headers are now part of your product maturity score!")

if __name__ == "__main__":
    asyncio.run(test_security_integration())