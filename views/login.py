import streamlit as st


def login_page(cookies):
    st.title("Login")
    
    # Login-Formular
    user = st.text_input("Benutzername")
    
    if st.button("Login"):
        if user:
            # Cookies setzen (7 Tage gültig)
            cookies["user_logged_in"] = "true"
            cookies["username"] = user
            cookies.save()  # Cookies speichern
            
            st.success("Login erfolgreich!")
            st.rerun()  # App neu laden
        else:
            st.error("Ungültige Anmeldedaten")
