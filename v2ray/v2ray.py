import urllib.parse
import base64
import json

class V2Ray:
    def __init__(self, url: str):
        self.url = url
        self.host = None
        self.port = None
        self.uuid = None
        self.remark = None
        self.all_params = {}

    def parse(self, url: str):
        raise NotImplementedError("Subclasses must implement this method.")

    def build_url(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def update(self, newhost: str, remark: str = None):
        raise NotImplementedError("Subclasses must implement this method.")

    def __str__(self):
        return self.url

    def __repr__(self):
        return f"{self.__class__.__name__}({self.url})"


class VLESS(V2Ray):
    def parse(self, url: str):
        url_parts = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(url_parts.query)

        userinfo, _, hostport = url_parts.netloc.partition('@')
        uuid = userinfo
        host, _, port = hostport.partition(':')

        self.uuid = uuid
        self.host = host
        self.port = port if port else None
        self.remark = url_parts.fragment if url_parts.fragment else None
        self.new_remark = ""
        self.all_params = query_params

    def build_url(self):
        netloc = f"{self.uuid}@{self.host}:{self.port}"
        query_string = urllib.parse.urlencode(self.all_params, doseq=True)
        fragment = f"#{self.new_remark}" if self.remark else ""
        self.url = f"vless://{netloc}?{query_string}{fragment}"
        self.new_remark = self.remark  # Reset new_remark after building URL

    def update(self, newhost: str, provider_remark: str = None):
        self.host = newhost
        self.port = 443
        generated_remark = f"{provider_remark or 'insta-v2ray-generated'}-{self.remark}"
        self.new_remark = generated_remark
        self.all_params.update({
            'sni': newhost,
            'security': 'tls',
            'host': newhost,
        })
        self.build_url()


class VMESS(V2Ray):
    def parse(self, url: str):
        url_parts = urllib.parse.urlparse(url)
        encoded_data = url_parts.netloc

        try:
            decoded_json = base64.b64decode(encoded_data).decode('utf-8')
            all_params = json.loads(decoded_json)
        except Exception as e:
            raise ValueError(f"Failed to decode VMESS URL: {e}")

        self.all_params = all_params
        self.uuid = all_params.get('id', None)
        self.host = all_params.get('add', None)
        self.port = all_params.get('port', None)
        self.remark = all_params.get('ps', None)

    def build_url(self):
        self.url = f"vmess://{base64.b64encode(json.dumps(self.all_params).encode('utf-8')).decode('utf-8')}"

    def update(self, newhost: str, remark: str = None):
        self.host = newhost
        self.port = 443
        self.remark = remark or "insta-v2ray-generated"
        self.all_params.update({
            'add': newhost,
            'port': str(self.port),
            'sni': newhost,
            'host': newhost,
            'tls': 'tls',
            'ps': self.remark,
        })
        self.build_url()

if __name__ == "__main__":
    
    vless_example = ""
    vmess_example = ""

    vless = VLESS(vless_example)
    vmess = VMESS(vmess_example)
    print(vless)
    print(vmess)
    vless.parse(vless_example)
    print(vless.host)
    vless.update("newhost.com", "New Remark")
    print(vless)
    vmess.parse(vmess_example)
    vmess.update("newhost.com", "New Remark")
    print(vmess.host)
    print(vmess)
