"""
main.py
-------
Entry point program.

"""

import sys
import time
from typing import Dict, Tuple

from data_loader import baca_dataset
from utils       import (
    parse_budget, format_euro,
    tampilkan_hasil, tampilkan_ringkasan,
)
from algoritma  import branch_and_bound, dynamic_programming, genetic_algorithm




nama_file = 'dataset/dataset_player.csv'   # File CSV sudah tersedia

posisi_valid = {"Kiper", "Bek", "Gelandang", "Penyerang"}
default_budget    = '300M'
default_kebutuhan= {'Kiper': 1, 'Bek': 3, 'Gelandang': 3, 'Penyerang': 2}




def ambil_input() -> Tuple[float, Dict[str, int]]:
    """
    Mengambil input budget dan kebutuhan posisi dari pengguna.

    Returns
    -------
    (budget_euro, kebutuhan_posisi)
    """
    print("\n" + "=" * 62)
    print("  OPTIMASI PEMILIHAN PEMAIN MUDA – PERBANDINGAN ALGORITMA")
    print("=" * 62)
    print(f"\n  Dataset : dataset_player.csv")

    #  Budget 
    budget_str = input(
        f"\nBudget maksimum [default: {default_budget}]: "
    ).strip() or default_budget
    budget = parse_budget(budget_str)
    print(f"  → Budget: {format_euro(budget)}")

    #  Kebutuhan posisi 
    print(
        "\nKebutuhan posisi — format: Posisi Jumlah, pisahkan koma\n"
        "  Contoh : Kiper 1, Bek 3, Gelandang 3, Penyerang 2\n"
        "  Posisi valid: Kiper, Bek, Gelandang, Penyerang\n"
        "  (Tekan Enter untuk default: 1 Kiper, 3 Bek, 3 Gelandang, 2 Penyerang)"
    )
    baris = input("Kebutuhan: ").strip()

    kebutuhan: Dict[str, int] = {}
    if baris:
        for bagian in baris.split(','):
            parts = bagian.strip().split()
            if len(parts) >= 2:
                pos = parts[0].capitalize()
                if pos in posisi_valid:
                    try:
                        kebutuhan[pos] = int(parts[1])
                    except ValueError:
                        pass

    if not kebutuhan:
        kebutuhan = dict(default_kebutuhan)

    print(f"\n  Kebutuhan Posisi:")
    for pos, jml in kebutuhan.items():
        print(f"    {pos}: {jml} pemain")
    print(f"  Total: {sum(kebutuhan.values())} pemain")

    return budget, kebutuhan




def main() -> None:
    #  Input (budget & kebutuhan posisi saja) 
    budget, kebutuhan = ambil_input()

    #  Muat dataset 
    print(f"\nMemuat dataset dari '{nama_file}'...")
    try:
        players = baca_dataset(nama_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"[Error] {e}")
        sys.exit(1)

    print(f"  → {len(players)} pemain berhasil dimuat.")

    # Hanya ambil pemain dengan posisi yang dibutuhkan
    posisi_dibutuhkan = set(kebutuhan.keys())
    players = [p for p in players if p.posisi in posisi_dibutuhkan]
    print(f"  → {len(players)} pemain sesuai posisi yang dibutuhkan.")

    if len(players) < sum(kebutuhan.values()):
        print("[Error] Jumlah pemain tidak mencukupi untuk memenuhi kebutuhan posisi.")
        sys.exit(1)

    print("\nMenjalankan tiga algoritma secara independen...\n")

    #  Branch and Bound  
    print("  [1/3] Branch and Bound...")
    t0 = time.perf_counter()
    bnb_players, bnb_skor = branch_and_bound(players, budget, kebutuhan)
    bnb_waktu = time.perf_counter() - t0
    print(f"        Selesai dalam {bnb_waktu:.4f} s  |  Skor: {bnb_skor}")

    #  Dynamic Programming  
    print("  [2/3] Dynamic Programming...")
    t0 = time.perf_counter()
    dp_players, dp_skor = dynamic_programming(players, budget, kebutuhan)
    dp_waktu = time.perf_counter() - t0
    print(f"        Selesai dalam {dp_waktu:.4f} s  |  Skor: {dp_skor}")

    #  Genetic Algorithm  ─
    print("  [3/3] Genetic Algorithm...")
    t0 = time.perf_counter()
    ga_players, ga_skor = genetic_algorithm(players, budget, kebutuhan)
    ga_waktu = time.perf_counter() - t0
    print(f"        Selesai dalam {ga_waktu:.4f} s  |  Skor: {ga_skor}")

    #  Z* = nilai optimal terbaik dari algoritma eksak 
    z_star = float(max(bnb_skor, dp_skor))

    #  Tampilkan hasil masing-masing algoritma 
    tampilkan_hasil("Branch and Bound",    bnb_players, bnb_waktu, budget, kebutuhan)
    tampilkan_hasil("Dynamic Programming", dp_players,  dp_waktu,  budget, kebutuhan)
    tampilkan_hasil("Genetic Algorithm",   ga_players,  ga_waktu,  budget, kebutuhan,
                    z_star=z_star)

    #  Ringkasan perbandingan 
    tampilkan_ringkasan(
        hasil=[
            ("Branch and Bound",    bnb_skor, bnb_waktu),
            ("Dynamic Programming", dp_skor,  dp_waktu),
            ("Genetic Algorithm",   ga_skor,  ga_waktu),
        ],
        z_star=z_star,
    )


if __name__ == "__main__":
    main()
