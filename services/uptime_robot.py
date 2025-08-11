import requests
import os
import time
from dotenv import load_dotenv
from typing import Dict, Optional, List

load_dotenv()

UPTIMEROBOT_API_KEY = os.getenv("UPTIMEROBOT_API_KEY")
UPTIMEROBOT_URL = "https://api.uptimerobot.com/v2"

# Cache for storing monitors data to avoid repeated API calls
_monitors_cache = {
    'data': None,
    'timestamp': 0,
    'ttl': 300  # 5 minutes cache TTL
}

async def _get_all_monitors(include_response_times: bool = False) -> Optional[List[Dict]]:
    """
    Get all monitors from UptimeRobot API with caching to reduce API calls
    
    Args:
        include_response_times: Whether to include response time data
    
    Returns:
        List of monitors or None if error
    """
    if not UPTIMEROBOT_API_KEY:
        print("Missing UptimeRobot API key")
        return None
    
    current_time = time.time()
    cache_key = f"monitors_rt_{include_response_times}"
    
    # Check if we have valid cached data
    if (_monitors_cache['data'] is not None and 
        cache_key in _monitors_cache['data'] and
        current_time - _monitors_cache['timestamp'] < _monitors_cache['ttl']):
        print("Using cached UptimeRobot data")
        return _monitors_cache['data'][cache_key]
    
    try:
        monitors_url = f"{UPTIMEROBOT_URL}/getMonitors"
        
        params = {
            'api_key': UPTIMEROBOT_API_KEY,
            'format': 'json',
            'custom_uptime_ratios': '30',  # Get 30-day uptime
            'logs': '0'
        }
        
        if include_response_times:
            params['response_times'] = '1'
            params['response_times_limit'] = '50'
        else:
            params['response_times'] = '0'
        
        response = requests.post(monitors_url, data=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('stat') != 'ok':
            print(f"UptimeRobot API error: {data.get('error', {}).get('message', 'Unknown error')}")
            return None
        
        monitors = data.get('monitors', [])
        
        # Initialize cache data structure if needed
        if _monitors_cache['data'] is None:
            _monitors_cache['data'] = {}
        
        # Cache the result
        _monitors_cache['data'][cache_key] = monitors
        _monitors_cache['timestamp'] = current_time
        
        print(f"Fetched {len(monitors)} monitors from UptimeRobot API")
        return monitors
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching monitors from UptimeRobot: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

async def get_monitor_uptime_by_url(monitor_url: str) -> Optional[float]:
    """
    Get uptime percentage for a specific monitor URL
    
    Args:
        monitor_url: The URL to check uptime for
    
    Returns:
        Uptime percentage (0-100) or None if not found/error
    """
    monitors = await _get_all_monitors(include_response_times=False)
    if not monitors:
        return None
    
    # Find monitor matching the URL
    target_monitor = None
    for monitor in monitors:
        if monitor.get('url') == monitor_url:
            target_monitor = monitor
            break
    
    if not target_monitor:
        print(f"Monitor not found for URL: {monitor_url}")
        return None
    
    # Extract uptime ratio (30-day)
    custom_uptime_ratio = target_monitor.get('custom_uptime_ratio')
    if custom_uptime_ratio:
        uptime_percentage = float(custom_uptime_ratio)
        print(f"Uptime for {monitor_url}: {uptime_percentage}%")
        return uptime_percentage
    
    # Fallback to all-time ratio if custom ratios not available
    all_time_uptime = target_monitor.get('all_time_uptime_ratio', 0)
    uptime_percentage = float(all_time_uptime)
    print(f"All-time uptime for {monitor_url}: {uptime_percentage}%")
    return uptime_percentage

async def get_monitor_uptime(friendly_name: str) -> Optional[float]:
    """
    Get uptime percentage for a monitor by friendly name
    
    Args:
        friendly_name: The friendly name of the monitor (e.g., 'chorus')
    
    Returns:
        Uptime percentage (0-100) or None if not found/error
    """
    monitors = await _get_all_monitors(include_response_times=False)
    if not monitors:
        return None
    
    # Find monitor matching the friendly name
    target_monitor = None
    for monitor in monitors:
        if monitor.get('friendly_name') == friendly_name:
            target_monitor = monitor
            break
    
    if not target_monitor:
        print(f"Monitor not found for friendly name: {friendly_name}")
        return None
    
    # Extract uptime ratio (30-day)
    custom_uptime_ratio = target_monitor.get('custom_uptime_ratio')
    if custom_uptime_ratio:
        uptime_percentage = float(custom_uptime_ratio)
        print(f"Uptime for {friendly_name}: {uptime_percentage}%")
        return uptime_percentage
    
    # Fallback to all-time ratio if custom ratios not available
    all_time_uptime = target_monitor.get('all_time_uptime_ratio', 0)
    uptime_percentage = float(all_time_uptime)
    print(f"All-time uptime for {friendly_name}: {uptime_percentage}%")
    return uptime_percentage

async def get_monitor_response_times(friendly_name: str) -> Optional[Dict]:
    """
    Get response time data for a monitor by friendly name
    
    Args:
        friendly_name: The friendly name of the monitor (e.g., 'chorus')
    
    Returns:
        Dictionary with response time data or None if not found/error
    """
    monitors = await _get_all_monitors(include_response_times=True)
    if not monitors:
        return None
    
    # Find monitor matching the friendly name
    target_monitor = None
    for monitor in monitors:
        if monitor.get('friendly_name') == friendly_name:
            target_monitor = monitor
            break
    
    if not target_monitor:
        print(f"Monitor not found for friendly name: {friendly_name}")
        return None
    
    # Extract response times
    response_times = target_monitor.get('response_times', [])
    
    if not response_times:
        print(f"No response time data available for {friendly_name}")
        return None
    
    # Process response times to get statistics
    values = [rt.get('value', 0) for rt in response_times if rt.get('value')]
    
    if not values:
        return None
    
    avg_response_time = sum(values) / len(values)
    min_response_time = min(values)
    max_response_time = max(values)
    
    # Sort values to get percentiles
    sorted_values = sorted(values)
    n = len(sorted_values)
    p95_index = int(0.95 * n)
    p99_index = int(0.99 * n)
    
    p95_response_time = sorted_values[min(p95_index, n-1)]
    p99_response_time = sorted_values[min(p99_index, n-1)]
    
    result = {
        'friendly_name': friendly_name,
        'average_ms': round(avg_response_time, 2),
        'min_ms': min_response_time,
        'max_ms': max_response_time,
        'p95_ms': p95_response_time,
        'p99_ms': p99_response_time,
        'sample_count': len(values),
        'raw_data': response_times[-10:]  # Last 10 data points
    }
    
    print(f"Response times for {friendly_name}: Avg={result['average_ms']}ms, P95={result['p95_ms']}ms")
    return result

async def get_product_uptime(product_id: str) -> Optional[float]:
    """
    Get uptime for a specific product by friendly name
    
    Args:
        product_id: Product identifier (e.g., 'chorus', 'cadence')
    
    Returns:
        Uptime percentage (0-100) or None if not found/error
    """
    return await get_monitor_uptime(product_id)

async def get_product_response_times(product_id: str) -> Optional[Dict]:
    """
    Get response time data for a specific product by friendly name
    
    Args:
        product_id: Product identifier (e.g., 'chorus', 'cadence')
    
    Returns:
        Dictionary with response time data or None if not found/error
    """
    return await get_monitor_response_times(product_id)

async def get_all_products_data(product_ids: List[str]) -> Dict[str, Dict]:
    """
    Get both uptime and response time data for multiple products in a single API call
    
    Args:
        product_ids: List of product identifiers
    
    Returns:
        Dictionary mapping product_id to their uptime and response time data
    """
    # Fetch monitors with response times (this includes uptime data too)
    monitors = await _get_all_monitors(include_response_times=True)
    if not monitors:
        return {}
    
    result = {}
    
    for product_id in product_ids:
        # Find monitor for this product
        target_monitor = None
        for monitor in monitors:
            if monitor.get('friendly_name') == product_id:
                target_monitor = monitor
                break
        
        if not target_monitor:
            print(f"Monitor not found for product: {product_id}")
            result[product_id] = {'uptime': None, 'response_times': None}
            continue
        
        # Get uptime
        uptime = None
        custom_uptime_ratio = target_monitor.get('custom_uptime_ratio')
        if custom_uptime_ratio:
            uptime = float(custom_uptime_ratio)
        else:
            all_time_uptime = target_monitor.get('all_time_uptime_ratio', 0)
            uptime = float(all_time_uptime)
        
        # Get response times
        response_times_data = None
        response_times = target_monitor.get('response_times', [])
        if response_times:
            values = [rt.get('value', 0) for rt in response_times if rt.get('value')]
            if values:
                avg_response_time = sum(values) / len(values)
                sorted_values = sorted(values)
                n = len(sorted_values)
                p95_index = int(0.95 * n)
                p95_response_time = sorted_values[min(p95_index, n-1)]
                
                response_times_data = {
                    'friendly_name': product_id,
                    'average_ms': round(avg_response_time, 2),
                    'min_ms': min(values),
                    'max_ms': max(values),
                    'p95_ms': p95_response_time,
                    'p99_ms': sorted_values[min(int(0.99 * n), n-1)],
                    'sample_count': len(values)
                }
        
        result[product_id] = {
            'uptime': uptime,
            'response_times': response_times_data
        }
        
        print(f"Data for {product_id}: uptime={uptime}%, avg_response={response_times_data['average_ms'] if response_times_data else 'N/A'}ms")
    
    return result

def clear_uptime_cache():
    """Clear the UptimeRobot cache to force fresh data on next request"""
    global _monitors_cache
    _monitors_cache['data'] = None
    _monitors_cache['timestamp'] = 0
    print("UptimeRobot cache cleared")