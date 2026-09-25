# Gerador de Etiquetas & Declaração de Envio

Aplicação Flask pronta para produção no Render com suporte a Gunicorn e autenticação de acesso HTTP Basic Auth.

## 🚀 Como subir para o GitHub

1. Extraia o conteúdo deste arquivo zip em uma pasta no seu computador.
2. Abra o terminal nessa pasta e execute:
```bash
git init
git add .
git commit -m "feat: configuracao de producao para Render com autenticacao"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

## 🌐 Como configurar no Render

1. Crie uma conta ou faça login em [render.com](https://render.com).
2. Clique em **New +** > **Web Service**.
3. Conecte seu repositório do GitHub recém-criado.
4. Preencha as configurações:
   - **Name:** `gerador-etiquetas`
   - **Environment / Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`
5. Na aba **Environment** (Variáveis de Ambiente), adicione:
   - `APP_USER`: Usuário de acesso desejado (padrão se vazio: `admin`)
   - `APP_PASSWORD`: Senha segura de acesso (padrão se vazio: `admin123`)
   - `SECRET_KEY`: Uma sequência de caracteres aleatórios para segurança da sessão Flask
6. Clique em **Create Web Service**.
