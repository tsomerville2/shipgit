# Ship It - CI/CD Philosophy and Workflow

Ship It embraces a CI/CD philosophy that encourages developers to code on the main branch and commit changes daily. This approach keeps the main branch somewhat volatile but ensures that the codebase is always moving forward with incremental changes.

To manage this volatility and identify stable or QA-ready states, we use a tagging system. Tags are applied to commits on the main branch that represent good release candidates or versions that have passed certain quality assurance checks.

Once a commit is tagged, it can be pulled onto a new branch, which Ship It does under the Deploy path. It is expected that action workflows are set up by someone else and when Ship It pulls to that branch it's triggered. Depending on the branch, this could trigger updates to a production server tied to a specific URL, a UAT server, or any other environment as required.

In our CI/CD workflow, branches represent individual customers or important machines. Each customer branch receives a forced copy of the tag from the main branch. This ensures that each customer has a version of the software that has been certified and tagged as stable from the main development line.

The use of branches in this way allows for a clear separation of concerns. The main branch remains the hub of continuous integration and development, while branches serve as stable snapshots for deployment to customer-specific environments. This strategy allows for a flexible yet controlled deployment process, catering to the unique needs of each customer.

Remember, the success of this CI/CD approach relies on diligent and frequent integration, clear tagging of stable commits, and well-defined action workflows to handle the deployment process. Happy shipping!

# Ship It commands

Ship It provides two main interactive commands that users can choose from within the menu:

1. **TAGGING**: This command allows users to create a tag for a specific commit. The user is prompted to enter a search phrase to find commits, select the desired commit from a list, and then provide a tag name. The tag is then created and pushed to the remote repository.

2. **DEPLOYING**: This command is used to deploy a specific tag to a branch. The user selects a tag from a list of the most recent tags and then chooses a branch to deploy to. If the branch does not exist, it is created. The selected tag is then merged into the chosen branch and pushed to the remote repository, effectively deploying the code.

These commands are part of an interactive menu that guides the user through the process, ensuring that the CI/CD workflow is followed and that the main branch and customer-specific branches are managed effectively.
