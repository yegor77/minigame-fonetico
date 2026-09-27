from __future__ import annotations
import logging
import random
import threading
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
VALID_LETTERS_VF: frozenset[str] = frozenset({"v", "f"})
VALID_LETTERS_SZ: frozenset[str] = frozenset({"s", "z"})

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
# Com os botões do menu em grade 2x2 (ver MenuScreen), esta altura é
# suficiente mesmo em telas menores; ainda assim a janela permanece
# redimensionável (ver App._configure_window) como rede de segurança.
GEOMETRY: str = "1000x800"

# Cores (acessibilidade infantil)
COLOR_BG: str = "#F0F8FF"  # Alice Blue
COLOR_SUCCESS: str = "#228B22"  # Forest Green
COLOR_ERROR: str = "#DC143C"  # Crimson
COLOR_NEUTRAL: str = "#2F4F4F"  # Dark Slate Gray

# GIFs
GIF_TIMEOUT: int = 8
GIF_TARGET_WIDTH: int = 150 * SCALE
GIF_MIN_DURATION: int = 50
GIF_URLS: Dict[str, str] = {
    "error": "https://media1.tenor.com/m/OHb60YjsOgcAAAAC/lyon-manchester-city-neymar-crying.gif",
    "success": "https://media1.tenor.com/m/MhpcPDesURYAAAAd/neymar-neymar-jr.gif",
}

# Fallback: caminhos locais (se disponíveis)
GIF_PATHS: Dict[str, Optional[str]] = {
    "error": None,
    "success": None
}

# ============================ BANCO DE PALAVRAS ============================
# As palavras sao definidas como (palavra, letra_alvo[, ocorrencia]).
# O indice da letra mascarada e' CALCULADO AUTOMATICAMENTE por resolve_words(),
# em vez de contado manualmente -- isso elimina erros de indice/letra invalida
# que existiam no banco original (varias palavras tinham indice incorreto e
# eram descartadas silenciosamente por Challenge.__post_init__).
def resolve_words(entries: List[Tuple], valid_letters: frozenset[str]) -> List[Tuple[str, int]]:
    """Converte (palavra, letra[, ocorrencia]) em (palavra, indice), sem contagem manual."""
    resolved: List[Tuple[str, int]] = []
    for item in entries:
        word, letter, occurrence = (*item, 1)[:3] if len(item) == 2 else item
        lw = word.lower()
        seen = 0
        index = -1
        for i, ch in enumerate(lw):
            if ch == letter:
                seen += 1
                if seen == occurrence:
                    index = i
                    break
        if index == -1:
            logger.warning(f"Palavra ignorada - letra '{letter}' (ocorrencia {occurrence}) nao encontrada em '{word}'")
            continue
        resolved.append((word, index))
    return resolved

DT_SRC = [
    # Faceis - T no inicio
    ("teto","t"), ("tubo","t"), ("tigre","t"), ("trem","t"), ("torre","t"),
    ("trigo","t"), ("turma","t"), ("tempo","t"), ("tigela","t"), ("tomate","t"),
    ("tampa","t"), ("tocha","t"), ("trilha","t"), ("torrada","t"), ("tesouro","t"),
    ("telefone","t"), ("tijolo","t"), ("toalha","t"), ("teatro","t"), ("tapete","t"),
    # Faceis - D no inicio
    ("dedo","d"), ("dente","d"), ("doce","d"), ("dono","d"), ("duro","d"),
    ("duplo","d"), ("duende","d"), ("dormir","d"), ("descer","d"), ("disco","d"),
    ("desejo","d"), ("detalhe","d"), ("desenho","d"), ("dentista","d"), ("dezena","d"),
    ("diploma","d"), ("domingo","d"), ("dourado","d"), ("docinho","d"), ("dinossauro","d"),
    ("degrau","d"), ("delfim","d"), ("dedal","d"), ("dobradica","d"), ("decisao","d"),
    # Medio - T no meio/fim
    ("moto","t",1), ("voto","t",1), ("foto","t",1), ("luto","t",1), ("rito","t",1),
    ("rato","t",1), ("pato","t",1), ("gato","t",1), ("prato","t",1), ("chute","t",1),
    ("fruto","t",1), ("bruto","t",1), ("cesto","t",1), ("gesto","t",1), ("futebol","t",1),
    ("curtir","t",1), ("partir","t",1), ("sortear","t",1), ("mentir","t",1), ("contar","t",1),
    ("portal","t",1), ("mortal","t",1), ("costume","t",1), ("planeta","t",1), ("presente","t",1),
    ("caneta","t",1), ("bilhete","t",1), ("assunto","t",1), ("história","t",1),
    # Medio - D no meio/fim
    ("poder","d",1), ("ceder","d",1), ("medir","d",1), ("pedir","d",1),
    ("moldura","d",1), ("pendente","d",1), ("condomínio","d",1), ("redor","d",1), ("fedor","d",1),
    ("suador","d",1), ("orador","d",1), ("quadro","d",1), ("pedro","d",1), ("vidro","d",1),
    ("cedo","d",1), ("surdo","d",1), ("modelo","d",1), ("moderno","d",1), ("médico","d",1),
    ("código","d",1), ("soldado","d",1), ("cuidado","d",1), ("estudar","d",1), ("duvidar","d",1),
    ("ordenar","d",1), ("agenda","d",1), ("bandeira","d",1), ("cidade","d",1), ("verdade","d",2),
    # Dificil - T
    ("prestar","t",1), ("questão","t",1), ("prática","t",1), ("frontal","t",1), ("cristal","t",1),
    ("brutal","t",1), ("eterno","t",1), ("inventar","t",1), ("formato","t",1), ("catástrofe","t",1),
    ("estrutura","t",1), ("intervalo","t",1), ("apartamento","t",1), ("investimento","t",1),
    ("temperatura","t",1), ("atmosfera","t",1), ("estatística","t",1), ("particular","t",1),
    ("território","t",1), ("automático","t",1), ("instrumento","t",1), ("aeroporto","t",1),
    # Dificil - D
    ("prudente","d",1), ("comunidade","d",1), ("dificuldade","d",1), ("identidade","d",1),
    ("universidade","d",1), ("qualidade","d",1), ("necessidade","d",1), ("realidade","d",1),
    ("dedicação","d",1), ("desconfiado","d",1), ("desordenado","d",1), ("procedimento","d",1),
    ("independência","d",1), ("adequado","d",1), ("dedução","d",1), ("advogado","d",1),
    ("descoberta","d",1), ("dedicado","d",1), ("adiantado","d",1), ("desperdício","d",1),
]

MN_SRC = [
    # Faceis - M inicio
    ("mato","m"), ("mala","m"), ("mesa","m"), ("meia","m"), ("moeda","m"),
    ("muro","m"), ("mapa","m"), ("mimo","m"), ("mula","m"), ("monte","m"),
    ("mate","m"), ("mania","m"), ("manga","m"), ("marco","m"), ("massa","m"),
    ("maior","m"), ("malha","m"), ("manso","m"), ("motor","m"), ("macio","m"),
    ("montanha","m"), ("mistério","m"), ("mercado","m"), ("moldura","m"), ("morango","m"),
    # Faceis - N inicio
    ("nabo","n"), ("nada","n"), ("nave","n"), ("neto","n"), ("nora","n"),
    ("nota","n"), ("novo","n"), ("nuca","n"), ("ninho","n"), ("nervo","n"),
    ("nome","n"), ("nunca","n"), ("navio","n"), ("nariz","n"), ("neve","n"),
    ("nuvem","n"), ("natal","n"), ("noite","n"), ("norte","n"), ("negro","n"),
    ("nogueira","n"), ("notícia","n"), ("namorado","n"), ("numeral","n"), ("nervoso","n"),
    # Medio - M meio/fim
    ("cama","m",1), ("gema","m",1), ("remo","m",1), ("toma","m",1), ("lima","m",1),
    ("rama","m",1), ("fumo","m",1), ("rima","m",1), ("tema","m",1), ("clima","m",1),
    ("grama","m",1), ("chama","m",1), ("palma","m",1), ("calma","m",1), ("firma","m",1),
    ("amar","m",1), ("aroma","m",1), ("pomar","m",1), ("formar","m",1), ("somar","m",1),
    ("firme","m",1), ("norma","m",1), ("forma","m",1), ("arma","m",1), ("alma","m",1),
    ("filma","m",1), ("palmo","m",1), ("termo","m",1), ("gomo","m",1), ("ramo","m",1),
    ("cumprir","m",1), ("compra","m",1), ("tempo","m",1), ("campo","m",1), ("comprido","m",1),
    # Medio - N meio/fim
    ("cana","n",1), ("pena","n",1), ("lona","n",1), ("dona","n",1), ("zona","n",1),
    ("cano","n",1), ("pano","n",1), ("plano","n",1), ("mano","n",1), ("sono","n",1),
    ("cone","n",1), ("pino","n",1), ("sino","n",1), ("vinho","n",1), ("linha","n",1),
    ("final","n",1), ("sinal","n",1), ("canal","n",1), ("penal","n",1), ("terno","n",1),
    ("turno","n",1), ("carne","n",1), ("perna","n",1), ("forno","n",1), ("trono","n",1),
    ("piano","n",1), ("grande","n",1), ("reinado","n",1), ("moreno","n",1), ("ninar","n",1),
    ("banana","n",1), ("janela","n",1), ("bonito","n",1), ("moinho","n",1),
    # Dificil - M
    ("emprestar","m",1), ("dinamite","m",1), ("temporada","m",1), ("democracia","m",1),
    ("comércio","m",1), ("importante","m",1), ("compromisso","m",1), ("elemento","m",1),
    ("simetria","m",1), ("ambiente","m",1), ("emprego","m",1), ("computador","m",1),
    ("temperatura","m",1), ("recomendar","m",1), ("complicado","m",1), ("compreensão","m",1),
    ("harmonia","m",1), ("gramática","m",1), ("comunicar","m",1), ("membro","m",1),
    # Dificil - N
    ("consciência","n",1), ("independente","n",1), ("universo","n",1), ("necessário","n",1),
    ("intenção","n",1), ("continente","n",1), ("engenheiro","n",1),
    ("intensivo","n",1), ("condicional","n",1), ("inteligente","n",1), ("naturalmente","n",1),
    ("aniversário","n",1), ("nascimento","n",1), ("panorama","n",1), ("consumidor","n",1),
    ("energia","n",1), ("interessante","n",1), ("naufrágio","n",1), ("montanhoso","n",1),
]

VF_SRC = [
    # Faceis - V no inicio
    ("vaso","v"), ("vela","v"), ("vento","v"), ("vidro","v"), ("vovô","v"),
    ("vaca","v"), ("vale","v"), ("verde","v"), ("viola","v"), ("vulcão","v"),
    ("vidraça","v"), ("valente","v"), ("vitamina","v"), ("viagem","v"), ("vizinho","v"),
    ("varal","v"), ("veludo","v"), ("vagalume","v"), ("ventania","v"), ("violino","v"),
    # Faceis - F no inicio
    ("fada","f"), ("faca","f"), ("febre","f"), ("fita","f"), ("foca","f"),
    ("fogo","f"), ("fumo","f"), ("fundo","f"), ("farol","f"), ("favo","f"),
    ("feira","f"), ("filho","f"), ("fivela","f"), ("floresta","f"), ("fantasma","f"),
    ("formiga","f"), ("fogueira","f"), ("fazenda","f"), ("feriado","f"), ("futebol","f"),
    # Medio - V meio/fim
    ("uva","v",1), ("cova","v",1), ("luva","v",1), ("nave","v",1), ("chave","v",1),
    ("trave","v",1), ("cravo","v",1), ("novo","v",1), ("avô","v",1), ("javali","v",1),
    ("cavalo","v",1), ("gaveta","v",1), ("motivo","v",1), ("positivo","v",1),
    ("ativo","v",1), ("nervoso","v",1), ("serviço","v",1), ("reserva","v",1),
    ("conversa","v",1), ("universo","v",1), ("inverno","v",1),
    # Medio - F meio/fim
    ("café","f",1), ("gafanhoto","f",1), ("telefone","f",1), ("elefante","f",1),
    ("girafa","f",1), ("profeta","f",1), ("perfume","f",1), ("infantil","f",1),
    ("conforto","f",1), ("informe","f",1), ("reforma","f",1), ("esfera","f",1),
    ("surfar","f",1), ("profundo","f",1), ("confuso","f",1),
    # Dificil - V
    ("aventura","v",1), ("avental","v",1), ("diversão","v",1), ("universidade","v",1),
    ("investimento","v",1), ("conservar","v",1), ("resolver","v",1), ("envolver","v",1),
    ("avançado","v",1), ("individual","v",1),
    # Dificil - F
    ("dificuldade","f",1), ("confiança","f",1), ("informação","f",1), ("referência","f",1),
    ("profissional","f",1), ("significado","f",1), ("eficiente","f",1),
    ("conferência","f",1), ("infelizmente","f",1),
]

SZ_SRC = [
    # Faceis - S no inicio
    ("sapo","s"), ("sopa","s"), ("sino","s"), ("saco","s"), ("suco","s"),
    ("sede","s"), ("selo","s"), ("sala","s"), ("seda","s"), ("sopro","s"),
    ("sorvete","s"), ("sandália","s"), ("samba","s"), ("sereia","s"), ("sabonete","s"),
    ("salada","s"), ("semana","s"), ("segredo","s"), ("silêncio","s"), ("simples","s"),
    # Faceis - Z no inicio
    ("zebra","z"), ("zero","z"), ("zoológico","z"), ("zangado","z"), ("zumbido","z"),
    ("zíper","z"), ("zombar","z"), ("zelador","z"), ("zanzar","z"), ("zunido","z"),
    # Medio - S meio/fim
    ("casa","s",1), ("mesa","s",1), ("rosa","s",1), ("asa","s",1), ("brasa","s",1),
    ("presa","s",1), ("musa","s",1), ("usar","s",1), ("casaco","s",1), ("pesado","s",1),
    ("musical","s",1), ("positivo","s",1), ("presente","s",1), ("escola","s",1),
    ("esporte","s",1), ("pessoa","s",1),
    # Medio - Z meio/fim
    ("vazio","z",1), ("prazo","z",1), ("cozinha","z",1), ("razão","z",1),
    ("buzina","z",1), ("dezena","z",1), ("gozar","z",1), ("fazenda","z",1),
    ("azedo","z",1), ("lazer","z",1), ("horizonte","z",1),
    # Dificil - S
    ("necessário","s",1), ("responsável","s",1), ("consciência","s",1),
    ("observar","s",1), ("pesquisa","s",1), ("consequência","s",1),
    ("apresentar","s",1), ("resultado","s",1), ("essencial","s",1), ("responder","s",1),
    # Dificil - Z
    ("realizar","z",1), ("organizar","z",1), ("civilização","z",1), ("utilizar","z",1),
    ("finalizar","z",1), ("localizar","z",1), ("cartaz","z",1), ("capaz","z",1),
    ("audaz","z",1),
]

WORDS_DT: List[Tuple[str, int]] = resolve_words(DT_SRC, VALID_LETTERS_DT)
WORDS_MN: List[Tuple[str, int]] = resolve_words(MN_SRC, VALID_LETTERS_MN)
WORDS_VF: List[Tuple[str, int]] = resolve_words(VF_SRC, VALID_LETTERS_VF)
WORDS_SZ: List[Tuple[str, int]] = resolve_words(SZ_SRC, VALID_LETTERS_SZ)

# Registro central de modos: cada modo aponta para suas letras válidas, seu
# nome de exibição e seu banco de palavras já resolvido. Adicionar um novo
# modo no futuro (ex.: "pb") significa só acrescentar uma entrada aqui e o
# respectivo _SRC/WORDS_*, sem tocar em build_challenges, DTGame ou MenuScreen.
MODE_REGISTRY: Dict[str, Dict[str, object]] = {
    "dt": {"valid_letters": VALID_LETTERS_DT, "display": "D × T", "words": WORDS_DT},
    "mn": {"valid_letters": VALID_LETTERS_MN, "display": "M × N", "words": WORDS_MN},
    "vf": {"valid_letters": VALID_LETTERS_VF, "display": "V × F", "words": WORDS_VF},
    "sz": {"valid_letters": VALID_LETTERS_SZ, "display": "S × Z", "words": WORDS_SZ},
}

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
    """Constrói lista de desafios baseado no modo (dt, mn, vf ou sz)."""
    if mode not in MODE_REGISTRY:
        raise ValueError(f"Modo inválido: {mode}")

    info = MODE_REGISTRY[mode]
    raw_data: List[Tuple[str, int]] = info["words"]  # type: ignore[assignment]
    valid_letters: frozenset[str] = info["valid_letters"]  # type: ignore[assignment]
    mode_name: str = info["display"]  # type: ignore[assignment]

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
        # Carrega GIFs em segundo plano: são baixados da internet (urlopen),
        # e fazer isso de forma síncrona no __init__ trava a janela por vários
        # segundos antes do primeiro desenho. Uma thread evita esse congelamento;
        # o resultado só é aplicado na UI através de root.after (thread-safe).
        self._preload_gifs_async()

    def _preload_gifs_async(self) -> None:
        def worker() -> None:
            for kind in ("error", "success"):
                try:
                    frames_raw, durations = self._load_gif(kind)
                    # ImageTk.PhotoImage só pode ser criado na thread principal do Tk,
                    # então a thread de fundo prepara os dados e agenda a criação real.
                    self.root.after(0, self._store_gif, kind, frames_raw, durations)
                except Exception as e:
                    logger.error(f"Falha ao carregar GIF '{kind}': {e}")

        threading.Thread(target=worker, daemon=True).start()

    def _store_gif(
        self, kind: str, pil_frames: List[Image.Image], durations: List[int]
    ) -> None:
        """Converte os frames PIL em PhotoImage (só é seguro na thread principal)."""
        self.frames[kind] = [ImageTk.PhotoImage(f) for f in pil_frames]
        self.durations[kind] = durations
        logger.info(f"GIF '{kind}' carregado: {len(pil_frames)} frames")

    def _load_gif(self, kind: str) -> Tuple[List[Image.Image], List[int]]:
        """Baixa/decodifica o GIF e devolve frames PIL (ainda não PhotoImage).

        Roda em thread de fundo, então não pode tocar em ImageTk.PhotoImage
        (não é thread-safe); essa conversão acontece depois, em _store_gif,
        já na thread principal do Tk.
        """
        frames: List[Image.Image] = []
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
            frames.append(pil_frame)
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
# Configuração de cada botão do menu: (modo, texto, cor de fundo, cor ao ativar)
MENU_BUTTONS: List[Tuple[str, str, str, str]] = [
    ("dt", "🔤 Jogo D × T", "#FF6B6B", "#FF5252"),
    ("mn", "🔤 Jogo M × N", "#4ECDC4", "#45B7AF"),
    ("vf", "🔤 Jogo V × F", "#FFA726", "#FB8C00"),
    ("sz", "🔤 Jogo S × Z", "#AB47BC", "#8E24AA"),
]

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

        # Botões (gerados a partir de MENU_BUTTONS, em grade 2x2).
        # Empilhar N botões verticalmente com fonte grande facilmente estoura
        # a altura da janela em telas menores (o pack() não rola sozinho, o
        # botão simplesmente fica invisível fora da área visível). Uma grade
        # 2 colunas x N linhas mantém a altura sob controle mesmo somando
        # mais jogos no futuro.
        buttons_frame = tk.Frame(self.frame, bg=COLOR_BG)
        buttons_frame.pack(pady=10 * SCALE)
        columns = 2
        for i in range(columns):
            buttons_frame.columnconfigure(i, weight=1)

        for i, (mode, label, bg, active_bg) in enumerate(MENU_BUTTONS):
            row, col = divmod(i, columns)
            btn = tk.Button(
                buttons_frame,
                text=label,
                font=FONT_BTN_MENU,
                command=lambda m=mode: self.on_select(m),
                bg=bg,
                fg="white",
                activebackground=active_bg,
                cursor="hand2",
                bd=0,
                padx=30,
                pady=18,
                width=13
            )
            btn.grid(row=row, column=col, padx=12 * SCALE, pady=12 * SCALE)

    def show(self) -> None:
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self) -> None:
        self.frame.pack_forget()

# ============================ APLICAÇÃO PRINCIPAL ============================
class DTGame:
    def __init__(self, root: tk.Tk, mode: str, on_back_callback) -> None:
        self.root = root
        self.mode = mode  # "dt", "mn", "vf" ou "sz"
        self.on_back = on_back_callback

        # Define letras válidas e nome de exibição a partir do registro central
        info = MODE_REGISTRY[mode]
        self.valid_letters: frozenset[str] = info["valid_letters"]  # type: ignore[assignment]
        self.mode_display: str = info["display"]  # type: ignore[assignment]

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
        # Garante que a janela pode ser redimensionada/maximizada pelo
        # usuário caso o conteúdo ainda não caiba na tela (telas pequenas).
        self.root.resizable(True, True)

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
    assert is_valid_guess("v", VALID_LETTERS_VF)
    assert is_valid_guess("F", VALID_LETTERS_VF)
    assert is_valid_guess("s", VALID_LETTERS_SZ)
    assert is_valid_guess("Z", VALID_LETTERS_SZ)
    assert not is_valid_guess("", VALID_LETTERS_DT)
    assert not is_valid_guess("tt", VALID_LETTERS_DT)
    assert not is_valid_guess("x", VALID_LETTERS_DT)
    assert not is_valid_guess("d", VALID_LETTERS_MN)  # D não válido em M×N
    assert not is_valid_guess("s", VALID_LETTERS_VF)  # S não válido em V×F
    assert not is_valid_guess("v", VALID_LETTERS_SZ)  # V não válido em S×Z

    # Test 3: Verificação de resposta
    ch_dt = Challenge("teto", 0, VALID_LETTERS_DT)
    assert check_answer(ch_dt, "t")
    assert check_answer(ch_dt, "T")
    assert not check_answer(ch_dt, "d")

    ch_mn = Challenge("mato", 0, VALID_LETTERS_MN)
    assert check_answer(ch_mn, "m")
    assert check_answer(ch_mn, "M")
    assert not check_answer(ch_mn, "n")

    ch_vf = Challenge("vaso", 0, VALID_LETTERS_VF)
    assert check_answer(ch_vf, "v")
    assert check_answer(ch_vf, "V")
    assert not check_answer(ch_vf, "f")

    ch_sz = Challenge("sapo", 0, VALID_LETTERS_SZ)
    assert check_answer(ch_sz, "s")
    assert check_answer(ch_sz, "S")
    assert not check_answer(ch_sz, "z")

    # Test 4: Construção de desafios
    challenges_dt = build_challenges("dt")
    challenges_mn = build_challenges("mn")
    challenges_vf = build_challenges("vf")
    challenges_sz = build_challenges("sz")
    assert len(challenges_dt) > 0
    assert len(challenges_mn) > 0
    assert len(challenges_vf) > 0
    assert len(challenges_sz) > 0
    assert all(isinstance(c, Challenge) for c in challenges_dt)
    assert all(isinstance(c, Challenge) for c in challenges_mn)
    assert all(isinstance(c, Challenge) for c in challenges_vf)
    assert all(isinstance(c, Challenge) for c in challenges_sz)

    # Test 5: Nenhuma palavra do banco deve ser descartada por indice/letra
    # invalidos. Se isso falhar, alguma entrada de *_SRC está apontando para
    # uma ocorrência de letra que não existe na palavra.
    assert len(challenges_dt) == len(WORDS_DT), (
        f"{len(WORDS_DT) - len(challenges_dt)} palavra(s) de WORDS_DT foram "
        "descartadas - veja os avisos de log acima"
    )
    assert len(challenges_mn) == len(WORDS_MN), (
        f"{len(WORDS_MN) - len(challenges_mn)} palavra(s) de WORDS_MN foram "
        "descartadas - veja os avisos de log acima"
    )
    assert len(challenges_vf) == len(WORDS_VF), (
        f"{len(WORDS_VF) - len(challenges_vf)} palavra(s) de WORDS_VF foram "
        "descartadas - veja os avisos de log acima"
    )
    assert len(challenges_sz) == len(WORDS_SZ), (
        f"{len(WORDS_SZ) - len(challenges_sz)} palavra(s) de WORDS_SZ foram "
        "descartadas - veja os avisos de log acima"
    )

    logger.info("✅ Todos os testes passaram!")

# ============================ EXECUTION ============================
if __name__ == "__main__":
    run_tests()
    main()