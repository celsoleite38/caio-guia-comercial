# Guia Comercial - Django

Um sistema moderno e elegante de guia comercial local com design futurista, desenvolvido em Django com HTML, CSS e Bootstrap 5.

## 🚀 Características

- **Design Futurista**: Interface moderna com gradientes, animações e efeitos glassmorphism
- **Listagem de Anúncios**: Separação clara entre anúncios pagos (destaque) e gratuitos
- **Busca e Filtros**: Busca por nome/descrição e filtro por categorias
- **Paginação**: Navegação eficiente entre anúncios
- **Cadastro de Anúncios**: Formulário completo com upload de imagem
- **Painel Administrativo**: Gerenciamento de anúncios, aprovação/rejeição, marcação como pago
- **Sistema de Categorias**: Gerenciamento de categorias de negócios
- **Responsividade**: Totalmente responsivo para mobile e desktop
- **SQLite**: Banco de dados leve e fácil de usar

## 📋 Requisitos

- Python 3.8+
- Django 6.0+
- Pillow (para processamento de imagens)
- Django Crispy Forms
- Bootstrap 5

## 🔧 Instalação

1. **Clone ou extraia o projeto:**
```bash
cd guia_comercial_django_v2
```

2. **Crie e ative o ambiente virtual:**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Execute as migrations:**
```bash
python manage.py migrate
```

5. **Crie um superusuário:**
```bash
python manage.py createsuperuser
```

6. **Inicie o servidor:**
```bash
python manage.py runserver
```

7. **Acesse a aplicação:**
- Site público: http://localhost:8000/
- Painel admin: http://localhost:8000/admin/
- Login admin: http://localhost:8000/accounts/login/

## 📁 Estrutura do Projeto

```
guia_comercial_django_v2/
├── guia_comercial/          # Configurações do projeto
│   ├── settings.py          # Configurações Django
│   ├── urls.py              # URLs principais
│   └── wsgi.py
├── listings/                # App principal
│   ├── models.py            # Models: Category, Listing, AdminLog
│   ├── views.py             # Views e lógica
│   ├── forms.py             # Formulários
│   ├── urls.py              # URLs do app
│   └── migrations/
├── templates/               # Templates HTML
│   ├── base.html            # Template base com design futurista
│   ├── accounts/
│   │   └── login.html
│   └── listings/
│       ├── home.html        # Página inicial
│       ├── listing_detail.html
│       ├── create_listing.html
│       ├── admin_dashboard.html
│       ├── admin_listings.html
│       └── admin_categories.html
├── static/                  # Arquivos estáticos (CSS, JS)
├── media/                   # Imagens de anúncios
└── db.sqlite3               # Banco de dados SQLite
```

## 🎨 Design

O design futurista utiliza:
- **Paleta de Cores**: Cyan (#00d4ff), Magenta (#ff006e), fundo escuro (#0a0e27)
- **Animações**: Transições suaves, hover effects, efeitos de pulso
- **Glassmorphism**: Efeitos de vidro fosco com backdrop-filter
- **Tipografia**: Font Inter para interface moderna
- **Responsividade**: Mobile-first com Bootstrap 5

## 🔐 Autenticação

- Login de administrador protegido
- Apenas usuários com `is_staff=True` podem acessar o painel admin
- Sistema de permissões integrado do Django

## 📊 Modelos de Dados

### Category
- `name`: Nome da categoria
- `slug`: URL amigável
- `icon`: Emoji ou ícone
- `description`: Descrição

### Listing
- `business_name`: Nome do negócio
- `description`: Descrição
- `category`: Categoria (FK)
- `phone`, `whatsapp`, `email`, `address`: Contatos
- `logo`: Imagem
- `status`: pending/approved/rejected
- `is_paid`: Anúncio em destaque
- `owner_name`, `owner_email`: Informações do anunciante
- `views`: Contador de visualizações

### AdminLog
- `admin`: Usuário admin
- `listing`: Anúncio (FK)
- `action`: Ação realizada
- `reason`: Motivo (para rejeições)

## 🎯 Funcionalidades Principais

### Página Inicial
- Listagem de anúncios aprovados
- Anúncios pagos em destaque (com badge especial)
- Anúncios gratuitos com paginação
- Busca por nome/descrição
- Filtro por categorias
- Botões de contato direto (WhatsApp, telefone)

### Cadastro de Anúncios
- Formulário completo com validação
- Upload de imagem com validação (tipo e tamanho)
- Preview de imagem
- Status inicial: pendente (aguardando aprovação)

### Detalhes do Anúncio
- Visualização completa
- Botões de contato (WhatsApp, telefone, email)
- Sistema de compartilhamento (WhatsApp, Facebook, Twitter, copiar link)
- Contador de visualizações
- Anúncios relacionados (mesma categoria)

### Painel Administrativo
- Dashboard com estatísticas
- Gerenciamento de anúncios (aprovar, rejeitar, marcar como pago)
- Gerenciamento de categorias
- Auditoria de ações

## 🚀 Deploy

Para deploy em produção:

1. Configure `DEBUG = False` em `settings.py`
2. Configure `ALLOWED_HOSTS` com seu domínio
3. Configure um banco de dados PostgreSQL/MySQL
4. Use um servidor WSGI como Gunicorn
5. Configure um reverse proxy como Nginx
6. Use SSL/TLS com Let's Encrypt

## 📝 Licença

Este projeto é fornecido como está para uso educacional e comercial.

## 👨‍💻 Suporte

Para dúvidas ou problemas, entre em contato com o desenvolvedor.

---

**Desenvolvido com ❤️ em Django**
