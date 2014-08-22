"""Integration tests for the User class."""
import github3

from .helper import IntegrationHelper


class TestUser(IntegrationHelper):

    """Integration tests for methods on the User class."""

    def test_events(self):
        """Show that a user can retrieve a events performed by a user."""
        cassette_name = self.cassette_name('events')
        with self.recorder.use_cassette(cassette_name):
            user = self.gh.user('sigmavirus24')
            events = list(user.events(25))

        assert len(events) > 0
        for event in events:
            assert isinstance(event, github3.events.Event)

    def test_followers(self):
        """Show that a user can retrieve any user's followers."""
        cassette_name = self.cassette_name('followers')
        with self.recorder.use_cassette(cassette_name):
            user = self.gh.user('sigmavirus24')
            followers = list(user.followers(50))

        assert len(followers) > 0
        for follower in followers:
            assert isinstance(follower, github3.users.User)

    def test_following(self):
        """Show that a user can retrieve users that a user is following."""
        cassette_name = self.cassette_name('following')
        with self.recorder.use_cassette(cassette_name):
            user = self.gh.user('sigmavirus24')
            following = list(user.following(50))

        assert len(following) > 0
        for person in following:
            assert isinstance(person, github3.users.User)

    def test_keys(self):
        """Show that a user can retrieve any user's public keys."""
        cassette_name = self.cassette_name('keys')
        with self.recorder.use_cassette(cassette_name):
            user = self.gh.user('sigmavirus24')
            keys = list(user.keys())

        assert len(keys) > 0
        for key in keys:
            assert isinstance(key, github3.users.Key)

    def test_organizations(self):
        """Show that a user can retrieve any user's organizations."""
        cassette_name = self.cassette_name('organizations')
        with self.recorder.use_cassette(cassette_name):
            u = self.gh.user('sigmavirus24')
            for o in u.organizations(number=25):
                assert isinstance(o, github3.orgs.Organization)
