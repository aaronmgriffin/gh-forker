import github
from github.GithubException import UnknownObjectException

class GithubForker(object):
    def __init__(self, access_token):
        self.gh = github.Github(access_token)
        self.user = self.gh.get_user()

    def repo_exists(self, repo):
        repo_name = repo.split('/')[-1]
        try:
            return self.user.get_repo(repo_name) != None
        except UnknownObjectException:
            return False

    def fork_from(self, repo):
        # Forking a repo is a relatively straightforward use of
        # github's API, but PyGithub is gonna make this a lot easier...
        if self.repo_exists(repo):
            return 'Repo already exists, rename or delete gh-forker to use this tool.'
        else:
            self.user.create_fork(self.gh.get_repo(repo))
            # for fun, maybe...
            #repo.create_file('created-by-gh-forker', 'Add created-by file', '')
            return 'Forking gh-forker. Please give github a few moments...'
