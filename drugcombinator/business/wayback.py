import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class WaybackClient:
    # WM docs for getting snapshots:
    # https://archive.org/developers/tutorial-get-snapshot-wayback.html#steps

    # WM docs for capturing:
    # https://docs.google.com/document/d/1Nsv52MvSjbLb2PCpHlat0gkzw0EvtSgpKHu4mk0MnrA/

    def json_response(self, request):
        with urlopen(request) as response:
            data = response.read()
            return json.loads(data.decode('utf-8'))

    def get_last_snapshot(self, url):
        """Return a dict representing the last snapshot for a given URL.

        Return `None` if no snapshot is found.
        """
        params = urlencode({'url': url})
        request = 'https://archive.org/wayback/available?' + params

        return (
            self.json_response(request)['archived_snapshots']
            .get('closest', None)
        )

    def capture(self, url):
        """Request a capture for a given URL.

        Returns the bare Wayback JSON response.
        """
        data = urlencode({'url': url})
        request = Request(
            'https://web.archive.org/save',
            headers={'Accept': 'application/json'},
            data=data.encode()
        )

        return self.json_response(request)
