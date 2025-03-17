"""
Dieses Modul implementiert die Voting-Funktionalität der Anwendung.
Es ermöglicht Benutzern, für hochgeladene Bilder zu stimmen, wobei jeder Benutzer
insgesamt maximal 5 Stimmen abgeben kann und für jedes Bild nur einmal abstimmen darf.
"""

import streamlit as st
from datetime import datetime, timezone
from views.login import login_page
from connection.poketbase import PocketBaseClient

# Initialisiere den PocketBase-Client für Datenbankoperationen mit Admin-Rechten
client = PocketBaseClient(
    base_url=st.secrets["pocketbase"]["base_url"],
    collection=st.secrets["pocketbase"]["collection"],
    email=st.secrets["pocketbase"]["admin"]["email"],
    password=st.secrets["pocketbase"]["admin"]["password"],
    is_admin=True
)

def count_user_votes(records, username):
    """
    Zählt die Gesamtanzahl der bereits abgegebenen Stimmen eines Benutzers.
    
    Args:
        records (list): Liste aller Bild-Records aus der Datenbank
        username (str): Benutzername, dessen Stimmen gezählt werden sollen
    
    Returns:
        int: Anzahl der bereits abgegebenen Stimmen des Benutzers
    """
    # Optimierte Version: Nutze filter in der Datenbankabfrage
    response = client.get_records(filter=f'voted_users ?~ "{username}"')
    if response.status_code == 200:
        return len(response.json().get("items", []))
    return 0

def voting_page(cookies):
    """
    Hauptfunktion für die Voting-Seite. Zeigt alle hochgeladenen Bilder an und
    ermöglicht das Abstimmen unter Berücksichtigung der Stimmenbegrenzung.
    
    Args:
        cookies: Cookie-Objekt für die Benutzersession-Verwaltung
    """
    
    # Warten, bis die Cookies geladen sind
    if not cookies.ready():
        st.warning("Lade Cookies...")
        st.stop()

    # Prüfen, ob bereits Login-Informationen in den Cookies gespeichert sind
    if cookies.get("user_logged_in") == "true" and cookies.get("username"):
        user = cookies.get("username")
    else:
        # Wenn nicht eingeloggt, zur Login-Seite weiterleiten
        login_page(cookies)
        st.stop()
    
    st.title("Voting")
    
    # Hole die Anzahl der bereits abgegebenen Stimmen
    user_total_votes = count_user_votes(None, user)
    remaining_votes = 5 - user_total_votes
    st.info(f"Sie haben noch {remaining_votes} Stimmen übrig.")
    
    # Hole alle Bild-Records aus der Datenbank
    response = client.get_records()
    if response.status_code == 200:
        data = response.json()
        records = data.get("items", [])
        
        if not records:
            st.info("Es wurden noch keine Bilder hochgeladen.")
        else:
            # Zeige alle Bilder mit Voting-Möglichkeit an
            for record in records:
                with st.container(border=True):
                    
                    # Layout mit zwei Spalten: Links Info, rechts Bild
                    col1, col2 = st.columns(2)
                    
                    with col2:
                        # Bilder des Records anzeigen
                        if record.get("image"):
                            image_urls = []
                            for image_file in record.get("image"):
                                # Generiere URL für jedes Bild
                                image_url = client.get_file_url(record['id'], image_file)
                                image_urls.append(image_url)
                            st.image(image_urls, width=200)
                        else:
                            st.info("Keine Bilder für diesen Eintrag vorhanden.") 
                               
                    with col1:               
                        # Zeige den Namen des Uploaders
                        record_name = record.get("user")
                        st.title(f"**{record_name}**")
                        
                        # Voting-System
                        voted_users = record.get("voted_users", []) or []  # Stelle sicher, dass es eine Liste ist
                        votes = len(voted_users)  # Anzahl der Stimmen ist die Länge der voted_users-Liste
                        st.write(f"Aktuelle Stimmen: {votes}")
                        
                        if user not in voted_users:
                            # Prüfe ob noch Stimmen übrig sind
                            if remaining_votes > 0:
                                if st.button("👍 Abstimmen", key=f"vote_{record['id']}"):
                                    # Füge den User zur Liste der Abstimmenden hinzu
                                    voted_users.append(user)
                                    
                                    # Bereite Daten für das Update vor
                                    update_data = {
                                        "voted_users": voted_users
                                    }
                                    
                                    # Aktualisiere den Record in der Datenbank
                                    response = client.patch_record(record['id'], json=update_data)
                                    if response.status_code == 200:
                                        st.success("Stimme erfolgreich abgegeben!")
                                        st.rerun()  # Seite neu laden um aktuelle Daten anzuzeigen
                                    else:
                                        st.error("Fehler beim Abstimmen. Bitte versuchen Sie es später erneut.")
                            else:
                                st.warning("Sie haben keine Stimmen mehr übrig!")
                        else:
                            st.info("Sie haben bereits für diesen Eintrag abgestimmt.")
    else:
        st.error(f"Fehler beim Abrufen der Bilder: {response.text}")
