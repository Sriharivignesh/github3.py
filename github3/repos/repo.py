# -*- coding: utf-8 -*-
"""
github3.repos.repo
==================

This module contains the Repository object which is used to access the various
parts of GitHub's Repository API.

"""
from __future__ import unicode_literals

from json import dumps
from base64 import b64encode
from ..decorators import requires_auth
from ..events import Event
from ..git import Blob, Commit, Reference, Tag, Tree
from ..issues import issue_params, Issue
from ..issues.event import IssueEvent
from ..issues.label import Label
from ..issues.milestone import Milestone
from ..models import GitHubCore
from ..notifications import Subscription, Thread
from ..pulls import PullRequest
from .branch import Branch
from .comment import RepoComment
from .commit import RepoCommit
from .comparison import Comparison
from .contents import Contents, validate_commmitter
from .deployment import Deployment
from .hook import Hook
from .pages import PagesBuild, PagesInfo
from .status import Status
from .stats import ContributorStats
from .release import Release, Asset
from .tag import RepoTag
from ..users import User, Key
from ..utils import stream_response_to_file, timestamp_parameter
from uritemplate import URITemplate


class Repository(GitHubCore):

    """The :class:`Repository <Repository>` object. It represents how GitHub
    sends information about repositories.

    Two repository instances can be checked like so::

        r1 == r2
        r1 != r2

    And is equivalent to::

        r1.id == r2.id
        r1.id != r2.id

    See also: http://developer.github.com/v3/repos/

    """

    def __init__(self, repo, session=None):
        super(Repository, self).__init__(repo, session)
        #: URL used to clone via HTTPS.
        self.clone_url = repo.get('clone_url', '')
        #: ``datetime`` object representing when the Repository was created.
        self.created_at = self._strptime(repo.get('created_at'))
        #: Description of the repository.
        self.description = repo.get('description', '')

        # The number of forks
        #: The number of forks made of this repository. DEPRECATED
        self.forks = repo.get('forks', 0)

        #: The number of forks of this repository.
        self.forks_count = repo.get('forks_count')
        # For backward compatibility
        self.fork_count = self.forks_count

        #: Is this repository a fork?
        self.fork = repo.get('fork')

        #: Full name as login/name
        self.full_name = repo.get('full_name', '')

        # Clone url using git, e.g. git://github.com/sigmavirus24/github3.py
        #: Plain git url for an anonymous clone.
        self.git_url = repo.get('git_url', '')
        #: Whether or not this repository has downloads enabled
        self.has_downloads = repo.get('has_downloads')
        #: Whether or not this repository has an issue tracker
        self.has_issues = repo.get('has_issues')
        #: Whether or not this repository has the wiki enabled
        self.has_wiki = repo.get('has_wiki')

        # e.g. https://sigmavirus24.github.com/github3.py
        #: URL of the home page for the project.
        self.homepage = repo.get('homepage', '')

        # e.g. https://github.com/sigmavirus24/github3.py
        #: URL of the project at GitHub.
        self.html_url = repo.get('html_url', '')
        #: Unique id of the repository.
        self.id = repo.get('id', 0)
        #: Language property.
        self.language = repo.get('language', '')
        #: Mirror property.
        self.mirror_url = repo.get('mirror_url', '')

        # Repository name, e.g. github3.py
        #: Name of the repository.
        self.name = repo.get('name', '')

        #: Number of open issues on the repository. DEPRECATED
        self.open_issues = repo.get('open_issues', 0)

        #: Number of open issues on the repository
        self.open_issues_count = repo.get('open_issues_count')

        # Repository owner's name
        #: :class:`User <github3.users.User>` object representing the
        #: repository owner.
        self.owner = User(repo.get('owner', {}), self._session)

        #: Is this repository private?
        self.private = repo.get('private')
        #: ``datetime`` object representing the last time commits were pushed
        #: to the repository.
        self.pushed_at = self._strptime(repo.get('pushed_at'))
        #: Size of the repository.
        self.size = repo.get('size', 0)

        # The number of stargazers
        #: Number of users who starred the repository
        self.stargazers = repo.get('stargazers_count', 0)

        # SSH url e.g. git@github.com/sigmavirus24/github3.py
        #: URL to clone the repository via SSH.
        self.ssh_url = repo.get('ssh_url', '')
        #: If it exists, url to clone the repository via SVN.
        self.svn_url = repo.get('svn_url', '')
        #: ``datetime`` object representing the last time the repository was
        #: updated.
        self.updated_at = self._strptime(repo.get('updated_at'))
        self._api = repo.get('url', '')

        # The number of watchers
        #: Number of users watching the repository.
        self.watchers = repo.get('watchers', 0)

        #: Parent of this fork, if it exists :class:`Repository`
        self.source = repo.get('source')
        if self.source:
            self.source = Repository(self.source, self)

        #: Parent of this fork, if it exists :class:`Repository`
        self.parent = repo.get('parent')
        if self.parent:
            self.parent = Repository(self.parent, self)

        #: default branch for the repository
        self.default_branch = repo.get('default_branch', '')

        #: master (default) branch for the repository
        self.master_branch = repo.get('master_branch', '')

        #: Teams url (not a template)
        self.teams_url = repo.get('teams_url', '')

        #: Hooks url (not a template)
        self.hooks_url = repo.get('hooks_url', '')

        #: Events url (not a template)
        self.events_url = repo.get('events_url', '')

        #: Tags url (not a template)
        self.tags_url = repo.get('tags_url', '')

        #: Languages url (not a template)
        self.languages_url = repo.get('languages_url', '')

        #: Stargazers url (not a template)
        self.stargazers_url = repo.get('stargazers_url', '')

        #: Contributors url (not a template)
        self.contributors_url = repo.get('contributors_url', '')

        #: Subscribers url (not a template)
        self.subscribers_url = repo.get('subscribers_url', '')

        #: Subscription url (not a template)
        self.subscription_url = repo.get('subscription_url', '')

        #: Merges url (not a template)
        self.merges_url = repo.get('merges_url', '')

        #: Downloads url (not a template)
        self.download_url = repo.get('downloads_url', '')

        ## Template URLS
        ie_url_t = repo.get('issue_events_url')
        #: Issue events URL Template. Expand with ``number``
        self.issue_events_urlt = URITemplate(ie_url_t) if ie_url_t else None

        assignees = repo.get('assignees_url')
        #: Assignees URL Template. Expand with ``user``
        self.assignees_urlt = URITemplate(assignees) if assignees else None

        branches = repo.get('branches_url')
        #: Branches URL Template. Expand with ``branch``
        self.branches_urlt = URITemplate(branches) if branches else None

        blobs = repo.get('blobs_url')
        #: Blobs URL Template. Expand with ``sha``
        self.blobs_urlt = URITemplate(blobs) if blobs else None

        git_tags = repo.get('git_tags_url')
        #: Git tags URL Template. Expand with ``sha``
        self.git_tags_urlt = URITemplate(git_tags) if git_tags else None

        git_refs = repo.get('git_refs_url')
        #: Git refs URL Template. Expand with ``sha``
        self.git_refs_urlt = URITemplate(git_refs) if git_refs else None

        trees = repo.get('trees_url')
        #: Trres URL Template. Expand with ``sha``
        self.trees_urlt = URITemplate(trees) if trees else None

        statuses = repo.get('statuses_url')
        #: Statuses URL Template. Expand with ``sha``
        self.statuses_urlt = URITemplate(statuses) if statuses else None

        commits = repo.get('commits_url')
        #: Commits URL Template. Expand with ``sha``
        self.commits_urlt = URITemplate(commits) if commits else None

        commits = repo.get('git_commits_url')
        #: Git commits URL Template. Expand with ``sha``
        self.git_commits_urlt = URITemplate(commits) if commits else None

        comments = repo.get('comments_url')
        #: Comments URL Template. Expand with ``number``
        self.comments_urlt = URITemplate(comments) if comments else None

        comments = repo.get('issue_comment_url')
        #: Issue comment URL Template. Expand with ``number``
        self.issue_comment_urlt = URITemplate(comments) if comments else None

        contents = repo.get('contents_url')
        #: Contents URL Template. Expand with ``path``
        self.contents_urlt = URITemplate(contents) if contents else None

        compare = repo.get('compare_url')
        #: Comparison URL Template. Expand with ``base`` and ``head``
        self.compare_urlt = URITemplate(compare) if compare else None

        archive = repo.get('archive_url')
        #: Archive URL Template. Expand with ``archive_format`` and ``ref``
        self.archive_urlt = URITemplate(archive) if archive else None

        issues = repo.get('issues_url')
        #: Issues URL Template. Expand with ``number``
        self.issues_urlt = URITemplate(issues) if issues else None

        pulls = repo.get('pulls_url')
        #: Pull Requests URL Template. Expand with ``number``
        self.pulls_urlt = URITemplate(pulls) if issues else None

        miles = repo.get('milestones_url')
        #: Milestones URL Template. Expand with ``number``
        self.milestones_urlt = URITemplate(miles) if miles else None

        notif = repo.get('notifications_url')
        #: Notifications URL Template. Expand with ``since``, ``all``,
        #: ``participating``
        self.notifications_urlt = URITemplate(notif) if notif else None

        labels = repo.get('labels_url')
        #: Labels URL Template. Expand with ``name``
        self.labels_urlt = URITemplate(labels) if labels else None

    def _repr(self):
        return '<Repository [{0}]>'.format(self)

    def __str__(self):
        return self.full_name

    def _update_(self, repo):
        self.__init__(repo, self._session)

    def _create_pull(self, data):
        self._remove_none(data)
        json = None
        if data:
            url = self._build_url('pulls', base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return PullRequest(json, self._session) if json else None

    @requires_auth
    def add_collaborator(self, login):
        """Add ``login`` as a collaborator to a repository.

        :param str login: (required), login of the user
        :returns: bool -- True if successful, False otherwise
        """
        resp = False
        if login:
            url = self._build_url('collaborators', login, base_url=self._api)
            resp = self._boolean(self._put(url), 204, 404)
        return resp

    def archive(self, format, path='', ref='master'):
        """Get the tarball or zipball archive for this repo at ref.

        See: http://developer.github.com/v3/repos/contents/#get-archive-link

        :param str format: (required), accepted values: ('tarball',
            'zipball')
        :param path: (optional), path where the file should be saved
            to, default is the filename provided in the headers and will be
            written in the current directory.
            it can take a file-like object as well
        :type path: str, file
        :param str ref: (optional)
        :returns: bool -- True if successful, False otherwise

        """
        resp = None
        if format in ('tarball', 'zipball'):
            url = self._build_url(format, ref, base_url=self._api)
            resp = self._get(url, allow_redirects=True, stream=True)

        if resp and self._boolean(resp, 200, 404):
            stream_response_to_file(resp, path)
            return True
        return False

    def asset(self, id):
        """Returns a single Asset.

        :param int id: (required), id of the asset
        :returns: :class:`Asset <github3.repos.release.Asset>`
        """
        data = None
        if int(id) > 0:
            url = self._build_url('releases', 'assets', str(id),
                                  base_url=self._api)
            data = self._json(self._get(url, headers=Release.CUSTOM_HEADERS),
                              200)
        return Asset(data, self) if data else None

    def blob(self, sha):
        """Get the blob indicated by ``sha``.

        :param str sha: (required), sha of the blob
        :returns: :class:`Blob <github3.git.Blob>` if successful, otherwise
            None
        """
        url = self._build_url('git', 'blobs', sha, base_url=self._api)
        json = self._json(self._get(url), 200)
        return Blob(json) if json else None

    def branch(self, name):
        """Get the branch ``name`` of this repository.

        :param str name: (required), branch name
        :type name: str
        :returns: :class:`Branch <github3.repos.branch.Branch>`
        """
        json = None
        if name:
            url = self._build_url('branches', name, base_url=self._api)
            json = self._json(self._get(url), 200)
        return Branch(json, self) if json else None

    def commit(self, sha):
        """Get a single (repo) commit. See :func:`git_commit` for the Git Data
        Commit.

        :param str sha: (required), sha of the commit
        :returns: :class:`RepoCommit <github3.repos.commit.RepoCommit>` if
            successful, otherwise None
        """
        url = self._build_url('commits', sha, base_url=self._api)
        json = self._json(self._get(url), 200)
        return RepoCommit(json, self) if json else None

    def commit_comment(self, comment_id):
        """Get a single commit comment.

        :param int comment_id: (required), id of the comment used by GitHub
        :returns: :class:`RepoComment <github3.repos.comment.RepoComment>` if
            successful, otherwise None
        """
        url = self._build_url('comments', str(comment_id), base_url=self._api)
        json = self._json(self._get(url), 200)
        return RepoComment(json, self) if json else None

    def compare_commits(self, base, head):
        """Compare two commits.

        :param str base: (required), base for the comparison
        :param str head: (required), compare this against base
        :returns: :class:`Comparison <github3.repos.comparison.Comparison>` if
            successful, else None
        """
        url = self._build_url('compare', base + '...' + head,
                              base_url=self._api)
        json = self._json(self._get(url), 200)
        return Comparison(json) if json else None

    def contents(self, path, ref=None):
        """Get the contents of the file pointed to by ``path``.

        If the path provided is actually a directory, you will receive a
        dictionary back of the form::

            {
                'filename.md': Contents(),  # Where Contents an instance
                'github.py': Contents(),
            }

        :param str path: (required), path to file, e.g.
            github3/repo.py
        :param str ref: (optional), the string name of a commit/branch/tag.
            Default: master
        :returns: :class:`Contents <github3.repos.contents.Contents>` or dict
            if successful, else None
        """
        url = self._build_url('contents', path, base_url=self._api)
        json = self._json(self._get(url, params={'ref': ref}), 200)
        if isinstance(json, dict):
            return Contents(json, self)
        elif isinstance(json, list):
            return dict((j.get('name'), Contents(j, self)) for j in json)
        return None

    @requires_auth
    def create_blob(self, content, encoding):
        """Create a blob with ``content``.

        :param str content: (required), content of the blob
        :param str encoding: (required), ('base64', 'utf-8')
        :returns: string of the SHA returned
        """
        sha = ''
        if encoding in ('base64', 'utf-8'):
            url = self._build_url('git', 'blobs', base_url=self._api)
            data = {'content': content, 'encoding': encoding}
            json = self._json(self._post(url, data=data), 201)
            if json:
                sha = json.get('sha')
        return sha

    @requires_auth
    def create_comment(self, body, sha, path=None, position=None, line=1):
        """Create a comment on a commit.

        :param str body: (required), body of the message
        :param str sha: (required), commit id
        :param str path: (optional), relative path of the file to comment
            on
        :param str position: (optional), line index in the diff to comment on
        :param int line: (optional), line number of the file to comment on,
            default: 1
        :returns: :class:`RepoComment <github3.repos.comment.RepoComment>` if
            successful, otherwise None

        """
        json = None
        if body and sha and (line and int(line) > 0):
            data = {'body': body, 'line': line, 'path': path,
                    'position': position}
            self._remove_none(data)
            url = self._build_url('commits', sha, 'comments',
                                  base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return RepoComment(json, self) if json else None

    @requires_auth
    def create_commit(self, message, tree, parents, author={}, committer={}):
        """Create a commit on this repository.

        :param str message: (required), commit message
        :param str tree: (required), SHA of the tree object this
            commit points to
        :param list parents: (required), SHAs of the commits that were parents
            of this commit. If empty, the commit will be written as the root
            commit.  Even if there is only one parent, this should be an
            array.
        :param dict author: (optional), if omitted, GitHub will
            use the authenticated user's credentials and the current
            time. Format: {'name': 'Committer Name', 'email':
            'name@example.com', 'date': 'YYYY-MM-DDTHH:MM:SS+HH:00'}
        :param dict committer: (optional), if ommitted, GitHub will use the
            author parameters. Should be the same format as the author
            parameter.
        :returns: :class:`Commit <github3.git.Commit>` if successful, else
            None
        """
        json = None
        if message and tree and isinstance(parents, list):
            url = self._build_url('git', 'commits', base_url=self._api)
            data = {'message': message, 'tree': tree, 'parents': parents,
                    'author': author, 'committer': committer}
            json = self._json(self._post(url, data=data), 201)
        return Commit(json, self) if json else None

    @requires_auth
    def create_deployment(self, ref, force=False, payload='',
                          auto_merge=False, description='', environment=None):
        """Create a deployment.

        :param str ref: (required), The ref to deploy. This can be a branch,
            tag, or sha.
        :param bool force: Optional parameter to bypass any ahead/behind
            checks or commit status checks. Default: False
        :param str payload: Optional JSON payload with extra information about
            the deployment. Default: ""
        :param bool auto_merge: Optional parameter to merge the default branch
            into the requested deployment branch if necessary. Default: False
        :param str description: Optional short description. Default: ""
        :param str environment: Optional name for the target deployment
            environment (e.g., production, staging, qa). Default: "production"
        :returns: :class:`Deployment <github3.repos.deployment.Deployment>`
        """
        json = None
        if ref:
            url = self._build_url('deployments', base_url=self._api)
            data = {'ref': ref, 'force': force, 'payload': payload,
                    'auto_merge': auto_merge, 'description': description,
                    'environment': environment}
            self._remove_none(data)
            headers = Deployment.CUSTOM_HEADERS
            json = self._json(self._post(url, data=data, headers=headers),
                              201)
        return Deployment(json, self) if json else None

    @requires_auth
    def create_file(self, path, message, content, branch=None,
                    committer=None, author=None):
        """Create a file in this repository.

        See also: http://developer.github.com/v3/repos/contents/#create-a-file

        :param str path: (required), path of the file in the repository
        :param str message: (required), commit message
        :param bytes content: (required), the actual data in the file
        :param str branch: (optional), branch to create the commit on.
            Defaults to the default branch of the repository
        :param dict committer: (optional), if no information is given the
            authenticated user's information will be used. You must specify
            both a name and email.
        :param dict author: (optional), if omitted this will be filled in with
            committer information. If passed, you must specify both a name and
            email.
        :returns: {
            'content': :class:`Contents <github3.repos.contents.Contents>`:,
            'commit': :class:`Commit <github3.git.Commit>`}

        """
        if content and not isinstance(content, bytes):
            raise ValueError(  # (No coverage)
                'content must be a bytes object')  # (No coverage)

        json = None
        if path and message and content:
            url = self._build_url('contents', path, base_url=self._api)
            content = b64encode(content).decode('utf-8')
            data = {'message': message, 'content': content, 'branch': branch,
                    'committer': validate_commmitter(committer),
                    'author': validate_commmitter(author)}
            self._remove_none(data)
            json = self._json(self._put(url, data=dumps(data)), 201)
            if 'content' in json and 'commit' in json:
                json['content'] = Contents(json['content'], self)
                json['commit'] = Commit(json['commit'], self)
        return json

    @requires_auth
    def create_fork(self, organization=None):
        """Create a fork of this repository.

        :param str organization: (required), login for organization to create
            the fork under
        :returns: :class:`Repository <Repository>` if successful, else None
        """
        url = self._build_url('forks', base_url=self._api)
        if organization:
            resp = self._post(url, data={'organization': organization})
        else:
            resp = self._post(url)
        json = self._json(resp, 202)

        return Repository(json, self) if json else None

    @requires_auth
    def create_hook(self, name, config, events=['push'], active=True):
        """Create a hook on this repository.

        :param str name: (required), name of the hook
        :param dict config: (required), key-value pairs which act as settings
            for this hook
        :param list events: (optional), events the hook is triggered for
        :param bool active: (optional), whether the hook is actually
            triggered
        :returns: :class:`Hook <github3.repos.hook.Hook>` if successful,
            otherwise None
        """
        json = None
        if name and config and isinstance(config, dict):
            url = self._build_url('hooks', base_url=self._api)
            data = {'name': name, 'config': config, 'events': events,
                    'active': active}
            json = self._json(self._post(url, data=data), 201)
        return Hook(json, self) if json else None

    @requires_auth
    def create_issue(self,
                     title,
                     body=None,
                     assignee=None,
                     milestone=None,
                     labels=None):
        """Creates an issue on this repository.

        :param str title: (required), title of the issue
        :param str body: (optional), body of the issue
        :param str assignee: (optional), login of the user to assign the
            issue to
        :param int milestone: (optional), id number of the milestone to
            attribute this issue to (e.g. ``m`` is a :class:`Milestone
            <github3.issues.milestone.Milestone>` object, ``m.number`` is
            what you pass here.)
        :param labels: (optional), labels to apply to this
            issue
        :type labels: list of strings
        :returns: :class:`Issue <github3.issues.issue.Issue>` if successful,
            otherwise None
        """
        issue = {'title': title, 'body': body, 'assignee': assignee,
                 'milestone': milestone, 'labels': labels}
        self._remove_none(issue)
        json = None

        if issue:
            url = self._build_url('issues', base_url=self._api)
            json = self._json(self._post(url, data=issue), 201)

        return Issue(json, self) if json else None

    @requires_auth
    def create_key(self, title, key):
        """Create a deploy key.

        :param str title: (required), title of key
        :param str key: (required), key text
        :returns: :class:`Key <github3.users.Key>` if successful, else None
        """
        json = None
        if title and key:
            data = {'title': title, 'key': key}
            url = self._build_url('keys', base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return Key(json, self) if json else None

    @requires_auth
    def create_label(self, name, color):
        """Create a label for this repository.

        :param str name: (required), name to give to the label
        :param str color: (required), value of the color to assign to the
            label, e.g., '#fafafa' or 'fafafa' (the latter is what is sent)
        :returns: :class:`Label <github3.issues.label.Label>` if successful,
            else None
        """
        json = None
        if name and color:
            data = {'name': name, 'color': color.strip('#')}
            url = self._build_url('labels', base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return Label(json, self) if json else None

    @requires_auth
    def create_milestone(self, title, state=None, description=None,
                         due_on=None):
        """Create a milestone for this repository.

        :param str title: (required), title of the milestone
        :param str state: (optional), state of the milestone, accepted
            values: ('open', 'closed'), default: 'open'
        :param str description: (optional), description of the milestone
        :param str due_on: (optional), ISO 8601 formatted due date
        :returns: :class:`Milestone <github3.issues.milestone.Milestone>` if
            successful, otherwise None
        """
        url = self._build_url('milestones', base_url=self._api)
        if state not in ('open', 'closed'):
            state = None
        data = {'title': title, 'state': state,
                'description': description, 'due_on': due_on}
        self._remove_none(data)
        json = None
        if data:
            json = self._json(self._post(url, data=data), 201)
        return Milestone(json, self) if json else None

    @requires_auth
    def create_pull(self, title, base, head, body=None):
        """Create a pull request of ``head`` onto ``base`` branch in this repo.

        :param str title: (required)
        :param str base: (required), e.g., 'master'
        :param str head: (required), e.g., 'username:branch'
        :param str body: (optional), markdown formatted description
        :returns: :class:`PullRequest <github3.pulls.PullRequest>` if
            successful, else None
        """
        data = {'title': title, 'body': body, 'base': base,
                'head': head}
        return self._create_pull(data)

    @requires_auth
    def create_pull_from_issue(self, issue, base, head):
        """Create a pull request from issue #``issue``.

        :param int issue: (required), issue number
        :param str base: (required), e.g., 'master'
        :param str head: (required), e.g., 'username:branch'
        :returns: :class:`PullRequest <github3.pulls.PullRequest>` if
            successful, else None
        """
        if int(issue) > 0:
            data = {'issue': issue, 'base': base, 'head': head}
            return self._create_pull(data)
        return None

    @requires_auth
    def create_ref(self, ref, sha):
        """Create a reference in this repository.

        :param str ref: (required), fully qualified name of the reference,
            e.g. ``refs/heads/master``. If it doesn't start with ``refs`` and
            contain at least two slashes, GitHub's API will reject it.
        :param str sha: (required), SHA1 value to set the reference to
        :returns: :class:`Reference <github3.git.Reference>` if successful
            else None
        """
        json = None
        if ref and ref.count('/') >= 2 and sha:
            data = {'ref': ref, 'sha': sha}
            url = self._build_url('git', 'refs', base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return Reference(json, self) if json else None

    @requires_auth
    def create_release(self, tag_name, target_commitish=None, name=None,
                       body=None, draft=False, prerelease=False):
        """Create a release for this repository.

        :param str tag_name: (required), name to give to the tag
        :param str target_commitish: (optional), vague concept of a target,
            either a SHA or a branch name.
        :param str name: (optional), name of the release
        :param str body: (optional), description of the release
        :param bool draft: (optional), whether this release is a draft or not
        :param bool prerelease: (optional), whether this is a prerelease or
            not
        :returns: :class:`Release <github3.repos.release.Release>`
        """
        data = {'tag_name': str(tag_name),
                'target_commitish': target_commitish,
                'name': name,
                'body': body,
                'draft': draft,
                'prerelease': prerelease
                }
        self._remove_none(data)

        url = self._build_url('releases', base_url=self._api)
        json = self._json(self._post(
            url, data=data, headers=Release.CUSTOM_HEADERS
            ), 201)
        return Release(json, self)

    @requires_auth
    def create_status(self, sha, state, target_url='', description=''):
        """Create a status object on a commit.

        :param str sha: (required), SHA of the commit to create the status on
        :param str state: (required), state of the test; only the following
            are accepted: 'pending', 'success', 'error', 'failure'
        :param str target_url: (optional), URL to associate with this status.
        :param str description: (optional), short description of the status
        """
        json = {}
        if sha and state:
            data = {'state': state, 'target_url': target_url,
                    'description': description}
            url = self._build_url('statuses', sha, base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return Status(json) if json else None

    @requires_auth
    def create_tag(self, tag, message, sha, obj_type, tagger,
                   lightweight=False):
        """Create a tag in this repository.

        :param str tag: (required), name of the tag
        :param str message: (required), tag message
        :param str sha: (required), SHA of the git object this is tagging
        :param str obj_type: (required), type of object being tagged, e.g.,
            'commit', 'tree', 'blob'
        :param dict tagger: (required), containing the name, email of the
            tagger and the date it was tagged
        :param bool lightweight: (optional), if False, create an annotated
            tag, otherwise create a lightweight tag (a Reference).
        :returns: If lightweight == False: :class:`Tag <github3.git.Tag>` if
            successful, else None. If lightweight == True: :class:`Reference
            <github3.git.Reference>`
        """
        if lightweight and tag and sha:
            return self.create_ref('refs/tags/' + tag, sha)

        json = None
        if tag and message and sha and obj_type and len(tagger) == 3:
            data = {'tag': tag, 'message': message, 'object': sha,
                    'type': obj_type, 'tagger': tagger}
            url = self._build_url('git', 'tags', base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
            if json:
                self.create_ref('refs/tags/' + tag, sha)
        return Tag(json) if json else None

    @requires_auth
    def create_tree(self, tree, base_tree=''):
        """Create a tree on this repository.

        :param list tree: (required), specifies the tree structure.
            Format: [{'path': 'path/file', 'mode':
            'filemode', 'type': 'blob or tree', 'sha': '44bfc6d...'}]
        :param str base_tree: (optional), SHA1 of the tree you want
            to update with new data
        :returns: :class:`Tree <github3.git.Tree>` if successful, else None
        """
        json = None
        if tree and isinstance(tree, list):
            data = {'tree': tree, 'base_tree': base_tree}
            url = self._build_url('git', 'trees', base_url=self._api)
            json = self._json(self._post(url, data=data), 201)
        return Tree(json) if json else None

    @requires_auth
    def delete(self):
        """Delete this repository.

        :returns: bool -- True if successful, False otherwise
        """
        return self._boolean(self._delete(self._api), 204, 404)

    @requires_auth
    def delete_file(self, path, message, sha, branch=None, committer=None,
                    author=None):
        """Delete the file located at ``path``.

        This is part of the Contents CrUD (Create Update Delete) API. See
        http://developer.github.com/v3/repos/contents/#delete-a-file for more
        information.

        :param str path: (required), path to the file being removed
        :param str message: (required), commit message for the deletion
        :param str sha: (required), blob sha of the file being removed
        :param str branch: (optional), if not provided, uses the repository's
            default branch
        :param dict committer: (optional), if no information is given the
            authenticated user's information will be used. You must specify
            both a name and email.
        :param dict author: (optional), if omitted this will be filled in with
            committer information. If passed, you must specify both a name and
            email.
        :returns: :class:`Commit <github3.git.Commit>` if successful

        """
        json = None
        if path and message and sha:
            url = self._build_url('contents', path, base_url=self._api)
            data = {'message': message, 'sha': sha, 'branch': branch,
                    'committer': validate_commmitter(committer),
                    'author': validate_commmitter(author)}
            self._remove_none(data)
            json = self._json(self._delete(url, data=dumps(data)), 200)
            if json and 'commit' in json:
                json = Commit(json['commit'])
        return json

    @requires_auth
    def delete_key(self, key_id):
        """Delete the key with the specified id from your deploy keys list.

        :returns: bool -- True if successful, False otherwise
        """
        if int(key_id) <= 0:
            return False
        url = self._build_url('keys', str(key_id), base_url=self._api)
        return self._boolean(self._delete(url), 204, 404)

    @requires_auth
    def delete_subscription(self):
        """Delete the user's subscription to this repository.

        :returns: bool
        """
        url = self._build_url('subscription', base_url=self._api)
        return self._boolean(self._delete(url), 204, 404)

    @requires_auth
    def edit(self,
             name,
             description=None,
             homepage=None,
             private=None,
             has_issues=None,
             has_wiki=None,
             has_downloads=None,
             default_branch=None):
        """Edit this repository.

        :param str name: (required), name of the repository
        :param str description: (optional), If not ``None``, change the
            description for this repository. API default: ``None`` - leave
            value unchanged.
        :param str homepage: (optional), If not ``None``, change the homepage
            for this repository. API default: ``None`` - leave value unchanged.
        :param bool private: (optional), If ``True``, make the repository
            private. If ``False``, make the repository public. API default:
            ``None`` - leave value unchanged.
        :param bool has_issues: (optional), If ``True``, enable issues for
            this repository. If ``False``, disable issues for this repository.
            API default: ``None`` - leave value unchanged.
        :param bool has_wiki: (optional), If ``True``, enable the wiki for
            this repository. If ``False``, disable the wiki for this
            repository. API default: ``None`` - leave value unchanged.
        :param bool has_downloads: (optional), If ``True``, enable downloads
            for this repository. If ``False``, disable downloads for this
            repository. API default: ``None`` - leave value unchanged.
        :param str default_branch: (optional), If not ``None``, change the
            default branch for this repository. API default: ``None`` - leave
            value unchanged.
        :returns: bool -- True if successful, False otherwise
        """
        edit = {'name': name, 'description': description, 'homepage': homepage,
                'private': private, 'has_issues': has_issues,
                'has_wiki': has_wiki, 'has_downloads': has_downloads,
                'default_branch': default_branch}
        self._remove_none(edit)
        json = None
        if edit:
            json = self._json(self._patch(self._api, data=dumps(edit)), 200)
            self._update_(json)
            return True
        return False

    def is_collaborator(self, login):
        """Check to see if ``login`` is a collaborator on this repository.

        :param str login: (required), login for the user
        :returns: bool -- True if successful, False otherwise
        """
        if login:
            url = self._build_url('collaborators', login, base_url=self._api)
            return self._boolean(self._get(url), 204, 404)
        return False

    def git_commit(self, sha):
        """Get a single (git) commit.

        :param str sha: (required), sha of the commit
        :returns: :class:`Commit <github3.git.Commit>` if successful,
            otherwise None
        """
        json = {}
        if sha:
            url = self._build_url('git', 'commits', sha, base_url=self._api)
            json = self._json(self._get(url), 200)
        return Commit(json, self) if json else None

    @requires_auth
    def hook(self, id_num):
        """Get a single hook.

        :param int id_num: (required), id of the hook
        :returns: :class:`Hook <github3.repos.hook.Hook>` if successful,
            otherwise None
        """
        json = None
        if int(id_num) > 0:
            url = self._build_url('hooks', str(id_num), base_url=self._api)
            json = self._json(self._get(url), 200)
        return Hook(json, self) if json else None

    @requires_auth
    def ignore(self):
        """Ignore notifications from this repository for the user.

        .. versionadded:: 1.0

        This replaces ``Repository#set_subscription``.

        :returns: :class:`Subscription <github3.notifications.Subscription>`
        """
        url = self._build_url('subscription', base_url=self._api)
        json = self._json(self._put(url, data=dumps({'ignored': True})), 200)
        return Subscription(json, self) if json else None

    def is_assignee(self, login):
        """Check if the user is a possible assignee for an issue on this
        repository.

        :returns: :class:`bool`
        """
        if not login:
            return False
        url = self._build_url('assignees', login, base_url=self._api)
        return self._boolean(self._get(url), 204, 404)

    def issue(self, number):
        """Get the issue specified by ``number``.

        :param int number: (required), number of the issue on this repository
        :returns: :class:`Issue <github3.issues.issue.Issue>` if successful,
            otherwise None
        """
        json = None
        if int(number) > 0:
            url = self._build_url('issues', str(number), base_url=self._api)
            json = self._json(self._get(url), 200)
        return Issue(json, self) if json else None

    @requires_auth
    def key(self, id_num):
        """Get the specified deploy key.

        :param int id_num: (required), id of the key
        :returns: :class:`Key <github3.users.Key>` if successful, else None
        """
        json = None
        if int(id_num) > 0:
            url = self._build_url('keys', str(id_num), base_url=self._api)
            json = self._json(self._get(url), 200)
        return Key(json, self) if json else None

    def label(self, name):
        """Get the label specified by ``name``

        :param str name: (required), name of the label
        :returns: :class:`Label <github3.issues.label.Label>` if successful,
            else None
        """
        json = None
        if name:
            url = self._build_url('labels', name, base_url=self._api)
            json = self._json(self._get(url), 200)
        return Label(json, self) if json else None

    @requires_auth
    def latest_pages_build(self):
        """Get the build information for the most recent Pages build.

        :returns: :class:`PagesBuild <github3.repos.pages.PagesBuild>`
        """
        url = self._build_url('pages', 'builds', 'latest', base_url=self._api)
        json = self._json(self._get(url), 200)
        return PagesBuild(json) if json else None

    def iter_assignees(self, number=-1, etag=None):
        """Iterate over all available assignees to which an issue may be
        assigned.

        :param int number: (optional), number of assignees to return. Default:
            -1 returns all available assignees
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`User <github3.users.User>`\ s
        """
        url = self._build_url('assignees', base_url=self._api)
        return self._iter(int(number), url, User, etag=etag)

    def iter_branches(self, number=-1, etag=None):
        """Iterate over the branches in this repository.

        :param int number: (optional), number of branches to return. Default:
            -1 returns all branches
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of
            :class:`Branch <github3.repos.branch.Branch>`\ es
        """
        url = self._build_url('branches', base_url=self._api)
        return self._iter(int(number), url, Branch, etag=etag)

    def iter_code_frequency(self, number=-1, etag=None):
        """Iterate over the code frequency per week.

        Returns a weekly aggregate of the number of additions and deletions
        pushed to this repository.

        :param int number: (optional), number of weeks to return. Default: -1
            returns all weeks
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of lists ``[seconds_from_epoch, additions,
            deletions]``

        .. note:: All statistics methods may return a 202. On those occasions,
                  you will not receive any objects. You should store your
                  iterator and check the new ``last_status`` attribute. If it
                  is a 202 you should wait before re-requesting.

        .. versionadded:: 0.7

        """
        url = self._build_url('stats', 'code_frequency', base_url=self._api)
        return self._iter(int(number), url, list, etag=etag)

    def iter_collaborators(self, number=-1, etag=None):
        """Iterate over the collaborators of this repository.

        :param int number: (optional), number of collaborators to return.
            Default: -1 returns all collaborators
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`User <github3.users.User>`\ s
        """
        url = self._build_url('collaborators', base_url=self._api)
        return self._iter(int(number), url, User, etag=etag)

    def iter_comments(self, number=-1, etag=None):
        """Iterate over comments on all commits in the repository.

        :param int number: (optional), number of comments to return. Default:
            -1 returns all comments
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of
            :class:`RepoComment <github3.repos.comment.RepoComment>`\ s
        """
        url = self._build_url('comments', base_url=self._api)
        return self._iter(int(number), url, RepoComment, etag=etag)

    def iter_comments_on_commit(self, sha, number=1, etag=None):
        """Iterate over comments for a single commit.

        :param sha: (required), sha of the commit to list comments on
        :type sha: str
        :param int number: (optional), number of comments to return. Default:
            -1 returns all comments
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of
            :class:`RepoComment <github3.repos.comment.RepoComment>`\ s
        """
        url = self._build_url('commits', sha, 'comments', base_url=self._api)
        return self._iter(int(number), url, RepoComment, etag=etag)

    def iter_commit_activity(self, number=-1, etag=None):
        """Iterate over last year of commit activity by week.

        See: http://developer.github.com/v3/repos/statistics/

        :param int number: (optional), number of weeks to return. Default -1
            will return all of the weeks.
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of dictionaries

        .. note:: All statistics methods may return a 202. On those occasions,
                  you will not receive any objects. You should store your
                  iterator and check the new ``last_status`` attribute. If it
                  is a 202 you should wait before re-requesting.

        .. versionadded:: 0.7

        """
        url = self._build_url('stats', 'commit_activity', base_url=self._api)
        return self._iter(int(number), url, dict, etag=etag)

    def iter_commits(self, sha=None, path=None, author=None, number=-1,
                     etag=None, since=None, until=None):
        """Iterate over commits in this repository.

        :param str sha: (optional), sha or branch to start listing commits
            from
        :param str path: (optional), commits containing this path will be
            listed
        :param str author: (optional), GitHub login, real name, or email to
            filter commits by (using commit author)
        :param int number: (optional), number of commits to return. Default:
            -1 returns all commits
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :param since: (optional), Only commits after this date will
            be returned. This can be a `datetime` or an `ISO8601` formatted
            date string.
        :type since: datetime or string
        :param until: (optional), Only commits before this date will
            be returned. This can be a `datetime` or an `ISO8601` formatted
            date string.
        :type until: datetime or string

        :returns: generator of
            :class:`RepoCommit <github3.repos.commit.RepoCommit>`\ s
        """
        params = {'sha': sha, 'path': path, 'author': author,
                  'since': timestamp_parameter(since),
                  'until': timestamp_parameter(until)}

        self._remove_none(params)
        url = self._build_url('commits', base_url=self._api)
        return self._iter(int(number), url, RepoCommit, params, etag)

    def iter_contributors(self, anon=False, number=-1, etag=None):
        """Iterate over the contributors to this repository.

        :param bool anon: (optional), True lists anonymous contributors as
            well
        :param int number: (optional), number of contributors to return.
            Default: -1 returns all contributors
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`User <github3.users.User>`\ s
        """
        url = self._build_url('contributors', base_url=self._api)
        params = {}
        if anon:
            params = {'anon': True}
        return self._iter(int(number), url, User, params, etag)

    def iter_contributor_statistics(self, number=-1, etag=None):
        """Iterate over the contributors list.

        See also: http://developer.github.com/v3/repos/statistics/

        :param int number: (optional), number of weeks to return. Default -1
            will return all of the weeks.
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of
            :class:`ContributorStats <github3.repos.stats.ContributorStats>`

        .. note:: All statistics methods may return a 202. On those occasions,
                  you will not receive any objects. You should store your
                  iterator and check the new ``last_status`` attribute. If it
                  is a 202 you should wait before re-requesting.

        .. versionadded:: 0.7

        """
        url = self._build_url('stats', 'contributors', base_url=self._api)
        return self._iter(int(number), url, ContributorStats, etag=etag)

    def iter_deployments(self, number=-1, etag=None):
        """Iterate over deployments for this repository.

        :param int number: (optional), number of deployments to return.
            Default: -1, returns all available deployments
        :param str etag: (optional), ETag from a previous request for all
            deployments
        :returns: generator of
            :class:`Deployment <github3.repos.deployment.Deployment>`\ s
        """
        url = self._build_url('deployments', base_url=self._api)
        i = self._iter(int(number), url, Deployment, etag=etag)
        i.headers.update(Deployment.CUSTOM_HEADERS)
        return i

    def iter_events(self, number=-1, etag=None):
        """Iterate over events on this repository.

        :param int number: (optional), number of events to return. Default: -1
            returns all available events
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`Event <github3.events.Event>`\ s
        """
        url = self._build_url('events', base_url=self._api)
        return self._iter(int(number), url, Event, etag=etag)

    def iter_forks(self, sort='', number=-1, etag=None):
        """Iterate over forks of this repository.

        :param str sort: (optional), accepted values:
            ('newest', 'oldest', 'watchers'), API default: 'newest'
        :param int number: (optional), number of forks to return. Default: -1
            returns all forks
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`Repository <Repository>`
        """
        url = self._build_url('forks', base_url=self._api)
        params = {}
        if sort in ('newest', 'oldest', 'watchers'):
            params = {'sort': sort}
        return self._iter(int(number), url, Repository, params, etag)

    @requires_auth
    def iter_hooks(self, number=-1, etag=None):
        """Iterate over hooks registered on this repository.

        :param int number: (optional), number of hoks to return. Default: -1
            returns all hooks
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`Hook <github3.repos.hook.Hook>`\ s
        """
        url = self._build_url('hooks', base_url=self._api)
        return self._iter(int(number), url, Hook, etag=etag)

    def iter_issues(self,
                    milestone=None,
                    state=None,
                    assignee=None,
                    mentioned=None,
                    labels=None,
                    sort=None,
                    direction=None,
                    since=None,
                    number=-1,
                    etag=None):
        """Iterate over issues on this repo based upon parameters passed.

        .. versionchanged:: 0.9.0

            The ``state`` parameter now accepts 'all' in addition to 'open'
            and 'closed'.

        :param int milestone: (optional), 'none', or '*'
        :param str state: (optional), accepted values: ('all', 'open',
            'closed')
        :param str assignee: (optional), 'none', '*', or login name
        :param str mentioned: (optional), user's login name
        :param str labels: (optional), comma-separated list of labels, e.g.
            'bug,ui,@high'
        :param sort: (optional), accepted values:
            ('created', 'updated', 'comments', 'created')
        :param str direction: (optional), accepted values: ('asc', 'desc')
        :param since: (optional), Only issues after this date will
            be returned. This can be a `datetime` or an `ISO8601` formatted
            date string, e.g., 2012-05-20T23:10:27Z
        :type since: datetime or string
        :param int number: (optional), Number of issues to return.
            By default all issues are returned
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`Issue <github3.issues.issue.Issue>`\ s
        """
        url = self._build_url('issues', base_url=self._api)

        params = {'assignee': assignee, 'mentioned': mentioned}
        if milestone in ('*', 'none') or isinstance(milestone, int):
            params['milestone'] = milestone
        self._remove_none(params)
        params.update(
            issue_params(None, state, labels, sort, direction,
                         since)
        )

        return self._iter(int(number), url, Issue, params, etag)

    def iter_issue_events(self, number=-1, etag=None):
        """Iterates over issue events on this repository.

        :param int number: (optional), number of events to return. Default: -1
            returns all available events
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of
            :class:`IssueEvent <github3.issues.event.IssueEvent>`\ s
        """
        url = self._build_url('issues', 'events', base_url=self._api)
        return self._iter(int(number), url, IssueEvent, etag=etag)

    @requires_auth
    def iter_keys(self, number=-1, etag=None):
        """Iterates over deploy keys on this repository.

        :param int number: (optional), number of keys to return. Default: -1
            returns all available keys
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`Key <github3.users.Key>`\ s
        """
        url = self._build_url('keys', base_url=self._api)
        return self._iter(int(number), url, Key, etag=etag)

    def iter_labels(self, number=-1, etag=None):
        """Iterates over labels on this repository.

        :param int number: (optional), number of labels to return. Default: -1
            returns all available labels
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`Label <github3.issues.label.Label>`\ s
        """
        url = self._build_url('labels', base_url=self._api)
        return self._iter(int(number), url, Label, etag=etag)

    def iter_languages(self, number=-1, etag=None):
        """Iterate over the programming languages used in the repository.

        :param int number: (optional), number of languages to return. Default:
            -1 returns all used languages
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of tuples
        """
        url = self._build_url('languages', base_url=self._api)
        return self._iter(int(number), url, tuple, etag=etag)

    def iter_milestones(self, state=None, sort=None, direction=None,
                        number=-1, etag=None):
        """Iterates over the milestones on this repository.

        :param str state: (optional), state of the milestones, accepted
            values: ('open', 'closed')
        :param str sort: (optional), how to sort the milestones, accepted
            values: ('due_date', 'completeness')
        :param str direction: (optional), direction to sort the milestones,
            accepted values: ('asc', 'desc')
        :param int number: (optional), number of milestones to return.
            Default: -1 returns all milestones
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of
            :class:`Milestone <github3.issues.milestone.Milestone>`\ s
        """
        url = self._build_url('milestones', base_url=self._api)
        accepted = {'state': ('open', 'closed'),
                    'sort': ('due_date', 'completeness'),
                    'direction': ('asc', 'desc')}
        params = {'state': state, 'sort': sort, 'direction': direction}
        for (k, v) in list(params.items()):
            if not (v and (v in accepted[k])):  # e.g., '' or None
                del params[k]
        if not params:
            params = None
        return self._iter(int(number), url, Milestone, params, etag)

    def iter_network_events(self, number=-1, etag=None):
        """Iterates over events on a network of repositories.

        :param int number: (optional), number of events to return. Default: -1
            returns all available events
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`Event <github3.events.Event>`\ s
        """
        base = self._api.replace('repos', 'networks', 1)
        url = self._build_url('events', base_url=base)
        return self._iter(int(number), url, Event, etag)

    @requires_auth
    def iter_notifications(self, all=False, participating=False, since=None,
                           number=-1, etag=None):
        """Iterates over the notifications for this repository.

        :param bool all: (optional), show all notifications, including ones
            marked as read
        :param bool participating: (optional), show only the notifications the
            user is participating in directly
        :param since: (optional), filters out any notifications updated
            before the given time. This can be a `datetime` or an `ISO8601`
            formatted date string, e.g., 2012-05-20T23:10:27Z
        :type since: datetime or string
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`Thread <github3.notifications.Thread>`
        """
        url = self._build_url('notifications', base_url=self._api)
        params = {
            'all': all,
            'participating': participating,
            'since': timestamp_parameter(since)
        }
        for (k, v) in list(params.items()):
            if not v:
                del params[k]
        return self._iter(int(number), url, Thread, params, etag)

    @requires_auth
    def iter_pages_builds(self, number=-1, etag=None):
        """Iterate over pages builds of this repository.

        :returns: generator of :class:`PagesBuild
            <github3.repos.pages.PagesBuild>`
        """
        url = self._build_url('pages', 'builds', base_url=self._api)
        return self._iter(int(number), url, PagesBuild, etag=etag)

    def iter_pulls(self, state=None, head=None, base=None, sort='created',
                   direction='desc', number=-1, etag=None):
        """List pull requests on repository.

        .. versionchanged:: 0.9.0

            - The ``state`` parameter now accepts 'all' in addition to 'open'
              and 'closed'.

            - The ``sort`` parameter was added.

            - The ``direction`` parameter was added.

        :param str state: (optional), accepted values: ('all', 'open',
            'closed')
        :param str head: (optional), filters pulls by head user and branch
            name in the format ``user:ref-name``, e.g., ``seveas:debian``
        :param str base: (optional), filter pulls by base branch name.
            Example: ``develop``.
        :param str sort: (optional), Sort pull requests by ``created``,
            ``updated``, ``popularity``, ``long-running``. Default: 'created'
        :param str direction: (optional), Choose the direction to list pull
            requests. Accepted values: ('desc', 'asc'). Default: 'desc'
        :param int number: (optional), number of pulls to return. Default: -1
            returns all available pull requests
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of
            :class:`PullRequest <github3.pulls.PullRequest>`\ s
        """
        url = self._build_url('pulls', base_url=self._api)
        params = {}
        if state and state.lower() in ('all', 'open', 'closed'):
            params['state'] = state.lower()
        params.update(head=head, base=base, sort=sort, direction=direction)
        self._remove_none(params)
        return self._iter(int(number), url, PullRequest, params, etag)

    def iter_refs(self, subspace='', number=-1, etag=None):
        """Iterates over references for this repository.

        :param str subspace: (optional), e.g. 'tags', 'stashes', 'notes'
        :param int number: (optional), number of refs to return. Default: -1
            returns all available refs
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`Reference <github3.git.Reference>`\ s
        """
        if subspace:
            args = ('git', 'refs', subspace)
        else:
            args = ('git', 'refs')
        url = self._build_url(*args, base_url=self._api)
        return self._iter(int(number), url, Reference, etag=etag)

    def iter_releases(self, number=-1, etag=None):
        """Iterates over releases for this repository.

        :param int number: (optional), number of refs to return. Default: -1
            returns all available refs
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of
            :class:`Release <github3.repos.release.Release>`\ s
        """
        url = self._build_url('releases', base_url=self._api)
        iterator = self._iter(int(number), url, Release, etag=etag)
        iterator.headers.update(Release.CUSTOM_HEADERS)
        return iterator

    def iter_stargazers(self, number=-1, etag=None):
        """List users who have starred this repository.

        :param int number: (optional), number of stargazers to return.
            Default: -1 returns all subscribers available
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`User <github3.users.User>`\ s
        """
        url = self._build_url('stargazers', base_url=self._api)
        return self._iter(int(number), url, User, etag=etag)

    def iter_subscribers(self, number=-1, etag=None):
        """Iterates over users subscribed to this repository.

        :param int number: (optional), number of subscribers to return.
            Default: -1 returns all subscribers available
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`User <github3.users.User>`
        """
        url = self._build_url('subscribers', base_url=self._api)
        return self._iter(int(number), url, User, etag=etag)

    def iter_statuses(self, sha, number=-1, etag=None):
        """Iterates over the statuses for a specific SHA.

        :param str sha: SHA of the commit to list the statuses of
        :param int number: (optional), return up to number statuses. Default:
            -1 returns all available statuses.
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`Status <github3.repos.status.Status>`
        """
        url = ''
        if sha:
            url = self._build_url('statuses', sha, base_url=self._api)
        return self._iter(int(number), url, Status, etag=etag)

    def iter_tags(self, number=-1, etag=None):
        """Iterates over tags on this repository.

        :param int number: (optional), return up to at most number tags.
            Default: -1 returns all available tags.
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`RepoTag <github3.repos.tag.RepoTag>`\ s
        """
        url = self._build_url('tags', base_url=self._api)
        return self._iter(int(number), url, RepoTag, etag=etag)

    @requires_auth
    def iter_teams(self, number=-1, etag=None):
        """Iterates over teams with access to this repository.

        :param int number: (optional), return up to number Teams. Default: -1
            returns all Teams.
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`Team <github3.orgs.Team>`\ s
        """
        from ..orgs import Team
        url = self._build_url('teams', base_url=self._api)
        return self._iter(int(number), url, Team, etag=etag)

    @requires_auth
    def mark_notifications(self, last_read=''):
        """Mark all notifications in this repository as read.

        :param str last_read: (optional), Describes the last point that
            notifications were checked. Anything updated since this time will
            not be updated. Default: Now. Expected in ISO 8601 format:
            ``YYYY-MM-DDTHH:MM:SSZ``. Example: "2012-10-09T23:39:01Z".
        :returns: bool
        """
        url = self._build_url('notifications', base_url=self._api)
        mark = {'read': True}
        if last_read:
            mark['last_read_at'] = last_read
        return self._boolean(self._put(url, data=dumps(mark)),
                             205, 404)

    @requires_auth
    def merge(self, base, head, message=''):
        """Perform a merge from ``head`` into ``base``.

        :param str base: (required), where you're merging into
        :param str head: (required), where you're merging from
        :param str message: (optional), message to be used for the commit
        :returns: :class:`RepoCommit <github3.repos.commit.RepoCommit>`
        """
        url = self._build_url('merges', base_url=self._api)
        data = {'base': base, 'head': head}
        if message:
            data['commit_message'] = message
        json = self._json(self._post(url, data=data), 201)
        return RepoCommit(json, self) if json else None

    def milestone(self, number):
        """Get the milestone indicated by ``number``.

        :param int number: (required), unique id number of the milestone
        :returns: :class:`Milestone <github3.issues.milestone.Milestone>`
        """
        json = None
        if int(number) > 0:
            url = self._build_url('milestones', str(number),
                                  base_url=self._api)
            json = self._json(self._get(url), 200)
        return Milestone(json, self) if json else None

    @requires_auth
    def pages(self):
        """Get information about this repository's pages site.

        :returns: :class:`PagesInfo <github3.repos.pages.PagesInfo>`
        """
        url = self._build_url('pages', base_url=self._api)
        json = self._json(self._get(url), 200)
        return PagesInfo(json) if json else None

    def pull_request(self, number):
        """Get the pull request indicated by ``number``.

        :param int number: (required), number of the pull request.
        :returns: :class:`PullRequest <github3.pulls.PullRequest>`
        """
        json = None
        if int(number) > 0:
            url = self._build_url('pulls', str(number), base_url=self._api)
            json = self._json(self._get(url), 200)
        return PullRequest(json, self) if json else None

    def readme(self):
        """Get the README for this repository.

        :returns: :class:`Contents <github3.repos.contents.Contents>`
        """
        url = self._build_url('readme', base_url=self._api)
        json = self._json(self._get(url), 200)
        return Contents(json, self) if json else None

    def ref(self, ref):
        """Get a reference pointed to by ``ref``.

        The most common will be branches and tags. For a branch, you must
        specify 'heads/branchname' and for a tag, 'tags/tagname'. Essentially,
        the system should return any reference you provide it in the namespace,
        including notes and stashes (provided they exist on the server).

        :param str ref: (required)
        :returns: :class:`Reference <github3.git.Reference>`
        """
        json = None
        if ref:
            url = self._build_url('git', 'refs', ref, base_url=self._api)
            json = self._json(self._get(url), 200)
        return Reference(json, self) if json else None

    def release(self, id):
        """Get a single release.

        :param int id: (required), id of release
        :returns: :class:`Release <github3.repos.release.Release>`
        """
        json = None
        if int(id) > 0:
            url = self._build_url('releases', str(id), base_url=self._api)
            json = self._json(self._get(url), 200)
        return Release(json, self) if json else None

    @requires_auth
    def remove_collaborator(self, login):
        """Remove collaborator ``login`` from the repository.

        :param str login: (required), login name of the collaborator
        :returns: bool
        """
        resp = False
        if login:
            url = self._build_url('collaborators', login, base_url=self._api)
            resp = self._boolean(self._delete(url), 204, 404)
        return resp

    @requires_auth
    def subscribe(self):
        """Subscribe the user to this repository's notifications.

        .. versionadded:: 1.0

        This replaces ``Repository#set_subscription``

        :returns: :class:`Subscription <github3.notifications.Subscription>`
        """
        url = self._build_url('subscription', base_url=self._api)
        json = self._json(self._put(url, data=dumps({'subcribed': True})),
                          200)
        return Subscription(json, self) if json else None

    @requires_auth
    def subscription(self):
        """Return subscription for this Repository.

        :returns: :class:`Subscription <github3.notifications.Subscription>`
        """
        url = self._build_url('subscription', base_url=self._api)
        json = self._json(self._get(url), 200)
        return Subscription(json, self) if json else None

    def tag(self, sha):
        """Get an annotated tag.

        http://learn.github.com/p/tagging.html

        :param str sha: (required), sha of the object for this tag
        :returns: :class:`Tag <github3.git.Tag>`
        """
        json = None
        if sha:
            url = self._build_url('git', 'tags', sha, base_url=self._api)
            json = self._json(self._get(url), 200)
        return Tag(json) if json else None

    def tree(self, sha):
        """Get a tree.

        :param str sha: (required), sha of the object for this tree
        :returns: :class:`Tree <github3.git.Tree>`
        """
        json = None
        if sha:
            url = self._build_url('git', 'trees', sha, base_url=self._api)
            json = self._json(self._get(url), 200)
        return Tree(json, self) if json else None

    @requires_auth
    def update_file(self, path, message, content, sha, branch=None,
                    author=None, committer=None):
        """Update the file ``path`` with ``content``.

        This is part of the Contents CrUD (Create Update Delete) API. See
        http://developer.github.com/v3/repos/contents/#update-a-file for more
        information.

        :param str path: (required), path to the file being updated
        :param str message: (required), commit message
        :param str content: (required), updated contents of the file
        :param str sha: (required), blob sha of the file being updated
        :param str branch: (optional), uses the default branch on the
            repository if not provided.
        :param dict author: (optional), if omitted this will be filled in with
            committer information. If passed, you must specify both a name and
            email.
        :returns: {'commit': :class:`Commit <github3.git.Commit>`,
            'content': :class:`Contents <github3.repos.contents.Contents>`}

        """
        if content and not isinstance(content, bytes):
            raise ValueError(  # (No coverage)
                'content must be a bytes object')  # (No coverage)

        json = None
        if path and message and content and sha:
            url = self._build_url('contents', path, base_url=self._api)
            content = b64encode(content).decode('utf-8')
            data = {'message': message, 'content': content, 'sha': sha,
                    'committer': validate_commmitter(committer),
                    'author': validate_commmitter(author),
                    'branch': branch}
            self._remove_none(data)
            json = self._json(self._put(url, data=dumps(data)), 200)
            if 'content' in json and 'commit' in json:
                json['content'] = Contents(json['content'], self)
                json['commit'] = Commit(json['commit'], self)
        return json

    @requires_auth
    def update_label(self, name, color, new_name=''):
        """Update the label ``name``.

        :param str name: (required), name of the label
        :param str color: (required), color code
        :param str new_name: (optional), new name of the label
        :returns: bool
        """
        label = self.label(name)
        resp = False
        if label:
            upd = label.update
            resp = upd(new_name, color) if new_name else upd(name, color)
        return resp

    def weekly_commit_count(self):
        """Returns the total commit counts.

        The dictionary returned has two entries: ``all`` and ``owner``. Each
        has a fifty-two element long list of commit counts. (Note: ``all``
        includes the owner.) ``d['all'][0]`` will be the oldest week,
        ``d['all'][51]`` will be the most recent.

        :returns: dict

        .. note:: All statistics methods may return a 202. If github3.py
            receives a 202 in this case, it will return an emtpy dictionary.
            You should give the API a moment to compose the data and then re
            -request it via this method.

        ..versionadded:: 0.7

        """
        url = self._build_url('stats', 'participation', base_url=self._api)
        resp = self._get(url)
        if resp.status_code == 202:
            return {}
        json = self._json(resp, 200)
        if json.get('ETag'):
            del json['ETag']
        if json.get('Last-Modified'):
            del json['Last-Modified']
        return json
