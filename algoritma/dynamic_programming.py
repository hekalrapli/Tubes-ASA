"""
algorithms/dynamic_programming.py
-----------------------------------
Implementasi algoritma Dynamic Programming berbasis dictionary
untuk optimasi pemilihan pemain.

State DP:
    (budget_terpakai_skala, jml_Kiper, jml_Bek, jml_Gelandang, jml_Penyerang)

skala harga:
    Harga dan budget dikonversi ke satuan 500 ribu euro (skala = 500_000).
    Dengan budget €300M, dimensi state budget hanya 0–600,
    cukup kecil untuk dictionary DP namun presisi 2x lebih baik dari 1M
    sehingga harga seperti €42.5M tidak dibulatkan menjadi €43M.
    Harga tiap pemain dibulatkan ke atas (ceil) agar tidak melebihi budget.
"""

import math
from typing import Dict, List, Tuple

from models import Player


# Indeks posisi dalam tuple state (urutan tetap)
posisi_idx: Dict[str, int] = {
    'Kiper': 0, 'Bek': 1, 'Gelandang': 2, 'Penyerang': 3
}

# Satuan skala harga: 500 ribu euro (0.5M).
# Menggunakan 500K (bukan 1M) agar harga seperti €42.5M atau €33.5M
# tidak dibulatkan terlalu kasar — selisih pembulatan maksimal €0.5M
# sehingga kombinasi valid tidak terbuang karena kesalahan skala.
# Konsekuensinya dimensi state budget menjadi 2x lebih besar (misal
# budget €300M → 600 unit), namun tetap manageable dengan dictionary DP.
skala = 500_000


def dynamic_programming(
    players:   List[Player],
    budget:    float,
    kebutuhan: Dict[str, int],
) -> Tuple[List[Player], int]:
    """
    Dynamic Programming untuk memilih kombinasi pemain dengan total skor tertinggi.

    Parameters
    ----------
    players   : daftar semua pemain yang tersedia
    budget    : anggaran maksimum dalam euro
    kebutuhan : kebutuhan per posisi, misal {'Kiper':1, 'Bek':3, ...}

    Returns
    -------
    (list pemain terpilih, total skor)
    """
    budget_skala = math.floor(budget / skala)

    max_posisi = [
        kebutuhan.get('Kiper',     0),
        kebutuhan.get('Bek',       0),
        kebutuhan.get('Gelandang', 0),
        kebutuhan.get('Penyerang', 0),
    ]
    total_kebutuhan = sum(max_posisi)

    # dp[state] = (total_skor, [indeks pemain terpilih])
    # State awal: tidak ada pemain dipilih, budget terpakai = 0
    dp: Dict[Tuple, Tuple[int, List[int]]] = {
        (0, 0, 0, 0, 0): (0, [])
    }

    for i, pemain in enumerate(players):
        pos_idx = posisi_idx.get(pemain.posisi)
        if pos_idx is None:
            continue   # Posisi tidak dikenal, lewati

        harga_skala = math.ceil(pemain.harga / skala)

        # Iterasi salinan state saat ini (snapshot) agar tidak self-update
        for state, (skor, daftar_idx) in list(dp.items()):
            b, k, bk, g, py = state
            pos_count = [k, bk, g, py]

            # Constraint 1: posisi untuk pemain ini belum penuh
            if pos_count[pos_idx] >= max_posisi[pos_idx]:
                continue

            # Constraint 2: budget tidak melebihi
            b_baru = b + harga_skala
            if b_baru > budget_skala:
                continue

            # Constraint 3: total pemain tidak melebihi kebutuhan
            if k + bk + g + py + 1 > total_kebutuhan:
                continue

            # Bangun state baru
            pos_baru         = list(pos_count)
            pos_baru[pos_idx] += 1
            state_baru = (b_baru, pos_baru[0], pos_baru[1],
                          pos_baru[2], pos_baru[3])
            skor_baru  = skor + pemain.skor

            # Simpan hanya jika lebih baik dari state yang sudah ada
            if state_baru not in dp or dp[state_baru][0] < skor_baru:
                dp[state_baru] = (skor_baru, daftar_idx + [i])

    # Cari state akhir yang tepat memenuhi semua kebutuhan posisi
    k_max, bk_max, g_max, py_max = max_posisi
    best_skor    = 0
    best_indices: List[int] = []

    for state, (skor, indices) in dp.items():
        _, k, bk, g, py = state
        if k == k_max and bk == bk_max and g == g_max and py == py_max:
            if skor > best_skor:
                best_skor    = skor
                best_indices = indices

    best_players = [players[i] for i in best_indices]
    return best_players, best_skor
