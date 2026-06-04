"""
algorithms/genetic_algorithm.py
---------------------------------
Implementasi Genetic Algorithm untuk optimasi pemilihan pemain.

Representasi kromosom:
    List biner panjang n (jumlah pemain).
    Gen ke-i = 1 → pemain ke-i dipilih; 0 → tidak dipilih.

Fungsi fitness:
    fitness = total_skor - penalti_budget - penalti_posisi - penalti_total
    Penalti besar memastikan solusi tidak layak mendapat skor sangat rendah.

Operator genetika:
    Seleksi  : Tournament selection (k=3)
    Crossover: Single-point crossover
    Mutasi   : Bit-flip per gen
    Elitisme : Kromosom terbaik dipertahankan ke generasi berikutnya
"""

import random
from typing import Dict, List, Tuple

from models import Player


# Konstanta besar untuk  solusi yang melanggar constraint
penalti_budget = 1_000   # per juta euro kelebihan budget
penalti_posisi =   500   # per pemain yang kelebihan/kekurangan per posisi
penalti_total  =   300   # per pemain kelebihan/kekurangan dari total kebutuhan


def genetic_algorithm(
    players:         List[Player],
    budget:          float,
    kebutuhan:       Dict[str, int],
    population_size: int   = 100,
    generations:     int   = 200,
    crossover_rate:  float = 0.8,
    mutation_rate:   float = 0.05,
    random_seed:     int   = 42,
) -> Tuple[List[Player], int]:
    """
    Genetic Algorithm untuk memilih kombinasi pemain dengan total skor tertinggi.

    Parameters
    ----------
    players         : daftar semua pemain yang tersedia
    budget          : anggaran maksimum dalam euro
    kebutuhan       : kebutuhan per posisi
    population_size : ukuran populasi per generasi
    generations     : jumlah iterasi generasi
    crossover_rate  : probabilitas crossover antar dua induk
    mutation_rate   : probabilitas mutasi per gen
    random_seed     : seed untuk reproducibility

    Returns
    -------
    (list pemain terpilih, total skor)
    """
    random.seed(random_seed)
    n               = len(players)
    total_kebutuhan = sum(kebutuhan.values())



    def hitung_fitness(kromosom: List[int]) -> float:
        """
        Menghitung nilai fitness satu kromosom.
        Solusi yang melanggar constraint mendapat penalti besar.
        """
        skor_total  = 0
        biaya_total = 0.0
        posisi_count: Dict[str, int] = {}

        for i, gen in enumerate(kromosom):
            if gen == 1:
                p = players[i]
                skor_total  += p.skor
                biaya_total += p.harga
                posisi_count[p.posisi] = posisi_count.get(p.posisi, 0) + 1

        # Penalti 1: kelebihan budget (per juta euro)
        kelebihan  = max(0.0, biaya_total - budget)
        pen_budget = (kelebihan / 1_000_000) * penalti_budget

        # Penalti 2: komposisi posisi tidak sesuai target
        pen_posisi = sum(
            abs(posisi_count.get(pos, 0) - target) * penalti_posisi
            for pos, target in kebutuhan.items()
        )

        # Penalti 3: total pemain tidak sesuai kebutuhan
        pen_total = abs(sum(kromosom) - total_kebutuhan) * penalti_total

        return float(skor_total - pen_budget - pen_posisi - pen_total)

    def inisialisasi_kromosom() -> List[int]:
        """
        Membuat satu kromosom awal yang dibangun sesuai kebutuhan posisi
        (lebih pintar dari inisialisasi acak murni).
        """
        kromosom = [0] * n

        # Kelompokkan indeks pemain berdasarkan posisi
        idx_per_posisi: Dict[str, List[int]] = {}
        for i, p in enumerate(players):
            idx_per_posisi.setdefault(p.posisi, []).append(i)

        # Pilih secara acak sejumlah kebutuhan per posisi
        for pos, jumlah in kebutuhan.items():
            tersedia = idx_per_posisi.get(pos, [])
            dipilih  = random.sample(tersedia, min(jumlah, len(tersedia)))
            for idx in dipilih:
                kromosom[idx] = 1

        return kromosom

    def seleksi_turnamen(
        populasi:     List[List[int]],
        fitness_vals: List[float],
        k:            int = 3,
    ) -> List[int]:
        """
        Tournament selection: pilih k kromosom acak,
        kembalikan yang fitness-nya paling tinggi.
        """
        peserta = random.sample(range(len(populasi)), k)
        terbaik = max(peserta, key=lambda i: fitness_vals[i])
        return populasi[terbaik][:]

    def crossover_satu_titik(
        induk1: List[int],
        induk2: List[int],
    ) -> Tuple[List[int], List[int]]:
        """
        Single-point crossover: tukar segmen setelah titik potong acak.
        """
        titik = random.randint(1, n - 1)
        return (
            induk1[:titik] + induk2[titik:],
            induk2[:titik] + induk1[titik:],
        )

    def mutasi(kromosom: List[int]) -> List[int]:
        """
        Bit-flip mutation: balik nilai gen dengan probabilitas mutation_rate.
        """
        return [
            (1 - gen) if random.random() < mutation_rate else gen
            for gen in kromosom
        ]


    populasi     = [inisialisasi_kromosom() for _ in range(population_size)]
    fitness_vals = [hitung_fitness(k) for k in populasi]

    best_idx  = max(range(population_size), key=lambda i: fitness_vals[i])
    best_krom = populasi[best_idx][:]
    best_fit  = fitness_vals[best_idx]


    for _ in range(generations):
        populasi_baru: List[List[int]] = [best_krom[:]]   # Elitisme

        while len(populasi_baru) < population_size:
            induk1 = seleksi_turnamen(populasi, fitness_vals)
            induk2 = seleksi_turnamen(populasi, fitness_vals)

            if random.random() < crossover_rate:
                anak1, anak2 = crossover_satu_titik(induk1, induk2)
            else:
                anak1, anak2 = induk1[:], induk2[:]

            populasi_baru.append(mutasi(anak1))
            if len(populasi_baru) < population_size:
                populasi_baru.append(mutasi(anak2))

        populasi     = populasi_baru
        fitness_vals = [hitung_fitness(k) for k in populasi]

        # Update solusi terbaik
        idx = max(range(len(populasi)), key=lambda i: fitness_vals[i])
        if fitness_vals[idx] > best_fit:
            best_fit  = fitness_vals[idx]
            best_krom = populasi[idx][:]

    terpilih   = [players[i] for i, gen in enumerate(best_krom) if gen == 1]
    skor_total = sum(p.skor for p in terpilih)
    return terpilih, skor_total
