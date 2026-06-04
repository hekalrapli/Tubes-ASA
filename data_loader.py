"""
data_loader.py
--------------
Membaca file CSV dataset pemain dan mengembalikan list of Player.
Mendukung berbagai nama kolom secara fleksibel 
"""

import csv
from typing import List

from models import Player
from utils import deteksi_kolom, konversi_posisi, parse_harga


def baca_dataset(nama_file: str) -> List[Player]:
    """
    Membaca file CSV dan mengembalikan daftar objek Player.

    Kolom yang dibaca (nama fleksibel, lihat utils._KANDIDAT_KOLOM):
        nama, usia, posisi, skor kemampuan, harga pasar

    Parameters
    ----------
    nama_file : str
        Path ke file CSV.

    Returns
    -------
    List[Player]
        Daftar pemain yang berhasil dibaca.

    Raises
    ------
    FileNotFoundError
        Jika file tidak ditemukan.
    ValueError
        Jika kolom yang diperlukan tidak ada di header.
    """
    players: List[Player] = []

    with open(nama_file, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])
        kolom  = deteksi_kolom(header)

   
        diperlukan = ['nama', 'usia', 'posisi', 'skor', 'harga']
        hilang = [d for d in diperlukan if d not in kolom]
        if hilang:
            raise ValueError(
                f"Kolom berikut tidak ditemukan di CSV: {hilang}\n"
                f"Header yang terbaca: {header}"
            )

        for i, baris in enumerate(reader, start=1):
            try:
                posisi = konversi_posisi(baris[kolom['posisi']])
                harga  = parse_harga(baris[kolom['harga']])
                skor   = int(baris[kolom['skor']])
                usia   = int(baris[kolom['usia']])
                nama   = baris[kolom['nama']].strip()
                players.append(Player(i, nama, usia, posisi, skor, harga))
            except (ValueError, KeyError) as e:
           
                print(f"  [Peringatan] Baris {i + 1} dilewati: {e}")

    return players
