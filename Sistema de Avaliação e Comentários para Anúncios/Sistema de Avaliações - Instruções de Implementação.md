# Sistema de Avaliações - Instruções de Implementação

Este documento descreve como implementar o novo sistema de avaliações (ratings) no projeto Caio Guia Comercial.

## Arquivos Modificados

### 1. **listings/models.py**
- ✅ Adicionado import de `MinValueValidator` e `MaxValueValidator`
- ✅ Adicionados métodos `average_rating` e `total_ratings` ao modelo `Listing`
- ✅ Adicionado novo modelo `Rating` para armazenar avaliações

### 2. **listings/admin.py**
- ✅ Importado modelo `Rating`
- ✅ Adicionada classe `RatingAdmin` para gerenciar avaliações no painel administrativo

### 3. **listings/urls.py**
- ✅ Importado módulo `rating_views`
- ✅ Adicionadas 3 novas rotas:
  - `anuncio/<int:listing_id>/avaliar/` - Criar/editar avaliação
  - `avaliacao/<int:rating_id>/deletar/` - Deletar avaliação
  - `api/anuncio/<int:listing_id>/avaliacoes/` - API JSON com avaliações

### 4. **templates/listings/listing_detail.html**
- ✅ Incluída seção de avaliações usando `{% include 'listings/ratings_section.html' %}`

## Arquivos Novos

### 1. **listings/rating_forms.py**
Formulário Django para criar/editar avaliações com validação de 200 caracteres.

### 2. **listings/rating_views.py**
Views para gerenciar avaliações:
- `create_rating()` - Criar ou atualizar avaliação
- `delete_rating()` - Deletar avaliação
- `listing_ratings()` - API JSON com avaliações

### 3. **templates/listings/create_rating.html**
Template para formulário de avaliação com:
- Seleção de estrelas (1-5)
- Campo de comentário (até 200 caracteres)
- Contador de caracteres em tempo real
- Suporte a edição de avaliações existentes

### 4. **templates/listings/ratings_section.html**
Componente de exibição de avaliações com:
- Média de estrelas
- Distribuição de avaliações por estrela
- Lista de comentários
- Opções de editar/deletar (para autor ou admin)

## Passos de Implementação

### Passo 1: Copiar os arquivos novos
```bash
# Copiar os arquivos criados para o projeto
cp listings/rating_forms.py /seu/projeto/listings/
cp listings/rating_views.py /seu/projeto/listings/
cp templates/listings/create_rating.html /seu/projeto/templates/listings/
cp templates/listings/ratings_section.html /seu/projeto/templates/listings/
```

### Passo 2: Atualizar os arquivos existentes
Os arquivos já foram modificados:
- `listings/models.py` - Modelo Rating adicionado
- `listings/admin.py` - RatingAdmin adicionado
- `listings/urls.py` - Rotas de ratings adicionadas
- `templates/listings/listing_detail.html` - Seção de ratings incluída

### Passo 3: Criar as migrações
```bash
python manage.py makemigrations listings
python manage.py migrate listings
```

### Passo 4: Testar a funcionalidade

1. **Acessar um anúncio aprovado**
   - Navegue até a página de detalhes de um anúncio
   - Você verá a seção de avaliações no final

2. **Criar uma avaliação**
   - Clique no botão "Avaliar"
   - Selecione de 1 a 5 estrelas
   - Adicione um comentário (opcional, até 200 caracteres)
   - Clique em "Enviar Avaliação"

3. **Editar uma avaliação**
   - Clique no botão "Avaliar" novamente
   - Modifique as estrelas e/ou comentário
   - Clique em "Atualizar Avaliação"

4. **Deletar uma avaliação**
   - Clique no botão "Deletar" na sua avaliação
   - Confirme a exclusão

5. **Painel Administrativo**
   - Acesse `http://localhost:8000/admin/`
   - Vá para "Avaliações" para gerenciar todas as avaliações

## Recursos Implementados

✅ **Sistema de Estrelas (1-5)**
- Validação no backend
- Seleção visual com ícones no frontend

✅ **Comentários (até 200 caracteres)**
- Validação de comprimento
- Contador em tempo real
- Campo opcional

✅ **Média de Avaliações**
- Calculada automaticamente
- Exibida com 1 casa decimal
- Atualizada em tempo real

✅ **Distribuição de Avaliações**
- Gráfico visual com barras de progresso
- Mostra quantidade de avaliações por estrela

✅ **Gerenciamento de Avaliações**
- Cada usuário pode avaliar um anúncio apenas uma vez
- Usuários podem editar suas avaliações
- Usuários e admins podem deletar avaliações
- Avaliações ordenadas por data (mais recentes primeiro)

✅ **Painel Administrativo**
- Listagem de todas as avaliações
- Filtro por número de estrelas
- Filtro por data
- Busca por nome do anúncio ou usuário

✅ **API JSON**
- Endpoint para obter avaliações de um anúncio
- Útil para integrações futuras

## Segurança

- ✅ Autenticação obrigatória para avaliar
- ✅ Validação de permissões (apenas autor ou admin podem deletar)
- ✅ Proteção CSRF em formulários
- ✅ Validação de entrada no backend
- ✅ Constraint de unicidade: um usuário por anúncio

## Customizações Futuras

Você pode facilmente customizar:

1. **Limite de caracteres**: Edite `max_length=200` em `Rating.comment`
2. **Número de estrelas**: Modifique os validadores `MinValueValidator(1), MaxValueValidator(5)`
3. **Permissões**: Ajuste as verificações em `rating_views.py`
4. **Estilo**: Customize o CSS nos templates
5. **Notificações**: Adicione emails quando um anúncio for avaliado

## Troubleshooting

### Erro: "No such table: listings_rating"
**Solução**: Execute as migrações:
```bash
python manage.py migrate listings
```

### Erro: "RatingForm not found"
**Solução**: Verifique se `rating_forms.py` está no diretório `listings/`

### Erro: "Template not found: listings/ratings_section.html"
**Solução**: Verifique se `ratings_section.html` está em `templates/listings/`

## Suporte

Para dúvidas ou problemas, consulte:
- Documentação do Django: https://docs.djangoproject.com/
- Repositório do projeto: https://github.com/celsoleite38/caio-guia-comercial
