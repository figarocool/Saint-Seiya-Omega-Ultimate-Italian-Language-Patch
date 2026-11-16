import ctypes
import struct
from PIL import Image

lib = ctypes.CDLL("/tmp/libcrilayla.so")
libc = ctypes.CDLL("libc.so.6")
libc.free.argtypes = [ctypes.c_void_p]

lib.decompress_crilayla.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.POINTER(ctypes.c_size_t),
]
lib.decompress_crilayla.restype = ctypes.c_int

lib.compress_crilayla.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.POINTER(ctypes.c_size_t),
]
lib.compress_crilayla.restype = ctypes.c_int

def decompress_crilayla(data: bytes) -> bytes:
    if data[:8] != b"CRILAYLA":
        return data
    out_ptr = ctypes.c_void_p()
    out_sz = ctypes.c_size_t()
    rc = lib.decompress_crilayla(data, len(data), ctypes.byref(out_ptr), ctypes.byref(out_sz))
    if rc != 0:
        raise RuntimeError(f"decompress_crilayla failed: {rc}")
    res = ctypes.string_at(out_ptr.value, out_sz.value)
    libc.free(out_ptr)
    return res

def compress_crilayla(data: bytes) -> bytes:
    out_ptr = ctypes.c_void_p()
    out_sz = ctypes.c_size_t()
    rc = lib.compress_crilayla(data, len(data), ctypes.byref(out_ptr), ctypes.byref(out_sz))
    if rc != 0:
        raise RuntimeError(f"compress_crilayla failed: {rc}")
    res = ctypes.string_at(out_ptr.value, out_sz.value)
    libc.free(out_ptr)
    return res

def parse_utf_with_offsets(data: bytes):
    if data[:4] != b"@UTF":
        return None
    table_size, unk, rows_off, str_off, data_off, name_off, num_cols, row_len, num_rows = struct.unpack(
        ">IHHIIIHHI", data[4:32]
    )
    rows_off += 8
    str_off += 8
    data_off += 8
    pos = 32
    cols = []
    for _ in range(num_cols):
        flags = data[pos]
        ntype = flags & 0x0F
        sflag = flags >> 4
        cname_off = struct.unpack(">I", data[pos + 1 : pos + 5])[0]
        pos += 5
        cname_end = data.find(b"\x00", str_off + cname_off)
        cname = data[str_off + cname_off : cname_end].decode("utf-8", errors="replace")
        cval = None
        if sflag == 3:
            if ntype in (0, 1):
                cval = data[pos]
                pos += 1
            elif ntype in (2, 3):
                cval = struct.unpack(">H", data[pos : pos + 2])[0]
                pos += 2
            elif ntype in (4, 5, 8):
                cval = struct.unpack(">I", data[pos : pos + 4])[0]
                pos += 4
            elif ntype in (6, 7):
                cval = struct.unpack(">Q", data[pos : pos + 8])[0]
                pos += 8
            elif ntype == 10:
                so = struct.unpack(">I", data[pos : pos + 4])[0]
                pos += 4
                se = data.find(b"\x00", str_off + so)
                cval = data[str_off + so : se].decode("utf-8", errors="replace")
            elif ntype == 11:
                bo, bs = struct.unpack(">II", data[pos : pos + 8])
                pos += 8
                cval = data[data_off + bo : data_off + bo + bs]
        cols.append((cname, ntype, sflag, cval))
    rows = []
    for r in range(num_rows):
        rpos = rows_off + r * row_len
        row = {}
        row_offsets = {}
        for cname, ntype, sflag, cval in cols:
            if sflag == 5:
                row_offsets[cname] = (rpos, ntype)
                if ntype in (0, 1):
                    val = data[rpos]
                    rpos += 1
                elif ntype in (2, 3):
                    val = struct.unpack(">H", data[rpos : rpos + 2])[0]
                    rpos += 2
                elif ntype in (4, 5, 8):
                    val = struct.unpack(">I", data[rpos : rpos + 4])[0]
                    rpos += 4
                elif ntype in (6, 7):
                    val = struct.unpack(">Q", data[rpos : rpos + 8])[0]
                    rpos += 8
                elif ntype == 10:
                    so = struct.unpack(">I", data[rpos : rpos + 4])[0]
                    rpos += 4
                    se = data.find(b"\x00", str_off + so)
                    val = data[str_off + so : se].decode("utf-8", errors="replace")
                elif ntype == 11:
                    bo, bs = struct.unpack(">II", data[rpos : rpos + 8])
                    rpos += 8
                    val = data[data_off + bo : data_off + bo + bs]
            else:
                val = cval
            row[cname] = val
        row["_offsets"] = row_offsets
        rows.append(row)
    return rows

def parse_cpk(cpk: bytes):
    hdr = parse_utf_with_offsets(cpk[16:])[0]
    toc_off = hdr["TocOffset"]
    content_off = hdr["ContentOffset"]
    toc_rows = parse_utf_with_offsets(cpk[toc_off + 16 :])
    base = toc_off if toc_off < content_off else content_off
    entries = []
    for r in toc_rows:
        d = r.get("DirName", "")
        fn = r.get("FileName", "")
        full = f"{d}/{fn}" if d else fn
        foff = base + r["FileOffset"]
        fsz = r["FileSize"]
        usz = r["ExtractSize"]
        fsz_off, fsz_type = r["_offsets"]["FileSize"]
        usz_off, usz_type = r["_offsets"]["ExtractSize"]
        entries.append({
            "path": full,
            "dir": d,
            "name": fn,
            "file_offset": foff,
            "file_size": fsz,
            "extract_size": usz,
            "toc_filesize_offset": toc_off + 16 + fsz_off,
            "toc_filesize_type": fsz_type,
            "toc_extractsize_offset": toc_off + 16 + usz_off,
            "toc_extractsize_type": usz_type,
        })
    # Compute maximum available slot size for each entry
    sorted_by_off = sorted(entries, key=lambda e: e["file_offset"])
    for i, e in enumerate(sorted_by_off):
        if i + 1 < len(sorted_by_off):
            e["slot_size"] = sorted_by_off[i + 1]["file_offset"] - e["file_offset"]
        else:
            e["slot_size"] = len(cpk) - e["file_offset"]
    return entries

def parse_btx(b: bytes):
    if b[:4] != b"BTX ":
        return None
    u1, u2, u3, u4, count = struct.unpack("<5I", b[4:24])
    entries = []
    for i in range(count):
        pos = 24 + i * 8
        eid, rel_off = struct.unpack("<II", b[pos : pos + 8])
        abs_off = pos + rel_off
        end = abs_off
        while end + 1 < len(b):
            if b[end] == 0 and b[end + 1] == 0:
                break
            end += 2
        s = b[abs_off:end].decode("utf-16le", errors="replace")
        entries.append((eid, s))
    return entries, b[:24]

def build_btx(entries, header24=None):
    count = len(entries)
    if header24 is None:
        out = bytearray(b"BTX " + struct.pack("<5I", 1, 16, 0, 1, count))
    else:
        out = bytearray(header24[:20] + struct.pack("<I", count))
    table_pos = 24
    out.extend(b"\x00" * (count * 8))
    for i, (eid, s) in enumerate(entries):
        pos = table_pos + i * 8
        abs_str_off = len(out)
        rel_off = abs_str_off - pos
        struct.pack_into("<II", out, pos, eid, rel_off)
        encoded = s.encode("utf-16le") + b"\x00\x00\x00\x00"
        out.extend(encoded)
    return bytes(out)

def parse_pac(b: bytes):
    cnt, flg, tsz = struct.unpack("<HHI", b[:8])
    subfiles = []
    for i in range(cnt):
        eoff = 8 + i * 40
        raw_name = b[eoff : eoff + 32]
        s_name = raw_name.split(b"\x00")[0].decode("ascii", errors="replace")
        s_off, s_sz = struct.unpack("<II", b[eoff + 32 : eoff + 40])
        subfiles.append([s_name, b[s_off : s_off + s_sz], raw_name])
    return flg, subfiles

def build_pac(flg: int, subfiles) -> bytes:
    cnt = len(subfiles)
    header_size = 8 + cnt * 40
    entries_buf = bytearray(cnt * 40)
    data_buf = bytearray()
    for i, item in enumerate(subfiles):
        s_name = item[0]
        s_data = item[1]
        raw_name = item[2] if len(item) > 2 else s_name.encode("ascii")[:31].ljust(32, b"\x00")
        if len(s_data) % 16 != 0:
            s_data = s_data + b"\x00" * (16 - (len(s_data) % 16))
        s_off = header_size + len(data_buf)
        s_sz = len(s_data)
        entries_buf[i * 40 : i * 40 + 32] = raw_name
        struct.pack_into("<II", entries_buf, i * 40 + 32, s_off, s_sz)
        data_buf.extend(s_data)
    total_size = header_size + len(data_buf)
    hdr = struct.pack("<HHI", cnt, flg, total_size)
    return hdr + bytes(entries_buf) + bytes(data_buf)

def unswizzle_psp(data: bytes, row_bytes: int, height: int) -> bytes:
    if row_bytes < 16 or height < 8 or (row_bytes % 16 != 0) or (height % 8 != 0):
        return data
    out = bytearray(row_bytes * height)
    bx_count = row_bytes // 16
    by_count = height // 8
    src = 0
    for by in range(by_count):
        for bx in range(bx_count):
            for y in range(8):
                dst = (by * 8 + y) * row_bytes + bx * 16
                out[dst : dst + 16] = data[src : src + 16]
                src += 16
    return bytes(out)

def swizzle_psp(data: bytes, row_bytes: int, height: int) -> bytes:
    if row_bytes < 16 or height < 8 or (row_bytes % 16 != 0) or (height % 8 != 0):
        return data
    out = bytearray(row_bytes * height)
    bx_count = row_bytes // 16
    by_count = height // 8
    dst = 0
    for by in range(by_count):
        for bx in range(bx_count):
            for y in range(8):
                src = (by * 8 + y) * row_bytes + bx * 16
                out[dst : dst + 16] = data[src : src + 16]
                dst += 16
    return bytes(out)

def parse_gim_info(b: bytes):
    if b[:11] != b"MIG.00.1PSP":
        return None
    pos = 16
    img_hdr = None
    pal_hdr = None
    while pos < len(b):
        bid, unk, bsize, next_off, data_off = struct.unpack("<HHIII", b[pos : pos + 16])
        if bid == 4:
            img_hdr = pos + data_off
        elif bid == 5:
            pal_hdr = pos + data_off
        if bid == 2:
            pos += 16
        else:
            pos += next_off
    if img_hdr is None:
        return None
    fmt, order, width, height, bpp = struct.unpack("<5H", b[img_hdr + 4 : img_hdr + 14])
    pitch_align, height_align = struct.unpack("<2H", b[img_hdr + 14 : img_hdr + 18])
    level_off, pixel_off, pixel_end = struct.unpack("<3I", b[img_hdr + 24 : img_hdr + 36])
    pix_start = img_hdr + pixel_off
    pix_stop = img_hdr + pixel_end
    pal_start = pal_stop = None
    if pal_hdr is not None:
        p_fmt, p_order, p_w, p_h, p_bpp = struct.unpack("<5H", b[pal_hdr + 4 : pal_hdr + 14])
        _, p_off, p_end = struct.unpack("<3I", b[pal_hdr + 24 : pal_hdr + 36])
        pal_start = pal_hdr + p_off
        pal_stop = pal_hdr + p_end
    return {
        "fmt": fmt,
        "order": order,
        "width": width,
        "height": height,
        "bpp": bpp,
        "pitch_align": pitch_align,
        "height_align": height_align,
        "pix_start": pix_start,
        "pix_stop": pix_stop,
        "pal_start": pal_start,
        "pal_stop": pal_stop,
    }

def gim_to_image(b: bytes):
    info = parse_gim_info(b)
    if not info:
        return None
    fmt = info["fmt"]
    order = info["order"]
    width = info["width"]
    height = info["height"]
    pix_raw = b[info["pix_start"] : info["pix_stop"]]
    pal_raw = b[info["pal_start"] : info["pal_stop"]] if info["pal_start"] else None

    if fmt == 4:
        row_bytes = ((width // 2) + 15) & ~15
        stride_w = row_bytes * 2
    elif fmt == 5:
        row_bytes = (width + 15) & ~15
        stride_w = row_bytes
    elif fmt == 3:
        row_bytes = (width * 4 + 15) & ~15
        stride_w = row_bytes // 4
    else:
        return None

    alloc_h = (height + 7) & ~7 if order == 1 else height
    expected = row_bytes * alloc_h
    if len(pix_raw) < expected:
        alloc_h = height
        if fmt == 4:
            row_bytes = width // 2
            stride_w = width
        elif fmt == 5:
            row_bytes = width
            stride_w = width
        elif fmt == 3:
            row_bytes = width * 4
            stride_w = width
        expected = row_bytes * alloc_h

    if order == 1:
        pix_raw = unswizzle_psp(pix_raw[:expected], row_bytes, alloc_h)

    img = Image.new("RGBA", (width, height))
    px = img.load()

    if fmt == 4 and pal_raw:
        n_col = len(pal_raw) // 4
        pal = [struct.unpack("<4B", pal_raw[i * 4 : i * 4 + 4]) for i in range(n_col)]
        while len(pal) < 16:
            pal.append((0, 0, 0, 0))
        for y in range(height):
            for x in range(0, width, 2):
                idx = y * row_bytes + (x // 2)
                if idx < len(pix_raw):
                    bval = pix_raw[idx]
                    px[x, y] = pal[bval & 0x0F]
                    if x + 1 < width:
                        px[x + 1, y] = pal[(bval >> 4) & 0x0F]
    elif fmt == 5 and pal_raw:
        n_col = len(pal_raw) // 4
        pal = [struct.unpack("<4B", pal_raw[i * 4 : i * 4 + 4]) for i in range(n_col)]
        while len(pal) < 256:
            pal.append((0, 0, 0, 0))
        for y in range(height):
            for x in range(width):
                idx = y * row_bytes + x
                if idx < len(pix_raw):
                    px[x, y] = pal[pix_raw[idx]]
    elif fmt == 3:
        for y in range(height):
            for x in range(width):
                idx = (y * stride_w + x) * 4
                if idx + 4 <= len(pix_raw):
                    px[x, y] = struct.unpack("<4B", pix_raw[idx : idx + 4])
    return img

def image_to_gim(orig_gim: bytes, img: Image.Image) -> bytes:
    info = parse_gim_info(orig_gim)
    if not info:
        raise ValueError("Invalid GIM")
    fmt = info["fmt"]
    order = info["order"]
    width = info["width"]
    height = info["height"]
    img = img.convert("RGBA")
    if img.size != (width, height):
        img = img.resize((width, height), Image.Resampling.LANCZOS)

    out = bytearray(orig_gim)
    pix_len = info["pix_stop"] - info["pix_start"]

    if fmt == 4:
        row_bytes = ((width // 2) + 15) & ~15
    elif fmt == 5:
        row_bytes = (width + 15) & ~15
    elif fmt == 3:
        row_bytes = (width * 4 + 15) & ~15
    else:
        raise ValueError(f"Unsupported GIM fmt {fmt}")

    alloc_h = (height + 7) & ~7 if order == 1 else height
    expected = row_bytes * alloc_h
    if pix_len < expected:
        alloc_h = height
        if fmt == 4:
            row_bytes = width // 2
        elif fmt == 5:
            row_bytes = width
        elif fmt == 3:
            row_bytes = width * 4
        expected = row_bytes * alloc_h

    px = img.load()
    raw_buf = bytearray(pix_len)

    if fmt in (4, 5):
        pal_len = info["pal_stop"] - info["pal_start"]
        max_colors = pal_len // 4
        use_colors = min(max_colors, 16)
        # Quantize RGBA image to at most use_colors (rest of palette stays 0,0,0,0 for high LZSS compression!)
        unique_colors = {}
        for y in range(height):
            for x in range(width):
                c = px[x, y]
                if c[3] < 16:
                    c = (0, 0, 0, 0)
                else:
                    # Quantize channels slightly to reduce noise
                    c = ((c[0] >> 2) << 2, (c[1] >> 2) << 2, (c[2] >> 2) << 2, (c[3] >> 3) << 3)
                px[x, y] = c
                unique_colors[c] = unique_colors.get(c, 0) + 1

        if len(unique_colors) <= use_colors:
            pal = [(0, 0, 0, 0)]
            for c in sorted(unique_colors.keys(), key=lambda k: -unique_colors[k]):
                if c != (0, 0, 0, 0):
                    pal.append(c)
            while len(pal) < max_colors:
                pal.append((0, 0, 0, 0))
        else:
            sorted_cols = [c for c, _ in sorted(unique_colors.items(), key=lambda kv: -kv[1]) if c != (0, 0, 0, 0)]
            pal = [(0, 0, 0, 0)]
            step = max(1, len(sorted_cols) // (use_colors - 1))
            for i in range(0, len(sorted_cols), step):
                if len(pal) < use_colors:
                    pal.append(sorted_cols[i])
            while len(pal) < use_colors:
                pal.append((0, 0, 0, 0))
            for _ in range(4):
                clusters = [[] for _ in range(use_colors)]
                for c, count in unique_colors.items():
                    if c[3] == 0:
                        clusters[0].append((c, count))
                        continue
                    best_i = 1
                    best_d = 1e18
                    for i in range(1, use_colors):
                        pc = pal[i]
                        d = (c[0]-pc[0])**2 + (c[1]-pc[1])**2 + (c[2]-pc[2])**2 + (c[3]-pc[3])**2 * 2
                        if d < best_d:
                            best_d = d
                            best_i = i
                    clusters[best_i].append((c, count))
                for i in range(1, use_colors):
                    if clusters[i]:
                        tw = sum(cnt for _, cnt in clusters[i])
                        r = sum(c[0]*cnt for c, cnt in clusters[i]) // tw
                        g = sum(c[1]*cnt for c, cnt in clusters[i]) // tw
                        b_ = sum(c[2]*cnt for c, cnt in clusters[i]) // tw
                        a = sum(c[3]*cnt for c, cnt in clusters[i]) // tw
                        pal[i] = (r, g, b_, a)
            while len(pal) < max_colors:
                pal.append((0, 0, 0, 0))

        # Map each pixel to nearest palette index
        color_to_idx = {(0, 0, 0, 0): 0}
        def get_idx(c):
            if c[3] == 0:
                return 0
            if c in color_to_idx:
                return color_to_idx[c]
            best_i = 0
            best_d = 1e18
            for i, pc in enumerate(pal):
                d = (c[0]-pc[0])**2 + (c[1]-pc[1])**2 + (c[2]-pc[2])**2 + (c[3]-pc[3])**2 * 2
                if d < best_d:
                    best_d = d
                    best_i = i
            color_to_idx[c] = best_i
            return best_i

        # Write palette
        pal_bytes = bytearray(pal_len)
        for i in range(max_colors):
            struct.pack_into("<4B", pal_bytes, i * 4, *pal[i])
        out[info["pal_start"] : info["pal_stop"]] = pal_bytes

        if fmt == 4:
            for y in range(height):
                for x in range(0, width, 2):
                    i0 = get_idx(px[x, y]) & 0x0F
                    i1 = (get_idx(px[x + 1, y]) & 0x0F) if (x + 1 < width) else 0
                    raw_buf[y * row_bytes + (x // 2)] = i0 | (i1 << 4)
        else:
            for y in range(height):
                for x in range(width):
                    raw_buf[y * row_bytes + x] = get_idx(px[x, y]) & 0xFF
    elif fmt == 3:
        stride_w = row_bytes // 4
        for y in range(height):
            for x in range(width):
                idx = (y * stride_w + x) * 4
                struct.pack_into("<4B", raw_buf, idx, *px[x, y])

    if order == 1:
        swizzled = swizzle_psp(bytes(raw_buf[:expected]), row_bytes, alloc_h)
        raw_buf[:expected] = swizzled

    out[info["pix_start"] : info["pix_stop"]] = raw_buf
    return bytes(out)
