"""
utils.py
--------
Fungsi-fungsi utilitas:
  - Parsing harga dan budget
  - Konversi kode posisi FIFA
  - Deteksi nama kolom CSV secara fleksibel
  - Pemeriksaan kelayakan solusi
  - Formatting output
"""

import math
from typing import Dict, List, Tuple

from models import Player



def parse_harga(nilai_str: str) -> float:
    """
    Mengkonversi string harga ke angka euro.

    Contoh:
        '€165M'  -> 165_000_000
        '€50.5M' ->  50_500_000
        '€900K'  ->     900_000
        '1500000'->   1_500_000
    """
    s = nilai_str.strip().replace('€', '').replace(',', '').strip()
    if not s:
        return 0.0
    multiplier = 1.0
    if s.upper().endswith('M'):
        multiplier = 1_000_000
        s = s[:-1]
    elif s.upper().endswith('K'):
        multiplier = 1_000
        s = s[:-1]
    try:
        return float(s) * multiplier
    except ValueError:
        return 0.0


def parse_budget(budget_str: str) -> float:
    """
    Mengkonversi input budget dari user ke angka euro.

    Contoh:
        '300M'   -> 300_000_000
        '€300M'  -> 300_000_000
        '300000000' -> 300_000_000
    """
    return parse_harga(budget_str)



daftar_posisi: Dict[str, str] = {
    "GK":  "Kiper",
    "CB":  "Bek",  "LB":  "Bek",  "RB":  "Bek",
    "LWB": "Bek",  "RWB": "Bek",
    "CM":  "Gelandang", "CDM": "Gelandang", "CAM": "Gelandang",
    "LW":  "Penyerang", "RW":  "Penyerang",
    "LM":  "Penyerang", "RM":  "Penyerang",
    "ST":  "Penyerang", "CF":  "Penyerang",
}

posisi_valid = {"Kiper", "Bek", "Gelandang", "Penyerang"}


def konversi_posisi(posisi_raw: str) -> str:
    """
    Mengkonversi kode posisi FIFA ke salah satu dari empat kategori utama.
    Jika sudah dalam bahasa Indonesia (Kiper/Bek/Gelandang/Penyerang),
    langsung dikembalikan apa adanya.
    """
    posisi_raw = posisi_raw.strip()
    if posisi_raw in posisi_valid:
        return posisi_raw
    return daftar_posisi.get(posisi_raw.upper(), posisi_raw)


kandidat_kolom: Dict[str, List[str]] = {
    'nama':   ['Nama', 'name', 'Name', 'short_name', 'nama_pemain'],
    'usia':   ['Usia', 'Age', 'age', 'umur'],
    'posisi': ['Posisi', 'Position', 'position', 'pos'],
    'skor':   ['Skor kemampuan', 'Skor', 'Score', 'score',
               'Overall', 'overall', 'OVR'],
    'harga':  ['Harga Pasar', 'Value', 'value', 'value_eur', 'market_value'],
}


def deteksi_kolom(header: List[str]) -> Dict[str, str]:
    """
    Mendeteksi nama kolom aktual dari header CSV secara fleksibel.

    Returns
    -------
    dict  {field_name: nama_kolom_di_csv}
    Contoh: {'nama': 'Nama', 'usia': 'Usia', 'posisi': 'Posisi', ...}
    """
    hasil: Dict[str, str] = {}
    for field_name, kemungkinan in kandidat_kolom.items():
        for k in kemungkinan:
            if k in header:
                hasil[field_name] = k
                break
    return hasil




def cek_kelayakan(
    players: List[Player],
    budget: float,
    kebutuhan: Dict[str, int],
) -> Tuple[bool, str]:
    """
    Memeriksa apakah solusi memenuhi semua constraint.

    Returns
    -------
    (layak: bool, keterangan: str)
    """
    biaya = sum(p.harga for p in players)
    posisi_count: Dict[str, int] = {}
    for p in players:
        posisi_count[p.posisi] = posisi_count.get(p.posisi, 0) + 1

    masalah: List[str] = []

    if biaya > budget:
        masalah.append(
            f"Budget melebihi ({format_euro(biaya)} > {format_euro(budget)})"
        )
    for pos, target in kebutuhan.items():
        aktual = posisi_count.get(pos, 0)
        if aktual != target:
            masalah.append(
                f"Posisi {pos}: butuh {target}, terpilih {aktual}"
            )

    if masalah:
        return False, "TIDAK LAYAK – " + "; ".join(masalah)
    return True, "LAYAK ✓"



def format_euro(nilai: float) -> str:
    """Format nilai euro ke string ringkas (€165M, €50.5M, €900K, dst.)."""
    if nilai >= 1_000_000:
        v = nilai / 1_000_000
        return f"€{v:.1f}M" if v != int(v) else f"€{int(v)}M"
    elif nilai >= 1_000:
        v = nilai / 1_000
        return f"€{v:.1f}K" if v != int(v) else f"€{int(v)}K"
    return f"€{int(nilai)}"


def tampilkan_hasil(
    nama_algo:        str,
    players_terpilih: List[Player],
    waktu:            float,
    budget:           float,
    kebutuhan:        Dict[str, int],
    z_star:           float = None,
) -> None:
    """
    Mencetak hasil satu algoritma secara terformat ke stdout.

    Parameters
    ----------
    z_star  : Nilai solusi optimal referensi (Z*). Jika None, algoritma ini
              dianggap sebagai solusi referensi (gap = 0%).
    """
    lebar = 67
    print("\n" + "=" * lebar)
    print(f"  ALGORITMA : {nama_algo}")
    print("=" * lebar)

    if not players_terpilih:
        print("  [Tidak ditemukan solusi yang memenuhi constraint]")
        return

    print(f"\n  {'No':<4} {'Nama':<22} {'Usia':>4} {'Posisi':<12} {'Skor':>5} {'Harga':>10}")
    print("  " + "-" * 61)

    total_skor  = 0
    total_harga = 0.0
    posisi_count: Dict[str, int] = {}

    for i, p in enumerate(players_terpilih, 1):
        print(
            f"  {i:<4} {p.nama:<22} {p.usia:>4} {p.posisi:<12}"
            f" {p.skor:>5} {p.harga_format():>10}"
        )
        total_skor  += p.skor
        total_harga += p.harga
        posisi_count[p.posisi] = posisi_count.get(p.posisi, 0) + 1

    print("  " + "-" * 61)
    print(
        f"  {'TOTAL':>44} {total_skor:>5}"
        f" {format_euro(total_harga):>10}"
    )

    print(f"\n  Komposisi Posisi:")
    for pos in ['Kiper', 'Bek', 'Gelandang', 'Penyerang']:
        aktual = posisi_count.get(pos, 0)
        target = kebutuhan.get(pos, 0)
        if target > 0 or aktual > 0:
            print(f"    {pos:<12}: {aktual} pemain  (target: {target})")


    layak, status = cek_kelayakan(players_terpilih, budget, kebutuhan)
    print(f"\n  Total Skor      : {total_skor}")
    print(f"  Total Harga     : {format_euro(total_harga)}")
    print(f"  Budget          : {format_euro(budget)}")
    print(f"  Status          : {status}")
    print(f"  Waktu Komputasi : {waktu:.4f} detik")

    if z_star is not None and z_star > 0:
        gap = ((z_star - total_skor) / z_star) * 100
        print(
            f"  Optimality Gap  : {gap:.2f}%"
            f"  (Z* = {int(z_star)}, Z_alg = {int(total_skor)})"
        )
    else:
        print(f"  Optimality Gap  : 0.00%  (solusi referensi / algoritma eksak)")

    print("=" * lebar)


def tampilkan_ringkasan(
    hasil:  List[Tuple[str, int, float]],   
    z_star: float,
) -> None:
    """Mencetak tabel ringkasan perbandingan ketiga algoritma."""
    print("\n" + "=" * 62)
    print("  RINGKASAN PERBANDINGAN ALGORITMA")
    print("=" * 62)
    print(
        f"  {'Algoritma':<25} {'Skor':>6}"
        f" {'Waktu (s)':>12} {'Gap (%)':>10}"
    )
    print("  " + "-" * 57)
    for nama, skor, waktu in hasil:
        gap = ((z_star - skor) / z_star * 100) if z_star > 0 else 0.0
        print(
            f"  {nama:<25} {skor:>6}"
            f" {waktu:>12.4f} {gap:>9.2f}%"
        )
    print("  " + "-" * 57)
    print(f"\n  Z* (Solusi Optimal) = {int(z_star)}")
    print("=" * 62)
