---
description: Exibe o plano de estudos de uma trilha de tecnologia
argument-hint: <tecnologia>
---

O usuário quer ver o plano de estudos da trilha de **$1**.

Leia o arquivo `data/trilhas.json` que está na raiz deste projeto e localize a chave correspondente à tecnologia "$1" (a busca deve ser case-insensitive, então "python", "Python" e "PYTHON" devem funcionar).

Se a tecnologia for encontrada, apresente o plano de estudos formatado da seguinte forma:

---

# 🗺️ Trilha de $1

> {descricao da trilha}  
> **Nível:** {nivel}

## 📚 Módulos

Para cada módulo, exiba:

### Módulo {numero} — {titulo}

- Liste cada tópico com um bullet point `•`

---

Ao final, adicione uma seção motivacional curta (2-3 linhas) encorajando o usuário a começar pela trilha.

Se a tecnologia **não for encontrada** no arquivo, liste de forma amigável quais trilhas estão disponíveis no arquivo `data/trilhas.json` e pergunte ao usuário qual delas deseja explorar.
