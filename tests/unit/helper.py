try:
    from unittest import mock
except ImportError:
    import mock
import github3
import unittest


def build_url(self, *args, **kwargs):
    # We want to assert what is happening with the actual calls to the
    # Internet. We can proxy this.
    return github3.session.GitHubSession().build_url(*args, **kwargs)


class UnitHelper(unittest.TestCase):
    # Sub-classes must assign the class to this during definition
    described_class = None
    # Sub-classes must also assign a dictionary to this during definition
    example_data = {}

    def create_mocked_session(self):
        MockedSession = mock.create_autospec(github3.session.GitHubSession)
        return MockedSession()

    def create_session_mock(self, *args):
        session = self.create_mocked_session()
        base_attrs = ['headers', 'auth']
        attrs = dict(
            (key, mock.Mock()) for key in set(args).union(base_attrs)
        )
        session.configure_mock(**attrs)
        session.delete.return_value = None
        session.get.return_value = None
        session.patch.return_value = None
        session.post.return_value = None
        session.put.return_value = None
        return session

    def create_instance_of_described_class(self):
        if self.example_data:
            instance = self.described_class(self.example_data,
                                            self.session)
        else:
            instance = self.described_class()
            instance._session = self.session

        return instance

    def setUp(self):
        self.session = self.create_session_mock()
        self.instance = self.create_instance_of_described_class()
        # Proxy the build_url method to the class so it can build the URL and
        # we can assert things about the call that will be attempted to the
        # internet
        self.described_class._build_url = build_url


class UnitIteratorHelper(UnitHelper):
    def create_session_mock(self, *args):
        # Retrieve a mocked session object
        session = super(UnitIteratorHelper, self).create_mocked_session(*args)
        # Initialize a NullObject
        null = github3.structs.NullObject()
        # Set it as the return value for every method
        session.delete.return_value = null
        session.get.return_value = null
        session.patch.return_value = null
        session.post.return_value = null
        session.put.return_value = null
        return session

    def get_next(self, iterator):
        try:
            next(iterator)
        except StopIteration:
            pass

    def patch_get_json(self):
        """Patch a GitHubIterator's _get_json method"""
        self.get_json_mock = mock.patch.object(
            github3.structs.GitHubIterator, '_get_json'
        )
        self.patched_get_json = self.get_json_mock.start()
        self.patched_get_json.return_value = []

    def setUp(self):
        super(UnitIteratorHelper, self).setUp()
        self.patch_get_json()

    def tearDown(self):
        super(UnitIteratorHelper, self).tearDown()
        self.get_json_mock.stop()
