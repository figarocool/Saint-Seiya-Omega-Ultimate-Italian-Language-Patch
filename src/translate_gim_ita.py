import struct
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ss_tools import gim_to_image, image_to_gim, parse_gim_info

FONT_SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_SANS_NARROW = "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"

def load_fitted_font(font_path: str, text: str, max_w: int, max_h: int, start_size: int = 28, min_size: int = 8):
    for sz in range(start_size, min_size - 1, -1):
        f = ImageFont.truetype(font_path, sz)
        bbox = f.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        if tw <= max_w and th <= max_h:
            return f, bbox
    f = ImageFont.truetype(font_path, min_size)
    return f, f.getbbox(text)

def render_styled_text(
    canvas: Image.Image,
    box: tuple,
    text: str,
    font_path: str,
    top_color: tuple,
    bot_color: tuple,
    outline_color: tuple,
    glow_color: tuple = None,
    align: str = "center",
):
    x0, y0, x1, y1 = box
    bw = max(4, x1 - x0)
    bh = max(4, y1 - y0)

    # Render at 2x supersampling for crisp edges
    ss = 2
    sw, sh = bw * ss, bh * ss
    f, bbox = load_fitted_font(font_path, text, sw - 8 * ss, sh - 4 * ss, start_size=int(sh * 0.88), min_size=12)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    if align == "left":
        tx = 4 * ss - bbox[0]
    elif align == "right":
        tx = sw - 4 * ss - tw - bbox[0]
    else:
        tx = (sw - tw) // 2 - bbox[0]
    ty = (sh - th) // 2 - bbox[1]

    layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Optional glow
    if glow_color:
        glow_mask = Image.new("L", (sw, sh), 0)
        gdraw = ImageDraw.Draw(glow_mask)
        for dx in (-3, -2, 0, 2, 3):
            for dy in (-3, -2, 0, 2, 3):
                gdraw.text((tx + dx, ty + dy), text, font=f, fill=200)
        glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(radius=2.0))
        glow_img = Image.new("RGBA", (sw, sh), glow_color)
        glow_img.putalpha(glow_mask)
        layer = Image.alpha_composite(layer, glow_img)
        draw = ImageDraw.Draw(layer)

    # Outline
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            if dx != 0 or dy != 0:
                draw.text((tx + dx, ty + dy), text, font=f, fill=outline_color)

    # Vertical gradient fill mask
    fill_mask = Image.new("L", (sw, sh), 0)
    fdraw = ImageDraw.Draw(fill_mask)
    fdraw.text((tx, ty), text, font=f, fill=255)

    grad = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    gpx = grad.load()
    y_start = max(0, ty + bbox[1])
    y_end = min(sh - 1, ty + bbox[3])
    span = max(1, y_end - y_start)
    for y in range(sh):
        t = max(0.0, min(1.0, (y - y_start) / span))
        r = int(top_color[0] * (1 - t) + bot_color[0] * t)
        g = int(top_color[1] * (1 - t) + bot_color[1] * t)
        b = int(top_color[2] * (1 - t) + bot_color[2] * t)
        for x in range(sw):
            gpx[x, y] = (r, g, b, 255)
    grad.putalpha(fill_mask)
    layer = Image.alpha_composite(layer, grad)

    small = layer.resize((bw, bh), Image.Resampling.LANCZOS)
    canvas.alpha_composite(small, (x0, y0))

# 2-state Menu List Buttons (128x32)
TWO_STATE_LIST = {
    "MAIN_LIST_00.GIM": "STORIA",
    "MAIN_LIST_01.GIM": "ARCADE",
    "MAIN_LIST_02.GIM": "VERSUS",
    "MAIN_LIST_03.GIM": "ALLENAMENTO",
    "MAIN_LIST_04.GIM": "GALLERIA",
    "MAIN_LIST_05.GIM": "OPZIONI",
    "MAIN_LIST_06.GIM": "INSTALLA DATI",
    "MAIN_LIST_07.GIM": "CONTRO CPU",
    "MAIN_LIST_08.GIM": "SFIDA AD HOC",
    "MAIN_LIST_09.GIM": "ALLENAMENTO",
    "MAIN_LIST_10.GIM": "TUTORIAL",
    "MAIN_LIST_11.GIM": "PERSONAGGI",
    "MAIN_LIST_12.GIM": "ILLUSTRAZIONI",
    "MAIN_LIST_13.GIM": "FILMATI",
    "MAIN_LIST_14.GIM": "REPLAY",
    "MAIN_LIST_15.GIM": "I MIEI DATI",
    "NW_LIST_00.GIM": "STANZA PEGASUS",
    "NW_LIST_01.GIM": "STANZA LIONET",
    "NW_LIST_02.GIM": "STANZA AQUILA",
    "NW_LIST_03.GIM": "STANZA DRAGONE",
    "NW_LIST_04.GIM": "STANZA LUPO",
    "NW_LIST_05.GIM": "STANZA ORIONE",
}

# Screen Titles (gold serif/bold)
GOLD_TITLES = {
    "MAIN_TITLE.GIM": "MENU PRINCIPALE",
    "DIC_TITLE.GIM": "GALLERIA",
    "TRAINING_TITLE.GIM": "ALLENAMENTO",
    "VS_TITLE.GIM": "VERSUS",
    "ARCADE_TITLE.GIM": "ARCADE",
    "CPU_TITLE.GIM": "CONTRO CPU",
    "NETWORK_TITLE.GIM": "AD HOC",
    "NW_TITLE.GIM": "LOBBY AD HOC",
    "CONF_TITLE.GIM": "OPZIONI",
    "INSTALL_TITLE.GIM": "INSTALLA DATI",
    "STORY_TITLE.GIM": "MODALITA' STORIA",
    "MOVIE_TITLE.GIM": "FILMATI",
    "MYDATA_TITLE.GIM": "I MIEI DATI",
    "DIC_CHARA_TITLE.GIM": "PERSONAGGI",
    "DIC_CG_TITLE.GIM": "ILLUSTRAZIONI",
    "RESULT_TITLE.GIM": "VITTORIA",
}

CHARA_NAMES = {
    "KOG": "Koga",
    "KOGV2": "Koga (Triton)",
    "YUN": "Yuna",
    "YUNV2": "Yuna (Triton)",
    "RYO": "Ryuho",
    "RYOV2": "Ryuho (Triton)",
    "SOM": "Soma",
    "SOMV2": "Soma (Triton)",
    "EDE": "Eden",
    "EDEV2": "Eden (Triton)",
    "HAT": "Haruto",
    "HATV2": "Haruto (Triton)",
    "SEY": "Seiya",
    "SHN": "Shaina",
    "ION": "Ionia",
    "SOI": "Sonia",
    "MIK": "Micene",
    "GEN": "Genbu",
    "KIK": "Kiki",
    "ITI": "Ichi",
    "JYU": "Poseidone",
    "SOT": "Sorrento",
    "SHU": "Shun",
    "PAB": "Pavlin",
    "ATE": "Atena",
    "SAO": "Saori",
    "MAN": "Marina",
    "QUESTION": "???",
    "RANDOM": "Casuale",
    "LOCK": "???",
    "STORY": "Storia",
}

SMALL_LABELS = {
    "SELECT_SET00.GIM": ("Forza CPU", (255, 225, 240), (225, 130, 180), (65, 10, 35, 255)),
    "SELECT_SET01.GIM": ("Tempo", (255, 225, 240), (225, 130, 180), (65, 10, 35, 255)),
    "SELECT_SET02.GIM": ("Round", (255, 225, 240), (225, 130, 180), (65, 10, 35, 255)),
    "DIC_SKILLLIST.GIM": ("LISTA COMBO", (235, 245, 255), (140, 180, 230), (15, 25, 50, 255)),
}

def translate_gim_subfile(s_name: str, s_data: bytes) -> bytes:
    uname = s_name.upper()
    info = parse_gim_info(s_data)
    if not info:
        return None
    w, h = info["width"], info["height"]

    # 0. Startup Warning Screens in scene/logo/data.pac (480x272)
    if uname in ("LOGO_AUTOSAVE.GIM", "LOGO_COPY.GIM"):
        orig = gim_to_image(s_data)
        canvas = orig.copy()
        draw = ImageDraw.Draw(canvas)
        bg = orig.getpixel((100, 30))
        draw.rectangle([62, 22, 418, 248], fill=bg)
        f_title = ImageFont.truetype(FONT_SANS_BOLD, 20)
        f_body = ImageFont.truetype(FONT_SANS_BOLD, 13)
        if uname == "LOGO_AUTOSAVE.GIM":
            title = "ATTENZIONE"
            lines = [
                "Questo gioco supporta il salvataggio automatico.",
                "Durante il salvataggio automatico l'indicatore",
                "della Memory Stick(TM) lampeggia.",
                "Non rimuovere la Memory Stick e non spegnere",
                "la console durante questa operazione.",
            ]
        else:
            title = "AVVISO"
            lines = [
                "La distribuzione o condivisione non autorizzata",
                "di questo software tramite Internet costituisce",
                "una violazione delle leggi sul copyright.",
                "Anche il download consapevole di copie illegali",
                "e' vietato dalla legge e non rientra",
                "nell'uso privato.",
                "Grazie per la comprensione e collaborazione.",
            ]
        tb = f_title.getbbox(title)
        draw.text(((w - (tb[2] - tb[0])) // 2 - tb[0], 34), title, font=f_title, fill=(205, 45, 15, 255))
        y_cur = 78
        for ln in lines:
            draw.text((74, y_cur), ln, font=f_body, fill=(45, 45, 45, 255))
            y_cur += 22
        return image_to_gim(s_data, canvas)

    # 1. Two-state Menu / Lobby List items (128x32)
    if uname in TWO_STATE_LIST:
        txt = TWO_STATE_LIST[uname]
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        font_use = FONT_SANS_NARROW if len(txt) >= 11 else FONT_SANS_BOLD
        # Top half: unselected (silver-gray with dark navy outline)
        render_styled_text(
            canvas,
            (4, 0, w - 2, h // 2),
            txt,
            font_use,
            top_color=(215, 220, 230),
            bot_color=(130, 140, 160),
            outline_color=(15, 20, 35, 255),
            glow_color=None,
            align="center",
        )
        # Bottom half: selected (bright cyan-white with blue outline)
        render_styled_text(
            canvas,
            (4, h // 2, w - 2, h),
            txt,
            font_use,
            top_color=(255, 255, 255),
            bot_color=(165, 225, 255),
            outline_color=(10, 55, 155, 255),
            glow_color=None,
            align="center",
        )
        return image_to_gim(s_data, canvas)

    # 2. Gold Screen Titles
    if uname in GOLD_TITLES:
        txt = GOLD_TITLES[uname]
        orig = gim_to_image(s_data)
        bbox = orig.getbbox() if orig else (20, 1, w - 4, 19)
        if not bbox:
            bbox = (20, 1, w - 4, 19)
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        x0 = min(bbox[0], 18) if w >= 128 else 2
        y0 = max(0, bbox[1] - 1)
        y1 = min(h, max(bbox[3] + 1, 20))
        align = "center" if uname in ("DIC_CG_TITLE.GIM", "RESULT_TITLE.GIM", "NETWORK_TITLE.GIM") else "left"
        render_styled_text(
            canvas,
            (x0, y0, w - 2, y1),
            txt,
            FONT_SERIF_BOLD,
            top_color=(255, 248, 195),
            bot_color=(215, 155, 45),
            outline_color=(55, 30, 5, 255),
            glow_color=None,
            align=align,
        )
        return image_to_gim(s_data, canvas)

    # 3. Small labels (SELECT_SET00..02, DIC_SKILLLIST)
    if uname in SMALL_LABELS:
        txt, tc, bc, oc = SMALL_LABELS[uname]
        orig = gim_to_image(s_data)
        bbox = orig.getbbox() if orig else (2, 1, w - 2, h - 1)
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        render_styled_text(
            canvas,
            (2, bbox[1], w - 2, bbox[3]),
            txt,
            FONT_SANS_NARROW,
            top_color=tc,
            bot_color=bc,
            outline_color=oc,
            align="center",
        )
        return image_to_gim(s_data, canvas)

    # 4. CONF_OPERATION.GIM (64x32, 2 rows on dark box)
    if uname == "CONF_OPERATION.GIM":
        canvas = Image.new("RGBA", (w, h), (15, 18, 25, 230))
        render_styled_text(
            canvas, (2, 0, w - 2, 16), "Frecce", FONT_SANS_NARROW,
            (240, 240, 245), (180, 185, 195), (10, 10, 15, 255), align="center"
        )
        render_styled_text(
            canvas, (2, 16, w - 2, 32), "Analogico", FONT_SANS_NARROW,
            (240, 240, 245), (180, 185, 195), (10, 10, 15, 255), align="center"
        )
        return image_to_gim(s_data, canvas)

    # 4b. Result Screen labels in battleui.pac
    if uname in ("RST_SCORE01.GIM", "RST_SCORE02.GIM", "RST_SCORE04.GIM"):
        txt_map = {
            "RST_SCORE01.GIM": "Bonus Combo",
            "RST_SCORE02.GIM": "Punti",
            "RST_SCORE04.GIM": "Bonus HP",
        }
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        render_styled_text(
            canvas, (2, 0, w - 2, h), txt_map[uname], FONT_SERIF_BOLD,
            (255, 255, 255), (195, 215, 245), (10, 20, 50, 255), align="left"
        )
        return image_to_gim(s_data, canvas)

    if uname == "RST_SCORE03.GIM":
        orig = gim_to_image(s_data)
        canvas = orig.copy()
        px = canvas.load()
        # Clear white text area around x=30..135, y=28..50 using nearby blue banner pixels
        for y in range(28, 50):
            bg_col = px[145, y]
            for x in range(28, 138):
                px[x, y] = bg_col
        render_styled_text(
            canvas, (28, 28, 138, 50), "Totale Punti", FONT_SERIF_BOLD,
            (255, 255, 255), (210, 225, 255), (10, 15, 55, 255), align="left"
        )
        return image_to_gim(s_data, canvas)

    if uname == "RST_TITLE.GIM":
        orig = gim_to_image(s_data)
        canvas = orig.copy()
        px = canvas.load()
        for y in range(14, 48):
            bg_col = px[150, y]
            for x in range(52, 148):
                px[x, y] = bg_col
        render_styled_text(
            canvas, (52, 12, 150, 48), "Risultati", FONT_SERIF_BOLD,
            (255, 248, 195), (225, 165, 45), (45, 25, 5, 255), align="left"
        )
        return image_to_gim(s_data, canvas)

    # 4c. Remaining English UI labels (PAUSE, SETUP, STORY_CLEAR, STORY_NEW)
    if uname in ("PAUSE.GIM", "SETUP.GIM"):
        orig = gim_to_image(s_data)
        canvas = orig.copy()
        px = canvas.load()
        for y in range(h):
            bg_col = px[96, y]
            for x in range(97, 159):
                px[x, y] = bg_col
        lbl = "PAUSA" if uname == "PAUSE.GIM" else "IMPOSTA"
        render_styled_text(
            canvas, (94, 0, 162, h), lbl, FONT_SERIF_BOLD,
            (240, 248, 255), (185, 205, 230), (15, 25, 45, 255), align="center"
        )
        return image_to_gim(s_data, canvas)

    if uname == "STORY_CLEAR.GIM":
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        render_styled_text(
            canvas, (2, 0, w - 2, h), "FINITO", FONT_SERIF_BOLD,
            (255, 240, 180), (220, 145, 45), (60, 25, 5, 255), align="center"
        )
        return image_to_gim(s_data, canvas)

    if uname == "STORY_NEW.GIM":
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        render_styled_text(
            canvas, (1, 0, w - 1, h), "Nuovo", FONT_SANS_NARROW,
            (255, 245, 245), (255, 195, 195), (140, 15, 25, 255), align="center"
        )
        return image_to_gim(s_data, canvas)

    # 4d. Result "Next" guide & Stage Preview banners & Footer Guide bars
    if uname == "RST_GUIDE.GIM":
        orig = gim_to_image(s_data)
        canvas = orig.copy()
        px = canvas.load()
        for y in range(2, h - 2):
            bg_col = px[61, y]
            for x in range(27, 61):
                px[x, y] = bg_col
        render_styled_text(
            canvas, (27, 2, 62, h - 2), "Avanti", FONT_SANS_NARROW,
            (245, 245, 250), (210, 215, 225), (15, 20, 30, 255), align="center"
        )
        return image_to_gim(s_data, canvas)

    if uname == "MAP_STAGE_02.GIM":
        map_stages = [
            "Piazza Porto",
            "Villa Julian",
            "Spiaggia",
            "Prateria Sud",
            "Prateria Nord",
            "Foresta",
            "Rovine Arena",
            "Grotta Antica",
            "Tempio Poseidone",
            "Tempio Sotterr.",
        ]
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for idx, label in enumerate(map_stages):
            y0 = idx * 24 + 2
            render_styled_text(
                canvas, (2, y0, w - 2, y0 + 20), label, FONT_SERIF_BOLD,
                (235, 248, 255), (150, 200, 240), (10, 25, 45, 255), align="center"
            )
        return image_to_gim(s_data, canvas)

    ADV_GUIDES = {
        "ADV_GUIDE_00.GIM": (15, "Prec."),
        "ADV_GUIDE_01.GIM": (14, "Salta"),
        "ADV_GUIDE_02.GIM": (14, "Esci"),
        "ADV_GUIDE_03.GIM": (15, "Seg."),
        "ADV_GUIDE_04.GIM": (14, "Play"),
    }
    if uname in ADV_GUIDES:
        x_keep, label = ADV_GUIDES[uname]
        orig = gim_to_image(s_data)
        canvas = orig.copy()
        px = canvas.load()
        for y in range(h):
            for x in range(x_keep, w):
                px[x, y] = (0, 0, 0, 0)
        render_styled_text(
            canvas, (x_keep, 1, w - 1, h - 1), label, FONT_SANS_NARROW,
            (245, 245, 250), (215, 220, 230), (10, 12, 18, 255), align="left"
        )
        return image_to_gim(s_data, canvas)

    STAGE_NAMES = {
        "SELECT_STAGE_ARENA.GIM": "Rovine Arena",
        "SELECT_STAGE_BEACH.GIM": "Spiaggia",
        "SELECT_STAGE_CAVE.GIM": "Grotta",
        "SELECT_STAGE_FOREST.GIM": "Foresta",
        "SELECT_STAGE_POSEIDON.GIM": "Tempio Poseidone",
        "SELECT_STAGE_PRAIRIE.GIM": "Prateria",
        "SELECT_STAGE_SHRINE.GIM": "Santuario",
        "SELECT_STAGE_SUNSET.GIM": "Tramonto",
        "SELECT_STAGE_TOWN.GIM": "Citta'",
        "SELECT_STAGE_VILLA.GIM": "Villa Juliano",
    }
    if uname in STAGE_NAMES:
        orig = gim_to_image(s_data)
        canvas = orig.copy()
        px = canvas.load()
        for y in range(4, 24):
            bg_col = px[180, y]
            for x in range(24, 178):
                px[x, y] = bg_col
        render_styled_text(
            canvas, (24, 3, 188, 23), STAGE_NAMES[uname], FONT_SERIF_BOLD,
            (255, 255, 255), (215, 225, 240), (15, 10, 25, 255), align="left"
        )
        return image_to_gim(s_data, canvas)

    GUIDE_BARS = {
        "MENU_GUIDE_00.GIM": (16, "Scegli  O:OK  X:Indietro"),
        "MENU_GUIDE_01.GIM": (16, "Scegli  O:OK  X:Indietro"),
        "SELECT_GUIDE_00.GIM": (16, "Scegli  O:OK  X:Indietro  L/R:Handicap"),
        "SELECT_GUIDE_01.GIM": (16, "Scegli  O:OK  X:Indietro"),
        "SELECT_GUIDE_02.GIM": (16, "Scegli  Modifica  O:OK  X:Indietro"),
        "SELECT_GUIDE_03.GIM": (16, "Scegli  O:OK  X:Indietro"),
        "CONFU_GUIDE_00.GIM": (16, "Voce  Regola  O:OK  X:Fine  SELECT:Default"),
        "CONFU_GUIDE_01.GIM": (16, "Voce  Regola  X:Fine  SELECT:Default"),
        "DIC_GUIDE_00.GIM": (16, "X:Indietro  O:3D  []:Lista  L/R:PG"),
        "DIC_GUIDE_01.GIM": (16, "Ruota  []+D-Pad:Zoom  X:Indietro  O:Armatura  /\\:Colore  L/R:PG"),
        "DIC_GUIDE_03.GIM": (16, "Scegli  X:Indietro  []:Lista  L/R:PG"),
        "DIC_GUIDE_04.GIM": (16, "Scegli  O:Zoom  X:Indietro  L/R:Pag."),
        "DIC_GUIDE_05.GIM": (16, "Scegli  O:Play  X:Indietro"),
        "DIC_GUIDE_06.GIM": (16, "X:Indietro"),
        "DIC_GUIDE_07.GIM": (16, "Scegli  O:OK  X:Indietro"),
    }
    if uname in GUIDE_BARS:
        x_start, txt = GUIDE_BARS[uname]
        orig = gim_to_image(s_data)
        canvas = orig.copy()
        px = canvas.load()
        # Find where the dark bar actually starts in the middle row (alpha > 80)
        bar_x = x_start
        for x in range(w - 1):
            if px[x, h // 2][3] > 80:
                bar_x = min(w - 20, x + 10)
                break
        for y in range(1, h - 1):
            bg_col = px[w - 2, y]
            for x in range(bar_x, w - 2):
                px[x, y] = bg_col
        render_styled_text(
            canvas, (bar_x + 2, 1, w - 4, h - 1), txt, FONT_SANS_NARROW,
            (245, 245, 250), (215, 220, 230), (10, 12, 18, 255), align="right"
        )
        return image_to_gim(s_data, canvas)

    # 5. INSTALL_MESSAGE00.GIM (512x64)
    if uname == "INSTALL_MESSAGE00.GIM":
        orig = gim_to_image(s_data)
        # Preserve background gradient bar by sampling column x=40 (outside text)
        canvas = orig.copy()
        px = canvas.load()
        for y in range(h):
            bg_col = px[40, y]
            for x in range(40, w - 40):
                px[x, y] = bg_col
        render_styled_text(
            canvas, (40, 6, w - 40, 31),
            "Installazione dati in corso...",
            FONT_SANS_BOLD, (245, 245, 250), (200, 205, 215), (20, 20, 30, 255), align="center"
        )
        render_styled_text(
            canvas, (20, 32, w - 20, 58),
            "Non spegnere la console e non rimuovere la Memory Stick.",
            FONT_SANS_BOLD, (245, 245, 250), (200, 205, 215), (20, 20, 30, 255), align="center"
        )
        return image_to_gim(s_data, canvas)

    # 6. Story Select Character Buttons: STORY_BTTN_<CHR>.GIM (256x32) (skip _R.GIM which is ???)
    if uname.startswith("STORY_BTTN_") and uname != "STORY_BTTN_SELCT.GIM" and not uname.endswith("_R.GIM"):
        parts = uname[:-4].split("_")
        c_code = parts[2]
        if c_code in CHARA_NAMES:
            cname = CHARA_NAMES[c_code]
            orig = gim_to_image(s_data)
            canvas = orig.copy()
            px = canvas.load()
            # Clear text region on left button (x=64..115, y=7..24) using row background at x=114
            for y in range(7, 25):
                bg_l = px[114, y]
                for x in range(64, 115):
                    px[x, y] = bg_l
                bg_r = px[242, y]
                for x in range(192, 243):
                    px[x, y] = bg_r
            render_styled_text(
                canvas, (62, 6, 117, 25), cname, FONT_SANS_BOLD,
                (190, 195, 205), (130, 135, 145), (25, 25, 35, 255), align="center"
            )
            render_styled_text(
                canvas, (190, 6, 245, 25), cname, FONT_SANS_BOLD,
                (255, 255, 255), (200, 235, 255), (10, 50, 140, 255), align="center"
            )
            return image_to_gim(s_data, canvas)

    # 7. Character Name Plates: MENU_NAME_*, BATTLE_NAME_*, ADV_NAME_*
    for prefix in ("MENU_NAME_", "BATTLE_NAME_", "ADV_NAME_"):
        if uname.startswith(prefix) and uname.endswith(".GIM"):
            rest = uname[len(prefix) : -4]
            if rest in ("00", "019_00", "R_00"):
                return None
            # Strip _00 or _01 suffix if present
            variant = None
            if rest.endswith("_00") or rest.endswith("_01"):
                variant = rest[-2:]
                c_code = rest[:-3]
            else:
                c_code = rest
            if c_code not in CHARA_NAMES:
                return None
            cname = CHARA_NAMES[c_code]
            orig = gim_to_image(s_data)
            bbox = orig.getbbox() if orig else (2, 2, w - 2, h - 2)
            if not bbox:
                bbox = (2, 2, w - 2, h - 2)
            canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            font_use = FONT_SANS_NARROW if (w <= 32 or "Triton" in cname) else FONT_SERIF_BOLD

            if prefix == "MENU_NAME_" and variant == "01":
                # Gold/white character select plate
                if "(Triton)" in cname and h >= 48:
                    base_name = cname.split(" ")[0]
                    render_styled_text(
                        canvas, (4, 6, w - 4, h // 2 + 2), base_name, FONT_SERIF_BOLD,
                        (255, 250, 205), (220, 165, 55), (55, 35, 5, 255), align="center"
                    )
                    render_styled_text(
                        canvas, (4, h // 2, w - 4, h - 6), "(Triton)", FONT_SANS_NARROW,
                        (235, 245, 255), (160, 210, 250), (20, 45, 90, 255), align="center"
                    )
                else:
                    render_styled_text(
                        canvas, (2, bbox[1], w - 2, bbox[3]), cname, font_use,
                        (255, 250, 205), (220, 165, 55), (55, 35, 5, 255), align="center"
                    )
            elif prefix == "MENU_NAME_" and variant == "00":
                # Large portrait overlay name in Story Select / Gallery Profile
                if "(Triton)" in cname:
                    base_name = cname.split(" ")[0]
                    render_styled_text(
                        canvas, (8, 4, w - 8, h // 2 + 4), base_name, FONT_SERIF_BOLD,
                        (255, 255, 255), (195, 215, 240), (15, 20, 35, 255),
                        glow_color=(60, 120, 220, 255), align="center"
                    )
                    render_styled_text(
                        canvas, (8, h // 2 + 2, w - 8, h - 4), "(Triton)", FONT_SANS_BOLD,
                        (235, 245, 255), (150, 205, 250), (15, 25, 55, 255), align="center"
                    )
                else:
                    render_styled_text(
                        canvas, (4, max(2, bbox[1]), w - 4, min(h - 2, bbox[3])), cname, FONT_SERIF_BOLD,
                        (255, 255, 255), (195, 215, 240), (15, 20, 35, 255),
                        glow_color=(60, 120, 220, 255), align="center"
                    )
            else:
                # BATTLE_NAME_* and ADV_NAME_* (32x16, 64x16, 128x16)
                render_styled_text(
                    canvas, (1, 0, w - 1, h), cname, FONT_SANS_NARROW,
                    (255, 255, 255), (205, 220, 240), (10, 15, 25, 255), align="center"
                )
            return image_to_gim(s_data, canvas)

    return None

def patch_titledata_pac(b: bytes) -> bytes:
    out = bytearray(b)

    # 1. Copyright / Patch notice GIM at 2350704..2356856
    off = 2350704
    end = 2356856
    if b[off : off + 11] == b"MIG.00.1PSP":
        gim = b[off:end]
        canvas = Image.new("RGBA", (256, 32), (0, 0, 0, 0))
        render_styled_text(
            canvas, (2, 1, 254, 16),
            "(C) Masami Kurumada / Toei Animation",
            FONT_SANS_NARROW, (240, 240, 245), (195, 200, 210), (10, 10, 15, 255), align="left"
        )
        render_styled_text(
            canvas, (2, 16, 254, 31),
            "(C) 2012 NBGI  -  PATCH ITALIANA v1.0",
            FONT_SANS_NARROW, (255, 240, 175), (225, 175, 55), (15, 10, 5, 255), align="left"
        )
        out[off:end] = image_to_gim(gim, canvas)

    # 2. "Push START Button" GIMs (normal and highlighted) -> "Premi il tasto START"
    for g_off, g_end, glow in (
        (2356856, 2365808, False),
        (2365808, 2374720, True),
    ):
        if b[g_off : g_off + 11] == b"MIG.00.1PSP":
            gim = b[g_off:g_end]
            orig = gim_to_image(gim)
            canvas = orig.copy()
            px = canvas.load()
            # Preserve vertical gradient bar by sampling x=32 (outside text)
            for y in range(orig.height):
                bg_col = px[32, y]
                for x in range(32, orig.width - 32):
                    px[x, y] = bg_col
            render_styled_text(
                canvas, (28, 3, 228, 29),
                "Premi il tasto START",
                FONT_SERIF_BOLD,
                top_color=(255, 255, 255),
                bot_color=(210, 235, 255) if glow else (195, 220, 245),
                outline_color=(25, 75, 155, 255) if glow else (15, 50, 115, 255),
                glow_color=(120, 200, 255, 200) if glow else None,
                align="center",
            )
            out[g_off:g_end] = image_to_gim(gim, canvas)

    return bytes(out)


def patch_prebattle_csb(s_name: str, s_data: bytes) -> bytes:
    """Patch embedded character name GIMs inside PREB_*.CSB (pre-battle VS screen)."""
    uname = s_name.upper()
    if not (uname.startswith("PREB_") and uname.endswith(".CSB")):
        return s_data
    code = uname[5:-4]
    if code not in CHARA_NAMES:
        return s_data

    cname = CHARA_NAMES[code]
    base_name = cname.split(" ")[0] if "(Triton)" in cname else cname

    # Find all embedded GIMs in the SCDH container
    gims = []
    pos = 0
    while True:
        pos = s_data.find(b"MIG.00.1PSP", pos)
        if pos < 0:
            break
        _, _, c_sz = struct.unpack("<HHI", s_data[pos + 16 : pos + 24])
        gims.append((pos, pos + 16 + c_sz))
        pos += 16

    out = bytearray(s_data)
    # GIM #1: Character name plate (64x64, 128x64, or 256x64)
    if len(gims) >= 2:
        g_off, g_end = gims[1]
        gim = s_data[g_off:g_end]
        info = parse_gim_info(gim)
        if info:
            w, h = info["width"], info["height"]
            canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            font_use = FONT_SERIF_BOLD if w >= 128 else FONT_SANS_NARROW
            render_styled_text(
                canvas,
                (2, 4, w - 2, h - 4),
                base_name,
                font_use,
                top_color=(255, 240, 175),
                bot_color=(225, 155, 45),
                outline_color=(35, 20, 5, 255),
                glow_color=(180, 110, 20, 160),
                align="center",
            )
            patched = image_to_gim(gim, canvas)
            if len(patched) == len(gim):
                out[g_off:g_end] = patched

    # GIM #3 (on *V2 variants): "(Triton)" subtitle plate (128x32)
    if len(gims) >= 4 and "(Triton)" in cname:
        g_off, g_end = gims[3]
        gim = s_data[g_off:g_end]
        info = parse_gim_info(gim)
        if info:
            w, h = info["width"], info["height"]
            canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            render_styled_text(
                canvas,
                (2, 2, w - 2, h - 2),
                "(Triton)",
                FONT_SANS_NARROW,
                top_color=(255, 240, 200),
                bot_color=(210, 175, 110),
                outline_color=(35, 25, 10, 255),
                align="center",
            )
            patched = image_to_gim(gim, canvas)
            if len(patched) == len(gim):
                out[g_off:g_end] = patched

    return bytes(out)
