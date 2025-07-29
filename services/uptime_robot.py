import requests
import os
from dotenv import load_dotenv
from typing import Dict, Optional

load_dotenv()

UPTIMEROBOT_API_KEY = os.getenv("UPTIMEROBOT_API_KEY")
UPTIMEROBOT_URL = "https://api.uptimerobot.com/v2"

async def get_monitor_uptime_by_url(monitor_url: str) -> Optional[float]:
    """
    Get uptime percentage for a specific monitor URL
    
    Args:
        monitor_url: The URL to check uptime for
    
    Returns:
        Uptime percentage (0-100) or None if not found/error
    """
    if not UPTIMEROBOT_API_KEY:
        print("Missing UptimeRobot API key")
        return None
    
    try:
        # First, get all monitors to find the one matching our URL
        monitors_url = f"{UPTIMEROBOT_URL}/getMonitors"
        
        params = {
            'api_key': UPTIMEROBOT_API_KEY,
            'format': 'json',
            'custom_uptime_ratios': '30',  # Get 30-day uptime
            'response_times': '0',
            'logs': '0'
        }
        
        response = requests.post(monitors_url, data=params)
        response.raise_for_status()
        
        data = response.json()

        print(f"Response from UptimeRobot: {data}")
        
        if data.get('stat') != 'ok':
            print(f"UptimeRobot API error: {data.get('error', {}).get('message', 'Unknown error')}")
            return None
        
        # Find monitor matching the URL
        monitors = data.get('monitors', [])
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
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching uptime from UptimeRobot: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

async def get_monitor_uptime(friendly_name: str) -> Optional[float]:
    """
    Get uptime percentage for a monitor by friendly name
    
    Args:
        friendly_name: The friendly name of the monitor (e.g., 'chorus')
    
    Returns:
        Uptime percentage (0-100) or None if not found/error
    """
    if not UPTIMEROBOT_API_KEY:
        print("Missing UptimeRobot API key")
        return None
    
    try:
        # Get all monitors to find the one matching our friendly name
        monitors_url = f"{UPTIMEROBOT_URL}/getMonitors"
        
        params = {
            'api_key': UPTIMEROBOT_API_KEY,
            'format': 'json',
            'custom_uptime_ratios': '30',  # Get 30-day uptime
            'response_times': '0',
            'logs': '0'
        }
        
        response = requests.post(monitors_url, data=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('stat') != 'ok':
            print(f"UptimeRobot API error: {data.get('error', {}).get('message', 'Unknown error')}")
            return None
        
        # Find monitor matching the friendly name
        monitors = data.get('monitors', [])
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
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching uptime from UptimeRobot: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

async def get_product_uptime(product_id: str) -> Optional[float]:
    """
    Get uptime for a specific product by friendly name
    
    Args:
        product_id: Product identifier (e.g., 'chorus', 'cadence')
    
    Returns:
        Uptime percentage (0-100) or None if not found/error
    """
    return await get_monitor_uptime(product_id)