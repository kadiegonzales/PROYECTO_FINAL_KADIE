import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# CARGA LAS CREDENCIALES DE DTREAMLIT
try:
    key_dict = json.loads(st.secrets["textkey"])  
    creds = service_account.Credentials.from_service_account_info(key_dict)
except Exception as e:
    st.error(f"Error loading credentials: {e}")
    st.stop()  

# iNICIALIZAR CLIENTE DE FIRESTORE
try:
    db = firestore.Client(credentials=creds, project="PROYECTOFINALKADIE")
    dbNames = db.collection("name")
except Exception as e:
    st.error(f"Error initializing Firestore client: {e}")
    st.stop()


# CARGA LOS DOCUMENTOS DE FIRESTORE Y LOS CONVIENTE A UN DTAFRAME
def load_firestore_data():
    try:
        
        names_ref = list(dbNames.stream())
       
        names_dict = [doc.to_dict() for doc in names_ref]
        
        names_dataframe = pd.DataFrame(names_dict)
        return names_dataframe
    except Exception as e:
        st.error(f"Error fetching data from Firestore: {e}")
        return pd.DataFrame()  

# CARGA LA DATA DE FIRESTORE
names_dataframe = load_firestore_data()

###### BUSQUEDA ############################
def loadByName(name):
    try:
        # QUERY PARA BUSCAR NOMBRE
        names_ref = dbNames.where(u'name', u'==', name).stream()
        # RETORNA MATCH
        for myname in names_ref:
            return myname
        return None  # NADA SI NO ENCUENTRA
    except Exception as e:
        st.error(f"Error while searching for {name}: {e}")
        return None

st.sidebar.subheader("Buscar nombre")
nameSearch  = st.sidebar.text_input("nombre")
btnFiltrar = st.sidebar.button("Buscar")

if btnFiltrar:
    doc = loadByName(nameSearch)
    if doc is None:
        st.sidebar.write("Nombre no existe")
    else:
        st.sidebar.write(doc.to_dict())

########### ELIMINAR ##########################
st.sidebar.markdown("""---""")
btnEliminar = st.sidebar.button("Eliminar")

if btnEliminar:
    deletename = loadByName(nameSearch)
    if deletename is None:
        st.sidebar.write(f"{nameSearch} no existe")
    else:
        dbNames.document(deletename.id).delete()
        st.sidebar.write(f"{nameSearch} eliminado")

########### INSERTAR ##########################
st.sidebar.subheader("Inserte la informacion que desea agregar")
# Input fields for data
company = st.sidebar.text_input("Company")
director = st.sidebar.text_input("Director")
genre = st.sidebar.text_input("Genre")
name = st.sidebar.text_input("Name")

if st.sidebar.button("Insert into Firebase"):
    if company and director and genre and name:
       
        doc_ref = dbNames.document()  
        doc_ref.set({
            "company": company,
            "director": director,
            "genre": genre,
            "name": name
        })
        st.success("Información insertada correctamente!")
        
        names_dataframe = load_firestore_data()
        st.dataframe(names_dataframe)
    else:
        st.error("Por favor, llene todos los campos!")

################ SIDEBAR CHECKBOX ########################

genre_filter = st.sidebar.checkbox("Filter by Genre", key="genre_filter")

if genre_filter:
    if not names_dataframe.empty:
        genre = st.sidebar.text_input("Enter Genre to Filter By")
        if genre:
            filtered_df = names_dataframe[names_dataframe["genre"] == genre]
            st.write(f"Filtered by genre: {genre}")
            st.dataframe(filtered_df)
        else:
            st.write("Please enter a genre to filter.")
else:
    st.dataframe(names_dataframe)  
