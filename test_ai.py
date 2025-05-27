import requests

url = "http://localhost:5000/ai/rekomendasi"
payload = {
    "vehicle": {
      "tipe": "mobil",
      "merk": "Honda",
      "tipeKendaraan": "Jazz",
      "tahun": 2020,
      "bahanBakar": "Bensin"
    },
    "lastService": {
      "odo": 8000,
      "tanggal": "2024-04-15",
      "jenisServis": ["ganti oli"]
    },
    "masalahKendaraan": "Rem kurang pakem",
    "saranMekanik": "Ganti kampas rem"
}

resp = requests.post(url, json=payload)
print("Status:", resp.status_code)
print("Body:", resp.json())
