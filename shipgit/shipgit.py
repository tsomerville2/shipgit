# to build, change version in pyproject.toml, then run python -m build
# to upload, run twine upload dist/* or dist/*.8* if you're on version 0.0.8
# you will need to paste in your api key for pypi
#
# then any user can just 'pip install shipgit'
# then simply type 'shipgit' to run the program

import json
import subprocess

def colorize(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def main_menu(firsttime=False):
    if firsttime:
        print(colorize("""
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░      ░░░  ░░░░  ░░        ░░       ░░░░░░░░░░      ░░░        ░░        ░
▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒
▓▓      ▓▓▓        ▓▓▓▓▓  ▓▓▓▓▓       ▓▓▓▓▓▓▓▓▓  ▓▓▓   ▓▓▓▓▓  ▓▓▓▓▓▓▓▓  ▓▓▓▓
███████  ██  ████  █████  █████  ██████████████  ████  █████  ████████  ████
██      ███  ████  ██        ██  ███████████████      ███        █████  ████
████████████████████████████████████████████████████████████████████████████ 
░░░ CREATED BY TRAVIS SOMERVILLE ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                                    
    """, 32))  # Ensure the ASCII art string is properly terminated
    else:
        print("")

    branch = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True).stdout.strip()
    commit = subprocess.run("git rev-parse --short HEAD", shell=True, capture_output=True, text=True).stdout.strip()
    tag = subprocess.run(f"git describe --tags {commit}", shell=True, capture_output=True, text=True).stdout.strip()
    tag = tag if tag else "No tag"
    info = f"CURRENT: Branch: {branch}    Commit: {commit}    TAG: {tag}"
    print(colorize(info, 43)) 

    print(colorize("Select an operation:", 100))
    print(colorize("1) TAGGING", 46))
    print(colorize("2) DEPLOYING", 41))
    print(colorize("3) PERMISSIONS", 44))
    print(colorize("4) INFO", 45))
    print(colorize("5) EXIT", 47))
    choice = input(colorize("Enter your choice (1, 2, 3, 4, or 5): ", 100))  # Correct the input prompt
    if choice == '1':
        tagging_workflow()
    elif choice == '2':
        deploying_workflow()
    elif choice == '3':
        permissions_workflow()
    elif choice == '4':
        info_workflow()
    elif choice == '5':
        exit()
    else:
        print("Invalid choice. Please select 1, 2, 3, 4, or 5.")
        main_menu()

def info_workflow():
    branches = list_branches()
    header = "=" * 86
    print(colorize(header, 45))
    for branch in branches:
        print_branch_info(branch)
    
    print(colorize(header, 45))

    main_menu()

def print_branch_info(branch):
    branch = branch.strip('* ').strip()
    commit = subprocess.run(f"git rev-parse --short {branch}", shell=True, capture_output=True, text=True).stdout.strip()
    tag = subprocess.run(f"git describe --tags {commit}", shell=True, capture_output=True, text=True).stdout.strip()
    tag = tag if tag else "No tag"
    info = f"| Branch: {branch:<15} | Commit: {commit:<10} | TAG: {tag[:30].ljust(30)} |"
    #print(f"{info:^60}")
    print(colorize(info, 45))  # Cyan color code

def commit_and_push_changes(file_path, commit_message):
    # Check if there are changes to commit
    status_result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if status_result.stdout.strip() == "":
        print(colorize("No changes to commit.", 36))
        return
    subprocess.run(f"git add {file_path}", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    commit_result = subprocess.run(f'git commit -m "{commit_message}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if commit_result.returncode != 0:
        #print(colorize(f"Failed to commit changes: {commit_result.stderr}", 31))
        return False
    subprocess.run("git push", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(colorize("Changes to permissions have been committed and pushed to the repository.", 36))
    return True

def check_branch_permissions(branch, permissions):
    branch_permissions = permissions['branches'].get(branch.strip('* ').strip())
    if branch_permissions is None or len(branch_permissions) == 0:
        print("Please setup Permissions for at least 1 GitHub user to deploy to this branch.")
        permissions_workflow()

    github_username = get_github_username()
    if github_username in branch_permissions:
        print(f"Users with access to branch '{branch}': {', '.join(branch_permissions)}")
        return True
    else:
        print(colorize(f"Denied: User '{github_username}' does not have permission to perform operations on this branch. Press Enter to return to the main menu.", 41))
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
        print_permissions_grid(permissions)
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

def print_permissions_grid(permissions):
    branch_col_width = 20
    users_col_width = 70
    header = colorize(f"{'Branch':<{branch_col_width}} | {'Users with Access':<{users_col_width}}", 44)
    separator = colorize('-' * (branch_col_width + users_col_width + 3), 44)  # +3 for " | " separator
    print(header)
    print(separator)
    for branch in sorted(permissions['branches']):
        users = permissions['branches'][branch]
        users_str = ', '.join(users)
        if len(users_str) > users_col_width:
            users_str = users_str[:users_col_width-3] + '...'
        this_row = f"{branch:<{branch_col_width}} | {users_str:<{users_col_width}}"
        print(colorize(this_row, 44))
    print(separator)

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
                print_permissions_grid(permissions)
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
            print_permissions_grid(permissions)
        elif choice == '3':
            specific_username = input("Enter the specific username to add: ").strip()
            if specific_username and specific_username not in permissions['branches'][branch]:
                permissions['branches'][branch].append(specific_username)
                update_permissions_file(permissions, branch, file_path)
                print(f"Added '{specific_username}' to branch '{branch}'.")
                print_permissions_grid(permissions)
            elif specific_username:
                print(f"'{specific_username}' already has access to branch '{branch}'.")
            else:
                print("No username entered.")
        elif choice == '4':
            permissions['branches'][branch] = []
            update_permissions_file(permissions, branch, file_path)
            print(f"Removed all users from branch '{branch}'.")
            print_permissions_grid(permissions)
        elif choice == '5':
            user_to_remove = input("Enter the username to remove: ")
            if user_to_remove in permissions['branches'][branch]:
                permissions['branches'][branch].remove(user_to_remove)
                update_permissions_file(permissions, branch, file_path)
                print(f"Removed '{user_to_remove}' from branch '{branch}'.")
                print_permissions_grid(permissions)
            else:
                print(f"'{user_to_remove}' does not have access to branch '{branch}'.")
        elif choice == '6':
            main_menu()
        else:
            print("Invalid choice. Please select an option from 1 to 6.")

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
        print(f"Added branch '{branch}' to permissions.")
    with open(file_path, 'w') as file:
        json.dump(permissions, file, indent=4)
    commit_and_push_changes(file_path, f"Update permissions for branch '{branch}'")
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
   command = f"git log --oneline"
   result = subprocess.run(command, shell=True, capture_output=True, text=True)
   if result.returncode != 0:
       print(f"Error searching for commits: {result.stderr}")
       return []
   commits = []
   for line in result.stdout.splitlines():
        commit_hash, message = line.split(' ', 1)
        # Check if the commit message contains the search_phrase
        message_matches = search_phrase.lower() in message.lower()
        # Retrieve tags and check if they contain the search_phrase
        tags = get_tags_for_commit(commit_hash, search_phrase)
        tag_matches = len(tags) > 0
        # Only append the commit if the message or any of the tags match the search_phrase
        if message_matches or tag_matches:
            commits.append((commit_hash, message, tags))
   return commits

def get_tags_for_commit(commit_hash, search_phrase):
   command = f"git tag --points-at {commit_hash}"
   result = subprocess.run(command, shell=True, capture_output=True, text=True)
   if result.stdout:
       tags = result.stdout.strip().split('\n')
       return [tag for tag in tags if search_phrase.lower() in tag.lower()]
   else:
       return []

def select_commit(commits):
    if not commits:
        print("No commits found matching your search phrase.")
        return None
    print("Commits matching your search:")
    current_commit = subprocess.run("git rev-parse HEAD", shell=True, capture_output=True, text=True).stdout.strip()[:7]
    for i, (commit_hash, message, tags) in enumerate(commits[:200], start=1):
        tag_str = "TAG:>>> " + ", ".join(tags) + " <<<" if tags else ""
        tag_str = colorize(tag_str, 42)  # Green color code
        current_commit_marker = colorize(">CURRENT COMMIT<", 41) if commit_hash == current_commit else ""
        print(colorize(f"{i}) {current_commit_marker} {tag_str} {commit_hash} - {message}", 36))  # Cyan color code
    return user_choice_of_commit_by_number(commits)

def tag_commit(commit_hash):
   tag_name_input = input(colorize("Enter the tag name: ", 100))
   # Replace spaces with underscores to create a valid tag name
   tag_name = "_".join(tag_name_input.split())
   return tag_and_push(tag_name, commit_hash)

def tagging_workflow():
    print()
    you_chose_tagging = colorize("TAGGING Chosen", 46)
    print(you_chose_tagging)
    search_phrase = input("Enter your commit search phrase (or just press enter to see last 200): ")
    commits = find_commits_by_phrase(search_phrase)
    selected_hash = select_commit(commits)
    
    if selected_hash == None:
        main_menu()

    if selected_hash:
        success = tag_commit(selected_hash)
        if not success:
            print("Tagging process failed. Returning to main menu.")
            main_menu()
    
    main_menu()

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
   return user_choice(items, create_prompt, True)

def select_item_or_create_new_branch(items, message, create_prompt):
   print(f"{message}")
   for i, item in enumerate(items):
       print(colorize(f"{chr(ord('a') + i)}) {item}", 33))  # Green color code
   print(colorize(f"z) Create a new {create_prompt}", 32))  # Yellow color code
   return user_choice_tuple(items, create_prompt, True)

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
        selected_branch, wants_to_create_new = select_item_or_create_new_branch(branches, colorize("\nChoose a branch to deploy to:", 43), "branch")
        if wants_to_create_new:  # If the user chose to create a new branch make the new branch
            subprocess.run(f"git branch {selected_branch}", shell=True, check=True)
            print(f"New branch '{selected_branch}' created.")
            permissions['branches'][selected_branch] = []  # Add the selected branch to the list of branches in permissions
            update_permissions_file(permissions, original_branch, permissions_file)  # Update the permissions file

        if selected_branch and check_branch_permissions(selected_branch, permissions):
            tags = get_last_tags()
            selected_tag = select_item(tags, colorize("\nChoose a tag to deploy:", 41))
            if selected_tag:
                deployment_process(selected_tag, original_branch, permissions, selected_branch)
    else:
        print("Error: Unable to read permissions file.")

def select_item(items, message, allow_creation=False):
    print(f"{message}")
    for i, item in enumerate(items):
        print(colorize(f"{chr(ord('a') + i)}) {item}", 35))  # Green color code
    return user_choice(items, allow_creation=allow_creation)

# select one of the previously committed git commits
def user_choice_of_commit_by_number(commits):
    while True:
        try:
            choice = int(input("Select a commit by number (or 0 to cancel): "))
            if choice == 0:
                return None
            if 1 <= choice <= len(commits):
                return commits[choice - 1][0]
            else:
                print("Invalid number, please try again.")
        except ValueError:
            print("Invalid input, please enter a number.")

def user_choice_tuple(items, create_prompt=None, allow_creation=True):
    while True:
        choice = input("Select an item (a, b, c, ..., or z for new): ").lower()
        if choice >= 'a' and choice <= chr(ord('a') + len(items) - 1):
            return items[ord(choice) - ord('a')].lstrip('* '), False
        elif allow_creation and choice == 'z':
            new_item = input(f"Enter a new {create_prompt} name: ")
            return new_item, True
        else:
            print("Invalid choice. Please try again.")

def user_choice(items, create_prompt=None, allow_creation=True):
    while True:
        choice = input("Select an item (a, b, c, ..., or z for new): ").lower()
        if choice >= 'a' and choice <= chr(ord('a') + len(items) - 1):
            return items[ord(choice) - ord('a')].lstrip('* ')
        elif allow_creation and choice == 'z':
            new_item = input(f"Enter a new {create_prompt} name: ")
            return new_item
        else:
            print("Invalid choice. Please try again.")

def tag_and_push(tag_name, commit_hash):
   tag_command = f"git tag {tag_name} {commit_hash}"
   tag_result = subprocess.run(tag_command, shell=True, capture_output=True, text=True)
   push_command = f"git push origin {tag_name}"
   push_result = subprocess.run(push_command, shell=True, capture_output=True, text=True)
   if tag_result.returncode != 0:
       print(f"Tagging failed: {tag_result.stderr}")
       return False
   elif push_result.returncode != 0:
       print(f"Failed to push tag: {push_result.stderr}")
       return False
   else:
       print(colorize(f"Successfully tagged commit {commit_hash} with {tag_name}", 36))
       print("Tag pushed to remote.")
       return True

def deployment_process(selected_tag, original_branch, permissions, selected_branch):
    branches = list_branches()  # Assuming this function fetches a list of all branches
    deploy_to_branch(selected_tag, branches, selected_branch, original_branch)

def deploy_to_branch(selected_tag, branches, selected_branch, original_branch):
    selected_branch = selected_branch.replace('*', '').strip()
    print(colorize(f"\nSelected branch: {selected_branch}\n", 36))
    branch_exists = selected_branch in [branch.strip('* ').strip() for branch in branches]
    default_remote_branch = get_default_remote_branch()

    if selected_branch == default_remote_branch:
        print(f"Error: Deployment to the default remote branch '{default_remote_branch}' is not allowed.")
        return

    # Stash local changes on the current branch before switching
    subprocess.run("git stash push -m 'Auto-stash by deployment process'", shell=True, check=True)

    # Checkout the target branch, create if it doesn't exist
    if not branch_exists:
        subprocess.run(f"git checkout -b {selected_branch}", shell=True, check=True)
        print("New branch created and checked out.")
    else:
        subprocess.run(f"git checkout {selected_branch}", shell=True, check=True)

    # Force update the branch to the selected tag
    deploy_tag(selected_tag, selected_branch)

    # Return to the original branch and apply stashed changes, if any
    subprocess.run(f"git checkout {original_branch}", shell=True, check=True)
    
    # Check if there are stashes to pop
    stash_list_output = subprocess.run("git stash list", shell=True, capture_output=True, text=True).stdout
    if stash_list_output:
        try:
            subprocess.run("git stash pop", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while applying stashed changes: {e}")
    else:
        print("No stash entries found. Nothing to pop.")
    
    print(f"Returned to original branch: {original_branch}\nDeployment complete!")
    main_menu()  # Return to the main menu after deployment is complete

def deploy_tag(tag, branch):
    # Ensure the local repo is aware of all remote tags
    subprocess.run("git fetch --tags", shell=True, check=True)

    # Reset the branch to the state of the specified tag
    subprocess.run(f"git reset --hard {tag}", shell=True, check=True)

    # Force push the branch state to remote, aligning it with the tag
    subprocess.run(f"git push --force origin {branch}", shell=True, check=True)
    print(colorize("Deployment to branch complete! Branch is now at the state of the tag.", 36))

if __name__ == "__main__":
   main_menu(True)
    #show all colors for colorize
    # for i in range(30, 108):
    #     print(f"\033[{i}mColor {i}\033[0m")def list_branches():
