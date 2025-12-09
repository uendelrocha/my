import logging
import sys
import os

global logger

def setup_logging(app_name:str, log_to_file:bool=True, log_dir:str='.'):
    """
    Configura o sistema de logging.
    
    Args:
        app_name: Nome da aplicação (usado no nome do arquivo de log)
        log_to_file: Se True, grava logs em arquivo (útil para desabilitar no Colab)
        log_dir: Diretório onde o arquivo de log será salvo
    """
    # Obter o logger nomeado para a aplicação
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)

    # Evitar adicionar múltiplos handlers se esta função for chamada várias vezes
    if logger.hasHandlers():
        logger.handlers.clear()

    # --- Configuração do FileHandler (para gravar em arquivo) ---
    if log_to_file:
        # Criar diretório se não existir
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'{app_name}.log')
        
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Formato das mensagens no arquivo
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # --- Configuração do StreamHandler (para exibir na tela/notebook) ---
    stream_handler = logging.StreamHandler(sys.stdout)  # Usar sys.stdout explicitamente
    stream_handler.setLevel(logging.INFO)

    # Formato das mensagens na tela (mais simples para notebooks)
    stream_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    # Mensagem de que o logging foi configurado
    logger.info(f"Sistema de logging configurado para '{app_name}'")
    if log_to_file:
        logger.info(f"Logs sendo gravados em: {log_file}")

    return logger

# Função auxiliar para uso no Colab
def setup_colab_logging(app_name:str, drive_path:str=None):
    """
    Configura logging para Google Colab, opcionalmente salvando no Google Drive.
    
    Args:
        app_name: Nome da aplicação
        drive_path: Caminho no Google Drive (ex: '/content/drive/MyDrive/logs')
                    Se None, desabilita gravação em arquivo
    """
    if drive_path:
        # Verifica se o Google Drive está montado
        if not os.path.exists('/content/drive'):
            print("⚠️ Google Drive não está montado. Execute:")
            print("   from google.colab import drive")
            print("   drive.mount('/content/drive')")
            log_to_file = False
            log_dir = '.'
        else:
            log_to_file = True
            log_dir = drive_path
    else:
        log_to_file = False
        log_dir = '.'
    
    return setup_logging(app_name, log_to_file=log_to_file, log_dir=log_dir)