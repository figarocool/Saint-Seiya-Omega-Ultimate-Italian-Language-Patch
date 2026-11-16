import os
import shutil
import struct
import time
from ss_tools import (
    parse_cpk,
    decompress_crilayla,
    compress_crilayla,
    parse_btx,
    build_btx,
    parse_pac,
    build_pac,
)
from translate_btx_ita import translate_btx_entries
from translate_gim_ita import translate_gim_subfile, patch_titledata_pac, patch_prebattle_csb

def pack_utf_int(buf: bytearray, offset: int, ntype: int, val: int):
    if ntype in (0, 1):
        buf[offset] = val & 0xFF
    elif ntype in (2, 3):
        struct.pack_into(">H", buf, offset, val)
    elif ntype in (4, 5):
        struct.pack_into(">I", buf, offset, val)
    elif ntype in (6, 7):
        struct.pack_into(">Q", buf, offset, val)
    else:
        raise ValueError(f"Unsupported UTF int type {ntype}")

def patch_cpk_file(src_path: str, dst_path: str) -> dict:
    t0 = time.time()
    with open(src_path, "rb") as f:
        cpk = bytearray(f.read())

    entries = parse_cpk(bytes(cpk))
    stats = {"btx_files": 0, "pac_files": 0, "sub_btx": 0, "sub_gim": 0}

    for e in entries:
        path = e["path"]
        foff = e["file_offset"]
        fsz = e["file_size"]
        slot_sz = e["slot_size"]
        raw_comp = bytes(cpk[foff : foff + fsz])
        was_crilayla = raw_comp[:8] == b"CRILAYLA"

        if path.endswith(".btx"):
            raw = decompress_crilayla(raw_comp)
            parsed = parse_btx(raw)
            if not parsed:
                continue
            btx_entries, hdr24 = parsed
            new_entries = translate_btx_entries(path, btx_entries)
            if new_entries != btx_entries:
                new_raw = build_btx(new_entries, hdr24)
                new_comp = compress_crilayla(new_raw) if was_crilayla else new_raw
                if len(new_comp) > slot_sz:
                    raise RuntimeError(f"Slot overflow on {path}: {len(new_comp)} > {slot_sz}")
                cpk[foff : foff + slot_sz] = new_comp.ljust(slot_sz, b"\x00")
                pack_utf_int(cpk, e["toc_filesize_offset"], e["toc_filesize_type"], len(new_comp))
                pack_utf_int(cpk, e["toc_extractsize_offset"], e["toc_extractsize_type"], len(new_raw))
                stats["btx_files"] += 1

        elif path.endswith(".pac"):
            # Only decompress PACs that can contain BTX or UI GIMs
            if not (
                path.startswith("common/menu/")
                or path in ("common/globalobject.pac", "common/systemwindow.pac")
                or path.startswith("scene/mainmenu/")
                or path.startswith("scene/title/")
                or path.startswith("scene/logo/")
                or path.startswith("scene/characterselect/")
                or path.startswith("scene/storyselect/")
                or path.startswith("scene/config/")
                or path.startswith("scene/key/")
                or path.startswith("scene/install/")
                or path.startswith("scene/lobby/")
                or path.startswith("scene/gallery/")
                or path.startswith("scene/battle/battleui/")
                or path == "scene/adv/adv.pac"
                or path.startswith("common/image/select_stage_")
                or path.startswith("common/prebattle/")
                or path.startswith("event/script/")
            ):
                continue

            raw = decompress_crilayla(raw_comp)
            modified = False

            if path == "scene/title/titledata.pac":
                patched_title = patch_titledata_pac(raw)
                if patched_title != raw:
                    raw = patched_title
                    modified = True
                    stats["sub_gim"] += 1

            flg, subs = parse_pac(raw)
            for idx, item in enumerate(subs):
                s_name, s_data, raw_name = item
                uname = s_name.upper()
                if uname.endswith(".BTX") and s_data[:4] == b"BTX ":
                    btx_entries, hdr24 = parse_btx(s_data)
                    new_entries = translate_btx_entries(f"{path}:{s_name}", btx_entries)
                    if new_entries != btx_entries:
                        subs[idx][1] = build_btx(new_entries, hdr24)
                        modified = True
                        stats["sub_btx"] += 1
                elif uname.endswith(".GIM") and s_data[:11] == b"MIG.00.1PSP":
                    new_gim = translate_gim_subfile(s_name, s_data)
                    if new_gim is not None and new_gim != s_data:
                        subs[idx][1] = new_gim
                        modified = True
                        stats["sub_gim"] += 1
                elif uname.startswith("PREB_") and uname.endswith(".CSB"):
                    new_csb = patch_prebattle_csb(s_name, s_data)
                    if new_csb != s_data:
                        subs[idx][1] = new_csb
                        modified = True
                        stats["sub_gim"] += 1

            if modified:
                new_raw = build_pac(flg, subs)
                new_comp = compress_crilayla(new_raw) if was_crilayla else new_raw
                if len(new_comp) > slot_sz:
                    raise RuntimeError(
                        f"Slot overflow on {path}: new_comp={len(new_comp)} > slot_sz={slot_sz} (orig_fsz={fsz})"
                    )
                cpk[foff : foff + slot_sz] = new_comp.ljust(slot_sz, b"\x00")
                pack_utf_int(cpk, e["toc_filesize_offset"], e["toc_filesize_type"], len(new_comp))
                pack_utf_int(cpk, e["toc_extractsize_offset"], e["toc_extractsize_type"], len(new_raw))
                stats["pac_files"] += 1

    with open(dst_path, "wb") as f:
        f.write(cpk)
    elapsed = time.time() - t0
    print(f"Patched {os.path.basename(dst_path)} in {elapsed:.1f}s -> {stats}")
    return stats

def main():
    os.makedirs("/tmp/ss_patched", exist_ok=True)
    patch_cpk_file("/tmp/ss_iso/PSP_GAME/USRDIR/archive.cpk", "/tmp/ss_patched/archive.cpk")
    patch_cpk_file("/tmp/ss_iso/PSP_GAME/USRDIR/install.cpk", "/tmp/ss_patched/install.cpk")

    orig_iso = "/home/stefano/Scaricati/Saint Seiya Omega - Ultimate Cosmo (Japan).iso"
    ita_iso = "/home/stefano/Scaricati/Saint Seiya Omega - Ultimate Cosmo (ITA).iso"
    print("Copying original ISO to ITA ISO...")
    shutil.copyfile(orig_iso, ita_iso)

    with open(ita_iso, "r+b") as iso_f:
        with open("/tmp/ss_patched/archive.cpk", "rb") as af:
            adata = af.read()
        assert len(adata) == 9297096
        iso_f.seek(191987712)
        iso_f.write(adata)

        with open("/tmp/ss_patched/install.cpk", "rb") as inf:
            idata = inf.read()
        assert len(idata) == 75174872
        iso_f.seek(201293824)
        iso_f.write(idata)

        # Patch subtitled PMF videos into /PSP_GAME/USRDIR/movie/ (directory LBA 31)
        pmf_entries = [
            ("kog_vs_pos.pmf", 63642, 412656 * 2048, 14716928),
            ("op.pmf",         63704, 419856 * 2048, 20604928),
            ("sey_vs_pos.pmf", 63758, 429920 * 2048, 11667456),
            ("start.pmf",      63820, 435632 * 2048, 43945984),
        ]
        for fname, rec_off, data_off, slot_sz in pmf_entries:
            sub_path = f"/tmp/pmf_work/sub_out/{fname}"
            if os.path.exists(sub_path):
                with open(sub_path, "rb") as pf:
                    pdata = pf.read()
                if len(pdata) > slot_sz:
                    raise RuntimeError(f"PMF slot overflow on {fname}: {len(pdata)} > {slot_sz}")
                iso_f.seek(data_off)
                iso_f.write(pdata + b"\x00" * (slot_sz - len(pdata)))
                iso_f.seek(rec_off + 10)
                iso_f.write(struct.pack("<I", len(pdata)) + struct.pack(">I", len(pdata)))
                print(f"Patched PMF {fname}: {len(pdata)} / {slot_sz} bytes")

        # Patch decrypted EBOOT.BIN (sets sceImposeSetLanguageMode to Italian = 5)
        eboot_path = os.path.join(os.path.dirname(__file__), "EBOOT_ITA.BIN")
        if os.path.exists(eboot_path):
            with open(eboot_path, "rb") as ef:
                edata = ef.read()
            assert len(edata) == 2757200
            iso_f.seek(640 * 2048)
            iso_f.write(edata)
            print("Patched EBOOT.BIN (sceImposeSetLanguageMode -> Italian)")

    print(f"Successfully created: {ita_iso} ({os.path.getsize(ita_iso)} bytes)")

if __name__ == "__main__":
    main()
