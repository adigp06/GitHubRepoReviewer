from indexer import fetch_repo_contents


def filter_codebase(repo_structure):
    """
    Filters out non-essential assets and binary files form the repository inventory.

    This acys as our upstream context optimization layer, stripping heavy formats(like images, notebooks and other files)
    """
    if repo_structure is None:
        return []
    
    clean_files = []
    for item in repo_structure:
        file_path = item.get('path','')
        # Discard media formats and other bloated configurations that don't reveal code architecture
        if file_path.endswith('.png') or file_path.endswith('.lock') or file_path.endswith('.ipynb') :
            continue

        clean_files.append(item)
    
    return clean_files
