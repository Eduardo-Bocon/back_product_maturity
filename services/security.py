import httpx
import asyncio
from typing import Dict, Optional, List

async def check_security_headers(url: str) -> bool:
    """
    Check if essential security headers are present
    
    Args:
        url: The URL to check
    
    Returns:
        True if all essential security headers are present
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            headers = resp.headers

            required_headers = [
                "Strict-Transport-Security",
                "X-Content-Type-Options", 
                "X-Frame-Options"
            ]

            return all(h in headers for h in required_headers)
    except Exception as e:
        print(f"Error checking security headers for {url}: {e}")
        return False

async def check_security_headers_detailed(url: str) -> Optional[Dict]:
    """
    Get detailed security header information
    
    Args:
        url: The URL to check
    
    Returns:
        Dictionary with security header status and details
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            headers = resp.headers

            security_headers = {
                "Strict-Transport-Security": {
                    "present": "Strict-Transport-Security" in headers,
                    "value": headers.get("Strict-Transport-Security", ""),
                    "description": "Enforces HTTPS connections"
                },
                "X-Content-Type-Options": {
                    "present": "X-Content-Type-Options" in headers,
                    "value": headers.get("X-Content-Type-Options", ""),
                    "description": "Prevents MIME type sniffing"
                },
                "X-Frame-Options": {
                    "present": "X-Frame-Options" in headers,
                    "value": headers.get("X-Frame-Options", ""),
                    "description": "Prevents clickjacking attacks"
                },
                "Content-Security-Policy": {
                    "present": "Content-Security-Policy" in headers,
                    "value": headers.get("Content-Security-Policy", ""),
                    "description": "Controls resource loading"
                },
                "X-XSS-Protection": {
                    "present": "X-XSS-Protection" in headers,
                    "value": headers.get("X-XSS-Protection", ""),
                    "description": "XSS attack protection"
                },
                "Referrer-Policy": {
                    "present": "Referrer-Policy" in headers,
                    "value": headers.get("Referrer-Policy", ""),
                    "description": "Controls referrer information"
                }
            }

            # Calculate security score
            total_headers = len(security_headers)
            present_headers = sum(1 for h in security_headers.values() if h["present"])
            essential_headers = ["Strict-Transport-Security", "X-Content-Type-Options", "X-Frame-Options"]
            essential_present = sum(1 for name in essential_headers if security_headers[name]["present"])

            result = {
                "url": url,
                "status_code": resp.status_code,
                "headers": security_headers,
                "summary": {
                    "total_headers_checked": total_headers,
                    "headers_present": present_headers,
                    "essential_headers_present": essential_present,
                    "essential_headers_total": len(essential_headers),
                    "security_score": round((present_headers / total_headers) * 100, 1),
                    "essential_security_passed": essential_present == len(essential_headers)
                }
            }

            print(f"Security check for {url}: {present_headers}/{total_headers} headers present")
            return result

    except Exception as e:
        print(f"Error checking security headers for {url}: {e}")
        return None

async def check_product_security(product_id: str) -> bool:
    """
    Check security headers for a specific product
    
    Args:
        product_id: Product identifier (e.g., 'chorus', 'cadence')
    
    Returns:
        True if all essential security headers are present
    """
    staging_url = f"https://{product_id}-staging.dooor.ai"
    return await check_security_headers(staging_url)

async def check_product_security_detailed(product_id: str) -> Optional[Dict]:
    """
    Get detailed security information for a specific product
    
    Args:
        product_id: Product identifier (e.g., 'chorus', 'cadence')
    
    Returns:
        Dictionary with detailed security header information
    """
    staging_url = f"https://{product_id}-staging.dooor.ai"
    return await check_security_headers_detailed(staging_url)