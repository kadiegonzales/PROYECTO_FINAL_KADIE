import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
#db = firestore.Client(credentials=creds, project="names-project-demo")

#db = firestore.Client.from_service_account_json("proyectofinalkadie-firebase-adminsdk-fbsvc-49bb139411.json")
#dbNames = db.collection("name")


db = firestore.Client(credentials=creds, project="PROTECTOFINALKADIE")
dbNames = db.collection("name")




#names_ref = list(db.collection(u'name').stream())
#names_dict =list(map(lambda x: x.to_dict(), names_ref))
#names_dataframe = pd.DataFrame(names_dict)
#st.dataframe(names_dataframe)

######BUSQUEDA############################
def loadByName(name):
  names_ref = dbNames.where(u'name', u'==', name)
  currentName = None
  for myname in names_ref.stream():
    currentName = myname
    return currentName

st.sidebar.subheader("Buscar nombre")
nameSearch  = st.sidebar.text_input("nombre")
btnFiltrar = st.sidebar.button("Buscar")

if btnFiltrar:
  doc = loadByName(nameSearch)
  if doc is None:
    st.sidebar.write("Nombre no existe")
  else:
    st.sidebar.write(doc.to_dict())

###########ELIMNA##########################
st.sidebar.markdown("""---""")
btnEliminar = st.sidebar.button("Eliminar")

if btnEliminar:
  deletename = loadByName(nameSearch)
  if deletename is None:
    st.sidebar.write(f"{nameSearch} no existe")
  else:
    dbNames.document(deletename.id).delete()
    st.sidebar.write(f"{nameSearch} eliminado")

###########ACTUALIZAR##########################
#st.sidebar.markdown("""---""")
#newname = st.sidebar.text_input("Actualizar nombre")
#btnActualizar = st.sidebar.button("Actualizar")
#if btnActualizar:
# updatename = loadByName(nameSearch)
# if updatename is None:
#   st.write(f"{nameSearch} no existe")
# else:
#   myupdatename = dbNames.document(updatename.id)
#   myupdatename.update(
# {
#"name": newname
# }
# )

st.sidebar.subheader("Inserte la informacion que desea agregar")
# Input fields for data
company = st.sidebar.text_input("Company")
director = st.sidebar.text_input("Director")
genre = st.sidebar.text_input("Genre")
name = st.sidebar.text_input("Name")


if st.sidebar.button("Insert into Firebase"):
    if company and director and genre and name:
        # Reference to the Firestore collection
        doc_ref = db.collection("name").document()  # You can specify a document ID or let Firestore auto-generate one
        doc_ref.set({
            "company": company,
            "director": director,
            "genre": genre,
            "name": name
        })
        st.success("Informacion insertada correctamente!")
    else:
        st.error("Porfavor llene todos los campos!")

################SIDEBAR CHECKBOX########################

genre_filter = st.sidebar.checkbox("Filter by Genre", key="genre_filter")

if genre_filter:

    filtered_df = names_dataframe[names_dataframe["genre"] == "Your desired genre"]
    st.dataframe(filtered_df)
else:

    st.dataframe(names_dataframe)




# ...
names_ref = list(db.collection(u'names').stream())
names_dict = list(map(lambda x: x.to_dict(), names_ref))
names_dataframe = pd.DataFrame(names_dict)
st.dataframe(names_dataframe)
