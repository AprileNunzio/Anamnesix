import io
from typing import Optional, List, Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from pypdf import PdfReader, PdfWriter
from app.database.connection import get_db_connection
from app.analytics.health_score import health_score_calculator
from app.analytics.radar_anomalies import radar_anomalies_engine
from app.profiles.profile_manager import profile_manager

class PDFDossierGenerator:
    def __init__(self):
        self.ready = True

    def generate_dossier(
        self,
        profile_id: str | None = None,
        password: Optional[str] = None
    ) -> bytes:
        if not profile_id:
            profile_id = profile_manager.get_active_profile_id()

        profiles = profile_manager.list_profiles()
        current_profile = next((p for p in profiles if p["id"] == profile_id), {
            "nome": "Utente", "cognome": "Anamnesix", "data_nascita": "", "sesso": "", "gruppo_sanguigno": ""
        })

        scores = health_score_calculator.calculate_scores(profile_id=profile_id)
        anomalies = radar_anomalies_engine.get_ranked_anomalies(profile_id=profile_id)

        conn = get_db_connection(profile_id=profile_id)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT a.nome_standardizzato, a.categoria, a.valore_numerico, a.valore_testuale,
                       a.unita_misura, a.range_min, a.range_max, a.stato_flag, a.data_prelievo
                FROM analiti a
                ORDER BY a.categoria, a.nome_standardizzato, a.data_prelievo DESC
                """
            )
            all_analiti = [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a")
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#475569")
        )
        section_style = ParagraphStyle(
            "SectionTitle",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0284c7")
        )
        normal_style = styles["Normal"]

        story = []

        story.append(Paragraph("ANAMNESIX - DOSSIER CLINICO PERSONALE", title_style))
        story.append(Paragraph("Rapporto Storico Comparativo e Analisi Biomarcatori", subtitle_style))
        story.append(Spacer(1, 15))

        patient_info = [
            [
                f"Paziente: {current_profile.get('nome')} {current_profile.get('cognome')}",
                f"Data di Nascita: {current_profile.get('data_nascita')}"
            ],
            [
                f"Sesso: {current_profile.get('sesso')}",
                f"Gruppo Sanguigno: {current_profile.get('gruppo_sanguigno') or 'N/D'}"
            ],
            [
                f"Health Score Globale: {scores.get('overall_score')}/100",
                f"Stato Generale: {scores.get('stato_sintetico')}"
            ]
        ]
        t_patient = Table(patient_info, colWidths=[260, 260])
        t_patient.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("FONTSIZE", (0, 0), (-1, -1), 10)
        ]))
        story.append(t_patient)
        story.append(Spacer(1, 15))

        if anomalies:
            story.append(Paragraph("RADAR DELLE ANOMALIE ATTUALI", section_style))
            story.append(Spacer(1, 8))
            anom_data = [["Biomarcatore", "Valore", "Unita", "Intervallo", "Scostamento", "Stato"]]
            for a in anomalies[:12]:
                val = str(a.get("valore_numerico")) if a.get("valore_numerico") is not None else str(a.get("valore_testuale"))
                r_span = f"{a.get('range_min')} - {a.get('range_max')}"
                scost = f"+{a.get('scostamento_percentuale')}%"
                anom_data.append([
                    a.get("nome_standardizzato"),
                    val,
                    a.get("unita_misura"),
                    r_span,
                    scost,
                    a.get("stato_flag")
                ])
            t_anom = Table(anom_data, colWidths=[150, 60, 60, 90, 80, 80])
            t_anom.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fee2e2")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#991b1b")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fca5a5")),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("FONTSIZE", (0, 0), (-1, -1), 9)
            ]))
            story.append(t_anom)
            story.append(Spacer(1, 15))

        story.append(Paragraph("STORICO DEI BIOMARCATORI E COMPARAZIONI", section_style))
        story.append(Spacer(1, 8))
        bio_data = [["Data", "Categoria", "Esame", "Valore", "Unita", "Range", "Stato"]]
        for item in all_analiti[:45]:
            val = str(item.get("valore_numerico")) if item.get("valore_numerico") is not None else str(item.get("valore_testuale"))
            r_span = f"{item.get('range_min')} - {item.get('range_max')}" if item.get("range_min") is not None else "-"
            bio_data.append([
                item.get("data_prelievo"),
                item.get("categoria"),
                item.get("nome_standardizzato")[:22],
                val,
                item.get("unita_misura"),
                r_span,
                item.get("stato_flag")
            ])
        t_bio = Table(bio_data, colWidths=[65, 85, 140, 55, 55, 65, 55])
        t_bio.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("FONTSIZE", (0, 0), (-1, -1), 8)
        ]))
        story.append(t_bio)
        story.append(Spacer(1, 20))

        disclaimer_text = "AVVISO MEDICO: Il presente dossier clinico e generato a solo scopo informativo dal software Anamnesix e non sostituisce in alcun modo la valutazione diagnostica del medico curante."
        story.append(Paragraph(disclaimer_text, normal_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()

        if password:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(password)
            enc_buffer = io.BytesIO()
            writer.write(enc_buffer)
            return enc_buffer.getvalue()

        return pdf_bytes

pdf_dossier_generator = PDFDossierGenerator()
