import requests
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME") 
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

async def get_bug_tasks_by_project(project_key: str) -> List[Dict]:
    """
    Get all tasks with 'bug' label from a specific Jira project
    
    Args:
        project_key: The Jira project key (e.g., 'PROJ')
    
    Returns:
        List of bug tasks with relevant information
    """
    if not all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
        print("Missing Jira configuration")
        return []
    
    try:
        # Jira REST API endpoint for searching issues
        url = f"{JIRA_URL}/rest/api/3/search"
        
        # JQL query to find issues with bug label in specific project
        jql = f'project = "{project_key}" AND labels = "bug"'
        
        params = {
            'jql': jql,
            'fields': 'summary,status,priority,assignee,created,updated,labels',
            'maxResults': 100
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        auth = (JIRA_USERNAME, JIRA_API_TOKEN)
        
        response = requests.get(url, params=params, headers=headers, auth=auth)
        response.raise_for_status()
        
        data = response.json()
        
        bugs = []
        for issue in data.get('issues', []):
            bug_info = {
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'status': issue['fields']['status']['name'],
                'priority': issue['fields']['priority']['name'] if issue['fields']['priority'] else 'None',
                'assignee': issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned',
                'created': issue['fields']['created'],
                'updated': issue['fields']['updated'],
                'labels': issue['fields']['labels']
            }
            bugs.append(bug_info)
        
        print(f"Found {len(bugs)} bug tasks in project {project_key}")
        return bugs
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching bug tasks from Jira: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

async def get_open_bugs_by_priority(project_key: str, priorities: List[str]) -> int:
    """
    Get count of open bugs for specific priority levels
    
    Args:
        project_key: The Jira project key
        priorities: List of priority names (e.g., ['Highest', 'High'])
    
    Returns:
        Number of open bugs with specified priorities
    """
    if not all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
        print("Missing Jira configuration")
        return 0
    
    try:
        url = f"{JIRA_URL}/rest/api/3/search"
        
        # Build priority filter
        priority_filter = " OR ".join([f'priority = "{p}"' for p in priorities])
        
        # JQL for open bugs with specific priorities
        jql = f'project = "{project_key}" AND labels = "bug" AND status != "Done" AND ({priority_filter})'
        
        params = {
            'jql': jql,
            'maxResults': 0  # We only want the count
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        auth = (JIRA_USERNAME, JIRA_API_TOKEN)
        
        response = requests.get(url, params=params, headers=headers, auth=auth)
        response.raise_for_status()
        
        data = response.json()
        total_bugs = data.get('total', 0)
        
        print(f"Found {total_bugs} open bugs with priorities {priorities} in project {project_key}")
        return total_bugs
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching bugs from Jira: {e}")
        return 0
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 0

async def get_open_p1_bugs(project_key: str) -> int:
    """
    Get count of open P1 bugs for a specific project (backward compatibility)
    """
    return await get_open_bugs_by_priority(project_key, ['Highest', 'High'])

async def get_open_all_bugs(project_key: str) -> int:
    """
    Get count of all open bugs regardless of priority
    
    Args:
        project_key: The Jira project key
    
    Returns:
        Number of all open bugs
    """
    if not all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
        print("Missing Jira configuration")
        return 0
    
    try:
        url = f"{JIRA_URL}/rest/api/3/search"
        
        # JQL for all open bugs
        jql = f'project = "{project_key}" AND labels = "bug" AND status != "Done"'
        
        params = {
            'jql': jql,
            'maxResults': 0  # We only want the count
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        auth = (JIRA_USERNAME, JIRA_API_TOKEN)
        
        response = requests.get(url, params=params, headers=headers, auth=auth)
        response.raise_for_status()
        
        data = response.json()
        total_bugs = data.get('total', 0)
        
        print(f"Found {total_bugs} total open bugs in project {project_key}")
        return total_bugs
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all bugs from Jira: {e}")
        return 0
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 0