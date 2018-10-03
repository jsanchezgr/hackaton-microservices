import requests
import os

BB_USER = os.environ.get('BB_USER', '')
BB_KEY = os.environ.get('BB_KEY', '')


class ExORepository:

    @staticmethod
    def load_repositories():
        request_url = 'https://api.bitbucket.org/2.0/repositories/exolever/'

        # Main (non exo-XXXX) repositories
        repository_list = [
            'exolever',
            'exolever-populator',
            'end-to-end-testing',
        ]

        # BitBucket api results are paginated
        while request_url:
            r = requests.get(request_url, auth=(BB_USER, BB_KEY))

            if r.status_code != 200:
                # TODO: Raise proper exception
                # raise ApiException(r.status_code)
                pass

            result = r.json()

            for repo in result['values']:
                name = repo['full_name'].replace('exolever/', '')

                if name.startswith('exo-'):
                    repository_list.append(name)

            request_url = result.get('next', False)

        return repository_list

    def get_statuses(self, source_branch, repos=None):

        statuses = []
        full_list = self.load_repositories()

        if repos:
            for repo in repos:
                if repo not in full_list:
                    raise IndexError('{} repository not found'.format(repo))
        else:
            repos = full_list

        for repo in repos:
            statuses.append({
                repo: self.__get_repository_status(repo, source_branch)})

        return statuses

    @staticmethod
    def __get_repository_status(repo_slug, source_branch):

        request_url = 'https://api.bitbucket.org/2.0/repositories/' \
                      'exolever/%s/pipelines/?sort=-created_on' % repo_slug

        r = requests.get(request_url, auth=(BB_USER, BB_KEY))

        result = r.json()

        for value in result['values']:

            target = value.get('target')

            if target.get('ref_name') == source_branch:

                return value.get('state').get('type')

        return False
