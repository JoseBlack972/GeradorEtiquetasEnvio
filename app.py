import io
import os
import re
import unicodedata
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from services.document_service import DocumentService

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_secreta_padrao_altere_em_producao")

# ----------------- AUTENTICAÇÃO BÁSICA -----------------
auth = HTTPBasicAuth()

# Usuário e Senha configuráveis via Variáveis de Ambiente
ADMIN_USER = os.getenv("APP_USER", "admin")
ADMIN_PASSWORD = os.getenv("APP_PASSWORD", "admin123")

users = {
    ADMIN_USER: generate_password_hash(ADMIN_PASSWORD)
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None
# -------------------------------------------------------

ESTADOS_BRASIL = [
    ("AC", "Acre (AC)"),
    ("AL", "Alagoas (AL)"),
    ("AP", "Amapá (AP)"),
    ("AM", "Amazonas (AM)"),
    ("BA", "Bahia (BA)"),
    ("CE", "Ceará (CE)"),
    ("DF", "Distrito Federal (DF)"),
    ("ES", "Espírito Santo (ES)"),
    ("GO", "Goiás (GO)"),
    ("MA", "Maranhão (MA)"),
    ("MT", "Mato Grosso (MT)"),
    ("MS", "Mato Grosso do Sul (MS)"),
    ("MG", "Minas Gerais (MG)"),
    ("PA", "Pará (PA)"),
    ("PB", "Paraíba (PB)"),
    ("PR", "Paraná (PR)"),
    ("PE", "Pernambuco (PE)"),
    ("PI", "Piauí (PI)"),
    ("RJ", "Rio de Janeiro (RJ)"),
    ("RN", "Rio Grande do Norte (RN)"),
    ("RS", "Rio Grande do Sul (RS)"),
    ("RO", "Rondônia (RO)"),
    ("RR", "Roraima (RR)"),
    ("SC", "Santa Catarina (SC)"),
    ("SP", "São Paulo (SP)"),
    ("SE", "Sergipe (SE)"),
    ("TO", "Tocantins (TO)")
]

DEFAULT_VALUES = {
    "dest_nome": "",
    "dest_cnpj": "",
    "dest_endereco": "",
    "dest_bairro": "",
    "dest_cidade": "",
    "dest_uf": "",
    "dest_cep": "",
    "dest_fone": "",
    "nf_num": "",
    "nf_valor": "",
    "rem_empresa": "",
    "rem_cnpj": "",
    "rem_endereco": "",
    "layout_mode": "2x",
}

CAMPOS_OBRIGATORIOS = [
    ("dest_nome", "Destinatário / Razão Social"),
    ("dest_cnpj", "CNPJ do Destinatário"),
    ("dest_endereco", "Endereço Completo do Destinatário"),
    ("dest_bairro", "Bairro do Destinatário"),
    ("dest_cidade", "Cidade do Destinatário"),
    ("dest_uf", "UF do Destinatário"),
    ("dest_cep", "CEP do Destinatário"),
    ("nf_num", "Número da Nota Fiscal (NF)"),
    ("nf_valor", "Valor Declarado (R$)"),
    ("rem_empresa", "Empresa Remetente"),
    ("rem_cnpj", "CNPJ Remetente"),
    ("rem_endereco", "Endereço e Contato do Remetente"),
]

ALLOWED_LOGO_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_logo(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_LOGO_EXTENSIONS

def sanitize_filename_part(text: str) -> str:
    nfkd = unicodedata.normalize('NFKD', text)
    clean_text = "".join([c for c in nfkd if not unicodedata.combining(c)])
    clean_text = re.sub(r'[^a-zA-Z0-9_-]', '_', clean_text)
    clean_text = re.sub(r'_+', '_', clean_text).strip('_')
    return clean_text or "Destinatario"


@app.route("/", methods=["GET", "POST"])
@auth.login_required
def index():
    if request.method == "POST":
        layout_mode = request.form.get("layout_mode", "2x")
        dados = {
            "dest_nome": request.form.get("dest_nome", "").strip()[:50],
            "dest_cnpj": request.form.get("dest_cnpj", "").strip(),
            "dest_endereco": request.form.get("dest_endereco", "").strip()[:50],
            "dest_bairro": request.form.get("dest_bairro", "").strip(),
            "dest_cidade": request.form.get("dest_cidade", "").strip()[:20],
            "dest_uf": request.form.get("dest_uf", "").strip().upper()[:2],
            "dest_cep": request.form.get("dest_cep", "").strip(),
            "dest_fone": request.form.get("dest_fone", "").strip(),
            "nf_num": re.sub(r'\D', '', request.form.get("nf_num", "").strip()),
            "nf_valor": request.form.get("nf_valor", "").strip(),
            "rem_empresa": request.form.get("rem_empresa", "").strip()[:50],
            "rem_cnpj": request.form.get("rem_cnpj", "").strip(),
            "rem_endereco": request.form.get("rem_endereco", "").strip()[:50],
            "layout_mode": layout_mode
        }

        faltantes = [rotulo for campo, rotulo in CAMPOS_OBRIGATORIOS if not dados.get(campo)]
        if faltantes:
            flash(f"Preencha todos os campos obrigatórios: {', '.join(faltantes)}.", "error")
            return render_template("index.html", data=dados, estados=ESTADOS_BRASIL)

        logo_stream = None
        logo_file = request.files.get("logo")
        if logo_file and logo_file.filename:
            if allowed_logo(logo_file.filename):
                logo_stream = io.BytesIO(logo_file.read())
            else:
                flash("Formato do logo inválido. Envie imagem .PNG ou .JPG/.JPEG.", "error")
                return render_template("index.html", data=dados, estados=ESTADOS_BRASIL)

        dest_sanitizado = sanitize_filename_part(dados["dest_nome"])
        nf_sanitizada = sanitize_filename_part(dados["nf_num"])
        nome_arquivo = f"Envio_para_{dest_sanitizado}_NF{nf_sanitizada}.pdf"

        try:
            if layout_mode == "1x":
                pdf_stream = DocumentService.generate_pdf_inteira(dados, logo_stream=logo_stream)
            else:
                pdf_stream = DocumentService.generate_pdf_dupla(dados, logo_stream=logo_stream)

            return send_file(
                pdf_stream,
                as_attachment=True,
                download_name=nome_arquivo,
                mimetype="application/pdf",
            )
        except Exception as e:
            flash(f"Erro ao processar e gerar o arquivo PDF: {str(e)}", "error")
            return render_template("index.html", data=dados, estados=ESTADOS_BRASIL)

    return render_template("index.html", data=DEFAULT_VALUES, estados=ESTADOS_BRASIL)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
