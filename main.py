from __future__ import annotations
import logging
import random
import tkinter as tk
from dataclasses import dataclass
from io import BytesIO
from typing import Dict, List, Optional, Tuple
from urllib.request import Request, urlopen
from PIL import Image, ImageSequence, ImageTk

# ============================ CONFIGURAÇÃO DE LOGGING ============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================ CONSTANTES DE CONFIGURAÇÃO ============================
# Validação de entrada POR MODO
VALID_LETTERS_DT: frozenset[str] = frozenset({"d", "t"})
VALID_LETTERS_MN: frozenset[str] = frozenset({"m", "n"})

# Escalamento de UI
SCALE: int = 2

# Fontes (escaladas)
FONT_TITLE: Tuple[str, int] = ("Comic Sans MS", 32 * SCALE, "bold")
FONT_WORD: Tuple[str, int] = ("Comic Sans MS", 24 * SCALE, "bold")
FONT_ENTRY: Tuple[str, int] = ("Arial", 20 * SCALE)
FONT_FEEDBACK: Tuple[str, int] = ("Comic Sans MS", 18 * SCALE)
FONT_CORRECT: Tuple[str, int] = ("Arial", 15 * SCALE)
FONT_SCORE: Tuple[str, int] = ("Arial", 13 * SCALE, "bold")
FONT_BTN: Tuple[str, int] = ("Arial", 16 * SCALE, "bold")
FONT_BTN_MENU: Tuple[str, int] = ("Arial", 20 * SCALE, "bold")

# Paddings (escalados)
PAD_Y_WORD: Tuple[int, int] = (15 * SCALE, 10 * SCALE)
PAD_Y_ENTRY: Tuple[int, int] = (10 * SCALE, 10 * SCALE)
PAD_Y_FEEDBACK: Tuple[int, int] = (8 * SCALE, 5 * SCALE)
PAD_Y_CORRECT: Tuple[int, int] = (5 * SCALE, 10 * SCALE)
PAD_Y_SCORE: Tuple[int, int] = (0, 10 * SCALE)
PAD_Y_BTN: Tuple[int, int] = (0, 15 * SCALE)
PADX_ENTRY: int = 6 * SCALE

# Dimensões
WIDTH_ENTRY: int = 4
GEOMETRY: str = "1000x800"

# Cores (acessibilidade infantil)
COLOR_BG: str = "#F0F8FF"  # Alice Blue
COLOR_SUCCESS: str = "#228B22"  # Forest Green
COLOR_ERROR: str = "#DC143C"  # Crimson
COLOR_NEUTRAL: str = "#2F4F4F"  # Dark Slate Gray

# GIFs
GIF_TIMEOUT: int = 8
GIF_TARGET_WIDTH: int = 380 * SCALE
GIF_MIN_DURATION: int = 50
GIF_URLS: Dict[str, str] = {
    "error": "https://media.tenor.com/yVSAY2fGmuAAAAAM/messi-cry-llanto.gif",
    "success": "https://media.tenor.com/AAt9-haXb-YAAAAM/argentina-messi.gif",
}

# Fallback: caminhos locais (se disponíveis)
GIF_PATHS: Dict[str, Optional[str]] = {
    "error": None,
    "success": None
}

# ============================ BANCO DE PALAVRAS ============================
WORDS_DT: List[Tuple[str, int]] = [
    # === LETRA T (50 palavras) ===
    ("teto", 0), ("tubo", 0), ("tigre", 0), ("trem", 0), ("torre", 0),
    ("trigo", 0), ("turma", 0), ("tempo", 0), ("tigela", 0), ("tomate", 0),
    ("tampa", 0), ("tocha", 0), ("trilha", 0), ("torrada", 0), ("tesouro", 0),
    ("telefone", 0), ("tijolo", 0), ("toalha", 0), ("teatro", 0), ("tapete", 0),
    ("patrulha", 2), ("moto", 2), ("voto", 2), ("foto", 2), ("luto", 2),
    ("rito", 2), ("rato", 2), ("chute", 3), ("fruto", 3), ("bruto", 3),
    ("cesto", 3), ("gesto", 3), ("nestor", 3), ("prestar", 4), ("questão", 4),
    ("futebol", 2), ("curtir", 3), ("partir", 3), ("sortear", 3), ("mentir", 3),
    ("contar", 3), ("prática", 4), ("frontal", 4), ("cristal", 4), ("brutal", 4),
    ("portal", 3), ("mortal", 3), ("eterno", 4), ("inventar", 5), ("formato", 5),
    # === LETRA D (50 palavras) ===
    ("dedo", 0), ("dente", 0), ("doce", 0), ("dono", 0), ("duro", 0),
    ("duplo", 0), ("duende", 0), ("dormir", 0), ("descer", 0), ("disco", 0),
    ("desejo", 0), ("detalhe", 0), ("desenho", 0), ("dentista", 0), ("dezena", 0),
    ("diploma", 0), ("domingo", 0), ("dourado", 0), ("docinho", 0), ("dócil", 0),
    ("poder", 2), ("ceder", 2), ("medir", 2), ("pedir", 2), ("surdez", 3),
    ("moldura", 3), ("mato", 3), ("Douglas", 0), ("pendente", 3), ("prudente", 4),
    ("condominio", 3), ("redor", 3), ("fedor", 3), ("suador", 4), ("orador", 4),
    ("quadro", 4), ("pedro", 2), ("vidro", 3), ("cedo", 2), ("surdo", 4),
    ("dinossauro", 0), ("modelo", 2), ("moderno", 2), ("médico", 2), ("código", 3),
    ("soldado", 3), ("cuidado", 4), ("estudar", 4), ("duvidar", 2), ("ordenar", 3),
]

WORDS_MN: List[Tuple[str, int]] = [
    # === LETRA M (50 palavras) ===
    ("mato", 0), ("mala", 0), ("mesa", 0), ("meia", 0), ("moeda", 0),
    ("muro", 0), ("mapa", 0), ("mimo", 0), ("mula", 0), ("monte", 0),
    ("cama", 2), ("gema", 2), ("remo", 2), ("toma", 2), ("lima", 2),
    ("rama", 2), ("fumo", 2), ("rima", 2), ("tema", 2), ("clima", 3),
    ("grama", 3), ("chama", 3), ("palma", 3), ("calma", 3), ("firma", 3),
    ("mate", 0), ("mania", 0), ("manga", 0), ("marco", 0), ("massa", 0),
    ("maior", 0), ("malha", 0), ("manso", 0), ("motor", 0), ("macio", 0),
    ("amar", 1), ("aroma", 3), ("pomar", 2), ("formar", 3), ("somar", 2),
    ("firme", 3), ("norma", 3), ("forma", 3), ("arma", 2), ("alma", 2),
    ("filma", 3), ("palmo", 3), ("termo", 3), ("gomo", 2), ("ramo", 2),
    # === LETRA N (50 palavras) ===
    ("nabo", 0), ("nada", 0), ("nave", 0), ("neto", 0), ("nora", 0),
    ("nota", 0), ("novo", 0), ("nuca", 0), ("ninho", 0), ("nervo", 0),
    ("cana", 2), ("pena", 2), ("lona", 2), ("dona", 2), ("zona", 2),
    ("cano", 2), ("pano", 2), ("plano", 3), ("mano", 2), ("sono", 2),
    ("cone", 2), ("pino", 2), ("sino", 2), ("vinho", 3), ("linha", 3),
    ("nome", 0), ("nunca", 0), ("navio", 0), ("nariz", 0), ("neve", 0),
    ("nuvem", 0), ("natal", 0), ("noite", 0), ("norte", 0), ("negro", 0),
    ("anão", 1), ("final", 3), ("sinal", 3), ("canal", 2), ("penal", 3),
    ("terno", 3), ("turno", 3), ("carne", 3), ("perna", 3), ("forno", 3),
    ("Reino", 3), ("trono", 3), ("Bruno", 3), ("piano", 3), ("grão", 2),
]

# ============================ MODELOS DE DADOS ============================
@dataclass(frozen=True)
class Challenge:
    full_word: str
    missing_index: int
    valid_letters: frozenset[str]

    def __post_init__(self) -> None:
        """Validação pós-inicialização."""
        if not (0 <= self.missing_index < len(self.full_word)):
            raise ValueError(
                f"Índice {self.missing_index} inválido para palavra "
                f"'{self.full_word}' (tamanho {len(self.full_word)})"
            )
        target_letter = self.full_word[self.missing_index].lower()
        if target_letter not in self.valid_letters:
            raise ValueError(
                f"Letra na posição {self.missing_index} ('{target_letter}') "
                f"não é válida. Esperado: {self.valid_letters}"
            )

# ============================ FUNÇÕES AUXILIARES (LÓGICA) ============================
def mask_word(word: str, index: int) -> str:
    if not (0 <= index < len(word)):
        raise ValueError(f"Índice {index} fora do intervalo [0, {len(word)-1}]")
    return f"{word[:index]}_{word[index+1:]}"

def is_valid_guess(guess: str, valid_letters: frozenset[str]) -> bool:
    return (
        isinstance(guess, str) and
        len(guess) == 1 and
        guess.lower() in valid_letters
    )

def check_answer(challenge: Challenge, guess: str) -> bool:
    expected = challenge.full_word[challenge.missing_index].lower()
    return expected == guess.lower()

def build_challenges(mode: str) -> List[Challenge]:
    """Constrói lista de desafios baseado no modo (dt ou mn)."""
    if mode == "dt":
        raw_data = WORDS_DT
        valid_letters = VALID_LETTERS_DT
        mode_name = "D×T"
    elif mode == "mn":
        raw_data = WORDS_MN
        valid_letters = VALID_LETTERS_MN
        mode_name = "M×N"
    else:
        raise ValueError(f"Modo inválido: {mode}")

    challenges: List[Challenge] = []
    for word, idx in raw_data:
        try:
            challenge = Challenge(word, idx, valid_letters)
            challenges.append(challenge)
        except ValueError as e:
            logger.warning(f"Desafio inválido ignorado - {word}[{idx}]: {e}")
            continue

    random.shuffle(challenges)
    logger.info(f"Carregados {len(challenges)} desafios válidos para modo {mode_name}")
    return challenges

# ============================ COMPONENTE: REPRODUTOR DE GIF ANIMADO ============================
class GifPlayer:
    def __init__(self, root: tk.Tk, scale: int = SCALE) -> None:
        self.root = root
        self.scale = scale
        # Label único para todos os GIFs
        self.label = tk.Label(root, bd=0, bg=COLOR_BG)
        # Cache de frames e durações
        self.frames: Dict[str, List[ImageTk.PhotoImage]] = {
            "error": [],
            "success": []
        }
        self.durations: Dict[str, List[int]] = {
            "error": [],
            "success": []
        }
        # Estado da animação
        self.current_kind: Optional[str] = None
        self.after_id: Optional[str] = None
        self.visible: bool = False
        # Carrega GIFs de forma lazy
        self._preload_gifs()

    def _preload_gifs(self) -> None:
        for kind in ("error", "success"):
            try:
                frames, durations = self._load_gif(kind)
                self.frames[kind] = frames
                self.durations[kind] = durations
                logger.info(f"GIF '{kind}' carregado: {len(frames)} frames")
            except Exception as e:
                logger.error(f"Falha ao carregar GIF '{kind}': {e}")

    def _load_gif(self, kind: str) -> Tuple[List[ImageTk.PhotoImage], List[int]]:
        frames: List[ImageTk.PhotoImage] = []
        durations: List[int] = []

        # Tenta local primeiro, depois URL
        img: Optional[Image.Image] = None
        if GIF_PATHS.get(kind):
            try:
                img = Image.open(GIF_PATHS[kind])
                logger.debug(f"GIF '{kind}' carregado de arquivo local")
            except Exception as e:
                logger.warning(f"Falha ao abrir arquivo local '{kind}': {e}")

        if img is None:
            # Fallback para URL
            url = GIF_URLS[kind]
            request = Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urlopen(request, timeout=GIF_TIMEOUT) as response:
                data = response.read()
                img = Image.open(BytesIO(data))
                logger.debug(f"GIF '{kind}' carregado de URL")

        # Processa frames
        target_width = GIF_TARGET_WIDTH
        for frame in ImageSequence.Iterator(img):
            # Converte e redimensiona
            pil_frame = frame.convert("RGBA")
            w, h = pil_frame.size
            if w > target_width:
                ratio = target_width / w
                new_h = int(h * ratio)
                pil_frame = pil_frame.resize(
                    (target_width, new_h),
                    Image.Resampling.LANCZOS
                )
            # Converte para PhotoImage e armazena
            photo = ImageTk.PhotoImage(pil_frame)
            frames.append(photo)
            # Extrai duração
            duration = frame.info.get("duration", 
                                     img.info.get("duration", 100))
            durations.append(max(GIF_MIN_DURATION, duration))

        if not frames:
            raise ValueError(f"Nenhum frame extraído do GIF '{kind}'")

        return frames, durations

    def _animate(self, frame_index: int = 0) -> None:
        if not self.visible or not self.current_kind:
            return

        frame_list = self.frames.get(self.current_kind, [])
        duration_list = self.durations.get(self.current_kind, [])

        if not frame_list:
            logger.warning(f"Frames vazios para '{self.current_kind}'")
            return

        # Frame circular
        idx = frame_index % len(frame_list)
        current_frame = frame_list[idx]

        # Atualiza label (mantém referência viva)
        self.label.configure(image=current_frame)
        self.label.image = current_frame  # Previne GC

        # Agenda próximo frame
        delay = duration_list[idx] if duration_list else 80
        try:
            self.after_id = self.root.after(
                delay,
                self._animate,
                frame_index + 1
            )
        except tk.TclError as e:
            logger.error(f"Erro ao agendar animação: {e}")
            self.hide()

    def show(self, kind: str) -> None:
        if kind not in ("error", "success"):
            logger.warning(f"Tipo de GIF inválido: '{kind}'")
            return

        if not self.frames[kind]:
            logger.warning(f"GIF '{kind}' não disponível")
            return

        # Esconde anterior
        self.hide()

        # Configura novo
        self.current_kind = kind
        self.visible = True

        # Posiciona (canto inferior direito)
        self.label.place(
            relx=1.0,
            rely=1.0,
            x=-25,
            y=-25,
            anchor="se"
        )

        # Inicia animação
        self._animate(0)
        logger.debug(f"GIF '{kind}' exibido")

    def hide(self) -> None:
        """Oculta GIF e para animação de forma segura."""
        self.visible = False
        # Cancela timer pendente
        if self.after_id:
            try:
                self.root.after_cancel(self.after_id)
            except (tk.TclError, ValueError):
                pass
            finally:
                self.after_id = None

        # Remove do layout
        self.label.place_forget()
        self.label.configure(image="")
        self.label.image = None
        self.current_kind = None

# ============================ TELA DE MENU ============================
class MenuScreen:
    def __init__(self, root: tk.Tk, on_select_callback) -> None:
        self.root = root
        self.on_select = on_select_callback
        self.frame = tk.Frame(root, bg=COLOR_BG)

        # Título
        title = tk.Label(
            self.frame,
            text="🎮 Escolha o Jogo!",
            font=FONT_TITLE,
            bg=COLOR_BG,
            fg=COLOR_NEUTRAL
        )
        title.pack(pady=(50 * SCALE, 30 * SCALE))

        # Subtítulo
        subtitle = tk.Label(
            self.frame,
            text="Clique no jogo que deseja jogar:",
            font=FONT_FEEDBACK,
            bg=COLOR_BG,
            fg=COLOR_NEUTRAL
        )
        subtitle.pack(pady=(0, 40 * SCALE))

        # Botão D×T
        btn_dt = tk.Button(
            self.frame,
            text="🔤 Jogo D × T",
            font=FONT_BTN_MENU,
            command=lambda: self.on_select("dt"),
            bg="#FF6B6B",
            fg="white",
            activebackground="#FF5252",
            cursor="hand2",
            bd=0,
            padx=40,
            pady=20,
            width=15
        )
        btn_dt.pack(pady=15 * SCALE)

        # Botão M×N
        btn_mn = tk.Button(
            self.frame,
            text="🔤 Jogo M × N",
            font=FONT_BTN_MENU,
            command=lambda: self.on_select("mn"),
            bg="#4ECDC4",
            fg="white",
            activebackground="#45B7AF",
            cursor="hand2",
            bd=0,
            padx=40,
            pady=20,
            width=15
        )
        btn_mn.pack(pady=15 * SCALE)

    def show(self) -> None:
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self) -> None:
        self.frame.pack_forget()

# ============================ APLICAÇÃO PRINCIPAL ============================
class DTGame:
    def __init__(self, root: tk.Tk, mode: str, on_back_callback) -> None:
        self.root = root
        self.mode = mode  # "dt" ou "mn"
        self.on_back = on_back_callback

        # Define letras válidas baseado no modo
        self.valid_letters = VALID_LETTERS_DT if mode == "dt" else VALID_LETTERS_MN
        self.mode_display = "D × T" if mode == "dt" else "M × N"

        # Frame principal
        self.frame = tk.Frame(root, bg=COLOR_BG)

        # Estado do jogo
        self.score: int = 0
        self.total: int = 0
        self.challenges: List[Challenge] = build_challenges(mode)
        self.current: Optional[Challenge] = None
        self.evaluated: bool = False

        # UI
        self._build_ui()

        # Player de GIFs
        self.gifs = GifPlayer(root, scale=SCALE)

        # Bindings
        self.root.bind("<Return>", self._on_enter_key)

        logger.info(f"Jogo {self.mode_display} inicializado")

    def _build_ui(self) -> None:
        # Header com título do modo
        header = tk.Label(
            self.frame,
            text=f"🎮 Jogo {self.mode_display}",
            font=FONT_TITLE,
            bg=COLOR_BG,
            fg=COLOR_NEUTRAL
        )
        header.pack(pady=(10 * SCALE, 5 * SCALE))

        # Botão voltar
        btn_back = tk.Button(
            self.frame,
            text="⬅ Voltar ao Menu",
            font=("Arial", 12 * SCALE),
            command=self._go_back,
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            cursor="hand2",
            bd=0,
            padx=10,
            pady=5
        )
        btn_back.pack(pady=(0, 10 * SCALE))

        # Label da palavra
        self.word_label = tk.Label(
            self.frame,
            text="Palavra:",
            font=FONT_WORD,
            bg=COLOR_BG,
            fg=COLOR_NEUTRAL
        )
        self.word_label.pack(pady=PAD_Y_WORD)

        # Frame de entrada
        entry_frame = tk.Frame(self.frame, bg=COLOR_BG)
        entry_frame.pack(pady=PAD_Y_ENTRY)

        self.entry = tk.Entry(
            entry_frame,
            width=WIDTH_ENTRY,
            font=FONT_ENTRY,
            justify="center",
            bd=3,
            relief=tk.SOLID
        )
        self.entry.grid(row=0, column=0, padx=PADX_ENTRY)

        self.btn_check = tk.Button(
            entry_frame,
            text="✓ Verificar",
            font=FONT_BTN,
            command=self.check_answer,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            cursor="hand2",
            bd=0,
            padx=15,
            pady=8
        )
        self.btn_check.grid(row=0, column=1, padx=PADX_ENTRY)

        # Feedback da tentativa
        self.feedback_try = tk.Label(
            self.frame,
            text="",
            font=FONT_FEEDBACK,
            bg=COLOR_BG
        )
        self.feedback_try.pack(pady=PAD_Y_FEEDBACK)

        # Resposta correta
        self.feedback_correct = tk.Label(
            self.frame,
            text="",
            font=FONT_CORRECT,
            bg=COLOR_BG,
            fg=COLOR_NEUTRAL
        )
        self.feedback_correct.pack(pady=PAD_Y_CORRECT)

        # Placar
        self.score_label = tk.Label(
            self.frame,
            text="🏆 Placar: 0 / 0",
            font=FONT_SCORE,
            bg=COLOR_BG,
            fg=COLOR_NEUTRAL
        )
        self.score_label.pack(pady=PAD_Y_SCORE)

        # Botão próxima
        btn_next = tk.Button(
            self.frame,
            text="➡ Próxima Palavra",
            font=FONT_BTN,
            command=self.next_challenge,
            bg="#2196F3",
            fg="white",
            activebackground="#0b7dda",
            cursor="hand2",
            bd=0,
            padx=20,
            pady=10
        )
        btn_next.pack(pady=PAD_Y_BTN)

    def _go_back(self) -> None:
        """Volta para o menu principal."""
        self.gifs.hide()
        self.root.unbind("<Return>")
        self.hide()
        self.on_back()

    def _on_enter_key(self, event: Optional[tk.Event] = None) -> None:
        if not self.evaluated:
            self.check_answer()
        else:
            self.next_challenge()

    def check_answer(self) -> None:
        if self.current is None:
            logger.warning("Nenhum desafio ativo")
            return

        guess = self.entry.get().strip()

        # Validação de entrada
        if not is_valid_guess(guess, self.valid_letters):
            letters_display = "/".join(sorted(self.valid_letters)).upper()
            self.feedback_try.config(
                text=f"⚠️ Digite apenas {letters_display}",
                fg=COLOR_ERROR
            )
            self.entry.focus_set()
            self.entry.selection_range(0, tk.END)
            return

        # Incrementa contador
        self.total += 1

        # Letra correta
        correct_letter = self.current.full_word[self.current.missing_index].upper()

        # Verifica resposta
        if check_answer(self.current, guess):
            # ✅ ACERTO
            self.score += 1
            self.feedback_try.config(
                text=f"✅ ACERTOU! (letra {correct_letter})",
                fg=COLOR_SUCCESS
            )
            self.gifs.show("success")
            logger.info(f"Acerto: {self.current.full_word}")
        else:
            # ❌ ERRO
            wrong_attempt = self._render_guess(self.current, guess.upper())
            self.feedback_try.config(
                text=f"❌ Tentativa: {wrong_attempt}",
                fg=COLOR_ERROR
            )
            self.gifs.show("error")
            logger.info(f"Erro: {self.current.full_word} (tentou {guess})")

        # Mostra resposta correta
        self.feedback_correct.config(
            text=f"📖 Resposta: {self.current.full_word.upper()}"
        )

        # Atualiza placar
        self._update_score()

        # Mostra palavra completa
        self.word_label.config(
            text=f"Palavra: {self.current.full_word.upper()}"
        )

        # Marca como avaliado
        self.evaluated = True

        # Mantém foco e seleciona texto
        self.entry.selection_range(0, tk.END)
        self.entry.focus_set()

    def next_challenge(self) -> None:
        """Carrega próximo desafio."""
        # Recarrega desafios se necessário
        if not self.challenges:
            self.challenges = build_challenges(self.mode)
            logger.info("Lista de desafios recarregada")

        # Sorteia desafio
        self.current = self.challenges.pop()
        self.evaluated = False

        # Limpa feedback
        self.feedback_try.config(text="")
        self.feedback_correct.config(text="")

        # Exibe palavra mascarada
        masked = mask_word(self.current.full_word, self.current.missing_index)
        self.word_label.config(text=f"Palavra: {masked.upper()}")

        # Limpa entrada
        self.entry.delete(0, tk.END)
        self.entry.focus_set()

        # Esconde GIF anterior
        self.gifs.hide()

        logger.debug(f"Novo desafio: {self.current.full_word}")

    def _update_score(self) -> None:
        percentage = (self.score / self.total * 100) if self.total > 0 else 0
        self.score_label.config(
            text=f"🏆 Placar: {self.score} / {self.total} ({percentage:.0f}%)"
        )

    @staticmethod
    def _render_guess(challenge: Challenge, guess_upper: str) -> str:
        idx = challenge.missing_index
        return (
            f"{challenge.full_word[:idx]}"
            f"{guess_upper}"
            f"{challenge.full_word[idx+1:]}"
        )

    def show(self) -> None:
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.next_challenge()

    def hide(self) -> None:
        self.frame.pack_forget()

# ============================ CONTROLADOR PRINCIPAL ============================
class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._configure_window()

        # Telas
        self.menu = MenuScreen(root, self.start_game)
        self.game: Optional[DTGame] = None

        # Mostra menu inicial
        self.menu.show()

    def _configure_window(self) -> None:
        self.root.title("🎮 Jogo de Consciência Fonológica")
        self.root.geometry(GEOMETRY)
        self.root.configure(bg=COLOR_BG)

        # Tenta aplicar escala DPI
        try:
            self.root.tk.call('tk', 'scaling', float(SCALE))
        except tk.TclError:
            logger.warning("Falha ao aplicar escala DPI")

    def start_game(self, mode: str) -> None:
        """Inicia jogo no modo selecionado."""
        self.menu.hide()
        self.game = DTGame(self.root, mode, self.back_to_menu)
        self.game.show()

    def back_to_menu(self) -> None:
        """Retorna ao menu principal."""
        if self.game:
            self.game = None
        self.menu.show()

# ============================ PONTO DE ENTRADA ============================
def main() -> None:
    """Inicializa aplicação."""
    root = tk.Tk()
    # Força atualização de idle tasks (previne bugs de renderização)
    root.after(50, lambda: None)
    # Instancia aplicação
    App(root)
    # Loop principal
    root.mainloop()

# ============================ TESTES UNITÁRIOS ============================
def run_tests() -> None:
    logger.info("Executando testes...")

    # Test 1: Mascaramento de palavra
    assert mask_word("teto", 0) == "_eto"
    assert mask_word("dado", 2) == "da_o"

    # Test 2: Validação de entrada
    assert is_valid_guess("t", VALID_LETTERS_DT)
    assert is_valid_guess("D", VALID_LETTERS_DT)
    assert is_valid_guess("m", VALID_LETTERS_MN)
    assert is_valid_guess("N", VALID_LETTERS_MN)
    assert not is_valid_guess("", VALID_LETTERS_DT)
    assert not is_valid_guess("tt", VALID_LETTERS_DT)
    assert not is_valid_guess("x", VALID_LETTERS_DT)
    assert not is_valid_guess("d", VALID_LETTERS_MN)  # D não válido em M×N

    # Test 3: Verificação de resposta
    ch_dt = Challenge("teto", 0, VALID_LETTERS_DT)
    assert check_answer(ch_dt, "t")
    assert check_answer(ch_dt, "T")
    assert not check_answer(ch_dt, "d")

    ch_mn = Challenge("mato", 0, VALID_LETTERS_MN)
    assert check_answer(ch_mn, "m")
    assert check_answer(ch_mn, "M")
    assert not check_answer(ch_mn, "n")

    # Test 4: Construção de desafios
    challenges_dt = build_challenges("dt")
    challenges_mn = build_challenges("mn")
    assert len(challenges_dt) > 0
    assert len(challenges_mn) > 0
    assert all(isinstance(c, Challenge) for c in challenges_dt)
    assert all(isinstance(c, Challenge) for c in challenges_mn)

    logger.info("✅ Todos os testes passaram!")

# ============================ EXECUTION ============================
if __name__ == "__main__":
    run_tests()
    main()
