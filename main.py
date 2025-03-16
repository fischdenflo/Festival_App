import streamlit as st
from views.my_gallery import my_gallery_page
from views.upload import upload_page
from views.voting import voting_page
from streamlit_cookies_manager import EncryptedCookieManager

# Cookie-Manager initialisieren
cookies = EncryptedCookieManager(
    prefix="festival",  # Präfix für alle Cookie-Namen
    password=st.secrets["pocketbase"]["secret"]     # Passwort für die Verschlüsselung
)

def upload_page_wrapper():
    return upload_page(cookies)

def my_gallery_page_wrapper():
    return my_gallery_page(cookies)

def vote_page_wrapper():
    return voting_page(cookies)

pages = {
    "Wettbewerb": [
        st.Page(upload_page_wrapper, title="Upload"),
        st.Page(my_gallery_page_wrapper, title="Meine Bilder"),
        st.Page(vote_page_wrapper, title="Votings"),
    ]
}

pg = st.navigation(pages)
pg.run()
