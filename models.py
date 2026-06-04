"""
models.py
---------
Mendefinisikan struktur data Player yang digunakan di seluruh program.
"""

from dataclasses import dataclass


@dataclass
class Player:
    """Representasi satu pemain beserta atributnya."""
    id:     int
    nama:   str
    usia:   int
    posisi: str    # Kiper / Bek / Gelandang / Penyerang
    skor:   int    # Overall rating (skor kemampuan)
    harga:  float  # Harga pasar dalam euro (numerik)

    def harga_format(self) -> str:
        """Mengembalikan harga dalam format ringkas, misal €165M atau €50.5M."""
        if self.harga >= 1_000_000:
            v = self.harga / 1_000_000
            return f"€{v:.1f}M" if v != int(v) else f"€{int(v)}M"
        elif self.harga >= 1_000:
            v = self.harga / 1_000
            return f"€{v:.1f}K" if v != int(v) else f"€{int(v)}K"
        return f"€{int(self.harga)}"
