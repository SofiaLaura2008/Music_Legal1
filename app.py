import os

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "musicaseartistas.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class Musica(db.Model):
    nome = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    artista_nome = db.Column(db.String(80), db.ForeignKey('artista.nome'), nullable=True) 

    def __repr__(self):
        return "<Nome: {}>".format(self.nome)


class Artista(db.Model):
    nome = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    nacionalidade = db.Column(db.String(80))
    idade = db.Column(db.Integer)
    musicas = db.relationship('Musica', backref='artista', lazy=True)

with app.app_context():
    db.create_all() 

#Músicas
@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            nome_musica = request.form.get("nome")
            artista_nome = request.form.get("artista")  
            artista = Artista.query.filter_by(nome=artista_nome).first()  
            musica = Musica(nome=nome_musica, artista=artista)  
            db.session.add(musica)
            db.session.commit()
        except Exception as e:
            print("Falha em adicionar esta música")
            print(e)

    musicas = Musica.query.all()
    artistas = Artista.query.all()
    return render_template("index.html", musicas=musicas, artistas=artistas)



@app.route("/atualizar", methods=["POST"])
def atualizar():
    try:
        NovoNome = request.form.get("nomeNovo")
        NomeAntigo = request.form.get("nomeAntigo")
        musica = Musica.query.filter_by(nome=NomeAntigo).first()
        musica.nome = NovoNome
        db.session.commit()
    except Exception as e:
        print("Não foi possível atualizar o nome da música")
        print(e)
    return redirect("/")

@app.route("/deletar", methods=["POST"])
def deletar():
    nome = request.form.get("nome")
    musica = Musica.query.filter_by(nome=nome).first()
    if musica:
        db.session.delete(musica)
        db.session.commit()
    return redirect("/")


#Artistas
@app.route('/criar', methods=["GET", "POST"])
def criar():
    if request.method == "POST":
        try:
            nome_artista = request.form.get("nome")
            artista = Artista(nome=nome_artista)
            db.session.add(artista)
            db.session.commit()
        except Exception as e:
            print("Falha em adicionar este artista")
            print(e)

    musicas = Musica.query.all()
    artistas = Artista.query.all() 
    return render_template("index.html", musicas=musicas, artistas=artistas)  
    
@app.route("/alterar", methods=["POST"])
def alterar():
    try:
        NovoNome = request.form.get("nomeNovo")
        NomeAntigo = request.form.get("nomeAntigo")
        artista = Artista.query.filter_by(nome=NomeAntigo).first()
        artista.nome = NovoNome
        db.session.commit()
    except Exception as e:
        print("Não foi possível atualizar o nome do artista")
        print(e)
    return redirect("/")

@app.route("/apagar", methods=["POST"])
def apagar():
    nome = request.form.get("nome")
    artista = Artista.query.filter_by(nome=nome).first()
    if artista:
        db.session.delete(artista)
        db.session.commit()
    return redirect("/")

@app.route("/informacoes/<nome>", methods=["GET"])
def informacoes(nome):
    artista = Artista.query.filter_by(nome=nome).first()
    if not artista or not artista.nacionalidade or not artista.idade:
        return redirect(f"/adicionar_informacoes/{nome}")
    
    musicas = Musica.query.filter_by(artista_nome=artista.nome).all()  
    return render_template("informacoes.html", artista=artista, musicas=musicas)


@app.route("/adicionar_informacoes/<nome>", methods=["GET", "POST"])
def adicionar_informacoes(nome):
    artista = Artista.query.filter_by(nome=nome).first()
    if request.method == "POST":
        artista.nacionalidade = request.form.get("nacionalidade")
        artista.idade = request.form.get("idade")
        db.session.commit()
        return redirect(f"/informacoes/{nome}")
    
    return render_template("adicionar_informacoes.html", artista=artista)
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)    