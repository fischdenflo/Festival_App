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
                with st.container(border=True):
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Alle Bilder des Records anzeigen, sofern vorhanden.
                        if record.get("image"):
                            image_urls = []
                            for image_file in record.get("image"):
                                image_url = client.get_file_url(record['id'], image_file)
                                image_urls.append(image_url)
                            st.image(image_urls, width=200)
                                
                        else:
                            st.info("Keine Bilder für diesen Eintrag vorhanden.")    
                            
                    with col2:               
                        # Name des Records anzeigen. Passe 'name' an den tatsächlichen Feldnamen an, falls anders.
                        record_name = record.get("user")
                        st.title(f"**{record_name}**")
                
                    

    else:
        st.error(f"Fehler beim Abrufen der Bilder: {response.text}")
