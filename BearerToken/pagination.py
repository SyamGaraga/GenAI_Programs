import requests  # 1. Import the library

def list_all_issues(owner: str, repo: str, state: str = "open"):
    # GitHub API URL
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    
    # Parameters for pagination
    params = {"state": state, "per_page": 50, "page": 1}
    all_issues: list[dict] = []

    print(f"Fetching issues for {owner}/{repo}...") # Feedback to user

    while True:
        try:
            resp = requests.get(url, params=params, timeout=5)
            resp.raise_for_status() # Raises error for 404/500 codes
            
            data = resp.json()
            
            # If data is empty, we reached the last page
            if not data:
                break
            
            all_issues.extend(data)
            print(f"Collected page {params['page']}...") # Progress update
            params["page"] += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")
            break

    return all_issues

# --- THIS IS THE PART YOU WERE MISSING ---

# 2. specific 'Main' execution block
if __name__ == "__main__":
    # 3. Call the function with a real repository (e.g., FastAPI)
    issues = list_all_issues(owner="tiangolo", repo="fastapi", state="open")

    # 4. Print the output
    print("------------------------------------------------")
    print(f"Total Issues Found: {len(issues)}")
    
    # Print the titles of the first 5 issues found
    if issues:
        print("\nTop 5 Issue Titles:")
        for issue in issues[:5]:
            print(f"- {issue['title']}")