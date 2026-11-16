# Saint Seiya Omega: Ultimate Cosmo (PSP) — Patch Italiana v1.0

Traduzione completa in **italiano** per **Saint Seiya Omega: Ultimate Cosmo** (`NPJH-50699`, PlayStation Portable), compatibile con **PS Vita (Adrenaline)**, **PSP (CFW)** e **PPSSPP**.

---

## Cosa è stato tradotto

- **Menu e interfaccia (UI)**: tutti i menu principali, sottomenu, opzioni, galleria, profili dei personaggi, selezione personaggio, selezione storia, tutorial, lista mosse/combo, barre guida a piè di pagina e schermata titoli.
- **Modalità Storia (ADV)**: tutti i dialoghi e le scelte adattati con la terminologia italiana classica dei *Cavalieri dello Zodiaco* (*Armature*, *Cavalieri di Bronzo / d'Argento / d'Oro*, *Guerrieri degli Abissi*, *Squame*, *Gemme d'Acqua*, ecc.) e a-capo automatico per evitare testi tagliati.
- **Schermata pre-scontro (`A vs B`)**: tradotte tutte le grafiche dei nomi (e dei sottotitoli `(Triton)`) nei pacchetti `PREB_*.CSB`.
- **Messaggi di sistema e salvataggio**: avvisi di salvataggio, installazione dati e finestre di conferma.
- **Menu di uscita PSP/Adrenaline (`Sì / No`)**: patchato `EBOOT.BIN` (`sceImposeSetLanguageMode`) in modo che la finestra di uscita di sistema PSP/Adrenaline appaia in italiano anziché in giapponese.
- **Filmati `.PMF` sottotitolati in italiano**: sottotitoli impressi nei 4 video principali (`start.pmf`, `op.pmf`, `kog_vs_pos.pmf`, `sey_vs_pos.pmf`) con audio ATRAC3+ originale preservato.

---

## Come applicare la patch (Guida rapida)

> **Requisito:** Devi possedere una copia della ISO originale giapponese di *Saint Seiya Omega: Ultimate Cosmo* (`NPJH-50699`, dimensione esatta `941.096.960` byte) e **Python 3** installato sul PC.

1. **Scarica il pacchetto della patch** dalla sezione [**Releases**](https://github.com/figarocool/Saint-Seiya-Omega-Ultimate-Italian-Language-Patch/releases/latest):
   - Scarica `Patch_Italiano_Saint_Seiya_Omega_PSP.zip`.
2. **Estrai tutti i file** dell'archivio `.zip` in una cartella (troverai `patch_ita.bin`, `applica_patch_ita.py`, `applica_patch_ita.bat`, `applica_patch_ita.sh`, `LEGGIMI.txt`).
3. **Copia la tua ISO originale giapponese** nella stessa cartella e rinominala in:
   ```
   Saint Seiya Omega - Ultimate Cosmo (Japan).iso
   ```
4. **Avvia il patcher**:
   - **Windows**: fai doppio clic su `applica_patch_ita.bat` (oppure trascina il file `.iso` sopra `applica_patch_ita.bat`).
   - **Linux / macOS**: apri il terminale nella cartella ed esegui:
     ```bash
     chmod +x applica_patch_ita.sh
     ./applica_patch_ita.sh
     ```
     *(oppure `python3 applica_patch_ita.py "percorso/della/tua.iso"`)*
5. Al termine verrà generato il file:
   ```
   Saint Seiya Omega - Ultimate Cosmo (ITA).iso
   ```

---

## Come giocare

- **PS Vita (Adrenaline)**: copia `Saint Seiya Omega - Ultimate Cosmo (ITA).iso` in `ux0:/pspemu/ISO/` (via USB o FTP) e avvia il gioco da Adrenaline.
- **PSP (CFW)**: copia la ISO nella cartella `ms0:/ISO/` della Memory Stick.
- **PPSSPP (PC / Android / Steam Deck)**: apri direttamente `Saint Seiya Omega - Ultimate Cosmo (ITA).iso` dall'emulatore.

---

## Struttura del repository

- `applica_patch_ita.py` / `.bat` / `.sh` — Script per applicare la patch binaria (`patch_ita.bin`, disponibile nella Release) alla ISO giapponese originale con verifica di integrità.
- `LEGGIMI.txt` — Istruzioni rapide incluse nel pacchetto.
- `src/` — Tooling Python sviluppato per la localizzazione:
  - `ss_tools.py` — Parser/builder per archivi Criware `.cpk` (CRILAYLA), `.pac`, `.btx` e texture PSP `.gim`.
  - `translate_btx_ita.py` — Dizionario, traduzione e word-wrapping dei testi `.btx`.
  - `translate_gim_ita.py` — Rendering grafico delle texture `.gim` e patching dei container `PREB_*.CSB` e `titledata.pac`.
  - `build_ita_iso.py` — Ricostruzione completa della ISO italiana.
  - `make_patch_pkg.py` — Generazione del delta binario e del pacchetto distributivo `.zip`.

---

## Disclaimer

Questo progetto è una **traduzione amatoriale gratuita e senza scopo di lucro**.  
Non include né distribuisce alcuna ISO o copia completa del gioco originale: per applicare la patch è necessario possedere una propria copia di *Saint Seiya Omega: Ultimate Cosmo* (`NPJH-50699`). Tutti i diritti sul gioco, marchi, personaggi e musiche appartengono ai rispettivi proprietari (Masami Kurumada / Toei Animation / Bandai Namco).
