# 🏦 Sistema Bancário & API REST (Banco Brasil)

> **Status do Projeto:** 🚧 Em desenvolvimento

Sistema de gerenciamento bancário desenvolvido em Python para consolidar fundamentos de engenharia de software, arquitetura modular, persistência de dados relacionais, exposição de APIs REST e testes automatizados.

---

## 🚀 Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Framework Web:** FastAPI & Uvicorn
* **Banco de Dados:** SQLite3
* **Testes Automatizados:** Pytest & Unittest
* **Versionamento:** Git & GitHub

---

## ⚙️ Funcionalidades Principais

* Criação e gerenciamento de contas bancárias utilizando Programação Orientada a Objetos (POO).
* Operações financeiras básicas (depósito, saque, consulta de saldo e extrato) com validação de regras de negócio.
* Persistência de dados em banco relacional SQLite com módulo de conexão isolado.
* Endpoints RESTful estruturados com FastAPI para integração externa.

---

## 🏗️ Arquitetura e Boas Práticas Aplicadas

* **Isolamento de Conexão:** A conexão com o banco de dados SQLite foi desacoplada em um módulo independente para evitar importações circulares e facilitar a manutenção.
* **Ambiente de Testes Isolado:** Os testes automatizados utilizam manipulação de arquivos (`os`) para criar e destruir bancos de dados temporários a cada execução, garantindo que a base principal não seja poluída.

---

## 🛠️ Como Executar o Projeto Localmente
### 1. Clone o repositório
```bash
git clone https://github.com/CarlosEGL01/banco-brasil
cd banco-brasil

```

### 2. Crie e ative um ambiente virtual (Opcional, mas recomendado)
```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install fastapi uvicorn pytest
```

### 4. Inicie o servidor da API
> **Nota:** O repositório já inclui o arquivo `banco.db` pré-configurado com a estrutura de tabelas necessária para execução imediata.

```bash
python -m uvicorn api:app --reload
```

Acesse a documentação interativa automática da API no navegador em:
`[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`

---

## 🧪 Como Rodar os Testes Automatizados

Para executar a suíte de testes com o Pytest:

```bash
pytest -v
```

---

## 👨‍💻 Autor

Desenvolvido por **Carlos Eduardo Gutierrez Lezama**  
[LinkedIn](https://www.linkedin.com/in/carlos-eduardo-gutierrez-lezama-a5ba323ab) | [GitHub](https://github.com/CarlosEGL01)