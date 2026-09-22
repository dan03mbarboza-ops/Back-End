from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS
from pydantic import BaseModel

info = Info(title="API Biblioteca", version="1.0.0")
app = OpenAPI(
    __name__,
    info=info,
    doc_prefix='/docs',
    doc_url='/openapi.json'
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)
CORS(app)

# MODELOS DE BANCO DE DADOS


class Biblioteca(db.Model):
    __tablename__ = 'livros'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    genero = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "genero": self.genero
        }


# DEFININDO TAGS
home = Tag(name="Documentação", description="Seleção de documentação: Swagger")
livros = Tag(name="Livros",
             description="Lista, adição, pesquisa e remoção de livros à base")


class LivroPath(BaseModel):
    livro_id: int


class LivroBody(BaseModel):
    titulo: str
    autor: str
    genero: str

# ROTAS (ENDPOINTS DA API)


@app.get('/livros', tags=[livros])
def listar_livros():
    """
    Lista todos os livros cadastrados no banco  de dados

    tags: Livros
    responses:
        200:
          description: Livros carregados com sucesso
        500:
          description: Erro no servidor
    """

    try:
        livros = Biblioteca.query.all()
        livros_data = []

        for livro in livros:
            livro_dict = livro.to_dict()
            livros_data.append(livro_dict)

        return jsonify(livros_data), 200
    except Exception as e:
        return jsonify(f'Erro ao listar os Livros: {str(e)}'), 500


@app.delete('/livros/<int:livro_id>', tags=[livros])
def deletar(path: LivroPath):
    """
    Deleta um livro do Banco de Dados, correspondente ao ID informado

    tags: Livros
    responses:
        200:
            description: Livro deltado com sucesso
        500:
            description: Erro no servidor
    """

    try:
        livro_id = path.livro_id
        livro = Biblioteca.query.get_or_404(livro_id)

        db.session.delete(livro)
        db.session.commit()

        return jsonify({'message': 'Livro deletado com sucesso'}), 200
    except Exception as e:
        return jsonify(f'Erro ao deletar: {str(e)}'), 500


@app.post('/livros', tags=[livros])
def cadastrar_livro(body: LivroBody):
    """ 
    Cadastra um novo livro no Banco de Dados

    tags: Livros
    responses:
        201:
            description: Livro cadastrado com sucesso
        500:
            description: Erro no servidor

    """
    novo_livro = Biblioteca(
        titulo=body.titulo,
        autor=body.autor,
        genero=body.genero,
    )

    db.session.add(novo_livro)
    db.session.commit()

    return jsonify(novo_livro.to_dict()), 201


@app.get('/livros/<int:livro_id>', tags=[livros])
def pesquisar_livros_id(path: LivroPath):
    """
    Retorna um livro correspondente ao ID pesquisado

    tags: Livros
    responses:
        200:
            description: Livro localizado com sucesso
        500:
            description: Erro no servidor
    """
    try:
        livro_id = path.livro_id
        livro = Biblioteca.query.get_or_404(livro_id)
        return jsonify(livro.to_dict()), 200
    except Exception as e:
        return jsonify(f'Erro ao localizar o livro pesquisado: {str(e)}'), 500


if __name__ == '__main__':
    # Cria tabelas do banco de dados se não existirem
    with app.app_context():
        db.create_all()

    # Inicia servidor em modo debug
    app.run(debug=True, host='127.0.0.1', port=5000)
