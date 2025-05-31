# File: app.py (backend AI untuk Flutter KelarServis, AUTO-PARSE REKOMENDASI!)

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

    # Ambil dua field baru
    masalah = data.get("masalahKendaraan", "Tidak ada masalah spesifik")
    saran_mekanik = data.get("saranMekanik", "Tidak ada saran mekanik")

    # Buat prompt dengan semua data
    prompt = f"""
Kamu adalah asisten servis kendaraan yang andal.  
Berikan rekomendasi servis berikutnya berdasarkan data berikut:
- Tipe Kendaraan   : {kendaraan.get('tipe')}
- Merk & Model     : {kendaraan.get('merk')} / {kendaraan.get('tipeKendaraan', '-')}
- Tahun Perakitan  : {kendaraan.get('tahun')}
- Bahan Bakar      : {kendaraan.get('bahanBakar')}
- Servis Terakhir  : {servis.get('tanggal')} (ODO {servis.get('odo')} km, jenis {', '.join(servis.get('jenisServis', []))})
- Masalah Saat Ini : {masalah}
- Saran Mekanik    : {saran_mekanik}
Kamu bisa memberikan saran terkait kendaraan tersebut mengambil dari luar (berita terkini)
Berikan jawaban dalam 1 paragraf singkat yang mudah dipahami.
Setelah paragraf rekomendasi, tambahkan 2 baris di akhir:
jika ada servis ganti oli maka kamu akan melakukan:
di baris terpisah TULIS DENGAN TEPAT seperti berikut:
Saran Untuk pergantian oli mesin
KM_BERIKUTNYA: [angka] (tanpa titik, tanpa satuan, hanya angka)
TANGGAL_BERIKUTNYA: [tanggal lengkap, misal 15 Agustus 2025]
Contoh:
KM_BERIKUTNYA: 5000
TANGGAL_BERIKUTNYA: 15 Agustus 2025

Jika tidak ada estimasi, tulis:
Saran Untuk pergantian oli mesin
KM_BERIKUTNYA: -
TANGGAL_BERIKUTNYA: -
(hindari kata naratif di depan/di belakang tag!).
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah asisten servis kendaraan profesional."},
                {"role": "user",   "content": prompt}
            ]
        )
        hasil = response.choices[0].message.content.strip()

        # --- PATCH: Extract KM & Tanggal ---
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
            "estimasiJarakKmBerikutnya": estimasi_km,            # patch for Flutter
            "estimasiTanggalBerikutnya": estimasi_tgl
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
