#!/usr/bin/env python3
import hashlib
import lzma
import os
import shutil
import struct
import sys

PATCH_MAGIC = b"SSOPATCH1"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            c = f.read(1024 * 1024)
            if not c:
                break
            h.update(c)
    return h.digest()

def main():
    print("============================================================")
    print("  Saint Seiya Omega: Ultimate Cosmo - Patch Italiana v1.0")
    print("============================================================")
    here = os.path.dirname(os.path.abspath(__file__))
    patch_file = os.path.join(here, "patch_ita.bin")
    if not os.path.exists(patch_file):
        print("ERRORE: File 'patch_ita.bin' non trovato nella cartella.")
        sys.exit(1)

    with open(patch_file, "rb") as pf:
        pdata = pf.read()

    if pdata[:9] != PATCH_MAGIC:
        print("ERRORE: File patch non valido.")
        sys.exit(1)

    expected_size = struct.unpack("<Q", pdata[9:17])[0]
    expected_orig_sha = pdata[17:49]
    expected_ita_sha = pdata[49:81]

    if len(sys.argv) >= 2:
        src_iso = sys.argv[1]
    else:
        # Cerca automaticamente la ISO giapponese nella cartella corrente
        candidates = [
            f for f in os.listdir(here)
            if f.lower().endswith(".iso") and "(ita)" not in f.lower()
        ]
        if len(candidates) == 1:
            src_iso = os.path.join(here, candidates[0])
        else:
            print("Trascina la ISO giapponese su questo script oppure passa il percorso da terminale:")
            print('  python3 applica_patch_ita.py "Saint Seiya Omega - Ultimate Cosmo (Japan).iso"')
            sys.exit(1)

    if not os.path.exists(src_iso):
        print(f"ERRORE: File non trovato: {src_iso}")
        sys.exit(1)

    if os.path.getsize(src_iso) != expected_size:
        print(f"ERRORE: Dimensione ISO non corrispondente ({os.path.getsize(src_iso)} != {expected_size}).")
        print("Assicurati di usare la ISO originale giapponese (NPJH-50699, Redump).")
        sys.exit(1)

    print("Verifica integrita' ISO originale in corso...")
    if sha256_file(src_iso) != expected_orig_sha:
        print("ERRORE: Checksum SHA-256 della ISO non valido. Usa la ISO giapponese originale non modificata.")
        sys.exit(1)

    out_dir = os.path.dirname(os.path.abspath(src_iso))
    out_iso = os.path.join(out_dir, "Saint Seiya Omega - Ultimate Cosmo (ITA).iso")

    print(f"Creazione di '{os.path.basename(out_iso)}'...")
    shutil.copyfile(src_iso, out_iso)

    print("Applicazione patch italiana...")
    payload = lzma.decompress(pdata[81:])
    num_chunks = struct.unpack("<I", payload[:4])[0]
    pos = 4
    with open(out_iso, "r+b") as out_f:
        for _ in range(num_chunks):
            off, length = struct.unpack("<QI", payload[pos : pos + 12])
            pos += 12
            out_f.seek(off)
            out_f.write(payload[pos : pos + length])
            pos += length

    print("Verifica integrita' ISO italiana generata...")
    if sha256_file(out_iso) != expected_ita_sha:
        print("ERRORE: Verifica finale fallita!")
        sys.exit(1)

    print("\nCOMPLETATO! ISO italiana creata con successo:")
    print(f"  {out_iso}")
    print("Puoi copiarla direttamente su PS Vita (ux0:pspemu/ISO/) o aprirla con PPSSPP.")

if __name__ == "__main__":
    main()
