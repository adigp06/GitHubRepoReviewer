
def parse_github_url(url_string):
    """
    Parses a public GitHub repositoru URL to extract the owner and repository names.

    Arguments:
        url_string: Raw input from the user

    What it returns:
        A tuple of (owner,repo) if valid or a (None,None) if the parsing fails
    """
    url_string = url_string.strip().strip('/') # To get rid of in case there is an extra slash
    url_string = url_string.split('/')

    # To validate the structure to ensure its a correct link with enough path elements
    if('github.com' not in url_string or (len(url_string) < 2)):
        return None,None
    else:
        repo = url_string[-1]
        owner = url_string[-2]
        return owner,repo
