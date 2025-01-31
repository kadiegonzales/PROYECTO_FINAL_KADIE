import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Load credentials from Streamlit secrets (ensure this is set in your Streamlit secrets management)
#try:
#    key_dict = json.loads(st.secrets["textkey"])  # This should contain the service account credentials
#    creds = service_account.Credentials.from_service_account_info(key_dict)
#except Exception as e:
#    st.error(f"Error loading credentials: {e}")
#    st.stop()  # Stop execution if credentials can't be loaded

# Initialize Firestore client
#try:
#    db = firestore.Client(credentials=creds, project="PROYECTOFINALKADIE")
#    dbNames = db.collection("name")
#except Exception as e:
#    st.error(f"Error initializing Firestore client: {e}")
#    st.stop()


# ... (rest of your code)

# Initialize Firestore client
try:
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    # Specify your project explicitly
    db = firestore.Client(credentials=creds, project="PROYECTOFINALKADIE")  
    dbNames = db.collection("name")
except Exception as e:
    st.error(f"Error initializing Firestore client: {e}")
    st.stop()



# Function to load all documents from Firestore and convert to DataFrame
def load_firestore_data():
    try:
        # Fetch all documents from the Firestore collection
        names_ref = list(dbNames.stream())
        # Convert Firestore documents to a list of dictionaries
        names_dict = [doc.to_dict() for doc in names_ref]
        # Convert to DataFrame for easier display in Streamlit
        names_dataframe = pd.DataFrame(names_dict)
        return names_dataframe
    except Exception as e:
        st.error(f"Error fetching data from Firestore: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

# Load the Firestore data
names_dataframe = load_firestore_data()

###### BUSQUEDA ############################
def loadByName(name):
    try:
        # Query to search for the name
        names_ref = dbNames.where(u'name', u'==', name).stream()
        # Return the first matching document
        for myname in names_ref:
            return myname
        return None  # Return None if no matching name is found
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
        # Reference to the Firestore collection
        doc_ref = dbNames.document()  # Firestore will auto-generate a document ID
        doc_ref.set({
            "company": company,
            "director": director,
            "genre": genre,
            "name": name
        })
        st.success("Información insertada correctamente!")
        # Refresh the dataframe after insertion
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
    st.dataframe(names_dataframe)  # Show the full dataset if no filter is applie
