import hashlib
import lzma
import os
import struct
import zipfile

ORIG_ISO = "/home/stefano/Scaricati/Saint Seiya Omega - Ultimate Cosmo (Japan).iso"
ITA_ISO = "/home/stefano/Scaricati/Saint Seiya Omega - Ultimate Cosmo (ITA).iso"
OUT_ZIP = "/home/stefano/Scaricati/Patch_Italiano_Saint_Seiya_Omega_PSP.zip"
WORK_DIR = "/tmp/patch_pkg"

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def create_delta(orig_path: str, mod_path: str) -> bytes:
    # Compare 2048-byte sectors and pack changed contiguous runs with lzma
    buf = bytearray(b"SSOPATCH1")
    orig_size = os.path.getsize(orig_path)
    mod_size = os.path.getsize(mod_path)
    assert orig_size == mod_size
    buf.extend(struct.pack("<Q", orig_size))

    orig_sha = bytes.fromhex(sha256_file(orig_path))
    mod_sha = bytes.fromhex(sha256_file(mod_path))
    buf.extend(orig_sha)
    buf.extend(mod_sha)

    chunks = []
    with open(orig_path, "rb") as f1, open(mod_path, "rb") as f2:
        offset = 0
        cur_start = None
        cur_data = bytearray()
        while True:
            b1 = f1.read(2048)
            b2 = f2.read(2048)
            if not b1:
                break
            if b1 != b2:
                if cur_start is None:
                    cur_start = offset
                cur_data.extend(b2)
            else:
                if cur_start is not None:
                    chunks.append((cur_start, bytes(cur_data)))
                    cur_start = None
                    cur_data.clear()
            offset += len(b1)
        if cur_start is not None:
            chunks.append((cur_start, bytes(cur_data)))

    payload = bytearray()
    payload.extend(struct.pack("<I", len(chunks)))
    for off, data in chunks:
        payload.extend(struct.pack("<QI", off, len(data)))
        payload.extend(data)

    compressed = lzma.compress(bytes(payload), preset=6)
    buf.extend(compressed)
    return bytes(buf)

APPLIER_PY = '''#!/usr/bin/env python3
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

    print("\\nCOMPLETATO! ISO italiana creata con successo:")
    print(f"  {out_iso}")
    print("Puoi copiarla direttamente su PS Vita (ux0:pspemu/ISO/) o aprirla con PPSSPP.")

if __name__ == "__main__":
    main()
'''

BAT_SCRIPT = '''@echo off
python "%~dp0applica_patch_ita.py" %*
pause
'''

SH_SCRIPT = '''#!/usr/bin/env bash
python3 "$(dirname "$0")/applica_patch_ita.py" "$@"
'''

README_TXT = '''====================================================================
  SAINT SEIYA OMEGA: ULTIMATE COSMO (PSP) - PATCH ITALIANA v1.0
====================================================================

Questa patch converte la ISO originale giapponese di Saint Seiya Omega:
Ultimate Cosmo (NPJH-50699) in una ISO completamente giocabile in italiano,
compatibile con PS Vita (Adrenaline), PSP e PPSSPP.

CONTENUTO TRADOTTO:
- Tutti i menu principali, sottomenu, opzioni, galleria, profilo giocatori
- Schermata di selezione personaggio, selezione storia, tutorial e combo list
- Messaggi di sistema, salvataggio, installazione dati e avvisi
- Dialoghi della Modalita' Storia e nomi dei personaggi in battaglia
- Grafiche e pulsanti UI dei menu principali e dei titoli schermata

COME APPLICARE LA PATCH:
1. Estrai tutti i file di questo archivio in una cartella.
2. Copia nella stessa cartella la tua ISO originale giapponese:
   "Saint Seiya Omega - Ultimate Cosmo (Japan).iso" (941.096.960 byte)
3. Avvia la patch:
   - Su Windows: doppio click su "applica_patch_ita.bat"
     (oppure trascina la ISO su applica_patch_ita.bat; richiede Python 3)
   - Su Linux / macOS: esegui "./applica_patch_ita.sh"
     (oppure "python3 applica_patch_ita.py percorso/della/iso.iso")
4. Verra' creata la ISO:
   "Saint Seiya Omega - Ultimate Cosmo (ITA).iso"
5. Copia la ISO su PS Vita in "ux0:pspemu/ISO/" e gioca con Adrenaline!
'''

def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    print("Generating binary delta...")
    delta = create_delta(ORIG_ISO, ITA_ISO)
    patch_path = os.path.join(WORK_DIR, "patch_ita.bin")
    with open(patch_path, "wb") as f:
        f.write(delta)
    print(f"patch_ita.bin size: {len(delta) / (1024*1024):.2f} MB")

    py_path = os.path.join(WORK_DIR, "applica_patch_ita.py")
    bat_path = os.path.join(WORK_DIR, "applica_patch_ita.bat")
    sh_path = os.path.join(WORK_DIR, "applica_patch_ita.sh")
    readme_path = os.path.join(WORK_DIR, "LEGGIMI.txt")

    with open(py_path, "w", encoding="utf-8") as f:
        f.write(APPLIER_PY)
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(BAT_SCRIPT)
    with open(sh_path, "w", encoding="utf-8") as f:
        f.write(SH_SCRIPT)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(README_TXT)
    os.chmod(py_path, 0o755)
    os.chmod(sh_path, 0o755)

    # Test round-trip patching into /tmp/patch_pkg/test_out.iso
    test_src = os.path.join(WORK_DIR, "orig.iso")
    if os.path.exists(test_src):
        os.remove(test_src)
    os.symlink(ORIG_ISO, test_src)
    import subprocess
    subprocess.run(["python3", py_path, test_src], check=True)
    test_out = os.path.join(WORK_DIR, "Saint Seiya Omega - Ultimate Cosmo (ITA).iso")
    assert sha256_file(test_out) == sha256_file(ITA_ISO), "Test patched ISO does not match ITA_ISO!"
    os.remove(test_out)
    os.remove(test_src)

    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fn in ("patch_ita.bin", "applica_patch_ita.py", "applica_patch_ita.bat", "applica_patch_ita.sh", "LEGGIMI.txt"):
            zf.write(os.path.join(WORK_DIR, fn), arcname=fn)

    print(f"Created distributable patch package: {OUT_ZIP} ({os.path.getsize(OUT_ZIP) / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    main()
