# -*- coding: utf-8 -*-
"""Integration tests for methods implemented on PullRequest."""

import github3

from .helper import IntegrationHelper


class TestPullRequest(IntegrationHelper):

    """PullRequest integration tests."""

    def get_pull_request(self, repository='sigmavirus24/github3.py', num=235):
        """Get the pull request we wish to use in this test."""
        owner, repo = repository.split('/')
        p = self.gh.pull_request(owner, repo, num)
        assert isinstance(p, github3.pulls.PullRequest)
        return p

    def test_close(self):
        """Show that one can close an open Pull Request."""
        self.basic_login()
        cassette_name = self.cassette_name('close')
        with self.recorder.use_cassette(cassette_name):
            p = self.get_pull_request(num=241)
            assert p.close() is True

    def test_commits(self):
        """Show that one can iterate over a PR's commits."""
        cassette_name = self.cassette_name('commits')
        with self.recorder.use_cassette(cassette_name):
            p = self.get_pull_request()
            for commit in p.commits():
                assert isinstance(commit, github3.git.Commit)

    def test_diff(self):
        """Show that one can retrieve a bytestring diff of a PR."""
        cassette_name = self.cassette_name('diff')
        with self.recorder.use_cassette(cassette_name):
            p = self.get_pull_request()
            diff = p.diff()
            assert isinstance(diff, bytes)
            assert len(diff) > 0

    def test_files(self):
        """Show that one can iterate over a PR's files."""
        cassette_name = self.cassette_name('files')
        with self.recorder.use_cassette(cassette_name):
            p = self.get_pull_request()
            for pr_file in p.files():
                assert isinstance(pr_file, github3.pulls.PullFile)

    def test_is_merged(self):
        """Show that one can check if a PR was merged."""
        cassette_name = self.cassette_name('is_merged')
        with self.recorder.use_cassette(cassette_name):
            p = self.get_pull_request()
            assert p.is_merged() is True

    def test_issue_comments(self):
        """Show that one can iterate over a PR's issue comments."""
        cassette_name = self.cassette_name('issue_comments')
        with self.recorder.use_cassette(cassette_name):
            p = self.get_pull_request()
            for comment in p.issue_comments():
                assert isinstance(comment,
                                  github3.issues.comment.IssueComment)

    def test_patch(self):
        """Show that a user can get the patch from a PR."""
        cassette_name = self.cassette_name('patch')
        with self.recorder.use_cassette(cassette_name):
            p = self.get_pull_request()
            patch = p.patch()
            assert isinstance(patch, bytes)
            assert len(patch) > 0

    def test_review_comments(self):
        """Show that one can iterate over a PR's review comments."""
        cassette_name = self.cassette_name('review_comments')
        with self.recorder.use_cassette(cassette_name):
            p = self.get_pull_request()
            for comment in p.review_comments():
                assert isinstance(comment, github3.pulls.ReviewComment)
