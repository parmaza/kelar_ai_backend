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
    data = request.get_json()

    kendaraan = data.get("vehicle", {})
    servis = data.get("lastService", {})

    prompt = f"""
    Kamu adalah asisten pemilik kendaraan. Berikan rekomendasi servis berikutnya berdasarkan data berikut:
    - Tipe Kendaraan: {kendaraan.get('tipe')}
    - Merk: {kendaraan.get('merk')}
    - Tahun: {kendaraan.get('tahun')}
    - Bahan Bakar: {kendaraan.get('bahanBakar')}
    - Servis terakhir pada: {servis.get('tanggal')} dengan ODO: {servis.get('odo')} km
    - Jenis servis terakhir: {', '.join(servis.get('jenisServis', []))}

    Berikan rekomendasi dalam 1 paragraf singkat dan mudah dipahami.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah asisten servis kendaraan yang andal."},
                {"role": "user", "content": prompt}
            ]
        )
        hasil = response.choices[0].message.content.strip()
        return jsonify({"rekomendasi": hasil})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
