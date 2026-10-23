import math
import random
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Optimasi Rute Sampah CVRP Irwan+RENXY", page_icon="🗑️", layout="wide"
)

st.title("🗑️ Sistem Penjemputan Sampah Terjadwal (CVRP)")
st.write(
    "Aplikasi Optimasi Rute Penjemputan Sampah menggunakan **Algoritma Genetika (Genetic Algorithm)** oleh IRWAN ABDULLAH & RENXY LICHANDY."    
)
st.write(
    "Mata Kuliah ALGORITHM DESIGN AND ANALYSIS, Dosen : Dr. CHOIRUL BASIR S.Si. , M.Si"
)

# Sidebar - Parameter Sistem
st.sidebar.header("⚙️ Parameter Sistem")
kapasitas_truk = st.sidebar.number_input(
    "Kapasitas Maksimal Truk (kg)", value=1000, step=100
)
jumlah_pelanggan = st.sidebar.number_input(
    "Jumlah Lokasi Penjemputan", min_value=2, max_value=15, value=5
)
generasi = st.sidebar.slider("Jumlah Generasi (GA)", 50, 500, 100)

# Form Input Pelanggan
st.header("📋 Input Data Pelanggan & Sampah")
daftar_pesanan = []

# Membuat kolom input interaktif
col1, col2 = st.columns(2)

for i in range(1, jumlah_pelanggan + 1):
    target_col = col1 if i % 2 != 0 else col2
    with target_col:
        with st.expander(f"📍 Data Lokasi #{i}", expanded=True):
            nama = st.text_input(
                f"Nama Lokasi/Pelanggan #{i}", value=f"Lokasi {i}"
            )
            alamat = st.text_input(f"Alamat/Area #{i}", value=f"Jl. Area {i}")
            berat = st.number_input(
                f"Berat Sampah (kg) #{i}",
                min_value=50,
                max_value=800,
                value=random.choice([200, 300, 400, 500]),
            )
            tanggal = st.date_input(f"Tanggal Penjemputan #{i}")

            # Simulasi Koordinat Lokasi
            random.seed(i * 10)
            x_pos = random.randint(-10, 10)
            y_pos = random.randint(-10, 10)

            daftar_pesanan.append({
                "id": i,
                "nama": nama,
                "alamat": alamat,
                "berat": berat,
                "tanggal": tanggal,
                "pos": (x_pos, y_pos),
            })


# Fungsi Jarak & Fitness
def hitung_jarak(pos1, pos2):
    return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1])


def dekode_rute(kromosom, dict_p, kap_max):
    rute_total, rute_saat_ini, beban = [], [], 0
    for p_id in kromosom:
        demand = dict_p[p_id]["berat"]
        if beban + demand <= kap_max:
            rute_saat_ini.append(p_id)
            beban += demand
        else:
            rute_total.append(rute_saat_ini)
            rute_saat_ini = [p_id]
            beban = demand
    if rute_saat_ini:
        rute_total.append(rute_saat_ini)
    return rute_total


# Tombol Proses Optimasi
st.markdown("---")
if st.button("🚀 HITUNG RUTE OPTIMAL", type="primary", use_container_width=True):
    pelanggan_ids = [p["id"] for p in daftar_pesanan]
    dict_pelanggan = {p["id"]: p for p in daftar_pesanan}
    depot = (0, 0)

    # Simple Genetic Algorithm Exec
    populasi = [
        random.sample(pelanggan_ids, len(pelanggan_ids)) for _ in range(30)
    ]

    for _ in range(generasi):

        def fitness(k):
            rutes = dekode_rute(k, dict_pelanggan, kapasitas_truk)
            tot = 0
            for r in rutes:
                p_seb = depot
                for p_id in r:
                    p_skrg = dict_pelanggan[p_id]["pos"]
                    tot += hitung_jarak(p_seb, p_skrg)
                    p_seb = p_skrg
                tot += hitung_jarak(p_seb, depot)
            return tot

        populasi.sort(key=fitness)
        pop_baru = populasi[:2]  # Elitismus
        while len(pop_baru) < 30:
            parent = random.choice(populasi[:10]).copy()
            i1, i2 = random.sample(range(len(parent)), 2)
            parent[i1], parent[i2] = parent[i2], parent[i1]  # Mutasi
            pop_baru.append(parent)
        populasi = pop_baru

    kromosom_terbaik = min(populasi, key=fitness)
    rute_optimal = dekode_rute(
        kromosom_terbaik, dict_pelanggan, kapasitas_truk
    )

    # TAMPILKAN HASIL
    st.subheader("📊 Hasil Optimasi Rute Armada")

    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("### Detail Jadwal Penjemputan")
        for idx, rute in enumerate(rute_optimal, 1):
            total_beban = sum(dict_pelanggan[p_id]["berat"] for p_id in rute)
            st.info(
                f"**Armada #{idx}** | Total Muatan: **{total_beban} kg** / {kapasitas_truk} kg"
            )
            for p_id in rute:
                p = dict_pelanggan[p_id]
                st.write(
                    f" - 📍 **{p['nama']}** ({p['alamat']}) — `{p['berat']} kg`"
                )

    with c2:
        st.markdown("### Peta Rute Visual")
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.plot(
            depot[0],
            depot[1],
            "rs",
            markersize=12,
            label="Depot / TPA",
            zorder=5,
        )

        colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b"]
        for idx, rute in enumerate(rute_optimal):
            color = colors[(idx - 1) % len(colors)]
            x_c, y_c = [depot[0]], [depot[1]]

            for p_id in rute:
                p = dict_pelanggan[p_id]
                x_c.append(p["pos"][0])
                y_c.append(p["pos"][1])
                ax.plot(
                    p["pos"][0],
                    p["pos"][1],
                    "o",
                    color=color,
                    markersize=8,
                    zorder=4,
                )
                ax.annotate(
                    f"{p['nama']}",
                    (p["pos"][0] + 0.3, p["pos"][1] + 0.3),
                    fontsize=8,
                )

            x_c.append(depot[0])
            y_c.append(depot[1])
            ax.plot(
                x_c,
                y_c,
                color=color,
                linestyle="--",
                linewidth=2,
                label=f"Armada #{idx + 1}",
            )

        ax.set_title("Visualisasi Rute Penjemputan Sampah")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper right", fontsize="small")
        st.pyplot(fig)
