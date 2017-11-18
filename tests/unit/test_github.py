import pytest

from github3 import GitHubError
from github3.github import GitHub

from .helper import UnitHelper, UnitIteratorHelper


def url_for(path=''):
    return 'https://api.github.com/' + path.strip('/')


class TestGitHub(UnitHelper):
    described_class = GitHub
    example_data = None

    def test_two_factor_login(self):
        self.instance.login('username', 'password',
                            two_factor_callback=lambda *args: 'foo')

    def test_can_login_without_two_factor_callback(self):
        self.instance.login('username', 'password')
        self.instance.login(token='token')


class TestGitHubIterators(UnitIteratorHelper):
    described_class = GitHub
    example_data = None

    def test_all_repos(self):
        """Show that one can iterate over all repositories."""
        i = self.instance.all_repos()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('repositories'),
            params={'per_page': 100},
            headers={}
        )

    def test_all_repos_per_page(self):
        """Show that one can iterate over all repositories with per_page."""
        i = self.instance.all_repos(per_page=25)
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('repositories'),
            params={'per_page': 25},
            headers={}
        )

    def test_all_repos_since(self):
        """Show that one can limit the repositories returned."""
        since = 100000
        i = self.instance.all_repos(since=since)
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('repositories'),
            params={'per_page': 100, 'since': since},
            headers={}
        )

    def test_all_users(self):
        """Show that one can iterate over all users."""
        i = self.instance.all_users()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users'),
            params={'per_page': 100},
            headers={}
        )

    def test_all_users_per_page(self):
        """Show that one can iterate over all users with per_page."""
        i = self.instance.all_users(per_page=25)
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users'),
            params={'per_page': 25},
            headers={}
        )

    def test_all_users_since(self):
        """Show that one can limit the users returned."""
        since = 100000
        i = self.instance.all_users(since=since)
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users'),
            params={'per_page': 100, 'since': since},
            headers={}
        )

    def test_authorizations(self):
        """
        Show that an authenticated user can iterate over their authorizations.
        """
        i = self.instance.authorizations()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('authorizations'),
            params={'per_page': 100},
            headers={}
        )

    def test_authorizations_requires_auth(self):
        """Show that one needs to authenticate to use #authorizations."""
        self.session.auth = None
        with pytest.raises(GitHubError):
            self.instance.authorizations()

    def test_starred(self):
        """
        Show that one can iterate over an authenticated user's stars.
        """
        i = self.instance.starred()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/starred'),
            params={'per_page': 100},
            headers={}
        )

    def test_starred_requires_auth(self):
        """Show that one needs to authenticate to use #starred."""
        self.session.has_auth.return_value = False
        with pytest.raises(GitHubError):
            self.instance.starred()

    def test_starred_by(self):
        """Show that one can iterate over a user's stars."""
        i = self.instance.starred_by('sigmavirus24')
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/starred'),
            params={'per_page': 100},
            headers={}
        )

    def test_subscriptions(self):
        """
        Show that one can iterate over an authenticated user's subscriptions.
        """
        i = self.instance.subscriptions()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/subscriptions'),
            params={'per_page': 100},
            headers={}
        )

    def test_subscriptions_for(self):
        """Show that one can iterate over a user's subscriptions."""
        i = self.instance.subscriptions_for('sigmavirus24')
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/subscriptions'),
            params={'per_page': 100},
            headers={}
        )

    def test_user_issues(self):
        """Test that one can iterate over a user's issues."""
        i = self.instance.user_issues()
        # Get the next item from the iterator
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/issues'),
            params={'per_page': 100},
            headers={}
        )

    def test_user_issues_requires_auth(self):
        """
        Test that one must authenticate to interate over a user's issues.
        """
        self.session.has_auth.return_value = False
        with pytest.raises(GitHubError):
            self.instance.user_issues()

    def test_user_issues_with_parameters(self):
        """Test that one may pass parameters to GitHub#user_issues."""
        # Set up the parameters to be sent
        params = {'filter': 'assigned', 'state': 'closed', 'labels': 'bug',
                  'sort': 'created', 'direction': 'asc',
                  'since': '2012-05-20T23:10:27Z', 'per_page': 25}

        # Make the call with the paramters
        i = self.instance.user_issues(**params)
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/issues'),
            params=params,
            headers={}
        )

    def test_user_repos(self):
        """Test that one can iterate over a user's repositories."""
        i = self.instance.user_repos('sigmavirus24')

        # Get the next item from the iterator
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/repos'),
            params={'per_page': 100},
            headers={}
        )

    def test_user_repos_with_type(self):
        """
        Test that one can iterate over a user's repositories with a type.
        """
        i = self.instance.user_repos('sigmavirus24', 'all')

        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/repos'),
            params={'per_page': 100, 'type': 'all'},
            headers={}
        )
