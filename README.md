# TheGadflyProject
by the VANDALs

## Description
To create a robust, automatic, extensible question generation service.

## Requirements
- Python 3.X
- [spaCy 1.X](https://spacy.io)

## How to use as a library
1. Add the Gadfly Project Repository as a git submodule to your project's git repository `git submodule add https://github.com/TheGadflyProject/TheGadflyProject.git`
2. Navigate to TheGadflyProject directory `cd ./TheGadflyProject`
3. Install Python requirements `pip install -r requirements.txt`
4. Install Spacy Modules `python -m spacy.en.download`
5. You can create generate gapfill questions by:
  - adding `from TheGadflyProject.gadfly.gap_fill_generator import GapFillGenerator` to your python file
  - instantiating the GapFillGenerator by passing it the input text of your choice `g = GapFillGenerator("This is my input texts. "It will probably be much longer than this, hopefully" said Daniel.")`
  - You can access the questions by using questions attribute on the generator object `for q in g.questions: print(q)`
6. You can create generate multiple choice questions by:
  - adding `from TheGadflyProject.gadfly.gap_fill_generator import MCQGenerator` to your python file
  - instantiating the GapFillGenerator by passing it the input text of your choice `g = MCQGenerator("This is my input texts. "It will probably be much longer than this, hopefully" said Daniel.")`
  - You can access the questions by using questions attribute on the generator object `for q in g.questions: print(q)`

## How to Contribute
Review the section on [Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow) to get an overview of the git workflow that we use for this project.  

### Install Requirements
1. Clone the repo `git clone <repo url>`
2. (optionally) Create virtualenv
3. Install Python requirements `pip install -r requirements.txt`
4. Install spaCy Modules `python -m spacy.en.download`

### Add a feature, fix a bug
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

Submit a pull request by navigating to the project Github page and submitting a pull request ([more instructions here](https://help.github.com/articles/using-pull-requests/)). Give your project teammates a few days to review your pull requests and address any questions or feedback that they have on your code and submit additional pull requests as necessary. Once your pull request has been accepted, it will merged for you.

