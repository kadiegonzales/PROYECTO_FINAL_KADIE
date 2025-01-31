import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Load credentials from secrets
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)


db = firestore.Client.from_service_account_json("proyectofinalkadie-firebase-adminsdk-fbsvc-49bb139411.json")



# Initialize Firestore client
db = firestore.Client(credentials=creds, project="PROYECTOFINALKADIE")
dbNames = db.collection("name")

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

# Display the Firestore data
if not names_dataframe.empty:
    st.dataframe(names_dataframe)
else:
    st.write("No data found in Firestore.")

###### BUSQUEDA ############################
def loadByName(name):
    try:
        names_ref = dbNames.where(u'name', u'==', name)
        names = list(names_ref.stream())  # Convert query results to a list
        return names  # Return list of matching documents
    except Exception as e:
        st.error(f"Error while searching for {name}: {e}")
        return []

st.sidebar.subheader("Buscar nombre")
nameSearch = st.sidebar.text_input("nombre")
btnFiltrar = st.sidebar.button("Buscar")

if btnFiltrar:
    names = loadByName(nameSearch)
    if not names:  # If no documents are found
        st.sidebar.write("Nombre no existe")
    else:
        # Display the first matching document as a dictionary
        st.sidebar.write(names[0].to_dict())

########### ELIMINAR ##########################
st.sidebar.markdown("""---""")
btnEliminar = st.sidebar.button("Eliminar")

if btnEliminar:
    names = loadByName(nameSearch)
    if not names:
        st.sidebar.write(f"{nameSearch} no existe")
    else:
        # Delete the first matching document
        dbNames.document(names[0].id).delete()
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
    st.dataframe(names_dataframe)  # Show the full dataset if no filter is applied
