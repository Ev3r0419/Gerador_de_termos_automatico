# ============================================================
# 👤 SERVIÇO DE USUÁRIO — Identificação e Localização de Drive
# ============================================================
# Módulo responsável por toda a lógica de identificação do
# usuário logado e localização da pasta do Google Drive.
# Separado da interface gráfica para promover reutilização
# e separação de responsabilidades.
# ============================================================

import os
import getpass
import shutil
from pathlib import Path


# ============================================================
# 🔍 IDENTIFICAÇÃO DO USUÁRIO
# ============================================================

def obter_usuario_sistema():
    """Obtém o nome de login do usuário atualmente logado no SO.
    Compatível com Windows, Linux e macOS.

    Tenta os seguintes métodos em ordem de prioridade:
      1. os.getlogin()      — método nativo do SO
      2. getpass.getuser()   — fallback cross-platform
      3. Variável USERNAME   — fallback específico do Windows

    Returns:
        str: Nome de login do usuário, ou "Desconhecido" se falhar.
    """
    try:
        return os.getlogin()
    except Exception:
        pass

    try:
        usuario = getpass.getuser()
        if usuario:
            return usuario
    except Exception:
        pass

    return os.getenv("USERNAME") or "Desconhecido"


def obter_nome_pasta_drive():
    """Deriva o nome da pasta do Google Drive a partir do
    usuário logado no sistema operacional.

    Capitaliza o nome de login para usar como nome da pasta.
    Exemplo: "eversonsilva" → "Eversonsilva"

    Returns:
        str: Nome capitalizado do usuário para uso como pasta.
    """
    usuario = obter_usuario_sistema()
    return usuario.capitalize()


# ============================================================
# 📂 LOCALIZAÇÃO DO GOOGLE DRIVE
# ============================================================

def localizar_pasta_drive_usuario(nome_drive):
    """Localiza a pasta do Google Drive no sistema de arquivos.

    Busca em múltiplos caminhos conhecidos onde o Google Drive
    pode estar montado (Windows, DriveFS, etc.).

    Args:
        nome_drive (str): Nome da subpasta dentro do Google Drive.

    Returns:
        Path: Caminho absoluto da pasta encontrada.

    Raises:
        FileNotFoundError: Se nenhum caminho válido for encontrado.
    """
    home = Path.home()
    caminhos_possiveis = [
        Path("G:/Meu Drive") / nome_drive,
        Path("D:/Meu Drive") / nome_drive,
        home / "Google Drive" / nome_drive,
        home / "Meu Drive" / nome_drive,
    ]

    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        drivefs = Path(local_appdata) / "Google" / "DriveFS"
        if drivefs.exists():
            for subdir in drivefs.iterdir():
                if subdir.is_dir():
                    caminho = subdir / "My Drive" / nome_drive
                    caminhos_possiveis.append(caminho)

    for caminho in caminhos_possiveis:
        if caminho.exists():
            return caminho

    raise FileNotFoundError(f"Não foi possível localizar a pasta 'Meu Drive/{nome_drive}'.")


def mover_para_pasta_drive(arquivo_pdf, pasta_drive):
    """Move um arquivo PDF para a pasta do Google Drive.

    Args:
        arquivo_pdf (Path): Caminho do arquivo PDF a ser movido.
        pasta_drive (Path): Caminho da pasta de destino no Drive.

    Returns:
        Path: Caminho final do arquivo no destino.
    """
    destino = pasta_drive / arquivo_pdf.name
    shutil.move(str(arquivo_pdf), str(destino))
    return destino
