import requests

class PocketBaseClient:
    def __init__(self, base_url, collection):
        self.base_url = base_url
        self.collection = collection

    def get_records(self, filter=None):
        params = {"filter": filter} if filter else {}
        return requests.get(f"{self.base_url}/api/collections/{self.collection}/records", params=params)

    def patch_record(self, record_id, json=None, files=None):
        url = f"{self.base_url}/api/collections/{self.collection}/records/{record_id}"
        return requests.patch(url, json=json, files=files)

    def post_record(self, data, files):
        url = f"{self.base_url}/api/collections/{self.collection}/records"
        return requests.post(url, data=data, files=files)

    def get_file_url(self, record_id, filename):
        return f"{self.base_url}/api/files/{self.collection}/{record_id}/{filename}"
    
    def get_imgage_from_user(self, user):
        response = self.get_records(filter=f"user = '{user}'")
        if response.status_code == 200:
            items = response.json().get("items", [])
            record = next(iter(items), None)
            images = record.get("image", []) if record else []
            return images
        else:    
            return None
