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

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
                'android': 'play.google.com/store/apps/details?id=com.koffeedevs.artkoffee'
            },
            'tech': ['HTML', 'CSS', 'MongoDB', 'Flask-SocketIO', 'Python', 'JavaScript', 'TailwindCSS', 'Bootstrap', 'JQuery'],
            'images': [
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/49ab5c7c-d4ca-4f3d-649f-47b439b19600/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/e5ac26c0-3258-4e11-53dc-d38590f46200/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/bcd76b07-f789-4821-8b9d-6c2905bd0600/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/c32f46b3-63ae-4551-d821-e5f82674b200/public'
            ]
        },
        {
            'name': 'Pousadas Casa Do Ivo',
            'description': 'Site oficial de uma rede de pousadas no oeste do Pará.',
            'tech': ['HTML', 'CSS', 'JavaScript', 'PHP'],
            'links': {'web': 'casadoivo.com.br'},
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
            'tech': ['HTML', 'CSS', 'JavaScript', 'PHP'],
            'links': {'web': 'hackatur.org'},
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
            'tech': ['HTML', 'CSS', 'JavaScript', 'PHP'],
            'links': {'web': 'riohacks.com.br'},
            'images': [
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/1ae5ffc1-c76f-45d2-4593-ed4f1f171300/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/d13af3c3-ea5c-4a06-3605-9cace6e81100/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/05d0ff50-9ace-4680-0c64-869998ddc400/public'
            ]
        },
        {
            'name': 'ManicScript',
            'description': 'Uma linguagem de programação espanhola criada como um projeto paródia.',
            'links': {'web': 'manic-script.replit.app'},
            'tech': ['Python', 'HTML', 'CSS', 'JavaScript', 'Bootstrap'],
            'images': [
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/d050d92c-344d-4ed8-b46b-ba3a497f7100/public'
            ]
        },
        {
            'name': 'PolarMind',
            'description': 'Web and Android app for mood tracking for bipolar disorder.',
            'links': {'web': 'app.polarmind.org'},
            'tech': ['HTML', 'CSS', 'JavaScript', 'MongoDB', 'Flask', 'Python'],
            'images': [
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/1f55ee7e-6dc5-4d90-3a53-2f3a52bc2000/public'
            ]
        },
        {
            'name': 'AriaMail',
            'description': 'Servidor seguro de e-mail para envio, recebimento e gerenciamento de e-mails com dominio do art-koffee.com.',
            'links': {'web': 'ariamail.art-koffee.com'},
            'tech': ['Python', 'Flask', 'MongoDB', 'HTML', 'CSS', 'JavaScript', 'Bootstrap', 'Scrypt Hashing', 'SMTP', 'IMAP', 'POP3', 'DNS', 'SSL', 'TLS', 'Mailgun'],
            'images': [
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/5790fff8-4c5f-4373-5d01-4cda1d9d1100/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/f7edfa65-1e36-488f-525a-236e10869300/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/5fd34258-6d73-4a5a-33f5-a132ed982c00/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/c932e4af-af30-42e1-f5c4-6217b36aca00/public',
                'https://imagedelivery.net/yaYNv-wtO5mXyEhI13Elfg/306ebad2-6c22-444d-18a7-1be46651b700/public'
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
                'Domínio .com.br gratis por 1 ano',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Integração com Google Analytics Gratuitamente'
            ]
        },
        {
            'name': 'Site Institucional Básico',
            'price': 2399.90,
            'features': [
                'Design personalizado',
                'Até 5 páginas',
                'Blog integrado',
                'Painel administrativo',
                'Servidor por 1 ano',
                'Banco de dados gratuito por 1 ano',
                'Suporte por 1 ano'
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
                'Servidor por 1 ano',
                'Banco de dados gratuito por 1 ano',
                'Suporte por 1 ano'
            ]
        },
        {
            'name': 'E-commerce Completo',
            'price': 2645.50,
            'features': [
                'Catálogo de produtos + carrinho de compras + checkout',
                'Gateway de pagamento',
                'Gestão de estoque',
                'Domínio .com.br gratis por 1 ano',
                'Painel administrativo',
                'Servidor por 1 ano',
                'Suporte por 1 ano',
                'Integração com Google Analytics + Stripe Gratuitamente'
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
                'Servidor por 1 ano',
                'Suporte por 1 ano',
            ]
        },
        {
            'name': 'Sistema de Delivery (Android)',
            'price': 5199.90,
            'features': [
                'Design personalizado',
                'Domínio .com.br gratis por 1 ano',
                'App android para clientes',
                'Painel para restaurantes',
                'Rastreamento em tempo real',
                'App android para entregadores',
                'Servidor por 1 ano',
                'Suporte por 1 ano'
            ]
        },
        {
            'name': 'Sistema de Delivery (iOS)',
            'price': 5799.90,
            'features': [
                'Design personalizado',
                'Domínio .com.br gratis por 1 ano',
                'App iOS para clientes',
                'Painel para restaurantes',
                'Rastreamento em tempo real',
                'App iOS para entregadores',
                'Servidor por 1 ano',
                'Suporte por 1 ano'
            ]
        },
        {
            'name': 'Sistema de Delivery (Android + iOS)',
            'price': 7347.15,
            'features': [
                '10% off - Preço original: R$ 8.163,50',
                'Design personalizado',
                'Domínio .com.br gratis por 1 ano',
                'App iOS + Android para clientes',
                'Painel para restaurantes',
                'Rastreamento em tempo real',
                'App iOS + Android para entregadores',
                'Servidor por 1 ano',
                'Suporte por 1 ano'
            ]
        },
        {
            'name': 'Sistema de Reservas Hoteleiras',
            'price': 3599.90,
            'features': [
                'Gestão de quartos',
                'Sistema de pagamento',
                'Área do hóspede',
                'App móvel incluso',
                'Servidor por 1 ano',
                'Suporte por 1 ano'
            ]
        },
        {
            'name': 'Aplicativo Mobile Completo',
            'price': 5329.90,
            'features': [
                'Domínio .com.br gratis por 1 ano',
                'Android & iOS',
                'Design personalizado',
                'Backend incluso',
                'Painel de controle',
                'Servidor por 1 ano',
                'Suporte por 1 ano'
            ]
        },
        {
            'name': 'Sistema ERP',
            'price': 5999.99,
            'features': [
                'Sistema de gerenciamento de estoque',
                'Domínio .com.br gratis por 1 ano',
                'Gestão financeira',
                'Controle de estoque',
                'Recursos humanos',
                'Relatórios avançados',
                'Painel de controle',
                'Sistema de Roles',
                'Servidor por 1 ano',
                'Suporte por 1 ano'
            ]
        },
        {
            'name': 'Sistema de Escola/Curso',
            'price': 4700.00,
            'features': [
                '20% off para instituições públicas',
                'Área do aluno',
                'Portal do professor',
                'Gestão de matrículas',
                'Sistema de avaliação',
                'Sistema de notas',
                'Sistema de acompanhamento de frequência',
                'Servidor por 1 ano',
                'Suporte por 1 ano'
            ]
        }
    ]
    return render_template('index.html', projects=projects, skills=skills, services=services)


# ─────────────────────────────────────────────
# Contact
# ─────────────────────────────────────────────
@app.route('/send-message', methods=['POST'])
def send_message():
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
            <p>Válido por 15 minutos.</p>
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
    content_html = markdown2.markdown(blog.content)
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