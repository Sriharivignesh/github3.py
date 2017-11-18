import github3
from unittest import TestCase
#from .utils.mock import patch, NonCallableMock
from .utils import mock


class TestAPI(TestCase):
    def setUp(self):
        self.mock = mock.patch('github3.api.gh', autospec=github3.GitHub)
        self.gh = self.mock.start()

    def tearDown(self):
        self.mock.stop()

    def test_repository(self):
        args = ('owner', 'repo')
        github3.repository(*args)
        self.gh.repository.assert_called_with(*args)

    def test_user(self):
        github3.user('login')
        self.gh.user.assert_called_with('login')

    def test_rate_limit(self):
        github3.rate_limit()
        self.gh.rate_limit.assert_called_once_with()

    def test_zen(self):
        github3.zen()
        assert self.gh.zen.called is True
