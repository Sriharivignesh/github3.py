"""Integration tests for Repositories."""
import github3

from .helper import IntegrationHelper


class TestRepository(IntegrationHelper):

    """Integration tests for the Repository object."""

    def test_assignees(self):
        """Test the ability to retrieve assignees of issues on a repo."""
        cassette_name = self.cassette_name('assignees')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('kennethreitz', 'requests')
            assert repository is not None
            for assignee in repository.assignees():
                assert isinstance(assignee, github3.users.User)

    def test_branches(self):
        """Test the ability to retrieve the brances in a repository."""
        cassette_name = self.cassette_name('branches')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            for branch in repository.branches():
                assert isinstance(branch, github3.repos.branch.Branch)

    def test_code_frequency(self):
        """Test the ability to retrieve the code frequency in a repo."""
        cassette_name = self.cassette_name('code_frequency')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            for code_freq in repository.code_frequency():
                assert isinstance(code_freq, list)
                assert len(code_freq) > 0

    def test_collaborators(self):
        """Test the ability to retrieve the collaborators on a repository."""
        cassette_name = self.cassette_name('collaborators')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            for collaborator in repository.collaborators():
                assert isinstance(collaborator, github3.users.User)

    def test_comments(self):
        """Test the ability to retrieve comments on a repository."""
        cassette_name = self.cassette_name('comments')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            for comment in repository.comments():
                assert isinstance(comment, github3.repos.comment.RepoComment)

    def test_comments_on_commit(self):
        """Test the ability to retrieve the comments on a commit."""
        sha = '65c0c7d58b3ef09a0b3d5f9779228f9d1a5ad552'
        cassette_name = self.cassette_name('comments_on_commit')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('glynnis',
                                            'Madison-Women-in-Tech')
            assert repository is not None
            for comment in repository.comments_on_commit(sha):
                assert isinstance(comment, github3.repos.comment.RepoComment)

    def test_commit_activity(self):
        """Test the ability to retrieve commit activity on a repo."""
        cassette_name = self.cassette_name('commit_activity')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            for activity in repository.commit_activity():
                assert isinstance(activity, dict)

    def test_commits(self):
        """Test the ability to retrieve commits on a repository."""
        cassette_name = self.cassette_name('commits')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            for commit in repository.commits(number=25):
                assert isinstance(commit, github3.repos.commit.RepoCommit)

    def test_contributor_statistics(self):
        """Test the ability to retrieve contributor statistics for a repo."""
        cassette_name = self.cassette_name('contributor_statistics')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            for stat in repository.contributor_statistics():
                assert isinstance(stat, github3.repos.stats.ContributorStats)

    def test_contributors(self):
        """Test the ability to retrieve the contributors to a repository."""
        cassette_name = self.cassette_name('contributors')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            for contributor in repository.contributors():
                assert isinstance(contributor, github3.users.User)
                assert isinstance(contributor.contributions, int)

    def test_create_empty_blob(self):
        """Test the ability to create an empty blob on a repository."""
        self.basic_login()
        cassette_name = self.cassette_name('create_empty_blob')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('github3py', 'fork_this')
            assert repository is not None
            blob_sha = repository.create_blob('', 'utf-8')

        assert blob_sha is not None
        assert blob_sha != ''

    def test_create_deployment(self):
        """Test the ability to create a deployment for a repository."""
        self.basic_login()
        cassette_name = self.cassette_name('create_deployment')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            deployment = repository.create_deployment('0.8.2')

        assert isinstance(deployment, github3.repos.deployment.Deployment)

    def test_create_release(self):
        """Test the ability to create a release on a repository."""
        self.token_login()
        cassette_name = self.cassette_name('create_release')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'charade')
            assert repository is not None
            release = repository.create_release(
                '1.0.3.test', 'f1d4e150be7070adfbbdca164328d69723e096ec',
                'Test release'
                )

        assert isinstance(release, github3.repos.release.Release)

    def test_deployments(self):
        """Test that a repository's deployments may be retrieved."""
        cassette_name = self.cassette_name('deployments')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            for d in repository.deployments():
                assert isinstance(d, github3.repos.deployment.Deployment)

    def test_events(self):
        """Test that a user can iterate over the events from a repository."""
        cassette_name = self.cassette_name('events')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            events = list(repository.events(number=100))

        assert len(events) > 0
        for event in events:
            assert isinstance(event, github3.events.Event)

    def test_forks(self):
        """Test that a user can iterate over the forks of a repository."""
        cassette_name = self.cassette_name('forks')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            forks = list(repository.forks())

        assert len(forks) > 0
        for fork in forks:
            assert isinstance(fork, github3.repos.Repository)

    def test_hooks(self):
        """Test that a user can iterate over the hooks of a repository."""
        self.basic_login()
        cassette_name = self.cassette_name('hooks')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            hooks = list(repository.hooks())

        assert len(hooks) > 0
        for hook in hooks:
            assert isinstance(hook, github3.repos.hook.Hook)

    def test_ignore(self):
        """Test that a user can ignore the notifications on a repository."""
        self.basic_login()
        cassette_name = self.cassette_name('ignore')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('jnewland',
                                            'gmond_python_modules')
            assert repository is not None
            subscription = repository.ignore()
            assert subscription.ignored is True

    def test_issue_events(self):
        """Test that a user can iterate over issue events in a repo."""
        cassette_name = self.cassette_name('issue_events')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            events = list(repository.issue_events(number=50))

        for ev in events:
            assert isinstance(ev, github3.issues.event.IssueEvent)

    def test_issues_sorts_ascendingly(self):
        """Test that issues will be returned in ascending order."""
        cassette_name = self.cassette_name('issues_ascending')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'betamax')
            assert repository is not None
            issues = list(repository.issues(direction='asc'))

        assert len(issues) > 0
        last_issue = None
        for issue in issues:
            assert isinstance(issue, github3.issues.Issue)
            if last_issue:
                assert last_issue.number < issue.number
            last_issue = issue

    def test_issues_accepts_state_all(self):
        """Test that the state parameter accets 'all'."""
        cassette_name = self.cassette_name('issues_state_all')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'betamax')
            assert repository is not None
            for issue in repository.issues(state='all'):
                assert issue.state in ('open', 'closed')

    def test_key(self):
        self.basic_login()
        cassette_name = self.cassette_name('key')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            key = repository.key(8820641)

        assert isinstance(key, github3.users.Key)

    def test_keys(self):
        """Test that the user can retrieve all deploy keys."""
        self.basic_login()
        cassette_name = self.cassette_name('keys')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            keys = list(repository.keys())

        assert len(keys) > 0
        for key in keys:
            assert isinstance(key, github3.users.Key)

    def test_labels(self):
        """Test that a user can retrieve a repository's labels."""
        cassette_name = self.cassette_name('labels')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            labels = list(repository.labels())

        assert len(labels) > 0
        for label in labels:
            assert isinstance(label, github3.issues.label.Label)

    def test_languages(self):
        """Test that a repository's languages can be retrieved."""
        cassette_name = self.cassette_name('languages')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            for l in repository.languages():
                assert 'ETag' not in l
                assert 'Last-Modified' not in l
                assert isinstance(l, tuple)

    def test_milestone(self):
        """Test the ability to retrieve a milestone on a repository."""
        cassette_name = self.cassette_name('milestone')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            milestone = repository.milestone(7)
        assert isinstance(milestone, github3.issues.milestone.Milestone)

    def test_milestones(self):
        """Test the ability to retrieve the milestones in a repository."""
        cassette_name = self.cassette_name('milestones')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            milestones = list(repository.milestones())

        assert len(milestones) > 0
        for milestone in milestones:
            assert isinstance(milestone, github3.issues.milestone.Milestone)

    def test_network_events(self):
        """Test that a user can retrieve the events of a repo's network."""
        cassette_name = self.cassette_name('network_events')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            events = list(repository.network_events())

        assert len(events) > 0
        for event in events:
            assert isinstance(event, github3.events.Event)

    def test_notifications(self):
        """Test that a user can retrieve their repo notifications."""
        self.basic_login()
        cassette_name = self.cassette_name('notifications')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            notifications = list(repository.notifications())

        assert len(notifications) > 0
        for notification in notifications:
            assert isinstance(notification, github3.notifications.Thread)

    def test_pull_requests(self):
        """Test that a user can retrieve the pull requests from a repo."""
        cassette_name = self.cassette_name('pull_requests')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            pulls = list(repository.pull_requests())

        assert len(pulls) > 0
        for pull in pulls:
            assert isinstance(pull, github3.pulls.PullRequest)

    def test_pull_requests_accepts_sort_and_direction(self):
        """Test that pull_requests now takes a sort parameter."""
        cassette_name = self.cassette_name('pull_requests_accept_sort')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'betamax')
            assert repository is not None
            last_pr = None
            for pr in repository.pull_requests(sort='updated',
                                               direction='asc'):
                assert pr is not None
                if last_pr:
                    assert last_pr.updated_at < pr.updated_at
                last_pr = pr

    def test_iter_releases(self):
        """Test the ability to iterate over releases on a repository."""
        cassette_name = self.cassette_name('iter_releases')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            for release in repository.iter_releases():
                assert isinstance(release, github3.repos.release.Release)

    def test_release(self):
        """Test the ability to retrieve a single release."""
        cassette_name = self.cassette_name('release')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('sigmavirus24', 'github3.py')
            assert repository is not None
            release = repository.release(76677)

        assert isinstance(release, github3.repos.release.Release)

    def test_subscription(self):
        """Test the ability to subscribe to a repository's notifications."""
        self.basic_login()
        cassette_name = self.cassette_name('subscription')
        with self.recorder.use_cassette(cassette_name):
            repository = self.gh.repository('vcr', 'vcr')
            assert repository is not None
            subscription = repository.subscribe()
            assert subscription.subscribed is True
