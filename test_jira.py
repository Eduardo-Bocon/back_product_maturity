import asyncio
import os
from dotenv import load_dotenv
from services.jira import get_bug_tasks_by_project, get_open_p1_bugs

load_dotenv()

async def test_jira_integration():
    """Test Jira integration with different project keys"""
    
    print("=== Testing Jira Integration ===\n")
    
    # Check if environment variables are set
    jira_url = os.getenv("JIRA_URL")
    jira_username = os.getenv("JIRA_USERNAME")
    jira_token = os.getenv("JIRA_API_TOKEN")
    
    print("Environment Variables:")
    print(f"JIRA_URL: {'[OK] Set' if jira_url else '[X] Missing'}")
    print(f"JIRA_USERNAME: {'[OK] Set' if jira_username else '[X] Missing'}")
    print(f"JIRA_API_TOKEN: {'[OK] Set' if jira_token else '[X] Missing'}")
    print()
    
    if not all([jira_url, jira_username, jira_token]):
        print("[X] Missing required environment variables. Please set:")
        print("   - JIRA_URL (e.g., https://yourcompany.atlassian.net)")
        print("   - JIRA_USERNAME (your email)")
        print("   - JIRA_API_TOKEN (API token from Jira)")
        return
    
    # Test with common project keys - you can modify these
    test_projects = ["CHORUS", "CADENCE", "KENNA", "DUET"]
    
    for project_key in test_projects:
        print(f"=== Testing Project: {project_key} ===")
        
        # Test getting all bug tasks
        print("Getting all bug tasks...")
        try:
            bugs = await get_bug_tasks_by_project(project_key)
            if bugs:
                print(f"[OK] Found {len(bugs)} bug tasks")
                for bug in bugs[:3]:  # Show first 3 bugs
                    print(f"   - {bug['key']}: {bug['summary']} [{bug['status']}]")
                if len(bugs) > 3:
                    print(f"   ... and {len(bugs) - 3} more")
            else:
                print("[INFO] No bug tasks found (or project doesn't exist)")
        except Exception as e:
            print(f"[X] Error getting bug tasks: {e}")
        
        # Test getting P1 bugs count
        print("Getting P1 bugs count...")
        try:
            p1_count = await get_open_p1_bugs(project_key)
            print(f"[OK] Found {p1_count} open P1 bugs")
        except Exception as e:
            print(f"[X] Error getting P1 bugs: {e}")
        
        print()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_jira_integration())