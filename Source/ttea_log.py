#################################################################################
######################### LOGGING - PROJETO T-TEA ###############################
#################################################################################
# log.txt   -> tudo que o jogo imprime (print), com hora em cada linha.
# debug.txt -> log.txt + erros, tracebacks, diagnostico de camera e sistema.
# Os arquivos ficam ao lado do executavel e nunca passam de 2048 KB: quando
# passam, as linhas mais antigas sao apagadas.
import atexit
import datetime
import faulthandler
import os
import sys
import threading
import traceback

MAX_BYTES = 2048 * 1024
KEEP_BYTES = MAX_BYTES // 2

_lock = threading.RLock()
_log = None
_debug = None


def _aparar(caminho):
    # Mantem apenas a metade final do arquivo, comecando em uma linha inteira.
    try:
        if os.path.getsize(caminho) <= MAX_BYTES:
            return
        with open(caminho, 'rb') as f:
            f.seek(-KEEP_BYTES, os.SEEK_END)
            dados = f.read()
        quebra = dados.find(b'\n')
        if quebra != -1:
            dados = dados[quebra + 1:]
        with open(caminho, 'wb') as f:
            f.write(dados)
    except OSError:
        pass


class _Arquivo:
    def __init__(self, caminho, ao_reabrir=None):
        self.caminho = caminho
        self.ao_reabrir = ao_reabrir
        _aparar(caminho)
        self.f = open(caminho, 'a', encoding='utf-8', errors='replace')
        self._inicio_de_linha = True
        self._escritas = 0

    def write(self, texto):
        with _lock:
            try:
                for linha in texto.splitlines(True):
                    if self._inicio_de_linha:
                        self.f.write(datetime.datetime.now().strftime('%H:%M:%S '))
                    self.f.write(linha)
                    self._inicio_de_linha = linha.endswith('\n')
                self.f.flush()
                self._escritas += 1
                if self._escritas % 200 == 0 and self.f.tell() > MAX_BYTES:
                    self.f.close()
                    _aparar(self.caminho)
                    self.f = open(self.caminho, 'a', encoding='utf-8', errors='replace')
                    if self.ao_reabrir:
                        self.ao_reabrir(self.f)
            except Exception:
                pass

    def flush(self):
        with _lock:
            try:
                self.f.flush()
            except Exception:
                pass

    def isatty(self):
        return False


class _Duplicador:
    # Faz o papel de sys.stdout/sys.stderr escrevendo em mais de um arquivo.
    def __init__(self, *alvos):
        self.alvos = alvos

    def write(self, texto):
        for alvo in self.alvos:
            alvo.write(texto)

    def flush(self):
        for alvo in self.alvos:
            alvo.flush()

    def isatty(self):
        return False


def debug(mensagem):
    # Escreve somente no debug.txt.
    if _debug is not None:
        _debug.write(str(mensagem) + '\n')


def _registrar_excecao(tipo, valor, tb):
    texto = ''.join(traceback.format_exception(tipo, valor, tb))
    debug('ERRO NAO TRATADO:\n' + texto)
    if _log is not None:
        _log.write(f'ERRO NAO TRATADO: {valor!r} (detalhes no debug.txt)\n')


def hook_tk(tipo, valor, tb):
    # Para root.report_callback_exception do tkinter.
    _registrar_excecao(tipo, valor, tb)


def _hook_thread(args):
    _registrar_excecao(args.exc_type, args.exc_value, args.exc_traceback)


def _rearmar_faulthandler(novo_arquivo):
    try:
        faulthandler.enable(file=novo_arquivo)
    except Exception:
        pass


def init():
    global _log, _debug
    if _debug is not None:
        return
    _debug = _Arquivo('debug.txt', ao_reabrir=_rearmar_faulthandler)
    _log = _Arquivo('log.txt')
    sys.stdout = _Duplicador(_log, _debug)
    sys.stderr = _Duplicador(_debug)
    sys.excepthook = _registrar_excecao
    try:
        threading.excepthook = _hook_thread
    except Exception:
        pass
    try:
        faulthandler.enable(file=_debug.f)
    except Exception:
        pass
    atexit.register(_encerrar)

    import platform
    debug('=' * 70)
    debug(f'T-TEA iniciado em {datetime.datetime.now():%Y-%m-%d %H:%M:%S}')
    debug(f'Sistema: {platform.platform()}')
    debug(f'Python {platform.python_version()} | frozen={getattr(sys, "frozen", False)}')
    debug(f'Executavel: {sys.executable}')
    debug(f'Pasta de trabalho: {os.getcwd()}')


def _encerrar():
    debug(f'T-TEA encerrado em {datetime.datetime.now():%Y-%m-%d %H:%M:%S}')
    for arquivo in (_log, _debug):
        if arquivo is not None:
            arquivo.flush()
