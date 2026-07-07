import requests


def fetch_repo_contents(owner, repo):
    """
    Queries GitHub's Git Trees API recursively to build an inventory of repository assets.

    Choosing the Trees API bypasses the need for local disk cloning,
    allowing us to inspect repository structure directly over the wire as an in-memory index.
    """
    target_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    response = requests.get(target_url)
    status_code = response.status_code
    if(status_code == 200):
        data = response.json()
        # Return the tree array representing all files and directories
        return data.get('tree',[])
    else:
        return None

    
