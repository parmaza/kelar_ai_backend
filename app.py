# File: app.py (untuk openai>=1.0.0)
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

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

jika ada servis ganti oli maka kamu akan melakukan:
1. Estimasi kilometer berikutnya untuk servis rutin dengan format KM_BERIKUTNYA
2. Estimasi waktu berikutnya (dan sebutkan juga tanggal dan hari tepatnya dihitung dari tanggal servis terakhir) dengan format TANGGAL_BERIKUTNYA
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
        return jsonify({"rekomendasi": hasil})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
