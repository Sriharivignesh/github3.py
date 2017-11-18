import pytest

from github3 import GitHubError
from github3.github import GitHub

from .helper import UnitHelper, UnitIteratorHelper


def url_for(path=''):
    """Simple function to generate URLs with the base GitHub URL."""
    return 'https://api.github.com/' + path.strip('/')


class TestGitHub(UnitHelper):
    described_class = GitHub
    example_data = None

    def test_authorization(self):
        """Show that a user can retrieve a specific authorization by id."""
        self.instance.authorization(10)

        self.session.get.assert_called_once_with(
            url_for('authorizations/10'),
        )

    def test_authorization_requires_auth(self):
        """A user must be authenticated to retrieve an authorization."""
        self.session.auth = None

        with pytest.raises(GitHubError):
            self.instance.authorization(1)

    def test_authorize(self):
        """Show an authorization can be created for a user."""
        self.instance.authorize('username', 'password', ['user', 'repo'])

        self.session.temporary_basic_auth.assert_called_once_with(
            'username', 'password'
        )
        self.post_called_with(
            url_for('authorizations'),
            data={'note': '', 'note_url': '', 'client_id': '',
                  'client_secret': '', 'scopes': ['user', 'repo']}
        )

    def test_two_factor_login(self):
        """Test the ability to pass two_factor_callback."""
        self.instance.login('username', 'password',
                            two_factor_callback=lambda *args: 'foo')

    def test_can_login_without_two_factor_callback(self):
        """Test that two_factor_callback is not required."""
        self.instance.login('username', 'password')
        self.instance.login(token='token')


class TestGitHubIterators(UnitIteratorHelper):
    described_class = GitHub
    example_data = None

    def test_all_events(self):
        """Show that one can iterate over all public events."""
        i = self.instance.all_events()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('events'),
            params={'per_page': 100},
            headers={}
        )

    def test_all_repositories(self):
        """Show that one can iterate over all repositories."""
        i = self.instance.all_repositories()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('repositories'),
            params={'per_page': 100},
            headers={}
        )

    def test_all_repositories_per_page(self):
        """Show that one can iterate over all repositories with per_page."""
        i = self.instance.all_repositories(per_page=25)
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('repositories'),
            params={'per_page': 25},
            headers={}
        )

    def test_all_repositories_since(self):
        """Show that one can limit the repositories returned."""
        since = 100000
        i = self.instance.all_repositories(since=since)
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

    def test_emails(self):
        """Show that an authenticated user can iterate over their emails."""
        i = self.instance.emails()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/emails'),
            params={'per_page': 100},
            headers={}
        )

    def test_emails_require_auth(self):
        """Show that one needs to authenticate to use #emails."""
        self.session.has_auth.return_value = False
        with pytest.raises(GitHubError):
            self.instance.emails()

    def test_followers(self):
        """
        Show that an authenticated user can iterate over their followers.
        """
        i = self.instance.followers()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/followers'),
            params={'per_page': 100},
            headers={}
        )

    def test_followers_require_auth(self):
        """Show that one needs to authenticate to use #followers."""
        self.session.has_auth.return_value = False
        with pytest.raises(GitHubError):
            self.instance.followers()

    def test_followers_of(self):
        """Show that one can authenticate over the followers of a user."""
        i = self.instance.followers_of('sigmavirus24')
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/followers'),
            params={'per_page': 100},
            headers={}
        )

    def test_following(self):
        """
        Show that an authenticated user can iterate the users they are
        following.
        """
        i = self.instance.following()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/following'),
            params={'per_page': 100},
            headers={}
        )

    def test_following_require_auth(self):
        """Show that one needs to authenticate to use #following."""
        self.session.has_auth.return_value = False
        with pytest.raises(GitHubError):
            self.instance.following()

    def test_followed_by(self):
        """
        Show that one can authenticate over the users followed by another.
        """
        i = self.instance.followed_by('sigmavirus24')
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/following'),
            params={'per_page': 100},
            headers={}
        )

    def test_gists(self):
        """Show that an authenticated user can iterate over their gists."""
        i = self.instance.gists()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('gists'),
            params={'per_page': 100},
            headers={}
        )

    def test_gists_requires_auth(self):
        """Show that one needs to authenticate to use #gists."""
        self.session.has_auth.return_value = False
        with pytest.raises(GitHubError):
            self.instance.gists()

    def test_gists_by(self):
        """Show that an user's gists can be iterated over."""
        i = self.instance.gists_by('sigmavirus24')
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/gists'),
            params={'per_page': 100},
            headers={}
        )

    def test_issues(self):
        """Show that an authenticated user can iterate over their issues."""
        i = self.instance.issues()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('issues'),
            params={'per_page': 100},
            headers={}
        )

    def test_issues_with_params(self):
        """Show that issues can be filtered."""
        params = {'filter': 'assigned', 'state': 'closed', 'labels': 'bug',
                  'sort': 'created', 'direction': 'asc',
                  'since': '2012-05-20T23:10:27Z'}
        p = {'per_page': 100}
        p.update(params)

        i = self.instance.issues(**params)
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('issues'),
            params=p,
            headers={}
        )

    def test_issues_requires_auth(self):
        """Show that one needs to authenticate to use #issues."""
        self.session.has_auth.return_value = False
        with pytest.raises(GitHubError):
            self.instance.issues()

    def test_keys(self):
        """
        Show that an authenticated user can iterate over their public keys.
        """
        i = self.instance.keys()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/keys'),
            params={'per_page': 100},
            headers={}
        )

    def test_keys_requires_auth(self):
        """Show that one needs to authenticate to use #keys."""
        self.session.has_auth.return_value = False
        with pytest.raises(GitHubError):
            self.instance.keys()

    def test_notifications(self):
        """
        Show that an authenticated user can iterate over their notifications.
        """
        i = self.instance.notifications()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('notifications'),
            params={'per_page': 100},
            headers={},
        )

    def test_notifications_participating_in(self):
        """Show that the user can filter by pariticpating."""
        i = self.instance.notifications(participating=True)
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('notifications'),
            params={'per_page': 100, 'participating': True},
            headers={}
        )

    def test_notifications_all(self):
        """Show that the user can iterate over all of their notifications."""
        i = self.instance.notifications(all=True)
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('notifications'),
            params={'per_page': 100, 'all': True},
            headers={}
        )

    def test_notifications_requires_auth(self):
        """Show that one needs to authenticate to use #gists."""
        self.session.has_auth.return_value = False
        with pytest.raises(GitHubError):
            self.instance.notifications()

    def test_organization_issues(self):
        """Show that one can iterate over an organization's issues."""
        i = self.instance.organization_issues('org')
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('orgs/org/issues'),
            params={'per_page': 100},
            headers={}
        )

    def test_organization_issues_with_params(self):
        """Show that one can pass parameters to #organization_issues."""
        params = {'filter': 'assigned', 'state': 'closed', 'labels': 'bug',
                  'sort': 'created', 'direction': 'asc',
                  'since': '2012-05-20T23:10:27Z'}
        i = self.instance.organization_issues('org', **params)
        self.get_next(i)

        p = {'per_page': 100}
        p.update(params)

        self.session.get.assert_called_once_with(
            url_for('orgs/org/issues'),
            params=p,
            headers={}
        )

    def test_organization_issues_requires_auth(self):
        """Show that one needs to authenticate to use #organization_issues."""
        self.session.has_auth.return_value = False

        with pytest.raises(GitHubError):
            self.instance.organization_issues('org')

    def test_organizations(self):
        """
        Show that one can iterate over all of the authenticated user's orgs.
        """
        i = self.instance.organizations()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/orgs'),
            params={'per_page': 100},
            headers={}
        )

    def test_organizations_requires_auth(self):
        """Show that one needs to authenticate to use #organizations."""
        self.session.has_auth.return_value = False

        with pytest.raises(GitHubError):
            self.instance.organizations()

    def test_organizations_with(self):
        """Show that one can iterate over all of a user's orgs."""
        i = self.instance.organizations_with('sigmavirus24')
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/orgs'),
            params={'per_page': 100},
            headers={}
        )

    def test_public_gists(self):
        """Show that all public gists can be iterated over."""
        i = self.instance.public_gists()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('gists/public'),
            params={'per_page': 100},
            headers={}
        )

    def test_respositories(self):
        """
        Show that an authenticated user can iterate over their repositories.
        """
        i = self.instance.repositories()
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/repos'),
            params={'per_page': 100},
            headers={}
        )

    def test_respositories_accepts_params(self):
        """Show that an #repositories accepts params."""
        i = self.instance.repositories(type='all',
                                       direction='desc',
                                       sort='created')
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('user/repos'),
            params={'per_page': 100, 'type': 'all', 'direction': 'desc',
                    'sort': 'created'},
            headers={}
        )

    def test_repositories_requires_auth(self):
        """Show that one needs to authenticate to use #repositories."""
        self.session.has_auth.return_value = False

        with pytest.raises(GitHubError):
            self.instance.repositories()

    def test_repository_issues(self):
        """Show that a user can iterate over a repository's issues."""
        i = self.instance.repository_issues('owner', 'repo')
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('repos/owner/repo/issues'),
            params={'per_page': 100},
            headers={}
        )

    def test_repository_issues_with_params(self):
        """Show that #repository_issues accepts multiple parameters."""
        params = {'milestone': 1, 'state': 'all', 'assignee': 'owner',
                  'mentioned': 'someone', 'labels': 'bug,high'}
        i = self.instance.repository_issues('owner', 'repo', **params)
        self.get_next(i)

        params.update(per_page=100)

        self.session.get.assert_called_once_with(
            url_for('repos/owner/repo/issues'),
            params=params,
            headers={}
        )

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

    def test_repositories_by(self):
        """Test that one can iterate over a user's repositories."""
        i = self.instance.repositories_by('sigmavirus24')

        # Get the next item from the iterator
        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/repos'),
            params={'per_page': 100},
            headers={}
        )

    def test_repositories_by_with_type(self):
        """
        Test that one can iterate over a user's repositories with a type.
        """
        i = self.instance.repositories_by('sigmavirus24', 'all')

        self.get_next(i)

        self.session.get.assert_called_once_with(
            url_for('users/sigmavirus24/repos'),
            params={'per_page': 100, 'type': 'all'},
            headers={}
        )
