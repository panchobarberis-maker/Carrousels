// The Lange Firm — Carousel Generator
// Crea 6 slides para el carrusel de Age Discrimination

async function run() {
  const page = figma.currentPage;

  // ─── Paleta de colores (valores 0–1) ───────────────────────
  const NAVY = { r: 0.106, g: 0.137, b: 0.251 }; // #1B2340
  const GOLD = { r: 0.784, g: 0.659, b: 0.431 }; // #C8A86E
  const WHITE = { r: 1.0, g: 1.0, b: 1.0 };
  const DARK = { r: 0.04, g: 0.06, b: 0.12 };    // overlay oscuro
  const CARD = { r: 0.13, g: 0.165, b: 0.27 };   // fondo cards

  const W = 1080, H = 1350, PAD = 70;

  // ─── Cargar fuentes ────────────────────────────────────────
  const FONTS = [
    { family: "Playfair Display", style: "Bold" },
    { family: "Playfair Display", style: "Bold Italic" },
    { family: "Playfair Display", style: "Italic" },
    { family: "Inter", style: "Regular" },
    { family: "Inter", style: "Medium" },
    { family: "Inter", style: "SemiBold" },
    { family: "Inter", style: "Bold" },
  ];
  for (const f of FONTS) {
    try { await figma.loadFontAsync(f); } catch (_) { console.warn("Font not found:", f.family, f.style); }
  }

  // ─── Helpers ───────────────────────────────────────────────
  const solid = (c, a = 1) => [{ type: "SOLID", color: c, opacity: a }];

  function mkFrame(name, w, h) {
    const f = figma.createFrame();
    f.name = name;
    f.resize(w, h);
    f.clipsContent = true;
    return f;
  }

  function mkRect(name, x, y, w, h, fills, radius = 0) {
    const r = figma.createRectangle();
    r.name = name;
    r.resize(w, h);
    r.x = x; r.y = y;
    r.fills = fills;
    if (radius) r.cornerRadius = radius;
    return r;
  }

  function mkText(content, x, y, opts = {}) {
    const t = figma.createText();
    t.fontName = opts.font || { family: "Inter", style: "Regular" };
    t.fontSize = opts.size || 32;
    t.fills = solid(opts.color || WHITE);
    t.letterSpacing = opts.ls || { value: 0, unit: "PERCENT" };
    t.lineHeight = opts.lh || { unit: "AUTO" };
    t.textAlignHorizontal = opts.align || "LEFT";
    if (opts.width) {
      t.textAutoResize = "HEIGHT";
      t.resize(opts.width, 50);
    } else {
      t.textAutoResize = "WIDTH_AND_HEIGHT";
    }
    t.characters = content;
    t.x = x; t.y = y;
    if (opts.opacity !== undefined) t.opacity = opts.opacity;
    return t;
  }

  function add(parent, ...children) {
    for (const c of children) parent.appendChild(c);
  }

  // ─── SLIDE 1: Cover ─────────────────────────────────────────
  function makeSlide1() {
    const s = mkFrame("1 — Cover", W, H);
    s.fills = solid(NAVY);

    // Placeholder de foto (reemplazar con la foto real)
    const photoBg = mkRect("⬜ FOTO — reemplazar con foto real", 0, 0, W, H, solid(DARK, 0.55));
    add(s, photoBg);

    // Número decorativo grande "58" arriba derecha, dorado muy tenue
    const bigNum = mkText("58", 580, -80, {
      font: { family: "Playfair Display", style: "Bold" },
      size: 420, color: GOLD, opacity: 0.13,
    });
    add(s, bigNum);

    // Tag pill superior
    const pill = mkFrame("Tag Pill", 665, 52);
    pill.x = PAD; pill.y = 215;
    pill.cornerRadius = 26;
    pill.fills = [];
    pill.strokes = [{ type: "SOLID", color: GOLD, opacity: 0.5 }];
    pill.strokeWeight = 1.5;
    pill.appendChild(mkText("AGE DISCRIMINATION  ·  EMPLOYMENT LAW  ·  TEXAS", 18, 14, {
      font: { family: "Inter", style: "SemiBold" },
      size: 17, color: GOLD,
      ls: { value: 7, unit: "PERCENT" }, width: 628,
    }));
    add(s, pill);

    // Headline línea 1 — blanco bold
    add(s, mkText("FIRED FOR\nBEING TOO", PAD, 298, {
      font: { family: "Playfair Display", style: "Bold" },
      size: 110, color: WHITE,
      lh: { value: 100, unit: "PERCENT" }, width: W - PAD * 2,
    }));

    // Headline línea 2 — dorado itálica
    add(s, mkText("EXPERIENCED.", PAD, 538, {
      font: { family: "Playfair Display", style: "Bold Italic" },
      size: 110, color: GOLD, width: W - PAD * 2,
    }));

    // Subtítulo
    add(s, mkText("15 years at the company. Then a layoff that only hit people over 50.", PAD, 698, {
      font: { family: "Inter", style: "Regular" },
      size: 33, color: WHITE, opacity: 0.85,
      lh: { value: 150, unit: "PERCENT" }, width: W - PAD * 2,
    }));

    // Stat cards × 3
    const statsData = [
      { n: "58", l: "YEARS OLD" },
      { n: "15", l: "YEARS THERE" },
      { n: "40+", l: "PROTECTED" },
    ];
    const cW = 290, cH = 115, cY = 878, gap = 20;
    statsData.forEach((st, i) => {
      const card = mkFrame(`Stat ${i + 1}`, cW, cH);
      card.x = PAD + i * (cW + gap);
      card.y = cY;
      card.cornerRadius = 10;
      card.fills = solid(CARD, 0.82);
      card.appendChild(mkText(st.n, 0, 9, {
        font: { family: "Playfair Display", style: "Bold" },
        size: 54, color: GOLD, align: "CENTER", width: cW,
      }));
      card.appendChild(mkText(st.l, 0, 74, {
        font: { family: "Inter", style: "SemiBold" },
        size: 15, color: WHITE, opacity: 0.65,
        ls: { value: 12, unit: "PERCENT" }, align: "CENTER", width: cW,
      }));
      add(s, card);
    });

    // Branding footer
    add(s, mkText("THE LANGE\nFIRM", 0, 1058, {
      font: { family: "Inter", style: "SemiBold" },
      size: 28, color: GOLD,
      ls: { value: 18, unit: "PERCENT" },
      lh: { value: 135, unit: "PERCENT" },
      align: "CENTER", width: W,
    }));

    return s;
  }

  // ─── Helper: slide tipo lista (slides 2 y 5) ────────────────
  function makeListSlide(name, num, total, sectionLabel, headline, items) {
    const s = mkFrame(name, W, H);
    s.fills = solid(NAVY);
    add(s, mkRect("⬜ FOTO — reemplazar", 0, 0, W, H, solid(DARK, 0.55)));

    // Logo top-left
    add(s, mkText("THE LANGE\nFIRM", PAD, 55, {
      font: { family: "Inter", style: "SemiBold" },
      size: 22, color: GOLD,
      ls: { value: 16, unit: "PERCENT" },
      lh: { value: 130, unit: "PERCENT" }, width: 220,
    }));

    // Contador de slide top-right
    add(s, mkText(`${num} / ${total}`, W - PAD - 65, 65, {
      font: { family: "Inter", style: "Regular" },
      size: 22, color: WHITE, opacity: 0.4,
    }));

    // Label de sección
    add(s, mkText(sectionLabel, PAD, 360, {
      font: { family: "Inter", style: "SemiBold" },
      size: 19, color: GOLD,
      ls: { value: 10, unit: "PERCENT" },
    }));
    // Línea bajo label
    add(s, mkRect("Label underline", PAD, 393, 65, 2.5, solid(GOLD, 0.6)));

    // Headline
    add(s, mkText(headline, PAD, 420, {
      font: { family: "Playfair Display", style: "Bold" },
      size: 100, color: WHITE,
      lh: { value: 98, unit: "PERCENT" }, width: W - PAD * 2,
    }));

    // List items
    items.forEach((item, i) => {
      const iCard = mkFrame(`Item ${i + 1}`, W - PAD * 2, 76);
      iCard.x = PAD;
      iCard.y = 760 + i * 96;
      iCard.cornerRadius = 8;
      iCard.fills = solid(CARD, 0.78);
      iCard.appendChild(mkText("→", 20, 20, {
        font: { family: "Inter", style: "Regular" },
        size: 26, color: GOLD,
      }));
      iCard.appendChild(mkText(item, 65, 18, {
        font: { family: "Inter", style: "Regular" },
        size: 27, color: WHITE, width: W - PAD * 2 - 88,
      }));
      add(s, iCard);
    });

    return s;
  }

  // ─── SLIDE 3: Big Stat ──────────────────────────────────────
  function makeSlide3() {
    const s = mkFrame("3 — You Are Protected", W, H);
    s.fills = solid(NAVY);
    add(s, mkRect("⬜ FOTO — reemplazar", 0, 0, W, H, solid(DARK, 0.55)));

    // Logo centrado
    add(s, mkText("THE LANGE\nFIRM", 0, 55, {
      font: { family: "Inter", style: "SemiBold" },
      size: 22, color: GOLD,
      ls: { value: 16, unit: "PERCENT" },
      lh: { value: 130, unit: "PERCENT" },
      align: "CENTER", width: W,
    }));
    add(s, mkText("3 / 6", W - PAD - 60, 65, {
      font: { family: "Inter", style: "Regular" },
      size: 22, color: WHITE, opacity: 0.4,
    }));

    // "40+" grande centrado
    add(s, mkText("40+", 0, 310, {
      font: { family: "Playfair Display", style: "Bold" },
      size: 215, color: GOLD, align: "CENTER", width: W,
    }));

    // "YOU ARE PROTECTED"
    add(s, mkText("YOU ARE PROTECTED", 0, 555, {
      font: { family: "Inter", style: "SemiBold" },
      size: 19, color: GOLD,
      ls: { value: 14, unit: "PERCENT" },
      align: "CENTER", width: W,
    }));

    // Body — blanco bold
    add(s, mkText("Workers 40 and older are\nprotected by law. Layoffs that", 0, 625, {
      font: { family: "Playfair Display", style: "Bold" },
      size: 46, color: WHITE,
      lh: { value: 125, unit: "PERCENT" },
      align: "CENTER", width: W,
    }));

    // Body — itálica dorada
    add(s, mkText("disproportionately target older\nemployees", 0, 800, {
      font: { family: "Playfair Display", style: "Bold Italic" },
      size: 46, color: GOLD,
      lh: { value: 125, unit: "PERCENT" },
      align: "CENTER", width: W,
    }));

    // Body — blanco bold cierre
    add(s, mkText("can be illegal.", 0, 915, {
      font: { family: "Playfair Display", style: "Bold" },
      size: 46, color: WHITE, align: "CENTER", width: W,
    }));

    // Subtítulo pequeño
    add(s, mkText("Age is not a performance issue. And it is not a\nlegal reason to let you go.", 0, 1012, {
      font: { family: "Inter", style: "Regular" },
      size: 29, color: WHITE, opacity: 0.7,
      lh: { value: 148, unit: "PERCENT" },
      align: "CENTER", width: W,
    }));

    return s;
  }

  // ─── SLIDE 4: Quote ─────────────────────────────────────────
  function makeSlide4() {
    const s = mkFrame('4 — "Fresh energy"', W, H);
    s.fills = solid(NAVY);
    add(s, mkRect("⬜ FOTO — reemplazar", 0, 0, W, H, solid(DARK, 0.55)));

    // Logo centrado
    add(s, mkText("THE LANGE\nFIRM", 0, 55, {
      font: { family: "Inter", style: "SemiBold" },
      size: 22, color: GOLD,
      ls: { value: 16, unit: "PERCENT" },
      lh: { value: 130, unit: "PERCENT" },
      align: "CENTER", width: W,
    }));
    add(s, mkText("4 / 6", W - PAD - 60, 65, {
      font: { family: "Inter", style: "Regular" },
      size: 22, color: WHITE, opacity: 0.4,
    }));

    // Quote grande en itálica dorada
    add(s, mkText('"Fresh energy"', 0, 395, {
      font: { family: "Playfair Display", style: "Bold Italic" },
      size: 96, color: GOLD, align: "CENTER", width: W,
    }));

    // Strikethrough text
    add(s, mkText("NOT A LEGAL JUSTIFICATION", 0, 545, {
      font: { family: "Inter", style: "SemiBold" },
      size: 19, color: GOLD,
      ls: { value: 8, unit: "PERCENT" },
      align: "CENTER", width: W, opacity: 0.45,
    }));
    // Línea de tachado
    add(s, mkRect("Strikethrough line", 212, 558, 656, 1.5, solid(GOLD, 0.4)));

    // Headline
    add(s, mkText("Your experience has value.\nSo does your case.", 0, 625, {
      font: { family: "Playfair Display", style: "Bold" },
      size: 60, color: WHITE,
      lh: { value: 120, unit: "PERCENT" },
      align: "CENTER", width: W,
    }));

    // Subtítulo
    add(s, mkText("If the pattern is clear, the law may be on your side.", 0, 830, {
      font: { family: "Inter", style: "Regular" },
      size: 30, color: WHITE, opacity: 0.7,
      align: "CENTER", width: W,
    }));

    return s;
  }

  // ─── SLIDE 6: CTA ───────────────────────────────────────────
  function makeSlide6() {
    const s = mkFrame("6 — CTA", W, H);
    s.fills = solid(NAVY);

    // Zona superior — placeholder de foto
    const photoH = 575;
    add(s, mkRect("⬜ FOTO de Evan — reemplazar con headshot real", 0, 0, W, photoH, [
      { type: "SOLID", color: { r: 0.72, g: 0.73, b: 0.75 } },
    ]));

    // Label de placeholder
    add(s, mkText("[ Foto de Evan Lange — reemplazar ]", 0, photoH / 2 - 20, {
      font: { family: "Inter", style: "Regular" },
      size: 26, color: { r: 0.3, g: 0.3, b: 0.35 },
      align: "CENTER", width: W,
    }));

    // Rectángulo oscuro que cubre el fondo en la parte baja (para que sea navy puro debajo)
    add(s, mkRect("Bottom navy bg", 0, photoH - 20, W, H - photoH + 20, solid(NAVY)));

    const bY = photoH + 30;

    // Nombre del abogado
    add(s, mkText("Evan Lange", 0, bY, {
      font: { family: "Playfair Display", style: "Bold" },
      size: 46, color: WHITE, align: "CENTER", width: W,
    }));

    // Título
    add(s, mkText("EMPLOYMENT ATTORNEY  ·  HOUSTON, TX", 0, bY + 60, {
      font: { family: "Inter", style: "Regular" },
      size: 19, color: WHITE, opacity: 0.55,
      ls: { value: 6, unit: "PERCENT" },
      align: "CENTER", width: W,
    }));

    // Headline
    add(s, mkText("YOUR STORY", 0, bY + 132, {
      font: { family: "Playfair Display", style: "Bold" },
      size: 82, color: WHITE, align: "CENTER", width: W,
    }));
    add(s, mkText("MATTERS.", 0, bY + 220, {
      font: { family: "Playfair Display", style: "Bold Italic" },
      size: 82, color: GOLD, align: "CENTER", width: W,
    }));

    // Botón 1 — Relleno dorado
    const btn1 = mkFrame("CTA — Primary", 620, 72);
    btn1.x = (W - 620) / 2;
    btn1.y = bY + 338;
    btn1.cornerRadius = 8;
    btn1.fills = solid(GOLD);
    btn1.appendChild(mkText("TALK TO EVAN NOW", 0, 20, {
      font: { family: "Inter", style: "Bold" },
      size: 22, color: NAVY,
      ls: { value: 8, unit: "PERCENT" },
      align: "CENTER", width: 620,
    }));
    add(s, btn1);

    // Botón 2 — Outline
    const btn2 = mkFrame("CTA — Secondary", 620, 60);
    btn2.x = (W - 620) / 2;
    btn2.y = bY + 426;
    btn2.cornerRadius = 30;
    btn2.fills = [];
    btn2.strokes = [{ type: "SOLID", color: WHITE, opacity: 0.35 }];
    btn2.strokeWeight = 1;
    btn2.appendChild(mkText("CONTACT US FOR A CONSULTATION", 0, 17, {
      font: { family: "Inter", style: "Regular" },
      size: 17, color: WHITE,
      ls: { value: 5, unit: "PERCENT" },
      align: "CENTER", width: 620,
    }));
    add(s, btn2);

    // Branding footer
    add(s, mkText("THE LANGE\nFIRM", 0, bY + 522, {
      font: { family: "Inter", style: "SemiBold" },
      size: 26, color: GOLD,
      ls: { value: 18, unit: "PERCENT" },
      lh: { value: 135, unit: "PERCENT" },
      align: "CENTER", width: W,
    }));

    return s;
  }

  // ─── Crear los 6 slides ─────────────────────────────────────
  const slides = [
    makeSlide1(),
    makeListSlide(
      "2 — Sound Familiar", 2, 6,
      "SOUND FAMILIAR?",
      "THIS IS\nWHAT IT\nLOOKS LIKE.",
      [
        "Everyone let go was over 50.",
        "Everyone they kept was under 35.",
        "They called it fresh energy.",
      ]
    ),
    makeSlide3(),
    makeSlide4(),
    makeListSlide(
      "5 — Red Flags", 5, 6,
      "RED FLAGS",
      "SIGNS YOU\nMAY HAVE\nA CLAIM.",
      [
        "Only older employees were laid off.",
        "Replaced by significantly younger hires.",
        "Comments about age or retirement made before.",
      ]
    ),
    makeSlide6(),
  ];

  // Posicionar slides horizontalmente con gap de 60px
  slides.forEach((s, i) => {
    s.x = i * (W + 60);
    s.y = 0;
    page.appendChild(s);
  });

  // Hacer zoom para ver todos los slides
  figma.viewport.scrollAndZoomIntoView(slides);

  figma.closePlugin(`✓ 6 slides creados — Age Discrimination · The Lange Firm`);
}

run().catch(err => figma.closePlugin("Error: " + err.message));
