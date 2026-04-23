# Construindo um Portfolio com Flask e MongoDB

Neste post vou te mostrar como estruturei meu portfolio pessoal usando **Python + Flask** no backend e **MongoDB** como banco de dados.

---

## Por que MongoDB?

Quando comecei este projeto, tinha duas opções na mesa:

1. PostgreSQL com SQLAlchemy
2. MongoDB com PyMongo

Escolhi o MongoDB por três razões principais:

- Flexibilidade de schema, perfeito para blogs com campos opcionais
- Integração natural com Python via dicionários
- Hospedagem gratuita no Atlas com tier generoso

> "A melhor tecnologia é aquela que resolve o problema sem criar outros." — eu mesmo, às 2 da manhã.

---

## Estrutura do Projeto

```
portfolio/
├── app.py
├── models.py
├── templates/
│   ├── base.html
│   ├── terms.html
│   ├── index.html
│   ├── blog/
│   │   ├── list.html
│   │   ├── detail.html
│   │   ├── editor.html
│   │   └── dashboard.html
│   └── auth/
│       ├── login.html
│       └── verify_code.html
└── static/
    ├── css/styles.css
    └── js/
        ├── main.js
        └── base.js
```

Utilizo as seguintes bibliotecas python, especificadas em `requirements.txt`:
```
flask
flask-login
flask-pymongo
pymongo
requests
markdown2
```

E, finalmente, configuro as variáveis de entorno em `.env` com as seguintes keys:
```
BREVO_API_KEY="minha api key de Brevo"
BREVO_SENDER="minha conta de email"
MONGODB_DB="minha db em mongodb"
MONGODB_URI="minha URI de mongodb"
SESSION_SECRET="minha key secreta de sessão para o servidor Flask"
TURNSTILE_SECRET_KEY="minha key secreta de Cloudflare Turnstile"
```

Logo, configuro meu projeto em Railway, atribuindo o comando de *deployment* como `python3 app.py`.

---

## Autenticação sem Senha

Em vez de senha tradicional, usei OTP por email. O fluxo é:

1. Usuário entra com o email
2. Sistema gera código de 6 dígitos de forma pseudoaleatória
3. Código é salvo no MongoDB com TTL de 3 minutos, o que facilita a segurança de que o código não pode ser adivinhado em uma janela de tempo tão curta
4. Email enviado via **Brevo API**
5. Usuário digita o código e é autenticado, após a autorização, o código é destruido automáticamente

---

## Veja o Resultado

O portfolio está hospedado no Railway e pode ser acessado em [zeuss.up.railway.app](https://zeuss.up.railway.app).

O código fonte está disponível no meu GitHub em [https://github.com/CatZeuss/Zeuss-Portfolio](https://github.com/CatZeuss/Zeuss-Portfolio). Você pode adaptá-lo e fazer sua própria versão se quiser!

---

## Tabela de Tecnologias

| Tecnologia | Função | Versão |
|---|---|---|
| Flask | Backend web | 3.x |
| PyMongo | Driver MongoDB | 4.x |
| Tailwind CSS | Estilização | CDN |
| Syne | Fonte display | Google Fonts |
| Brevo | Envio de emails | API v3 |
| Turnstile | Captcha | Cloudflare |

---

## Conclusão

A stack Flask + MongoDB se mostrou **extremamente produtiva** para um portfolio solo. O tempo de setup foi mínimo e a flexibilidade do schema me permitiu iterar rápido sem migrations.
