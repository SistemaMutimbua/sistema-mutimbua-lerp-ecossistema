# 🌐 SistemaMutimbua

## Plataforma de Sistemas de Gestão Empresarial

O **SistemaMutimbua** é um ecossistema de sistemas de gestão empresarial desenvolvido para atender diferentes áreas de negócio, utilizando uma arquitetura modular, escalável e padronizada.

O principal produto do ecossistema é o **LERP – Lina Enterprise Resource Program**.

---

## 🧠 O que é o LERP?

**LERP** significa **Lina Enterprise Resource Program**.

É um conjunto de **programas de gestão (LP)** organizados em **sistemas de gerenciamento (SM)**, criados para administrar recursos, processos e operações de organizações públicas e privadas.

---

## 🧩 Estrutura de Codificação do LERP

O ecossistema segue um padrão interno de identificação:

- **LERP** → Lina Enterprise Resource Program  
- **LP** → LERP Program  
- **SM** → System Management  

📌 Formato:


Onde:
- `000X` → Identificação do sistema  
- `Y` → Versão do sistema  

---

## 📦 Sistemas do Ecossistema LERP

### 🔹 LP-SM0001/1 – LERP Água
Sistema de gestão para serviços de fornecimento de água.

**Principais funcionalidades:**
- Gestão de clientes
- Controle de consumo
- Mensalidades automáticas
- Pagamentos
- Relatórios financeiros

---

### 🔹 LP-SM0002/1 – LERP Escola
Sistema de gestão escolar e educacional.

**Principais funcionalidades:**
- Gestão de alunos
- Turmas e disciplinas
- Mensalidades
- Pagamentos
- Estado financeiro do aluno
- Relatórios administrativos

---

### 🔹 LP-SM0003/1 – LERP Multi Funcional
Sistema de gestão comercial multiuso.

**Áreas atendidas:**
- Farmácia
- Ferragem
- Bar
- Lojas em geral

**Principais funcionalidades:**
- Vendas
- Controle de estoque
- Caixa
- Pagamentos
- Relatórios financeiros

---

## 🛠️ Tecnologias Utilizadas

Os sistemas do **SistemaMutimbua / LERP** utilizam, de forma geral:

🌐 SistemaMutimbua
Plataforma de Sistemas de Gestão Empresarial

O SistemaMutimbua é um ecossistema de sistemas de gestão empresarial modular, escalável e padronizado, desenvolvido para diferentes áreas de negócio.

O principal produto do ecossistema é o LERP – Lina Enterprise Resource Program.

🧠 O que é o LERP?

LERP significa Lina Enterprise Resource Program.
É um conjunto de programas de gestão (LP) organizados em sistemas de gerenciamento (SM), criados para administrar recursos, processos e operações de organizações públicas e privadas.

🧩 Estrutura de Codificação do LERP

LERP → Lina Enterprise Resource Program

LP → LERP Program

SM → System Management

Formato:

LP-SM000X/Y


000X → Identificação do sistema

Y → Versão do sistema

📦 Sistemas do Ecossistema LERP
🔹 LERP Água
 – LP-SM0001/1

Sistema de gestão para serviços de fornecimento de água.

Funcionalidades:

Gestão de clientes

Controle de consumo

Mensalidades automáticas

Pagamentos

Relatórios financeiros

🔹 LERP Escola
 – LP-SM0002/1

Sistema de gestão escolar.

Funcionalidades:

Gestão de alunos

Turmas e disciplinas

Mensalidades

Pagamentos

Estado financeiro do aluno

Relatórios administrativos

🔹 LERP Multi Funcional
 – LP-SM0003/1

Sistema de gestão comercial para farmácia, ferragem, bar e lojas.

Funcionalidades:

Vendas

Controle de estoque

Caixa

Pagamentos

Relatórios financeiros

🛠️ Tecnologias Utilizadas

Backend: Python + Flask

Frontend: HTML, CSS, Bootstrap

ORM: SQLAlchemy

Banco de dados: SQLite

Relatórios: ReportLab

Controle de versão: Git & GitHub

🧱 Arquitetura

Estrutura modular por domínio (alunos, clientes, financeiro, etc.)

Separação clara entre rotas, modelos e serviços

Padronização entre todos os sistemas LERP

Preparado para crescimento e novas versões

🔐 Segurança e Boas Práticas

Dados sensíveis fora do versionamento

Uso de .env

Controle de acesso por módulos

Organização preparada para produção

🚀 Como clonar o repositório completo com submódulos

Para baixar o repositório principal e todos os LERP:

git clone --recurse-submodules https://github.com/SistemaMutimbua/sistema-mutimbua-lerp-ecossistema.git


Se você já clonou sem submódulos, atualize-os com:

git submodule update --init --recursive

Atualizando submódulos

Para atualizar um submódulo específico (ex: LERP Água):

cd LERP-vs.lp-sm0001-1
git pull origin main
cd ..
git add LERP-vs.lp-sm0001-1
git commit -m "Atualiza submódulo LERP Água"
git push


Repita para os outros submódulos conforme necessário.

🚧 Status do Projeto

🚀 Em desenvolvimento contínuo
Novos sistemas LERP e melhorias nos existentes estão em constante evolução.

👤 Autor

Jojo Mutimbua
Fundador e Desenvolvedor do SistemaMutimbua
Criador do LERP – Lina Enterprise Resource Program

📄 Licença

Uso interno, educacional e institucional.
Distribuição externa apenas mediante autor

