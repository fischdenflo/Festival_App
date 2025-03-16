import streamlit as st
import random
from connection.poketbase import PocketBaseClient
from views.login import login_page

# Initialisiere den PocketBase-Client für Datenbankoperationen mit Admin-Rechten
client = PocketBaseClient(
    base_url=st.secrets["pocketbase"]["base_url"],
    collection=st.secrets["pocketbase"]["collection"],
    email=st.secrets["pocketbase"]["admin"]["email"],
    password=st.secrets["pocketbase"]["admin"]["password"],
    is_admin=True
)

def upload_page(cookies):
    
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
          
    st.title("Bild hochladen")
    
    images = client.get_imgage_from_user(user)
    if len(images) >= 2:
        st.info("Sie haben bereits maximal 2 Bilder hochgeladen.")
        return
    
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = "initial_key"
        
    uploaded_files = st.file_uploader(
        "Wähle ein oder mehrere Bilder aus", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True,
        key=st.session_state["uploader_key"]
    )
    if uploaded_files:
        st.write(f"{len(uploaded_files)} Datei(en) ausgewählt.")
    
    if st.button("Hochladen"):
        if uploaded_files and (len(images) + len(uploaded_files) > 2):
            st.error("Sie können insgesamt maximal 2 Bilder hochladen.")
            return
        if not uploaded_files:
            st.warning("Bitte wählen Sie zuerst Bilder aus.")
        else:
            data = {"user": user}
            response_get = client.get_records(filter=f"user = '{user}'")
            if response_get.status_code == 200:
                items = response_get.json().get("items", [])
                if items:
                    record_id = items[0]["id"]
                    existing_files = items[0].get("image", [])
                    files_payload = []
                    for file_name in existing_files:
                        files_payload.append(("image", (None, file_name)))
                    for file in uploaded_files:
                        files_payload.append(("image", (file.name, file, file.type)))
                    response = client.patch_record(record_id, json=data, files=files_payload)
                else:
                    files_payload = [("image", (file.name, file, file.type)) for file in uploaded_files]
                    response = client.post_record(data=data, files=files_payload)
            else:
                st.error(f"Fehler beim Überprüfen des Users: {response_get.text}")
                return

            if response.status_code in [200, 201]:
                st.success("Bilder erfolgreich hochgeladen!")
                st.session_state["uploader_key"] = str(random.random())
                st.rerun()  # Seite neu laden
            else:
                st.error(f"Fehler beim Upload: {response.text}")


