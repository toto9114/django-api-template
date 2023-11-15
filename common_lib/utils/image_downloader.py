import ssl
import requests
from urllib3 import poolmanager
from requests.adapters import HTTPAdapter, Retry


class ImageDownloader:
    class TLSAdapter(HTTPAdapter):
        def init_poolmanager(self, connections, maxsize, block=False):
            """Create and initialize the urllib3 PoolManager."""
            ctx = ssl.create_default_context()
            ctx.set_ciphers("DEFAULT@SECLEVEL=1")
            ctx.check_hostname = False
            self.poolmanager = poolmanager.PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_context=ctx,
            )

    def __init__(self):
        self.session = requests.session()
        retries = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount("https://", self.TLSAdapter(max_retries=retries))
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    def download(self, url: str, headers: dict) -> requests.Response | None:
        return self.session.get(url, headers=headers, timeout=2, verify=False)

    def download_add_proxy_and_verify(
        self, url: str, headers: dict, proxy=None, verify: bool = False
    ) -> requests.Response | None:
        return self.session.get(
            url, headers=headers, timeout=2, proxies=proxy, verify=verify
        )

    def head(self, url: str, headers: dict) -> requests.Response:
        return self.session.head(url, headers=headers, timeout=0.1)

    def options(self, url: str, headers: dict) -> requests.Response:
        return self.session.options(url, headers=headers, timeout=0.1)
