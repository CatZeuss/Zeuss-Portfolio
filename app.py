import os
import requests as http_requests
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import logging
import markdown2
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key")

# Brevo API configuration
BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
BREVO_URL = "https://api.brevo.com/v3/smtp/email"
SENDER_EMAIL = os.environ.get("BREVO_SENDER")
SENDER_NAME = "KattZeuss System"

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

import requests as http_requests

def verify_turnstile(token):
    r = http_requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data={
        "secret": os.environ.get("TURNSTILE_SECRET_KEY"),
        "response": token
    })
    return r.json().get("success", False)

# ─────────────────────────────────────────────
# Brevo email helper
# ─────────────────────────────────────────────
def send_email(to_email, to_name, subject, html_content):
    """Envia um e-mail via Brevo API."""
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": BREVO_API_KEY
    }
    data = {
        "sender": {"email": SENDER_EMAIL, "name": SENDER_NAME},
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "htmlContent": html_content
    }
    response = http_requests.post(BREVO_URL, headers=headers, json=data)
    if not response.ok:
        raise Exception(f"Brevo API error {response.status_code}: {response.text}")
    return response


# Import models
from models import User, VerificationCode, Blog, BlogCategory, seed_admin

# Seed admin user on startup
with app.app_context():
    seed_admin()


@login_manager.user_loader
def load_user(user_id):
    return User.find_by_id(user_id)


# ─────────────────────────────────────────────
# Index
# ─────────────────────────────────────────────
@app.route('/')
def index():
    projects = [
        {
            'name': 'ArtKoffee',
            'description': 'Uma rede social para artistas compartilharem arte digital.',
            'links': {
                'web': 'www.art-koffee.com/home',
                'android': 'play.google.com/store/apps/details?id=com.koffeedevs.artkoffee',
                'github': 'github.com/ArtKoffee/ArtKoffee'
            },
            'tech': ['HTML', 'CSS', 'MongoDB', 'Websockets', 'Python', 'JavaScript', 'TailwindCSS', 'Bootstrap', 'JQuery', 'Backend', 'Frontend', 'API', 'Redis', 'JWT', 'Cibersegurança', 'Gestão de projetos', 'Pentesting'],
            'images': [
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-22%20065108.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-22%20065406.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-22%20065532.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-22%20065626.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-22%20065729.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-22%20065826.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-22%20065928.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-22%20070042.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-22%20070218.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-22%20070256.jpg'
            ]
        },
        {
            'name': 'Pousadas Casa Do Ivo',
            'description': 'Site oficial de uma rede de pousadas no oeste do Pará.',
            'tech': ['HTML', 'CSS', 'JavaScript', 'PHP', 'Frontend', 'UI/UX', 'Prototipagem', 'Design'],
            'links': {'web': 'casadoivo.up.railway.app/', 'github': 'github.com/CatZeuss/Casa-Do-Ivo-Landing-Page'},
            'images': [
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/ae13ab3e-dbde-4e2e-58ec-218862000e00/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/86e08e9c-04d9-40c5-335e-014a0b36e300/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/1e03cc07-30da-4722-3eeb-1cde1ce55d00/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/1883edfc-649e-4898-38b3-f8a1522bcd00/public'
            ]
        },
        {
            'name': 'Hackatur',
            'description': 'Site oficial de um projeto que reúne diversas startups de Santarém.',
            'tech': ['HTML', 'CSS', 'JavaScript', 'PHP', 'Frontend', 'UI/UX', 'Prototipagem', 'Design'],
            'links': {'web': 'hackatur.up.railway.app', 'github': 'github.com/CatZeuss/Hackatur-Landing-Page'},
            'images': [
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/d73a0fd6-c599-44ad-043b-c2f9c0810500/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/0953f785-8c6e-4ffe-2a17-5e3d15bb0800/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/59ee5896-2303-4d2a-ee4d-c8c23640b100/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/c9ee1f78-7058-4194-37a0-b46aa9065c00/public'
            ]
        },
        {
            'name': 'RioHacks',
            'description': 'Site oficial da RioHacks Soluções em Tecnologia.',
            'tech': ['HTML', 'CSS', 'JavaScript', 'PHP', 'Frontend', 'UI/UX', 'Prototipagem', 'Design'],
            'links': {'web': 'riohacks.up.railway.app', 'github': 'github.com/CatZeuss/RioHacks-Landing-Page'},
            'images': [
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/1ae5ffc1-c76f-45d2-4593-ed4f1f171300/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/d13af3c3-ea5c-4a06-3605-9cace6e81100/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/05d0ff50-9ace-4680-0c64-869998ddc400/public'
            ]
        },
        {
            'name': 'ManicScript',
            'description': 'Uma linguagem de programação e compilador gamificado em espanhol criada como um projeto paródia para a comunidade.',
            'links': {'web': 'manicscript.up.railway.app', 'github': 'github.com/CatZeuss/ManicScript'},
            'tech': ['Python', 'HTML', 'CSS', 'JavaScript', 'Bootstrap', 'Flask', 'Parser', 'UI/UX', 'Prototipagem', 'Design', 'Frontend', 'Backend', 'API', 'Lexer'],
            'images': [
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/d050d92c-344d-4ed8-b46b-ba3a497f7100/public'
            ]
        },
        {
            'name': 'PolarMind',
            'description': 'Projeto de aplicativo e site de registros de humor e ajuda psicológica especialmente direcionado para indivíduos com transtorno afetivo bipolar.',
            'links': {'github': 'github.com/CatZeuss/PolarMind'},
            'tech': ['HTML', 'CSS', 'JavaScript', 'MongoDB', 'Flask', 'Python'],
            'images': [
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/1f55ee7e-6dc5-4d90-3a53-2f3a52bc2000/public'
            ]
        },
        {
            'name': 'AriaMail',
            'description': 'Servidor seguro de e-mail para envio, recebimento e gerenciamento de e-mails com dominio do art-koffee.com.',
            'links': {'web': 'ariamail.art-koffee.com'},
            'tech': ['Python', 'Flask', 'MongoDB', 'HTML', 'CSS', 'JavaScript', 'Bootstrap', 'Scrypt Hashing', 'SMTP', 'IMAP', 'POP3', 'DNS', 'SSL', 'TLS', 'Mailgun', 'Backend', 'Frontend', 'API', 'Cibersegurança', 'Gestão de projetos', 'Pentesting', 'Design', 'UI/UX', 'Prototipagem'],
            'images': [
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/5790fff8-4c5f-4373-5d01-4cda1d9d1100/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/f7edfa65-1e36-488f-525a-236e10869300/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/5fd34258-6d73-4a5a-33f5-a132ed982c00/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/c932e4af-af30-42e1-f5c4-6217b36aca00/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/306ebad2-6c22-444d-18a7-1be46651b700/public'
            ]
        },
        {
            'name': 'ArtKoffee Support Center',
            'description': 'Sistema completo e seguro de suporte para a comunidade ArtKoffee similar a Zendesk, incluindo ticketing, chat, blogs de ajuda e gestão de tickets.',
            'links': {'web': 'support.art-koffee.com', 'github': 'github.com/ArtKoffee/ArtKoffee-Support'},
            'tech': ['HTML', 'CSS', 'MongoDB', 'Python', 'JavaScript', 'TailwindCSS', 'Bootstrap', 'Backend', 'Single Sign-On', 'Frontend', 'API', 'JWT', 'Cibersegurança', 'Gestão de projetos', 'Pentesting', 'Design', 'UI/UX', 'Prototipagem'],
            'images': [
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-21%20030033.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-21%20030129.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-21%20030151.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-21%20030214.jpg',
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-21%20030242.jpg'
            ]
        },
        {
            'name': 'ArtKoffee Atlas',
            'description': 'Sistema de ArtKoffee que consiste em um painel de administração altamente seguro, onde o ArtKoffee pode ser administrado, moderado e gerenciado. Este sistema oferece funcionalidades para análise, moderação, suporte, depuração, administração geral e segurança.',
            'links': {'web': 'admin.art-koffee.com', 'github': 'github.com/ArtKoffee/ArtKoffee-Admin'},
            'tech': ['HTML', 'CSS', 'MongoDB', 'Python', 'JavaScript', 'TailwindCSS', 'Bootstrap', 'Backend', 'Single Sign-On', 'Frontend', 'API', 'JWT', 'Cibersegurança', 'Gestão de projetos', 'Pentesting', 'Design', 'UI/UX', 'Prototipagem'],
            'images': [
                'https://artkoffee.b-cdn.net/default/Captura%20de%20tela%202026-04-21%20031145.jpg'
            ]
        }
    ]
    skills = {
        'Desenvolvimento': [
            {'name': 'Desenvolvimento Full-Stack', 'proficiency': 95,
             'description': 'Experiência em desenvolvimento de aplicativos de ponta a ponta, desde o design de banco de dados até a implementação de UI'},
            {'name': 'Python', 'proficiency': 100,
             'description': 'Desenvolvimento avançado em Python, incluindo estruturas da web, análise de dados e automação'},
            {'name': 'JavaScript/React', 'proficiency': 70,
             'description': 'Desenvolvimento moderno de JavaScript com React, Redux e ecossistemas relacionados'},
            {'name': 'Desenvolvimento Mobile', 'proficiency': 80,
             'description': 'Desenvolvimento de aplicativos móveis multiplataforma com React Native e tecnologias nativas'},
            {'name': 'Desenvolvimento Web', 'proficiency': 100,
             'description': 'Desenvolvimento de sites e portais com HTML, CSS, JavaScript e PHP'},
            {'name': 'Bancos de Dados', 'proficiency': 80,
             'description': 'Conhecimento avançado em bancos de dados relacionais e não-relacionais, com especial ênfase em NoSQL, Firestore e MongoDB'}
        ],
        'Design': [
            {'name': 'UI/UX Design', 'proficiency': 100,
             'description': 'Design de interface e experiência do usuário com foco em usabilidade e acessibilidade'},
            {'name': 'Design Gráfica', 'proficiency': 100,
             'description': 'Design criativo para mídia digital e impressa usando ferramentas padrão da indústria'},
            {'name': 'Adobe Creative Suite', 'proficiency': 80,
             'description': 'Proficiente em Photoshop, Illustrator e outras ferramentas criativas da Adobe.'},
            {'name': 'Figma/Canva', 'proficiency': 95,
             'description': 'Design de interface moderna e prototipagem usando Figma e Canva'},
            {'name': 'Ilustração', 'proficiency': 90,
             'description': 'Criação de ilustrações para produtos, serviços e identidades visuais'}
        ],
        'Gerenciamento': [
            {'name': 'Gerência de Projeto', 'proficiency': 90,
             'description': 'Liderando projetos complexos desde a concepção até a entrega'},
            {'name': 'Liderança', 'proficiency': 70,
             'description': 'Gerenciando e orientando equipes de desenvolvimento'},
            {'name': 'Metodologias Ágeis', 'proficiency': 95,
             'description': 'Implementação de práticas Agile/Scrum em equipes de desenvolvimento'},
            {'name': 'Trello/Asana/ClickUp', 'proficiency': 100,
             'description': 'Utilização de ferramentas de gerenciamento de projetos para organização e eficiência'}
        ],
        'Escritura': [
            {'name': 'Escritura técnica', 'proficiency': 90,
             'description': 'Criação de documentação técnica clara e abrangente'},
            {'name': 'Documentação', 'proficiency': 85,
             'description': 'Documentação da API e guias do usuário'},
            {'name': 'Criação de Conteúdo', 'proficiency': 80,
             'description': 'Postagens de blog, artigos e redação de conteúdo técnico'},
            {'name': 'Redação Científica', 'proficiency': 85,
             'description': 'Redação de artigos científicos e resumos de artigos'},
            {'name': 'Redação de normas/ToS/Políticas', 'proficiency': 75,
             'description': 'Redação de normas, políticas e termos de serviço'}
        ]
    }
    services = [
        {
            'name': 'Landing Page',
            'price': 599.90,
            'features': [
                'Design responsivo e personalizado',
                'SEO otimizado',
                'Formulário de contato',
                'Animações suaves',
                'Integração com Google Analytics Gratuitamente',
                'CTA Otimizados',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Otimização de performance + SEO técnico'
            ]
        },
        {
            'name': 'Site Institucional Básico',
            'price': 2899.90,
            'features': [
                'Design personalizado',
                'Até 5 páginas',
                'Blog integrado',
                'Painel administrativo',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet para você e sua equipe',
                'Segurança avançada',
                'Otimização de performance + SEO técnico'
            ]
        },
        {
            'name': 'Site Institucional Avançado',
            'price': 3599.90,
            'features': [
                'Design personalizado e mais elaborado',
                'Até 15 páginas',
                'Blog integrado com funcionalidades avançadas',
                'Painel administrativo completo',
                'Integração com WhatsApp Business API',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet para você e sua equipe',
                'Segurança avançada',
                'Otimização de performance + SEO técnico'
            ]
        },
        {
            'name': 'E-commerce Completo',
            'price': 4999.90,
            'features': [
                'Catálogo de produtos + carrinho de compras + checkout',
                'Gateway de pagamento',
                'Gestão de estoque',
                'Painel administrativo',
                'Catálogo de até 500 produtos (com possibilidade de expansão)',
                'Integração com Google Analytics + Stripe',
                'Integração Pix',
                'Integração com Mercado Pago',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet para você e sua equipe',
                'Segurança avançada',
                'Otimização de performance + SEO técnico'
            ]
        },
        {
            'name': 'Sistema de Agendamento',
            'price': 2399.90,
            'features': [
                'Calendário interativo',
                'Gestão de horários',
                'Notificações por email',
                'Área do cliente',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet para você e sua equipe',
                'Segurança avançada',
                'Otimização de performance + SEO técnico'
            ]
        },
        {
            'name': 'Sistema de Delivery Híbrido (Android + iOS)',
            'price': 7816.76,
            'features': [
                '10% off - Preço original: R$ 8.685,29',
                'Design personalizado',
                'Apps iOS + Android para clientes',
                'Apps iOS + Android para entregadores',
                'Painel para restaurantes',
                'Rastreamento em tempo real',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet para você e sua equipe',
                'Segurança avançada',
                'Otimização de performance + SEO técnico',
                'Importante: Apps Android e iOS são WebViews do sistema principal desenvolvidas com Appilix (não são nativas).'
            ]
        },
        {
            'name': 'Sistema de Reservas Hoteleiras',
            'price': 4499.90,
            'features': [
                'Gestão de quartos',
                'Sistema de pagamento',
                'Área do hóspede',
                'Painel de controle',
                'Integração com WhatsApp',
                'Integração com Google Calendar',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet para você e sua equipe',
                'Segurança avançada',
                'Otimização de performance + SEO técnico'
            ]
        },
        {
            'name': 'Aplicativo Mobile Híbrido Completo (Android + iOS)',
            'price': 3533.99,
            'features': [
                'Design personalizado',
                'Apps iOS + Android',
                'Frontend + Backend + API incluso',
                'Painel de controle',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet para você e sua equipe',
                'Segurança avançada',
                'Otimização de performance + SEO técnico',
                'Importante: Apps Android e iOS são WebViews do sistema principal desenvolvidas com Appilix (não são nativas).'
            ]
        },
        {
            'name': 'Sistema ERP',
            'price': 6999.99,
            'features': [
                'Sistema de gerenciamento de estoque',
                'Gestão financeira',
                'Controle de estoque',
                'Recursos humanos',
                'Relatórios avançados',
                'Painel de controle',
                'Sistema de Roles',
                'Relatórios em tempo real',
                'Exportação Excel/PDF',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet para você e sua equipe',
                'Segurança avançada',
                'Otimização de performance + SEO técnico'
            ]
        },
        {
            'name': 'Sistema de Escola/Curso',
            'price': 4799.90,
            'features': [
                '20% off para instituições públicas',
                'Área do aluno',
                'Portal do professor',
                'Domínio .com.br gratis por 1 ano',
                'Gestão de matrículas',
                'Sistema de avaliação',
                'Sistema de notas',
                'Sistema de acompanhamento de frequência',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet para você e sua equipe',
                'Segurança avançada',
                'Otimização de performance + SEO técnico'
            ]
        },
        {
            'name': 'Plataforma / Rede Social Personalizada',
            'price': 9799.90,
            'features': [
                'Design personalizado',
                'Postagens e feeds',
                'Configurações avançadas para usuários',
                'Integração de chat em tempo real',
                'Painel de controle para moderação, administração e gestão',
                'Sistema de segurança avançado e robusto',
                'Sistema de notificação em tempo real',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet para você e sua equipe',
                'Otimização de performance + SEO técnico'
            ]
        },
        {
            'name': 'Sistema com IA integrada',
            'price': 1599.90,
            'features': [
                'Chatbot',
                'Automações',
                'Suporte automático',
                'Integração com WhatsApp, Telegram e/ou Discord',
                'Domínio .com.br gratis por 1 ano caso aplicável',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet para você e sua equipe',
                'Segurança avançada',
                'Otimização de performance + SEO técnico'
            ]
        },
        {
            'name': 'CRM Simples para Pequenas Empresas',
            'price': 3499.90,
            'features': [
                'Gestão de leads e clientes',
                'Pipeline de vendas visual',
                'Integração com WhatsApp Business',
                'Notificações automáticas',
                'Relatórios de conversão',
                'Painel administrativo',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet',
                'Segurança avançada',
                'Otimização de performance'
            ]
        },
        {
            'name': 'Plataforma de Membresia / Assinaturas',
            'price': 5299.90,
            'features': [
                'Área de membros com login',
                'Planos de assinatura (mensal/anual)',
                'Pagamento recorrente (Pix + cartão)',
                'Conteúdo exclusivo (vídeos, arquivos, posts)',
                'Comunidade / fórum interno',
                'Painel administrativo completo',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet',
                'Segurança avançada',
                'Otimização de performance'
            ]
        },
        {
            'name': 'Dashboard Analítico Personalizado',
            'price': 2899.90,
            'features': [
                'Dashboards em tempo real (vendas, usuários, métricas)',
                'Gráficos interativos (DAU/MAU, funil de vendas, etc.)',
                'Exportação Excel/PDF',
                'Integração com Google Analytics e APIs externas',
                'Alertas automáticos',
                'Painel administrativo',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet',
                'Segurança avançada'
            ]
        },
        {
            'name': 'Sistema de Ticketing / Helpdesk',
            'price': 2599.90,
            'features': [
                'Gestão de tickets e suporte',
                'Base de conhecimento (FAQ)',
                'Notificações por email e WhatsApp',
                'Sistema de roles e permissões',
                'Relatórios de desempenho do suporte',
                'Painel administrativo',
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Código fonte 100% entregue + documentação',
                'Treinamento de 1h via Google Meet',
                'Segurança avançada',
            ]
        },
        {
            'name': 'Manutenção e Suporte Mensal',
            'price': "199.90/mês",
            'features': [
                'Servidor gratis durante o período',
                'Solução de bugs e erros',
                'Manutenção básica para funcionamento adequado',
                'Prevenção de falhas identificadas pelo Desenvolvedor',
                'Atualizações de segurança críticas',
                'Atualizações mínimas de design, funcionalidades e conteúdo',
                'Importante: Esse serviço é gratuito durante 1 ano em caso de desenvolvimento de algum dos produtos anteriores. Após esse prazo, serviços de manutenção poderão ser contratados separadamente mediante novo orçamento.'
            ]
        }
    ]
    return render_template('index.html', projects=projects, skills=skills, services=services, str=str)


# ─────────────────────────────────────────────
# Contact
# ─────────────────────────────────────────────
@app.route('/send-message', methods=['POST'])
def send_message():
    token = request.form.get("cf-turnstile-response", "")
    if not token:
        flash("Captcha ausente.", "error")
        return redirect(url_for("login"))
    
    if not verify_turnstile(token):
        flash("Verificação de segurança falhou. Tente novamente.", "error")
        return redirect(url_for("login"))
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        if not all([name, email, subject, message]):
            flash('Por favor, preencha todos os campos.', 'error')
            return redirect(url_for('index', _anchor='contact'))
        send_email(
            to_email=SENDER_EMAIL,
            to_name=SENDER_NAME,
            subject=f"Contato desde o portfólio: {subject}",
            html_content=f"""
            <p><strong>Nome:</strong> {name}</p>
            <p><strong>E-mail:</strong> {email}</p>
            <p><strong>Assunto:</strong> {subject}</p>
            <p><strong>Mensagem:</strong><br>{message}</p>
            """
        )
        flash('Mensagem enviada com sucesso!', 'success')
    except Exception as e:
        logging.error(f"Erro enviando o e-mail: {str(e)}")
        flash('Um erro ocorreu durante o envio da sua mensagem.', 'error')
    return redirect(url_for('index', _anchor='contact'))


# ─────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = request.form.get("cf-turnstile-response", "")
        if not token:
            flash("Captcha ausente.", "error")
            return redirect(url_for("login"))
        if not verify_turnstile(token):
            flash("Verificação de segurança falhou. Tente novamente.", "error")
            return redirect(url_for("login"))
        email = request.form.get('email')
        if User.find_by_email(email) is None:
            flash('E-mail inválido', 'error')
            return redirect(url_for('login'))
        code = VerificationCode.create(email)
        send_email(
            to_email=email,
            to_name=User.find_by_email(email).username,
            subject="Seu código de verificação",
            html_content=f"""
            <p>Seu código de verificação do portfólio é:</p>
            <h2 style="letter-spacing:4px">{code}</h2>
            <p>Válido por 3 minutos.</p>
            """
        )
        flash('Código de verificação enviado.', 'success')
        return redirect(url_for('verify_code', email=email))
    return render_template('auth/login.html')


@app.route('/verify-code/<email>', methods=['GET', 'POST'])
def verify_code(email):
    if User.find_by_email(email) is None:
        abort(404)
    if request.method == 'POST':
        code = request.form.get('code')
        if VerificationCode.verify(email, code):
            user = User.find_by_email(email)
            if not user:
                user = User.create(email=email, is_admin=False)
            user.update_last_login()
            login_user(user, remember=True)
            return redirect(url_for('blog_dashboard'))
        flash('Código inválido ou expirado', 'error')
    return render_template('auth/verify_code.html', email=email)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ─────────────────────────────────────────────
# Blog
# ─────────────────────────────────────────────
@app.route('/blog')
def blog_list():
    categories = BlogCategory.get_all()
    category_id = request.args.get('category')
    if category_id:
        blogs = Blog.get_by_category(category_id, status='published')
    else:
        blogs = Blog.get_all(status='published')
    return render_template('blog/list.html', blogs=blogs, categories=categories)


@app.route('/blog/<blog_id>')
def blog_detail(blog_id):
    blog = Blog.get(blog_id)
    if not blog or (blog.status != 'published' and not current_user.is_authenticated):
        abort(404)
    content_html = markdown2.markdown(
        blog.content,
        extras=["fenced-code-blocks", "tables", "task_list", "strike", "break-on-newline"]
    )
    import re
    def fix_href(m):
        href = m.group(1)
        href = re.sub(r"^/(?!/)", "", href)
        if href and not href.startswith(("http", "mailto:", "#", "/")):
            href = "https://" + href
        return f'href="{href}"'
    content_html = re.sub(r'href="([^"]*?)"', fix_href, content_html)
    return render_template('blog/detail.html', blog=blog, content_html=content_html)


@app.route('/dashboard', methods=['GET'])
@login_required
def blog_dashboard():
    if User.find_by_email(current_user.email) is None:
        abort(403)
    blogs = Blog.get_all()
    categories = BlogCategory.get_all()
    return render_template('blog/dashboard.html', blogs=blogs, categories=categories)


@app.route('/blog/new', methods=['GET', 'POST'])
@login_required
def blog_create():
    if User.find_by_email(current_user.email) is None:
        abort(403)
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        if not category_id:
            flash('Por favor, selecione uma categoria.', 'error')
            categories = BlogCategory.get_all()
            return render_template('blog/editor.html', categories=categories)
        try:
            category = BlogCategory.get_by_id(category_id)
            if not category:
                raise ValueError("Categoria inválida")
            Blog.create(
                title=request.form.get('title'),
                content=request.form.get('content'),
                category_id=category_id,
                author_id=current_user.id,
                status=request.form.get('status', 'draft')
            )
            flash('Blog criado com sucesso!', 'success')
            return redirect(url_for('blog_dashboard'))
        except (ValueError, TypeError):
            flash('Categoria inválida!', 'error')
            categories = BlogCategory.get_all()
            return render_template('blog/editor.html', categories=categories)
    categories = BlogCategory.get_all()
    return render_template('blog/editor.html', categories=categories)


@app.route('/blog/edit/<blog_id>', methods=['GET', 'POST'])
@login_required
def blog_edit(blog_id):
    if User.find_by_email(current_user.email) is None:
        abort(403)
    blog = Blog.get(blog_id)
    if not blog:
        abort(404)
    if request.method == 'POST':
        blog.title = request.form.get('title')
        blog.content = request.form.get('content')
        blog.category_id = request.form.get('category_id')
        blog.status = request.form.get('status', 'draft')
        blog.save()
        flash('Blog atualizado com sucesso!', 'success')
        return redirect(url_for('blog_dashboard'))
    categories = BlogCategory.get_all()
    return render_template('blog/editor.html', blog=blog, categories=categories)


# ─────────────────────────────────────────────
# Terms
# ─────────────────────────────────────────────
@app.route('/terms')
def terms():
    return render_template('terms.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)