import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image
from PIL import Image as PILImage


class DocumentService:
    @staticmethod
    def _criar_bloco_etiqueta_compacta(dados: dict, logo_bytes: bytes = None) -> list:
        styles = getSampleStyleSheet()
        normal_bold = ParagraphStyle(
            "CompactBold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11
        )
        normal_text = ParagraphStyle(
            "CompactText", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=11
        )
        title_style = ParagraphStyle(
            "CompactTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            alignment=1,
            textColor=colors.HexColor("#1e293b"),
        )

        elementos = []

        if logo_bytes:
            try:
                logo_io = io.BytesIO(logo_bytes)
                pil_img = PILImage.open(logo_io)
                orig_w, orig_h = pil_img.size

                max_w = 4.8 * cm
                max_h = 1.3 * cm
                ratio = min(max_w / orig_w, max_h / orig_h)
                target_w = orig_w * ratio
                target_h = orig_h * ratio

                logo_io.seek(0)
                img = Image(logo_io, width=target_w, height=target_h)
                img.hAlign = "CENTER"
                elementos.append(img)
                elementos.append(Spacer(1, 0.15 * cm))
            except Exception:
                pass

        elementos.append(Paragraph("DECLARAÇÃO / ETIQUETA DE ENVIO", title_style))
        elementos.append(Spacer(1, 0.15 * cm))

        conteudo = [
            [Paragraph("<b>Destinatário:</b>", normal_bold), Paragraph(dados.get("dest_nome", ""), normal_text)],
            [Paragraph("<b>CNPJ / CPF:</b>", normal_bold), Paragraph(dados.get("dest_cnpj", ""), normal_text)],
            [Paragraph("<b>Endereço:</b>", normal_bold), Paragraph(dados.get("dest_endereco", ""), normal_text)],
            [Paragraph("<b>Bairro / Cidade:</b>", normal_bold), Paragraph(f"{dados.get('dest_bairro', '')} - {dados.get('dest_cidade', '')} / {dados.get('dest_uf', '')}", normal_text)],
            [Paragraph("<b>CEP / Contato:</b>", normal_bold), Paragraph(f"CEP: {dados.get('dest_cep', '')} &nbsp;|&nbsp; Fone: {dados.get('dest_fone', '') or '-'}", normal_text)],
            [
                Paragraph("<b>NF / Valor:</b>", normal_bold),
                Paragraph(f"NF: {dados.get('nf_num', '')} &nbsp;&nbsp;|&nbsp;&nbsp; R$: {dados.get('nf_valor', '')}", normal_bold),
            ],
            [
                Paragraph("<b>Remetente:</b>", normal_bold),
                Paragraph(
                    f"<b>{dados.get('rem_empresa', '')}</b> &nbsp;|&nbsp; CNPJ: {dados.get('rem_cnpj', '')}<br/>{dados.get('rem_endereco', '')}",
                    normal_text,
                ),
            ],
        ]

        tabela = Table(conteudo, colWidths=[3.2 * cm, 15.3 * cm])
        tabela.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#334155")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8fafc")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3.2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
                ]
            )
        )

        elementos.append(tabela)
        return elementos

    @classmethod
    def generate_pdf_dupla(cls, dados: dict, logo_stream: io.BytesIO = None) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.2 * cm,
            leftMargin=1.2 * cm,
            topMargin=1.0 * cm,
            bottomMargin=1.0 * cm,
        )

        logo_bytes = logo_stream.getvalue() if logo_stream else None
        story = []

        story.extend(cls._criar_bloco_etiqueta_compacta(dados, logo_bytes))

        story.append(Spacer(1, 0.4 * cm))
        styles = getSampleStyleSheet()
        cut_style = ParagraphStyle(
            "CutLine",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7,
            alignment=1,
            textColor=colors.HexColor("#64748b")
        )
        story.append(Paragraph("✂ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - LINHA DE CORTE - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ✂", cut_style))
        story.append(Spacer(1, 0.4 * cm))

        story.extend(cls._criar_bloco_etiqueta_compacta(dados, logo_bytes))

        doc.build(story)
        buffer.seek(0)
        return buffer

    @classmethod
    def generate_pdf_inteira(cls, dados: dict, logo_stream: io.BytesIO = None) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        styles = getSampleStyleSheet()
        normal_bold = ParagraphStyle(
            "FullBold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11, leading=15
        )
        normal_text = ParagraphStyle(
            "FullText", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=15
        )
        title_style = ParagraphStyle(
            "FullTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            alignment=1,
            textColor=colors.HexColor("#1e293b"),
        )

        story = []

        if logo_stream:
            try:
                logo_stream.seek(0)
                pil_img = PILImage.open(logo_stream)
                orig_w, orig_h = pil_img.size

                max_w = 6.5 * cm
                max_h = 2.4 * cm
                ratio = min(max_w / orig_w, max_h / orig_h)
                target_w = orig_w * ratio
                target_h = orig_h * ratio

                logo_stream.seek(0)
                logo_img = Image(logo_stream, width=target_w, height=target_h)
                logo_img.hAlign = "CENTER"
                story.append(logo_img)
                story.append(Spacer(1, 0.4 * cm))
            except Exception:
                pass

        story.append(Paragraph("DECLARAÇÃO / ETIQUETA DE ENVIO", title_style))
        story.append(Spacer(1, 0.5 * cm))

        conteudo = [
            [Paragraph("<b>Destinatário:</b>", normal_bold), Paragraph(dados.get("dest_nome", ""), normal_text)],
            [Paragraph("<b>CNPJ / CPF:</b>", normal_bold), Paragraph(dados.get("dest_cnpj", ""), normal_text)],
            [Paragraph("<b>Endereço:</b>", normal_bold), Paragraph(dados.get("dest_endereco", ""), normal_text)],
            [Paragraph("<b>Bairro:</b>", normal_bold), Paragraph(dados.get("dest_bairro", ""), normal_text)],
            [Paragraph("<b>Cidade / UF:</b>", normal_bold), Paragraph(f"{dados.get('dest_cidade', '')} / {dados.get('dest_uf', '')}", normal_text)],
            [Paragraph("<b>CEP:</b>", normal_bold), Paragraph(dados.get("dest_cep", ""), normal_text)],
            [Paragraph("<b>Telefone / Contato:</b>", normal_bold), Paragraph(dados.get("dest_fone", "") or "-", normal_text)],
            [
                Paragraph("<b>NF / Valor:</b>", normal_bold),
                Paragraph(f"NF: {dados.get('nf_num', '')} &nbsp;&nbsp;|&nbsp;&nbsp; R$: {dados.get('nf_valor', '')}", normal_bold),
            ],
            [
                Paragraph("<b>Remetente:</b>", normal_bold),
                Paragraph(
                    f"<b>{dados.get('rem_empresa', '')}</b><br/>CNPJ: {dados.get('rem_cnpj', '')}<br/>{dados.get('rem_endereco', '')}",
                    normal_text,
                ),
            ],
        ]

        tabela = Table(conteudo, colWidths=[4.2 * cm, 13.8 * cm])
        tabela.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#334155")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8fafc")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )

        story.append(tabela)
        doc.build(story)
        buffer.seek(0)
        return buffer
