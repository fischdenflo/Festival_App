import requests

class PocketBaseClient:
    def __init__(self, base_url, collection, email=None, password=None, is_admin=False):
        """
        Initialisiert den PocketBase-Client und führt die Authentifizierung durch.
        
        Args:
            base_url (str): Die Basis-URL des PocketBase-Servers
            collection (str): Name der zu verwendenden Collection
            email (str, optional): E-Mail/Benutzername für die Authentifizierung
            password (str, optional): Passwort für die Authentifizierung
            is_admin (bool, optional): True wenn Admin-Auth verwendet werden soll
        """
        self.base_url = base_url
        self.collection = collection
        self.token = None
        self.admin_token = None
        
        # Automatische Authentifizierung, wenn Credentials angegeben wurden
        if email and password:
            if is_admin:
                self.admin_auth(email, password)
            else:
                self.auth(email, password)

    def admin_auth(self, email, password):
        """
        Authentifiziert einen Admin-Benutzer (Superuser).
        
        Args:
            email (str): Admin E-Mail
            password (str): Admin Passwort
            
        Returns:
            bool: True wenn die Authentifizierung erfolgreich war, sonst False
        
        Raises:
            Exception: Wenn die Authentifizierung fehlschlägt
        """
        url = f"{self.base_url}/api/collections/_superusers/auth-with-password"
        data = {
            "identity": email,
            "password": password
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            self.admin_token = response.json().get("token")
            return True
        raise Exception(f"Admin-Authentifizierung fehlgeschlagen: {response.text}")

    def auth(self, username, password, collection="users"):
        """
        Authentifiziert einen normalen Benutzer.
        
        Args:
            username (str): Benutzername oder E-Mail
            password (str): Passwort
            collection (str): Name der Auth-Collection (Standard: "users")
            
        Returns:
            bool: True wenn die Authentifizierung erfolgreich war, sonst False
            
        Raises:
            Exception: Wenn die Authentifizierung fehlschlägt
        """
        url = f"{self.base_url}/api/collections/{collection}/auth-with-password"
        data = {
            "identity": username,
            "password": password
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            self.token = response.json().get("token")
            return True
        raise Exception(f"Benutzer-Authentifizierung fehlgeschlagen: {response.text}")

    def _get_headers(self):
        """
        Erstellt die Header für Requests mit Authentifizierung.
        
        Returns:
            dict: Header mit Auth-Token wenn vorhanden
            
        Raises:
            Exception: Wenn kein Auth-Token vorhanden ist
        """
        if not (self.token or self.admin_token):
            raise Exception("Keine Authentifizierung vorhanden. Bitte zuerst auth() oder admin_auth() aufrufen.")
            
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif self.admin_token:
            headers["Authorization"] = f"Bearer {self.admin_token}"
        return headers

    def get_records(self, filter=None):
        """
        Holt Records aus der Collection.
        
        Args:
            filter (str, optional): Filterstring für die Abfrage
            
        Returns:
            Response: Die Server-Antwort
            
        Raises:
            Exception: Wenn keine Authentifizierung vorhanden ist
        """
        params = {"filter": filter} if filter else {}
        return requests.get(
            f"{self.base_url}/api/collections/{self.collection}/records",
            params=params,
            headers=self._get_headers()
        )

    def patch_record(self, record_id, json=None, files=None):
        """
        Aktualisiert einen Record.
        
        Args:
            record_id (str): ID des zu aktualisierenden Records
            json (dict, optional): JSON-Daten für das Update
            files (dict, optional): Dateien für das Update
            
        Returns:
            Response: Die Server-Antwort
            
        Raises:
            Exception: Wenn keine Authentifizierung vorhanden ist
        """
        url = f"{self.base_url}/api/collections/{self.collection}/records/{record_id}"
        return requests.patch(
            url,
            json=json,
            files=files,
            headers=self._get_headers()
        )

    def post_record(self, data, files):
        """
        Erstellt einen neuen Record.
        
        Args:
            data (dict): Daten für den neuen Record
            files (dict): Dateien für den neuen Record
            
        Returns:
            Response: Die Server-Antwort
            
        Raises:
            Exception: Wenn keine Authentifizierung vorhanden ist
        """
        url = f"{self.base_url}/api/collections/{self.collection}/records"
        return requests.post(
            url,
            data=data,
            files=files,
            headers=self._get_headers()
        )

    def get_file_url(self, record_id, filename):
        """
        Generiert die URL für eine Datei.
        
        Args:
            record_id (str): ID des Records
            filename (str): Name der Datei
            
        Returns:
            str: Die generierte URL
        """
        return f"{self.base_url}/api/files/{self.collection}/{record_id}/{filename}"
    
    def get_imgage_from_user(self, user):
        """
        Holt alle Bilder eines bestimmten Benutzers.
        
        Args:
            user (str): Benutzername
            
        Returns:
            list: Liste der Bilder oder None bei einem Fehler
            
        Raises:
            Exception: Wenn keine Authentifizierung vorhanden ist
        """
        response = self.get_records(filter=f"user = '{user}'")
        if response.status_code == 200:
            items = response.json().get("items", [])
            record = next(iter(items), None)
            images = record.get("image", []) if record else []
            return images
        else:    
            return None
