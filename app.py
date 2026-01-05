from flask import Flask, render_template
from rdflib import Graph
import os
import streamlit as st

# --- INISIALISASI FLASK ---
app = Flask(__name__)

def get_staylink_data():
    g = Graph()
    try:
        # Pastikan file staylink.ttl ada di folder utama repo GitHub Anda
        g.parse("staylink.ttl", format="turtle") 
    except Exception as e:
        print(f"Error loading RDF: {e}")
    
    q_hotel = """
    PREFIX schema: <http://schema.org/>
    SELECT ?namaAkomodasi ?rating ?kategori
    WHERE {
        { ?h a schema:Hotel . BIND("Hotel" AS ?kategori) }
        UNION
        { ?h a schema:LodgingBusiness . FILTER NOT EXISTS { ?h a schema:Hotel } BIND("Non-Hotel" AS ?kategori) }
        ?h schema:name ?namaAkomodasi .
        OPTIONAL { ?h schema:starRating ?rating . }
    }
    """
    q_wisata = "PREFIX pref: <http://example.com/preference#> SELECT DISTINCT ?minat WHERE { ?u pref:likes ?minat . }"
    return g.query(q_hotel), g.query(q_wisata)

# Fungsi render halaman index
def get_index_html():
    hotels, wisata = get_staylink_data()
    return render_template('index.html', hotels=hotels, wisata=wisata)

# Fungsi render halaman detail
def get_detail_html(nama, kategori):
    hotel_prices = {
        "cozrooms near mrt, plaza indonesia, and grand indonesia": "200.000",
        "grand hyatt jakarta": "2.500.000", 
        "hotel indonesia kempinski": "2.500.000",
        "ibis styles tanah abang": "600.000", 
        "jw marriott hotel jakarta": "1.700.000",
        "jambuluwuk heritage menteng suites": "350.000", 
        "legreen suite tondano pejompongan": "300.000",
        "lugano arte": "280.000", 
        "mercure jakarta cikini": "750.000", 
        "moxy jakarta kemang": "600.000",
        "residence 100": "230.000", 
        "the sultan hotel & residence": "1.500.000",
        "aston priority simatupang": "600.000",
        "favehotel tanah abang": "400.000",
        "grand mercure kemayoran": "750.000",
        "homestay 2 putra pulau harapan": "350.000", 
        "homestay amarudin pulau harapan": "300.000",
        "homestay anam pulau harapan": "300.000", 
        "homestay emen pulau harapan": "300.000",
        "homestay goby pulau harapan": "330.000", 
        "homestay marisa muridi pulau harapan": "330.000",
        "homestay melli surya pulau harapan": "250.000", 
        "homestay zahra pulau harapan": "300.000",
        "homestay koja bahrudin pulau harapan": "250.000", 
        "lobster homestay pulau untungjawa": "250.000"
    }

    hotel_coords = {
        "jw marriott hotel jakarta": {"lat": "-6.227028", "long": "106.826940"},
        "hotel indonesia kempinski": {"lat": "-6.195579570620385", "long": "106.82228453602718"},
        "grand hyatt jakarta": {"lat": "-6.1937531", "long": "106.820341"},
        "mercure jakarta cikini": {"lat": "-6.196310", "long": "106.841760"},
        "grand mercure kemayoran": {"lat": "-6.162690", "long": "106.849910"},
        "the sultan hotel & residence": {"lat": "-6.223300", "long": "106.808200"},
        "ibis styles tanah abang": {"lat": "-6.185910", "long": "106.815050"},
        "aston priority simatupang": {"lat": "-6.291240", "long": "106.821620"},
        "favehotel tanah abang": {"lat": "-6.186000", "long": "106.816100"},
        "moxy jakarta kemang": {"lat": "-6.267190", "long": "106.812240"},
        "lobster homestay pulau untungjawa": {"lat": "-6.0385", "long": "106.8790"},
        "homestay anam pulau harapan": {"lat": "-5.5780", "long": "106.5710"},
        "homestay emen pulau harapan": {"lat": "-5.5785", "long": "106.5712"},
        "homestay koja bahrudin pulau harapan": {"lat": "-5.5783", "long": "106.5715"},
        "homestay marisa muridi pulau harapan": {"lat": "-5.5781", "long": "106.5714"},
        "homestay zahra pulau harapan": {"lat": "-5.5779", "long": "106.5711"},
        "homestay melli surya pulau harapan": {"lat": "-5.5777", "long": "106.5713"},
        "homestay 2 putra pulau harapan": {"lat": "-5.5775", "long": "106.5715"},
        "homestay goby pulau harapan": {"lat": "-5.5773", "long": "106.5716"},
        "homestay amarudin pulau harapan": {"lat": "-5.5771", "long": "106.5717"}
    }
    
    nama_lower = nama.lower()
    img_dir = os.path.join(app.root_path, 'static/images')
    image_file = "no_image.jpg"
    coords = hotel_coords.get(nama_lower, {"lat": "-6.2088", "long": "106.8456"})
    
    full_name = nama_lower.replace(" jakarta", "").replace(" hotel", "").replace(" & residence", "").replace(" ", "_").replace(",", "")
    
    extensions = ['.jpeg', '.jpg', '.webp', '.png', '.JPG']
    for ext in extensions:
        if os.path.exists(os.path.join(img_dir, full_name + ext)):
            image_file = full_name + ext
            break
        elif "aston" in full_name and os.path.exists(os.path.join(img_dir, "aston_priority" + ext)):
            image_file = "aston_priority" + ext
            break

    facilities = ["Free Wi-Fi", "Swimming Pool", "Fitness Center", "Restaurant", "Parking Space", "24-Hour Room Service"] if kategori == "Hotel" else ["Free Wi-Fi", "AC", "Cafe", "24-Hour Room Service", "Parking Space"]
    price = hotel_prices.get(nama_lower, "---")
    
    return render_template('detail.html', 
                           nama_hotel=nama, harga=price, facilities=facilities, 
                           kategori=kategori, image_file=image_file,
                           lat=coords['lat'], long=coords['long'])

# --- KONFIGURASI STREAMLIT ---
st.set_page_config(page_title="StayLink Jakarta", layout="wide")

# CSS untuk menyembunyikan header/footer Streamlit
st.markdown("""
    <style>
    .block-container { padding: 0rem; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Logika Navigasi Halaman
query_params = st.query_params

if "page" in query_params and query_params["page"] == "detail":
    nama_req = query_params.get("nama", "Hotel")
    kat_req = query_params.get("kat", "Hotel")
    with app.app_context():
        content = get_detail_html(nama_req, kat_req)
        st.components.v1.html(content, height=1200, scrolling=True)
else:
    with app.app_context():
        content = get_index_html()
        st.components.v1.html(content, height=1500, scrolling=True)