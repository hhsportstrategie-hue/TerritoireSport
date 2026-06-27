"""
Génération PDF pour les shortlists TerritoireSport.

Utilise reportlab. Le PDF est généré à la volée, jamais stocké sur disque.

Usage :
    from pdf_export import generate_shortlist_pdf
    pdf_bytes = generate_shortlist_pdf(partners, filters)
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# Couleurs TerritoireSport (vert = sport/nature, gris = institutionnel)
COLOR_PRIMARY = colors.HexColor("#2E7D32")  # Vert foncé
COLOR_SECONDARY = colors.HexColor("#66BB6A")  # Vert clair
COLOR_ACCENT = colors.HexColor("#FFA726")  # Orange
COLOR_TEXT = colors.HexColor("#212121")
COLOR_GREY = colors.HexColor("#757575")
COLOR_BG_HEADER = colors.HexColor("#E8F5E9")  # Vert très clair


def _build_styles():
    """Construit les styles utilisés dans le PDF."""
    styles = getSampleStyleSheet()

    # Titre principal
    styles.add(ParagraphStyle(
        name="TSTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=COLOR_PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName="Helvetica-Bold"
    ))

    # Sous-titre
    styles.add(ParagraphStyle(
        name="TSSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=COLOR_GREY,
        alignment=TA_CENTER,
        spaceAfter=24
    ))

    # Section header
    styles.add(ParagraphStyle(
        name="TSSectionHeader",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=COLOR_PRIMARY,
        spaceBefore=18,
        spaceAfter=10,
        fontName="Helvetica-Bold"
    ))

    # Corps
    styles.add(ParagraphStyle(
        name="TSBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=COLOR_TEXT,
        alignment=TA_LEFT,
        spaceAfter=6
    ))

    # Footer
    styles.add(ParagraphStyle(
        name="TSFooter",
        parent=styles["Normal"],
        fontSize=8,
        textColor=COLOR_GREY,
        alignment=TA_CENTER
    ))

    return styles


def _score_color(score):
    """Retourne la couleur d'un score (rouge<40, orange<70, vert>=70)."""
    if score >= 70:
        return colors.HexColor("#4CAF50")  # Vert
    elif score >= 40:
        return colors.HexColor("#FF9800")  # Orange
    else:
        return colors.HexColor("#F44336")  # Rouge


def generate_shortlist_pdf(partners: list, filters: dict, commune_label: str = None) -> bytes:
    """
    Génère un PDF de shortlist au format paysage A4.

    Args:
        partners: liste de dicts {name, type, category, city, themes, score, contact_email, contact_url, description}
        filters: dict des filtres appliqués (pour affichage dans le PDF)
        commune_label: libellé lisible de la commune (optionnel)

    Returns:
        bytes: contenu du PDF prêt à être envoyé en réponse HTTP
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="TerritoireSport — Shortlist Partenaires",
        author="TerritoireSport",
    )

    styles = _build_styles()
    story = []

    # ════════════════════════════════════════════════════════════════
    # Page de garde
    # ════════════════════════════════════════════════════════════════

    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("⚽ TerritoireSport", styles["TSTitle"]))
    story.append(Paragraph("Shortlist de partenaires potentiels", styles["TSSubtitle"]))

    # Bloc d'info : date, commune, nombre de partenaires
    now = datetime.now().strftime("%d/%m/%Y à %Hh%M")
    location = commune_label or filters.get("commune") or "Toutes communes"
    theme_label = filters.get("theme_label", "")
    info_data = [
        ["Date de génération", now],
        ["Localisation", location],
        ["Thématique", theme_label or "Toutes thématiques"],
        ["Partenaires identifiés", str(len(partners))],
    ]
    if filters.get("type"):
        type_labels = {
            "association": "Associations",
            "company": "Entreprises",
            "public": "Structures publiques",
        }
        info_data.append(["Type de partenaire", type_labels.get(filters["type"], filters["type"])])
    if filters.get("search"):
        info_data.append(["Recherche", filters["search"]])

    info_table = Table(info_data, colWidths=[5 * cm, 12 * cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("TEXTCOLOR", (0, 0), (0, -1), COLOR_PRIMARY),
        ("TEXTCOLOR", (1, 0), (1, -1), COLOR_TEXT),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, COLOR_GREY),
    ]))
    story.append(info_table)

    # Légende scoring
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("Légende du score de compatibilité", styles["TSSectionHeader"]))
    legend_data = [
        ["Score", "Interprétation"],
        ["≥ 70", "Partenaire très pertinent — à contacter en priorité"],
        ["40 à 69", "Partenaire pertinent — évaluer le potentiel"],
        ["< 40", "Partenaire à explorer davantage avant contact"],
    ]
    legend_table = Table(legend_data, colWidths=[3 * cm, 14 * cm])
    legend_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_BG_HEADER]),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_GREY),
    ]))
    story.append(legend_table)

    # Saut de page vers le tableau des partenaires
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════
    # Tableau des partenaires
    # ════════════════════════════════════════════════════════════════

    story.append(Paragraph("Partenaires identifiés", styles["TSSectionHeader"]))

    if not partners:
        story.append(Paragraph(
            "Aucun partenaire ne correspond aux critères sélectionnés. "
            "Essayez d'élargir votre recherche en supprimant certains filtres.",
            styles["TSBody"]
        ))
    else:
        # En-tête du tableau
        data = [["#", "Partenaire", "Type", "Ville", "Thématiques", "Score", "Contact"]]

        for idx, p in enumerate(partners, start=1):
            # Décodage des thèmes (stockés en JSON string)
            themes_raw = p.get("themes", "[]")
            try:
                import json
                themes_list = json.loads(themes_raw) if isinstance(themes_raw, str) else themes_raw
            except Exception:
                themes_list = []
            themes_short = ", ".join(themes_list[:3]) if themes_list else "—"
            if len(themes_list) > 3:
                themes_short += f" (+{len(themes_list) - 3})"

            contact = p.get("contact_email") or p.get("contact_url") or "—"

            score = p.get("score", 0)

            data.append([
                str(idx),
                Paragraph(str(p.get("name", "")), styles["TSBody"]),
                str(p.get("type", "") or p.get("category", "")),
                str(p.get("city", "") or p.get("commune", "")),
                themes_short,
                f"{score:.0f}",
                contact
            ])

        # Largeurs en paysage A4 (29.7cm - marges)
        col_widths = [1 * cm, 5 * cm, 2.5 * cm, 2.5 * cm, 5 * cm, 1.5 * cm, 5 * cm]
        table = Table(data, colWidths=col_widths, repeatRows=1)

        # Style du tableau
        style_cmds = [
            # En-tête
            ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            # Corps
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 1), (0, -1), "CENTER"),  # Numéro
            ("ALIGN", (5, 1), (5, -1), "CENTER"),  # Score
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_BG_HEADER]),
            ("GRID", (0, 0), (-1, -1), 0.5, COLOR_GREY),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]

        # Coloration des scores (colonne 5)
        for idx, p in enumerate(partners, start=1):
            score = p.get("score", 0)
            style_cmds.append(("TEXTCOLOR", (5, idx), (5, idx), _score_color(score)))
            style_cmds.append(("FONTNAME", (5, idx), (5, idx), "Helvetica-Bold"))

        table.setStyle(TableStyle(style_cmds))
        story.append(table)

    # Footer / source
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f"Document généré par TerritoireSport · Données ouvertes · "
        f"https://ts-backend-production.up.railway.app",
        styles["TSFooter"]
    ))

    # Construction du PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def get_theme_label(theme_id: int) -> str:
    """Retourne un libellé lisible pour un theme_id."""
    labels = {
        1: "Sport & Santé",
        2: "Insertion / Cohésion Sociale",
        3: "Environnement",
        4: "Éducation / Jeunesse",
        5: "Culture / Patrimoine",
        6: "Économie Locale / Emploi",
        7: "Citoyenneté",
        8: "Innovation / Technologie",
        9: "Alimentation",
        10: "Tourisme",
        11: "Intergénérationnel",
        12: "Handicap",
        13: "Éducation Populaire",
        14: "Santé Mentale",
        15: "Égalité des Chances",
        16: "Écologie",
        17: "Patrimoine Immatériel",
        18: "Innovation Sociale",
        19: "Urgence Sociale",
    }
    return labels.get(theme_id, "")
