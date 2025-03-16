import streamlit as st
from config import BASE_URL, COLLECTION
from connection.poketbase import PocketBaseClient
from views.login import login_page

client = PocketBaseClient(BASE_URL, COLLECTION)

def voting_page(cookies):
    
     # Warten, bis die Cookies geladen sind
    if not cookies.ready():
        st.warning("Lade Cookies...")
        st.stop()

    # Prüfen, ob bereits Login-Informationen in den Cookies gespeichert sind
    if cookies.get("user_logged_in") == "true" and cookies.get("username"):
        user = cookies.get("username")
    else:
        login_page(cookies)
        st.stop()
    
    st.title("Voting")
    response = client.get_records()
    if response.status_code == 200:
        data = response.json()
        records = data.get("items", [])
        if not records:
            st.info("Es wurden noch keine Bilder hochgeladen.")
        else:
            for record in records:
                if record.get("image"):
                    image_url = client.get_file_url(record['id'], record['image'][0])
                    st.image(image_url)
    else:
        st.error(f"Fehler beim Abrufen der Bilder: {response.text}")
