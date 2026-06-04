"""
algorithms/branch_and_bound.py
-------------------------------
Implementasi algoritma Branch and Bound (rekursif) untuk optimasi
pemilihan pemain. Berjalan sepenuhnya mandiri tanpa bantuan algoritma lain.

Strategi:
  - Pemain dikelompokkan per posisi, tiap kelompok diurutkan skor menurun
  - Eksplorasi dilakukan posisi per posisi (bukan pemain per pemain)
    sehingga setiap cabang selalu menghasilkan solusi yang valid secara posisi
  - Pruning: upper bound skor sisa ≤ gap yang dibutuhkan → cabang dipangkas
  - Time limit 10 detik: jika waktu habis, kembalikan solusi terbaik saat itu
"""

import time
from typing import Dict, List, Tuple

from models import Player

time_limit = 10.0


def branch_and_bound(
    players:    List[Player],
    budget:     float,
    kebutuhan:  Dict[str, int],
    time_limit: float = time_limit,
) -> Tuple[List[Player], int]:
    """
    Branch and Bound untuk memilih kombinasi pemain dengan total skor tertinggi.

    Pendekatan: eksplorasi per-posisi.
    Urutan posisi: Kiper → Bek → Gelandang → Penyerang.
    Untuk tiap posisi, coba semua kombinasi C(kandidat, jumlah_dibutuhkan)
    secara rekursif dengan pruning.

    Parameters
    ----------
    players    : daftar semua pemain yang tersedia
    budget     : anggaran maksimum dalam euro
    kebutuhan  : kebutuhan per posisi, misal {'Kiper':1, 'Bek':3, ...}
    time_limit : batas waktu eksekusi dalam detik (default 10 detik)

    Returns
    -------
    (list pemain terpilih, total skor)
    """
    start_time = time.perf_counter()
    timed_out  = [False]

    # Urutan posisi yang dieksplorasi
    urutan_posisi = [p for p in ['Kiper', 'Bek', 'Gelandang', 'Penyerang']
                     if p in kebutuhan]

    # Kelompokkan dan urutkan kandidat per posisi (skor menurun)
    kandidat_per_posisi: Dict[str, List[Player]] = {
        pos: sorted(
            [p for p in players if p.posisi == pos],
            key=lambda p: p.skor,
            reverse=True,
        )
        for pos in urutan_posisi
    }

    # Hitung upper bound skor per posisi: ambil top-N skor tanpa peduli budget
    # Digunakan untuk pruning: jika skor_skrg + maks_sisa ≤ best, pangkas
    maks_skor_sisa: Dict[str, int] = {}
    for pos in urutan_posisi:
        n   = kebutuhan[pos]
        top = kandidat_per_posisi[pos][:n]
        maks_skor_sisa[pos] = sum(p.skor for p in top)

    # Hitung terlebih dahulu prefix max scores dari posisi ke-i sampai akhir
    # upper_sisa[i] = maksimum skor yang bisa dikumpulkan dari posisi i ke akhir
    upper_sisa = [0] * (len(urutan_posisi) + 1)
    for i in range(len(urutan_posisi) - 1, -1, -1):
        upper_sisa[i] = upper_sisa[i + 1] + maks_skor_sisa[urutan_posisi[i]]

    best_score   = [0]
    best_players: List[List[Player]] = [[]]

    def rekursif(
        pos_idx:    int,          # indeks posisi yang sedang diisi
        terpilih:   List[Player], # pemain yang sudah dipilih
        biaya:      float,        # total biaya saat ini
        skor:       int,          # total skor saat ini
    ) -> None:
       
        if time.perf_counter() - start_time >= time_limit:
            timed_out[0] = True
            return
        if timed_out[0]:
            return

    
        if pos_idx == len(urutan_posisi):
            if skor > best_score[0]:
                best_score[0]   = skor
                best_players[0] = terpilih[:]
            return

        # ── Pruning: upper bound 
        # Bahkan jika semua posisi sisa diisi dengan pemain terbaik,
        # tidak bisa melampaui best_score → pangkas
        if skor + upper_sisa[pos_idx] <= best_score[0]:
            return

        pos       = urutan_posisi[pos_idx]
        jumlah    = kebutuhan[pos]
        kandidat  = kandidat_per_posisi[pos]
        n_kand    = len(kandidat)

        # ── Pilih kombinasi 'jumlah' pemain dari kandidat posisi ini ──
        # Rekursi kombinatorial: pilih pemain ke-k dari indeks start
        def pilih_posisi(k: int, start: int, dipilih_pos: List[Player], biaya_pos: float, skor_pos: int) -> None:
            if timed_out[0]:
                return
            if time.perf_counter() - start_time >= time_limit:
                timed_out[0] = True
                return

            if k == jumlah:
                # Semua slot posisi ini terisi, lanjut ke posisi berikutnya
                rekursif(pos_idx + 1, terpilih + dipilih_pos, biaya + biaya_pos, skor + skor_pos)
                return

            sisa_slot = jumlah - k
            # Tidak cukup kandidat tersisa
            if start + sisa_slot > n_kand:
                return

            # Pruning: bahkan ambil top sisa_slot dari start pun tidak cukup
            top_sisa = sum(p.skor for p in kandidat[start:start + sisa_slot])
            if skor + skor_pos + top_sisa + upper_sisa[pos_idx + 1] <= best_score[0]:
                return

            for i in range(start, n_kand - sisa_slot + 1):
                if timed_out[0]:
                    return
                p = kandidat[i]
                if biaya + biaya_pos + p.harga <= budget:
                    pilih_posisi(k + 1, i + 1, dipilih_pos + [p],
                                 biaya_pos + p.harga, skor_pos + p.skor)

        pilih_posisi(0, 0, [], 0.0, 0)

    rekursif(0, [], 0.0, 0)

    if timed_out[0]:
        print(
            f"        [Peringatan] BnB mencapai batas waktu {time_limit:.0f} detik. "
            f"Mengembalikan solusi terbaik yang ditemukan hingga saat ini."
        )

    return best_players[0], best_score[0]
