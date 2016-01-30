# TheGadflyProject
by the Vandals

## Description
To create a robust, automatic, extensible question generation service.

## How to Contribute
Review the section on [Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow) to get an overview of how to contribute to this project.  

Clone the repo.  
`git clone <repo url>`

Create a new branch for the feature that you are working on. You should not be developing on the master branch. "Feature branches should have descriptive names, like animated-menu-items or issue-#1061. The idea is to give a clear, highly-focused purpose to each branch."   
`git checkout -b <feature_name>`

Focus on committing your code often to the branch. Each commit should have a useful commit message that explains what has been commited.  
`git add <all_files_to_include_in_commit>`  
`git commit -m "<useful_commit_message>`

When you feel like you have completed working on your feature, review the commits on your branch.  
`git log --oneline`

During this step, you may recognize that several commits can/should be collapsed into one commit. You can/should edit your git commit history by using the following command. Read the following link on [git rebase -i](https://github.com/vijayv/TheGadflyProject/new/master?readme=1). Combine/split your commits into an easy to follow history.  
`git rebase -i`

Push your branch to remote.  
`git push origin <branch_name>`

Submit a pull request by navigating to the project Github page and submitting a pull request ([More Instructions Here](https://help.github.com/articles/using-pull-requests/)). Give your project teammates a few days to review your pull requests and address any questions or feedback that they have on your code and submit additional pull requests as necessary. Once your pull request has been accepted, you may merge to master and push to origin.

## References
Coming Soon
