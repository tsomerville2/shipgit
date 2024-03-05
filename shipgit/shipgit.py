import subprocess

def colorize(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def main_menu():
    print(colorize(r"""
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░      ░░░  ░░░░  ░░        ░░       ░░░░░░░░░░      ░░░        ░░        ░
▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒
▓▓      ▓▓▓        ▓▓▓▓▓  ▓▓▓▓▓       ▓▓▓▓▓▓▓▓▓  ▓▓▓   ▓▓▓▓▓  ▓▓▓▓▓▓▓▓  ▓▓▓▓
███████  ██  ████  █████  █████  ██████████████  ████  █████  ████████  ████
██      ███  ████  ██        ██  ███████████████      ███        █████  ████
████████████████████████████████████████████████████████████████████████████                                                                  

    """, 32))
    print(colorize("Select an operation:", 100))
    print(colorize("1) TAGGING", 46))
    print(colorize("2) DEPLOYING", 41))
    choice = input(colorize("Enter your choice (1 or 2): ", 100))
    if choice == '1':
        tagging_workflow()
    elif choice == '2':
        deploying_workflow()
    else:
        print("Invalid choice. Please select 1 or 2.")
        main_menu()

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
   tags = get_last_tags()
   selected_tag = select_item(tags, colorize("\nChoose a tag to deploy:", 41))
   original_branch = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True).stdout.strip()
   if selected_tag:
       deployment_process(selected_tag, original_branch)

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

def deployment_process(selected_tag, original_branch):
   branch_output = subprocess.run("git branch", shell=True, capture_output=True, text=True).stdout
   branches = branch_output.splitlines()
   selected_branch = select_item_or_create_new(branches, colorize("\nChoose a branch to deploy to:", 43), "branch")
   if selected_branch:
       deploy_to_branch(selected_branch, selected_tag, branches, original_branch)

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
    #     print(f"\033[{i}mColor {i}\033[0m")