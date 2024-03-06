import json
import subprocess

def colorize(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def main_menu():
    print(colorize("""
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░      ░░░  ░░░░  ░░        ░░       ░░░░░░░░░░      ░░░        ░░        ░
▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒
▓▓      ▓▓▓        ▓▓▓▓▓  ▓▓▓▓▓       ▓▓▓▓▓▓▓▓▓  ▓▓▓   ▓▓▓▓▓  ▓▓▓▓▓▓▓▓  ▓▓▓▓
███████  ██  ████  █████  █████  ██████████████  ████  █████  ████████  ████
██      ███  ████  ██        ██  ███████████████      ███        █████  ████
████████████████████████████████████████████████████████████████████████████                                                                  
    """, 32))  # Ensure the ASCII art string is properly terminated
 
    print(colorize("Select an operation:", 100))
    print(colorize("1) TAGGING", 46))
    print(colorize("2) DEPLOYING", 41))
    print(colorize("3) PERMISSIONS", 44))
    choice = input(colorize("Enter your choice (1, 2, or 3): ", 100))  # Correct the input prompt
    if choice == '1':
        tagging_workflow()
    elif choice == '2':
        deploying_workflow()
    elif choice == '3':
        permissions_workflow()
    else:
        print("Invalid choice. Please select 1, 2, or 3.")
        main_menu()

def check_branch_permissions(branch, permissions):
    branch_permissions = permissions['branches'].get(branch.strip('* ').strip(), [])
    if not branch_permissions:
        print("All users are allowed to perform operations on this branch.")
        return True
    github_username = get_github_username()
    if github_username in branch_permissions:
        print(f"Users with access to branch '{branch}': {', '.join(branch_permissions)}")
        return True
    else:
        print(f"Denied: User '{github_username}' does not have permission to perform operations on this branch. Press Enter to return to the main menu.")
        input()  # Wait for the user to hit enter
        main_menu()  # Return to the main menu

def list_branches():
    command = "git branch --list"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error listing branches: {result.stderr}")
        return []
    branches = [branch.strip().replace('* ', '') for branch in result.stdout.splitlines()]
    return branches

def permissions_workflow():
    print()
    you_chose_permissions = colorize("PERMISSIONS Chosen", 44)
    print(you_chose_permissions)
    permissions_file = 'permissions.shipgit'
    permissions = check_permissions_file(permissions_file)
    if permissions:
        print("Permissions file found and loaded.")
        branches = list_branches()
        if branches:
            print("Available branches:")
            for i, branch in enumerate(branches):
                print(colorize(f"{i + 1}) {branch}", 36))
            branch_number = input("Select a branch to add permissions for (number): ")
            try:
                branch_number = int(branch_number) - 1
                if branch_number >= 0 and branch_number < len(branches):
                    selected_branch = branches[branch_number]
                    permissions = update_permissions_file(permissions, selected_branch, permissions_file)
                    list_users_with_access(permissions, selected_branch)
                    github_username = get_github_username()
                    if github_username:
                        print(f"Your GitHub username is: {colorize(github_username, 36)}")
                        manage_user_permissions(permissions, selected_branch, github_username, permissions_file)
                    else:
                        print("GitHub username not found in local git config.")
                else:
                    print("Invalid branch number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        else:
            print("No branches available.")
        # Further processing can be done here as needed
    else:
        print("Permissions file not found or invalid.")

def manage_user_permissions(permissions, branch, username, file_path):
    while True:
        print(f"\n{colorize(branch, 44)} Permission Management Options:")
        print(colorize("1) Add my username to the list", 36))
        print(colorize("2) Add my username and remove all others", 36))
        print(colorize("3) Add a specific username to the list", 36))
        print(colorize("4) Remove all users", 36))
        print(colorize("5) Remove a single username", 36))
        print(colorize("6) Exit permission management", 36))
        choice = input("Select an option (1-6): ")
        if choice == '1':
            if username not in permissions['branches'][branch]:
                permissions['branches'][branch].append(username)
                update_permissions_file(permissions, branch, file_path)
                print(f"Added '{username}' to branch '{branch}'.")
            else:
                print(f"'{username}' already has access to branch '{branch}'.")
        elif choice == '2':
            if username not in permissions['branches'][branch]:
                permissions['branches'][branch].append(username)
            else:
                permissions['branches'][branch] = [username]
            permissions['branches'][branch] = [username]
            update_permissions_file(permissions, branch, file_path)
            print(f"Set '{username}' as the only user with access to branch '{branch}'.")
        elif choice == '3':
            specific_username = input("Enter the specific username to add: ").strip()
            if specific_username and specific_username not in permissions['branches'][branch]:
                permissions['branches'][branch].append(specific_username)
                update_permissions_file(permissions, branch, file_path)
                print(f"Added '{specific_username}' to branch '{branch}'.")
            elif specific_username:
                print(f"'{specific_username}' already has access to branch '{branch}'.")
            else:
                print("No username entered.")
        elif choice == '4':
            permissions['branches'][branch] = []
            update_permissions_file(permissions, branch, file_path)
            print(f"Removed all users from branch '{branch}'.")
        elif choice == '5':
            user_to_remove = input("Enter the username to remove: ")
            if user_to_remove in permissions['branches'][branch]:
                permissions['branches'][branch].remove(user_to_remove)
                update_permissions_file(permissions, branch, file_path)
                print(f"Removed '{user_to_remove}' from branch '{branch}'.")
            else:
                print(f"'{user_to_remove}' does not have access to branch '{branch}'.")
        elif choice == '6':
            main_menu()
        else:
            print("Invalid choice. Please select an option from 1 to 6.")
            print("Invalid choice. Please select an option from 1 to 5.")

def get_github_username():
    command = "git config user.name"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        return result.stdout.strip()
    return None

def list_users_with_access(permissions, branch):
    users = permissions['branches'].get(branch, [])
    if users:
        print(f"Users with access to branch '{branch}':")
        for user in users:
            print(colorize(user, 36))
    else:
        print(f"No users currently have access to branch '{branch}'.")

def update_permissions_file(permissions, branch, file_path):
    if branch not in permissions['branches']:
        permissions['branches'][branch] = []
    with open(file_path, 'w') as file:
        json.dump(permissions, file, indent=4)
    print(f"Added branch '{branch}' to permissions.")
    return permissions
def check_permissions_file(file_path):
    try:
        with open(file_path, 'r') as file:
            permissions_data = file.read()
            return parse_permissions(permissions_data) if permissions_data.strip() else create_default_permissions(file_path)
    except FileNotFoundError:
        return create_default_permissions(file_path)
    except Exception as e:
        print(f"An error occurred while reading the permissions file: {e}")
        return None

def create_default_permissions(file_path):
    default_permissions = {'branches': {}}
    with open(file_path, 'w') as file:
        json.dump(default_permissions, file, indent=4)
    print(f"Created default permissions file with default structure at {file_path}.")
    return default_permissions
def parse_permissions(json_data):
    import json
    try:
        permissions = json.loads(json_data)
        return permissions
    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing the permissions file: {e}")
        return None

def find_commits_by_phrase(search_phrase):
   command = f"git log --grep='{search_phrase}' --oneline"
   result = subprocess.run(command, shell=True, capture_output=True, text=True)
   if result.returncode != 0:
       print(f"Error searching for commits: {result.stderr}")
       return []
   commits = []
   for line in result.stdout.splitlines():
       commit_hash, message = line.split(' ', 1)
       tags = get_tags_for_commit(commit_hash)
       commits.append((commit_hash, message, tags))
   return commits

def get_tags_for_commit(commit_hash):
   command = f"git tag --points-at {commit_hash}"
   result = subprocess.run(command, shell=True, capture_output=True, text=True)
   if result.stdout:
       return result.stdout.strip().split('\n')
   else:
       return []

def select_commit(commits):
   if not commits:
       print("No commits found matching your search phrase.")
       return None
   print("Commits matching your search:")
   for i, (commit_hash, message, tags) in enumerate(commits[:20]):
       tag_str = "TAG:>>> " + ", ".join(tags) + " <<<" if tags else ""
       tag_str = colorize(tag_str, 42)  # Green color code
       print(colorize(f"{chr(ord('a') + i)}) {tag_str} {commit_hash} - {message}", 36))  # Cyan color code
   return user_choice_of_commit(commits)

def tag_commit(commit_hash):
   tag_name = input(colorize("Enter the tag name: ", 100))
   tag_and_push(tag_name, commit_hash)

def tagging_workflow():
   print()
   you_chose_tagging = colorize("TAGGING Chosen", 46)
   print(you_chose_tagging)
   search_phrase = input("Enter your commit search phrase (or just press enter to see last 20): ")
   commits = find_commits_by_phrase(search_phrase)
   selected_hash = select_commit(commits)
   if selected_hash:
       tag_commit(selected_hash)

def get_last_tags(limit=20):
   command = f"git tag --sort=-creatordate | head -n {limit}"
   result = subprocess.run(command, shell=True, capture_output=True, text=True)
   if result.returncode != 0:
       print(f"Error fetching tags: {result.stderr}")
       return []
   return result.stdout.splitlines()

def select_item_or_create_new(items, message, create_prompt):
   print(f"{message}")
   for i, item in enumerate(items):
       print(colorize(f"{chr(ord('a') + i)}) {item}", 33))  # Green color code
   print(colorize(f"z) Create a new {create_prompt}", 32))  # Yellow color code
   return user_choice(items, create_prompt)

def get_default_remote_branch():
   command = "git remote show origin | grep 'HEAD branch' | cut -d' ' -f5"
   result = subprocess.run(command, shell=True, capture_output=True, text=True)
   if result.returncode != 0:
       return "master"
   return result.stdout.strip()

def deploying_workflow():
    original_branch = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True).stdout.strip()
    permissions_file = 'permissions.shipgit'
    permissions = check_permissions_file(permissions_file)
    if permissions:
        branch_output = subprocess.run("git branch", shell=True, capture_output=True, text=True).stdout
        branches = branch_output.splitlines()
        selected_branch = select_item(branches, colorize("\nChoose a branch to deploy to:", 43))
        if selected_branch and check_branch_permissions(selected_branch, permissions):
            tags = get_last_tags()
            selected_tag = select_item(tags, colorize("\nChoose a tag to deploy:", 41))
            if selected_tag:
                deployment_process(selected_tag, original_branch, permissions, selected_branch)
        if check_branch_permissions(selected_branch, permissions):
            deployment_process(selected_tag, original_branch, permissions)
    else:
        print("Error: Unable to read permissions file.")

def select_item(items, message):
    print(f"{message}")
    for i, item in enumerate(items):
        print(colorize(f"{chr(ord('a') + i)}) {item}", 35))  # Green color code
    return user_choice(items)

# select one of the previously committed git commits
def user_choice_of_commit(commits):
   while True:
       choice = input("Select an item (a, b, c, ..., or z for new): ").lower()
       if choice >= 'a' and choice <= chr(ord('a') + len(commits) - 1):
           return commits[ord(choice) - ord('a')][0]
       else:
           print("Invalid choice. Please try again.")

def user_choice(commits, create_prompt=None):
   while True:
       choice = input("Select an item (a, b, c, ..., or z for new): ").lower()
       if choice >= 'a' and choice <= chr(ord('a') + len(commits) - 1):
           return commits[ord(choice) - ord('a')].lstrip('* ')
       elif create_prompt and choice == 'z':
           return input(f"Enter a new {create_prompt} name: ")
       else:
           print("Invalid choice. Please try again.")

def tag_and_push(tag_name, commit_hash):
   tag_command = f"git tag {tag_name} {commit_hash}"
   tag_result = subprocess.run(tag_command, shell=True, capture_output=True, text=True)
   push_command = f"git push origin {tag_name}"
   push_result = subprocess.run(push_command, shell=True, capture_output=True, text=True)
   if tag_result.returncode != 0:
       print(f"Tagging failed: {tag_result.stderr}")
   elif push_result.returncode != 0:
       print(f"Failed to push tag: {push_result.stderr}")
   else:
       print(colorize(f"Successfully tagged commit {commit_hash} with {tag_name}", 36))
       print("Tag pushed to remote.")

def deployment_process(selected_tag, original_branch, permissions, selected_branch):
   deploy_to_branch(selected_tag, original_branch, selected_branch)

def deploy_to_branch(selected_branch, selected_tag, branches, original_branch):
   selected_branch = selected_branch.replace('*', '').strip()
   print(colorize(f"\nSelected branch: {selected_branch}\n", 36))
   branch_exists = selected_branch.strip('* ').strip() in [branch.strip('* ').strip() for branch in branches]
   default_remote_branch = get_default_remote_branch()
   if selected_branch == default_remote_branch:
       print(f"Error: Deployment to the default remote branch '{default_remote_branch}' is not allowed.")
       return
   branch_exists = selected_branch in [branch.strip('* ').strip() for branch in branches]
   stash_result = subprocess.run("git stash push -m 'Auto-stash by onering.py'", shell=True, capture_output=True, text=True)
   if stash_result.returncode != 0:
       print(f"Error stashing changes: {stash_result.stderr}")
       return
   if not branch_exists:
       subprocess.run(f"git checkout -b {selected_branch}", shell=True, check=True)
       print("New branch created and checked out.")
   else:
       subprocess.run(f"git checkout {selected_branch}", shell=True, check=True)
   deploy_tag(selected_tag, selected_branch)
   pop_result = subprocess.run("git stash pop", shell=True, capture_output=True, text=True)
   if pop_result.returncode != 0:
       print(f"Error applying stashed changes: {pop_result.stderr}")
   subprocess.run(f"git checkout {original_branch}", shell=True, check=True)
   print(f"Returned to original branch: {original_branch}")


def deploy_tag(tag, branch):
   default_remote_branch = get_default_remote_branch()
   subprocess.run(f"git pull origin {default_remote_branch}", shell=True, check=True)
   subprocess.run(f"git fetch origin --tags", shell=True, check=True)
   subprocess.run(f"git merge tags/{tag}", shell=True, check=True)
   subprocess.run(f"git push --force origin {branch}", shell=True, check=True)
   print(colorize("Deployment complete!", 36))

if __name__ == "__main__":
   main_menu()
    #show all colors for colorize
    # for i in range(30, 108):
    #     print(f"\033[{i}mColor {i}\033[0m")def list_branches():


