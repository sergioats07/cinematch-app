import streamlit as st
import requests

st.set_page_config(page_title="CineMatch Global", layout="centered")

st.title("CineMatch: Buscador Mundial")
st.markdown("Busca películas y series de cualquier año combinando tus gustos, encuestas y peticiones libres.")

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

if not st.session_state.usuario:
    st.subheader("Registro de Usuario")
    nombre_input = st.text_input("Ingresa tu nombre de usuario:")
    
    if st.button("Empezar a Buscar"):
        if nombre_input.strip() != "":
            st.session_state.usuario = nombre_input.strip()
            st.rerun()
        else:
            st.warning("El nombre de usuario no puede estar vacío.")
else:
    st.sidebar.write(f"Usuario: {st.session_state.usuario}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario = ""
        st.rerun()

    st.divider()

    with st.form("form_encuesta_historica"):
        st.subheader("Tus Preferencias y Criterios")
        
        tipo_contenido = st.selectbox("¿Qué deseas explorar?", ["Película", "Serie de TV"])
        
        genero_seleccionado = st.selectbox(
            "Género principal:", 
            ["Todos", "Acción", "Aventura", "Ciencia Ficción", "Drama", "Comedia", "Terror", "Suspenso"]
        )
        
        peticion_libre = st.text_input(
            "¿Qué buscas específicamente?", 
            placeholder="Ej: autos veloces, viajes espaciales, clásicos..."
        )
        
        usar_filtro_rango = st.checkbox("Filtrar por un rango de años de estreno")
        rango_anos = st.slider("Selecciona el rango de años:", 1900, 2026, (2000, 2015))
        
        btn_buscar = st.form_submit_button("Buscar en la Base de Datos Mundial")

    if btn_buscar:
        try:
            api_key = st.secrets["TMDB_API_KEY"]
        except:
            api_key = ""

        if not api_key:
            st.error("La llave de acceso al sistema no está configurada en el servidor.")
        else:
            with st.spinner("Explorando el archivo histórico mundial de cine..."):
                
                generos_ids = {
                    "Acción": 28, "Aventura": 12, "Ciencia Ficción": 878, 
                    "Drama": 18, "Comedia": 35, "Terror": 27, "Suspenso": 53
                }
                
                endpoint_tipo = "movie" if tipo_contenido == "Película" else "tv"
                genre_id = generos_ids.get(genero_seleccionado, None)
                ano_inicio, ano_fin = rango_anos
                
                try:
                    if peticion_libre.strip() != "":
                        url_api = f"https://api.themoviedb.org/3/search/{endpoint_tipo}?api_key={api_key}&query={requests.utils.quote(peticion_libre)}&language=es-ES&include_adult=false"
                    else:
                        url_api = f"https://api.themoviedb.org/3/discover/{endpoint_tipo}?api_key={api_key}&language=es-ES&sort_by=vote_average.desc&vote_count.gte=200"
                        if endpoint_tipo == "movie" and usar_filtro_rango:
                            url_api += f"&primary_release_date.gte={ano_inicio}-01-01&primary_release_date.lte={ano_fin}-12-31"
                        elif endpoint_tipo == "tv" and usar_filtro_rango:
                            url_api += f"&first_air_date.gte={ano_inicio}-01-01&first_air_date.lte={ano_fin}-12-31"
                        
                        if genre_id:
                            url_api += f"&with_genres={genre_id}"

                    respuesta = requests.get(url_api, timeout=10)
                    
                    if respuesta.status_code == 200:
                        datos = respuesta.json()
                        resultados = datos.get("results", [])

                        if resultados:
                            st.success(f"Se encontraron {len(resultados)} títulos para {st.session_state.usuario}.")
                            st.markdown("---")
                            
                            for item in resultados[:10]:
                                titulo = item.get("title") or item.get("name") or "Título desconocido"
                                sinopsis = item.get("overview") or "Sin sinopsis detallada disponible."
                                calificacion = item.get("vote_average", 0.0)
                                votos = item.get("vote_count", 0)
                                fecha = item.get("release_date") or item.get("first_air_date") or "Fecha no disponible"
                                poster = item.get("poster_path")

                                col_img, col_info = st.columns([1, 3])
                                
                                with col_img:
                                    if poster:
                                        st.image(f"https://image.tmdb.org/t/p/w200{poster}", width=130)
                                    else:
                                        st.info("No hay imagen")
                                        
                                with col_info:
                                    st.markdown(f"### **{titulo}**")
                                    st.write(f"Estreno: {fecha}")
                                    st.markdown(f"Calificación Global: {calificacion}/10 ({votos} votos)")
                                    st.write(sinopsis)
                                    
                                st.markdown("---")
                        else:
                            st.warning("No se encontraron títulos con esos criterios específicos.")
                    
                    else:
                        st.error(f"Error al consultar la base de datos (Código: {respuesta.status_code})")

                except requests.exceptions.RequestException as err:
                    st.error(f"Error de conexión a internet: {err}")
                except Exception as e:
                    st.error(f"Ocurrió un error inesperado: {e}")