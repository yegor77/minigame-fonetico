# 🎮 Jogo de Consciência Fonológica

Como pai, percebi que meu filho precisava de apoio extra no desenvolvimento da consciência fonológica — especialmente na diferenciação entre D/T e M/N. Os cadernos tradicionais estavam deixando as atividades monótonas e cansativas.

A solução? Gamificar o aprendizado! 🚀

Transformei os exercicios repetitivos em um jogo python, aproveitando para aprender mais sobre, interativo onde cada acerto é comemorado pelo Messi feliz ⚽✨ e cada erro vem com aquele "Messi chorando" que é tão icônico. Resultado: muito mais engajamento, diversão e, claro, aprendizado de verdade.

Este projeto nasceu da necessidade real de tornar a fonoaudiologia mais atrativa — automatizando o que antes era papel e caneta, e adicionando feedback visual que realmente motiva.

Deixo aqui meus créditos a minha querida Esposa, professora, que sempre me apoia com as suas lindas idéias (e eu que me vire depois hahaha).

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Ativo-success)

## 📸 Demonstração

![Menu Principal](main/screenshoots/menu.PNG)
*Tela de seleção de modo de jogo*

![Gameplay ACERTO](main/screenshoots/acerto_mg_fonetico.png)
*Interface durante o jogo*

![Gameplay ERRO](main/screenshoots/erro_mg_fonetico.png)
*Interface durante o jogo*

---

## 🎯 Funcionalidades

- ✅ **Dois modos de jogo**: D×T e M×N
- ✅ **100 palavras por modo** com posições variadas da letra alvo
- ✅ **Feedback visual animado** com GIFs do Messi (acerto/erro)
- ✅ **Sistema de pontuação** em tempo real com percentual
- ✅ **Interface escalável** (2x para melhor visualização)
- ✅ **Validação de entrada** inteligente
- ✅ **Testes unitários** integrados
- ✅ **Logging detalhado** para debug

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia        | Uso                           |
|-------------------|-------------------------------|
| **Python 3.8+**   | Linguagem base                |
| **Tkinter**       | Interface gráfica             |
| **Pillow (PIL)**  | Manipulação de GIFs animados  |
| **Type Hints**    | Código mais robusto           |
| **Dataclasses**   | Modelagem de dados            |

---

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes)

## 🎮 Como Usar

1. **Inicie o jogo** executando `python main.py`
2. **Selecione o modo**:
   - **D × T**: Diferenciação entre D e T
   - **M × N**: Diferenciação entre M e N
3. **Complete as palavras** digitando a letra que falta
4. **Pressione Enter** ou clique em "Verificar"
5. **Acompanhe sua evolução** no placar
6. **Volte ao menu** a qualquer momento

### Atalhos
- `Enter`: Verificar resposta / Próxima palavra
- `Escape`: Voltar ao menu (futuro)

---

## 🧪 Testes

O projeto inclui testes unitários automáticos:
**Cobertura de testes:**
- ✅ Mascaramento de palavras
- ✅ Validação de entrada
- ✅ Verificação de respostas
- ✅ Construção de desafios

---

## 📊 Banco de Palavras

### Modo D×T
- 50 palavras com **T**
- 50 palavras com **D**
- Posições variadas: início, meio, fim

### Modo M×N
- 50 palavras com **M**
- 50 palavras com **N**
- Contextos diversos (vogais, consoantes)

**Total: 200 palavras únicas**

---

## 🎨 Design e UX

- **Cores acessíveis** para crianças
- **Fontes grandes** (Comic Sans MS / Arial)
- **Feedback claro** (✅ verde / ❌ vermelho)
- **Animações motivadoras** (GIFs do Messi)
- **Interface minimalista** sem distrações

---

## 🐛 Troubleshooting

### GIFs não aparecem
- Verifique sua conexão com a internet
- Os GIFs são baixados de URLs externas
- Logs no console indicam falhas

### Problema de escala DPI
- O jogo tenta ajustar automaticamente
- Em caso de falha, redimensione a janela manualmente

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**Douglas**

- GitHub: [@yegor77](https://github.com/yegor77)
- LinkedIn: [@douglasfch](https://www.linkedin.com/in/douglasfch/)
