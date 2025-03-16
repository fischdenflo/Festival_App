import streamlit as st
from config import BASE_URL, COLLECTION
from connection.poketbase import PocketBaseClient
from views.login import login_page

client = PocketBaseClient(BASE_URL, COLLECTION)

def my_gallery_page(cookies):
    
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
    
    st.title("Meine Bilder")

    response = client.get_records(filter=f"user = '{user}'")
        
    if response.status_code == 200:
        items = response.json().get("items", [])
        record = next(iter(items), None)  # Optimierte Extraktion des ersten Elements
        images = record.get("image", []) if record else []
        
        if not images:
            st.info("Sie haben noch keine Bilder hochgeladen.")
        else:
            for image in images:
                
                with st.container(border=True):
  
                    image_url = client.get_file_url(record['id'], image)
                    st.image(image_url, width=250)
                                        
                    if st.button(f"Löschen", key=f"delete_{record['id']}_{image}"):
                        remaining_images = [img for img in record.get("image", []) if img != image]
                        patch_response = client.patch_record(record['id'], json={"image": remaining_images})
                        if patch_response.status_code in [200, 204]:
                            st.success("Bild erfolgreich entfernt!")
                            st.rerun() 
                        else:
                            st.error(f"Fehler beim Entfernen: {patch_response.text}")
                
    else:
        st.error(f"Fehler beim Abrufen Ihrer Bilder: {response.text}")

