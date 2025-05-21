import logging

global logger

# Fun��o para configurar o logging
def setup_logging(app_name:str):
    # Obter o logger raiz ou um logger espec�fico para sua aplica��o
    # Usar um logger nomeado para a aplica��o � uma boa pr�tica
    logger = logging.getLogger(app_name) # Ou logging.getLogger() para o logger raiz
    logger.setLevel(logging.DEBUG)  # N�vel mais baixo para o logger processar

    # Evitar adicionar m�ltiplos handlers se esta fun��o for chamada v�rias vezes
    if logger.hasHandlers():
        logger.handlers.clear()

    # --- Configura��o do FileHandler (para gravar em arquivo) ---
    file_handler = logging.FileHandler(f'{app_name}.log', mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Grava tudo a partir de DEBUG no arquivo

    # Formato das mensagens no arquivo
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # --- Configura��o do StreamHandler (para exibir na tela) ---
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)  # Exibe a partir de INFO na tela

    # Formato das mensagens na tela (pode ser mais simples)
    stream_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    # Mensagem de que o logging foi configurado (opcional)
    logger.info("Sistema de logging configurado.")

    # return logger