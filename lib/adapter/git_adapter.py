"""
Implementation of `GitRepositoryAdapter`, adapter that is used to handle git repositories
"""

import os

from adapter import Adapter # pylint: disable=relative-import

class GitRepositoryAdapter(Adapter):    #pylint: disable=abstract-method
    """
    Implements all methods needed to handle cache handling
    for git-repository-based adatpers
    """

    @classmethod
    def fetch_command(cls):
        """
        Initial fetch of the repository.
        Return cmdline that has to be executed to fetch the repository.
        Skipping if `self._repository_url` is not specified
        """

        if not cls._repository_url:
            return None

        if not cls._repository_url.startswith('https://github.com/'):
            # in this case `fetch` has to be implemented
            # in the distinct adapter subclass
            raise RuntimeError(
                "Do not known how to handle this repository: %s" % cls._repository_url)

        local_repository_dir = cls.local_repository_location()
        if not local_repository_dir:
            return None

        return ['git', 'clone', cls._repository_url, local_repository_dir]

    @classmethod
    def update_command(cls):
        """
        Update of the repository.
        Return cmdline that has to be executed to update the repository
        inside `local_repository_location()`.
        """

        if not cls._repository_url:
            return None

        local_repository_dir = cls.local_repository_location()
        if not local_repository_dir:
            return None

        if not cls._repository_url.startswith('https://github.com/'):
            # in this case `update` has to be implemented
            # in the distinct adapter subclass
            raise RuntimeError(
                "Do not known how to handle this repository: %s" % cls._repository_url)

        return ['git', 'pull']

    @classmethod
    def current_state_command(cls):
        """
        Get current state of repository (current revision).
        This is used to find what cache entries should be invalidated.
        """

        if not cls._repository_url:
            return None

        local_repository_dir = cls.local_repository_location()
        if not local_repository_dir:
            return None

        if not cls._repository_url.startswith('https://github.com/'):
            # in this case `update` has to be implemented
            # in the distinct adapter subclass
            raise RuntimeError(
                "Do not known how to handle this repository: %s" % cls._repository_url)

        return ['git', 'rev-parse', '--short', 'HEAD']

    @classmethod
    def save_state(cls, state):
        """
        Save state `state` of the repository.
        Must be called after the cache clean up.
        """
        local_repository_dir = cls.local_repository_location()
        state_filename = os.path.join(local_repository_dir, '.cached_revision')
        open(state_filename, 'w').write(state)

    @classmethod
    def get_state(cls):
        """
        Return the saved `state` of the repository.
        If state cannot be read, return None
        """

        local_repository_dir = cls.local_repository_location()
        state_filename = os.path.join(local_repository_dir, '.cached_revision')
        if os.path.exists(state_filename):
            state = open(state_filename, 'r').read()
        return state

    @classmethod
    def get_updates_list_command(cls):
        """
        Return list of updates since the last update whose id is saved as the repository state.
        The list is used to invalidate the cache.
        """
        current_state = cls.get_state()
        if current_state is None:
            return ['git', 'ls-tree', '--full-tree', '-r', '--name-only', 'HEAD']
        return ['git', 'diff', '--name-only', current_state, 'HEAD']
