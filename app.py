# File: app.py (Backend AI untuk Flutter KelarServis, AI Otomatis & Output Rinci)

from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
import re

# Load .env
load_dotenv()

app = Flask(__name__)

# Init client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/ai/rekomendasi", methods=["POST"])
def rekomendasi_servis():
    data = request.get_json() or {}

    # Ambil data kendaraan & servis
    kendaraan = data.get("vehicle", {})
    servis = data.get("lastService", {})

    # Field baru untuk keluhan & saran mekanik
    masalah = data.get("masalahKendaraan", "Tidak ada masalah spesifik")
    saran_mekanik = data.get("saranMekanik", "Tidak ada saran mekanik")

    # Prompt AI terbaru: personal, spesifik, dan patuh format
    prompt = f"""
Kamu adalah asisten servis kendaraan berbasis AI yang sangat ahli dan akurat.
Tugas kamu:
1. Analisis semua data berikut secara menyeluruh.
2. Berikan rekomendasi servis berikutnya secara RINCI dan TEPAT, dengan mempertimbangkan seluruh informasi di bawah ini:
   - Tipe Kendaraan   : {kendaraan.get('tipe')}
   - Merk & Model     : {kendaraan.get('merk')} / {kendaraan.get('tipeKendaraan', '-')}
   - Tahun Perakitan  : {kendaraan.get('tahun')}
   - Bahan Bakar      : {kendaraan.get('bahanBakar')}
   - Servis Terakhir  : {servis.get('tanggal')} (ODO {servis.get('odo')} km, jenis {', '.join(servis.get('jenisServis', []))})
   - Masalah Saat Ini : {masalah}
   - Saran Mekanik    : {saran_mekanik}

Gunakan setiap data di atas untuk membuat rekomendasi yang benar-benar personal, spesifik, dan informatif.
Jelaskan alasan rekomendasi terkait kondisi kendaraan dan faktor-faktor yang relevan (misal: usia kendaraan, tipe mesin, bahan bakar, keluhan, dsb).

Setelah rekomendasi, TAMBAHKAN 2 baris berikut PERSIS seperti format ini (tidak boleh ada narasi tambahan di bawahnya!):
Saran Untuk pergantian oli mesin setelah menempuh jarak
KM_BERIKUTNYA: [angka]     # hanya angka, misal 7000. BUKAN "ODO sekarang + 4000". Jangan tulis satuan. Jika tidak diketahui, tulis tanda minus.
TANGGAL_BERIKUTNYA: [tanggal lengkap, misal 15 Agustus 2025]  # atau tanda minus jika tidak diketahui

Contoh output yang BENAR:
(paragraf rekomendasi)
Saran Untuk pergantian oli mesin 
(Jarak Tempuh) KM_BERIKUTNYA: 5000
TANGGAL_BERIKUTNYA: 15 Agustus 2025

Contoh yang SALAH (JANGAN BUAT INI!):
KM_BERIKUTNYA: ODO sekarang + 4000
KM_BERIKUTNYA: 10.000 km

Instruksi:
- Rekomendasi harus mempertimbangkan secara detail merk, tipe, tahun, bahan bakar, masalah, dan saran mekanik.
- Format output di bagian akhir HARUS mengikuti contoh BENAR tanpa narasi tambahan.
- Jika tidak ada data estimasi, tulis tanda "-".

Tunjukkan hasil analisis dan rekomendasi kamu dengan bahasa yang jelas, padat, dan tidak mengulang informasi yang sama.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah asisten servis kendaraan profesional, dan mekanik automotif yang handal"},
                {"role": "user",   "content": prompt}
            ]
        )
        hasil = response.choices[0].message.content.strip()

        # --- PATCH: Extract KM & Tanggal (Tetap Support Output yang Konsisten) ---
        km_match = re.search(r'KM_BERIKUTNYA:\s*([0-9\-]+)', hasil)
        tgl_match = re.search(r'TANGGAL_BERIKUTNYA:\s*([^\n\r]+)', hasil)

        estimasi_km = km_match.group(1) if km_match else None
        estimasi_tgl = tgl_match.group(1) if tgl_match else None

        # Hilangkan nilai "-" sebagai null
        if estimasi_km == '-' or not estimasi_km or not estimasi_km.strip():
            estimasi_km = None
        if estimasi_tgl == '-' or not estimasi_tgl or not estimasi_tgl.strip():
            estimasi_tgl = None

        return jsonify({
            "rekomendasi": hasil,
            "estimasiJarakKmBerikutnya": estimasi_km,      # Patch for Flutter
            "estimasiTanggalBerikutnya": estimasi_tgl
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
