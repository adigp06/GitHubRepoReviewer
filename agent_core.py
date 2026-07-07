import json
from indexer import fetch_repo_contents
from cleaner import filter_codebase
from google import genai
from google.genai import types
from preprocessor import preprocess_repository_assets
import time

client = genai.Client()

AGENT_ROLES = {
    "architecture": (
        "You are an expert achitecture reviewer. Assess how well codebase is organized,"
        "how responsibilities are split across directories, and whether the project structure feels scalable"

    ),
    "documentation": (
        "You are an Expert Documentation Reviewer, Check whether the repository explains itself clearly"
        "through README files, setup setups, usage examples and developer onboarding guidance"
    ),
    "testing": (
        "You are an expert teting reviewer. Evaluate whether the project has enough tests."
        "whether core behaviour is covered, and whether the testing strategy looks reliable."
    ),
    "code_quality": (
        "You are an expert code quality reviewer. Judge readability, consistency, modularity,"
        "variable naming conventions, and whether the codebase looks maintainable."
    ),
    "dependency": (
        "You are an expert Dependency Reviewer. Review external libraries and configuration setup files"
        "to identify dependency bloat, outdated choices, or unecessary architecture complexity"
    )
}



def execute_agent_action(json_string):
    try:
        # Because of reoccuring backticks
        clean_json_str = json_string.replace("```json","").replace("```","").strip()
        action_data = json.loads(clean_json_str)
    except json.JSONDecodeError:
        return "Error: Invalid JSON format received"
    
    action = action_data.get("action")

    if action == "fetch_repo_contents":
        owner = action_data.get("owner")
        repo = action_data.get("repo")

        if not owner or not repo:
            return "Error: Missing owner or repo arguments for fetch_repo_contents."
        
        raw_data = fetch_repo_contents(owner,repo)
        clean_structure = filter_codebase(raw_data)
        return clean_structure

    else:
        return f"Error: Unknown action '{action}'"
    

def run_agent_loop(user_prompt):
    planner_instruction = (
        "You are a repository extraction planner. Look at the user's request and output a single valid JSON block"
        "to fetch repositoru structure:\n"
        "{\n"
        " \"action\": \"fetch_repo_contents\",\n"
        " \"owner\":\"OWNER_NAME\",\n"
        " \"repo\": \"REPO_NAME\"\n"
        "}\n"
        "Do not include any other text of explanation when outputting this JSON block. Once you receive this tool's observation. "
    )
    planner_chat = client.chats.create(
        model="gemini-2.5-flash",
        config = types.GenerateContentConfig(system_instruction=planner_instruction)

    )
    response = planner_chat.send_message(user_prompt)
    model_response = response.text.strip()

    if "fetch_repo_contents" in model_response:
        print("\n executing local file cleaner tool pipeline")
        clean_json_str = model_response.replace("```json","").replace("```","").strip()

        observation_data = execute_agent_action(clean_json_str)
        print(f"Tool Observation: Loaded {len(observation_data)} cleaned codebase structural assets")

        optimized_assets = preprocess_repository_assets(observation_data)
        print(f"Preprocessor Matrix: generated {len(optimized_assets)} context-safe chunks")

        repo_context_str = json.dumps(optimized_assets)
    else:
        print("Failed to resolve repositoru target")
        return
    


    specialist_reviews = {}
    print("\n Parallel Agents Launched")
    for role_name, system_prompt in AGENT_ROLES.items():
        print(f"{role_name.upper()} Agent is inspecting the repository structure:")
        response = client.models.generate_content(
            model = 'gemini-2.5-flash',
            config = types.GenerateContentConfig(system_instruction=system_prompt),
            contents=f"Analyze this repository structure and provide your specialized breakdown:\n\n{repo_context_str}"
        )
        specialist_reviews[role_name] = response.text.strip()

    # RATE LIMIT BACKOFF, sleep for 2 seconds to let token per minute bucket clear
    time.sleep(2)
    
    print("Passing the reviews to the aggregator judge")

    judge_instruction=(
        "YOu are the Lead Systems Judge. Your task is to compile findings from five specialist reviews"
        "(Architecture, Documentation, Testing, Code Quality, and Dependencies) into a cohesive final engineering report.\n\n"
        "Your final report MUST be structured with clear markdown sections, includean overall project readiness score, "
        "and provide an actionable list of prioritized engineering recommendations"
    )

    aggregated_payload = ""
    for role_name, review_text in specialist_reviews.items():
        aggregated_payload += f"=== {role_name.upper()} REVIEW === \n{review_text}\n\n"

    judge_response = client.models.generate_content(
        model ='gemini-2.5-flash',
        config = types.GenerateContentConfig(system_instruction=judge_instruction),
        contents = f"Here are the findings from the specialists: \n\n{aggregated_payload}"

    )
    print("\n FINAL REVIEW")
    print(judge_response.text)


