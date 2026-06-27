# services/pdf_generator.py

from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generar_planilla_paciente(datos_paciente: dict, ruta_archivo: str):
    """Compila la planilla PDF de registro médico."""
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()

    # Estilos
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor("#3b4cb4"), alignment=1, spaceAfter=15)
    section_style = ParagraphStyle('S', parent=styles['Heading2'], fontSize=11, leading=14, textColor=colors.HexColor("#3b4cb4"), spaceBefore=12, spaceAfter=6)
    label_style = ParagraphStyle('L', parent=styles['Normal'], fontSize=9, leading=11, textColor=colors.HexColor("#475569"), fontName="Helvetica-Bold")
    value_style = ParagraphStyle('V', parent=styles['Normal'], fontSize=9, leading=11, textColor=colors.HexColor("#0f172a"))

    story.append(Paragraph("PLANILLA DE REGISTRO DE PACIENTE", title_style))
    story.append(Paragraph("SISTEMA DE GESTIÓN MÉDICA - CONSULTA ASISTIDA", ParagraphStyle('Sub', parent=styles['Normal'], alignment=1, spaceAfter=20, fontSize=9, textColor=colors.HexColor("#64748b"))))
    
    # Datos Personales
    story.append(Paragraph("1. DATOS PERSONALES DEL PACIENTE", section_style))
    tabla_personales_data = [
        [Paragraph("Apellidos:", label_style), Paragraph(datos_paciente.get("apellidos", ""), value_style),
         Paragraph("Nombres:", label_style), Paragraph(datos_paciente.get("nombres", ""), value_style)],
        [Paragraph("Cédula de Identidad:", label_style), Paragraph(datos_paciente.get("cedula", ""), value_style),
         Paragraph("Sexo:", label_style), Paragraph(datos_paciente.get("sexo", ""), value_style)],
        [Paragraph("Fecha Nacimiento:", label_style), Paragraph(datos_paciente.get("fecha_nac", ""), value_style),
         Paragraph("Fecha Registro:", label_style), Paragraph(datos_paciente.get("fecha_registro", ""), value_style)]
    ]
    t_personales = Table(tabla_personales_data, colWidths=[120, 146, 120, 146])
    t_personales.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t_personales)

    # Ubicación y Contacto
    story.append(Paragraph("2. INFORMACIÓN DE CONTACTO Y UBICACIÓN", section_style))
    tabla_ubicacion_data = [
        [Paragraph("Teléfono:", label_style), Paragraph(datos_paciente.get("telefono", ""), value_style),
         Paragraph("Estado/Lugar:", label_style), Paragraph(datos_paciente.get("lugar_nac", ""), value_style)],
        [Paragraph("Municipio:", label_style), Paragraph(datos_paciente.get("municipio", ""), value_style),
         Paragraph("Parroquia:", label_style), Paragraph(datos_paciente.get("parroquia", ""), value_style)],
        [Paragraph("Comunidad / Sector:", label_style), Paragraph(datos_paciente.get("comunidad", ""), value_style),
         Paragraph("", label_style), Paragraph("", value_style)]
    ]
    t_ubicacion = Table(tabla_ubicacion_data, colWidths=[120, 146, 120, 146])
    t_ubicacion.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t_ubicacion)

    # Dirección
    t_dir_data = [[Paragraph("Dirección de Habitación:", label_style), Paragraph(datos_paciente.get("direccion", ""), value_style)]]
    t_dir = Table(t_dir_data, colWidths=[120, 412])
    t_dir.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8), ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t_dir)

    # Datos Clínicos
    story.append(Paragraph("3. DIAGNÓSTICO / MOTIVO DE CONSULTA", section_style))
    tabla_clinica_data = [
        [Paragraph("Condición Inicial:", label_style), Paragraph(datos_paciente.get("condicion", ""), value_style),
         Paragraph("Tipo de Consulta:", label_style), Paragraph(datos_paciente.get("consulta", ""), value_style)]
    ]
    t_clinica = Table(tabla_clinica_data, colWidths=[120, 146, 120, 146])
    t_clinica.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t_clinica)
    story.append(Spacer(1, 45))

    # Firmas
    firma_data = [
        [Paragraph("________________________________________", ParagraphStyle('F', parent=styles['Normal'], alignment=1)),
         Paragraph("________________________________________", ParagraphStyle('F', parent=styles['Normal'], alignment=1))],
        [Paragraph("Firma del Médico Evaluador", ParagraphStyle('FL', parent=styles['Normal'], alignment=1, fontSize=8, textColor=colors.HexColor("#64748b"))),
         Paragraph("Sello del Consultorio", ParagraphStyle('FL', parent=styles['Normal'], alignment=1, fontSize=8, textColor=colors.HexColor("#64748b")))]
    ]
    t_firma = Table(firma_data, colWidths=[266, 266])
    t_firma.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_firma)

    doc.build(story)


def generar_receta_medica(receta_json: dict, ruta_archivo: str):
    """Compila la receta médica e indicaciones."""
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()

    # Estilos
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=15, leading=18, textColor=colors.HexColor("#3b4cb4"), alignment=1, spaceAfter=4)
    sub_style = ParagraphStyle('S', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor("#64748b"), alignment=1, spaceAfter=15)
    section_style = ParagraphStyle('Sec', parent=styles['Heading2'], fontSize=10, leading=12, textColor=colors.HexColor("#3b4cb4"), spaceBefore=10, spaceAfter=6, fontName="Helvetica-Bold")
    label_style = ParagraphStyle('L', parent=styles['Normal'], fontSize=9, leading=11, textColor=colors.HexColor("#475569"), fontName="Helvetica-Bold")
    value_style = ParagraphStyle('V', parent=styles['Normal'], fontSize=9, leading=11, textColor=colors.HexColor("#0f172a"))
    h_table_style = ParagraphStyle('H', parent=styles['Normal'], fontSize=9, leading=11, textColor=colors.HexColor("#ffffff"), fontName="Helvetica-Bold")

    story.append(Paragraph("SISTEMA MÉDICO DIGITAL HOSPITALARIO", title_style))
    story.append(Paragraph("PLANILLA OFICIAL DE RECETARIO MÉDICO E INDICACIONES", sub_style))

    # Paciente
    paciente_info = receta_json.get("paciente", {})
    tabla_paciente_data = [
        [Paragraph("Paciente:", label_style), Paragraph(paciente_info.get("nombre", "No especificado"), value_style),
         Paragraph("Fecha de Emisión:", label_style), Paragraph(receta_json.get("fecha_emision", datetime.now().strftime("%d/%m/%Y")), value_style)],
        [Paragraph("Cédula:", label_style), Paragraph(paciente_info.get("cedula", "No especificado"), value_style),
         Paragraph("Diagnóstico:", label_style), Paragraph(receta_json.get("diagnostico_resumido", "General"), value_style)]
    ]
    t_paciente = Table(tabla_paciente_data, colWidths=[65, 195, 110, 150])
    t_paciente.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_paciente)
    story.append(Spacer(1, 15))

    # Medicamentos
    story.append(Paragraph("PRESCRIPCIÓN DE TRATAMIENTO", section_style))
    tabla_receta_data = [[
        Paragraph("Medicamiento / Fármaco", h_table_style), Paragraph("Dosis", h_table_style),
        Paragraph("Frecuencia", h_table_style), Paragraph("Duración", h_table_style)
    ]]
    for med in receta_json.get("receta", {}).get("medicamentos", []):
        tabla_receta_data.append([
            Paragraph(med.get("nombre", ""), value_style), Paragraph(med.get("dosis", ""), value_style),
            Paragraph(med.get("frecuencia", ""), value_style), Paragraph(med.get("duracion", ""), value_style)
        ])
    t_receta = Table(tabla_receta_data, colWidths=[180, 110, 130, 100])
    t_receta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3b4cb4")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(t_receta)
    story.append(Spacer(1, 15))

    # Indicaciones
    story.append(Paragraph("INDICACIONES Y RECOMENDACIONES GENERALES", section_style))
    for ind in receta_json.get("receta", {}).get("indicaciones_generales", []):
        story.append(Paragraph(f"• {ind}", value_style))
        story.append(Spacer(1, 4))

    # Advertencias
    story.append(Spacer(1, 10))
    story.append(Paragraph("ADVERTENCIAS DE SEGURIDAD MÉDICA", ParagraphStyle('AdvTitle', parent=section_style, textColor=colors.HexColor("#ef4444"))))
    for adv in receta_json.get("receta", {}).get("advertencias", []):
        story.append(Paragraph(f"⚠ {adv}", ParagraphStyle('Adv', parent=value_style, textColor=colors.HexColor("#ef4444"))))
        story.append(Spacer(1, 4))

    # Firmas
    story.append(Spacer(1, 35))
    firma_data = [
        [Paragraph("________________________________________", ParagraphStyle('F', parent=styles['Normal'], alignment=1)),
         Paragraph("________________________________________", ParagraphStyle('F', parent=styles['Normal'], alignment=1))],
        [Paragraph("Firma del Médico Prescriptor", ParagraphStyle('FL', parent=styles['Normal'], alignment=1, fontSize=8, textColor=colors.HexColor("#64748b"))),
         Paragraph("Sello / Identificación Clínico", ParagraphStyle('FL', parent=styles['Normal'], alignment=1, fontSize=8, textColor=colors.HexColor("#64748b")))]
    ]
    t_firma = Table(firma_data, colWidths=[260, 260])
    t_firma.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_firma)

    doc.build(story)
