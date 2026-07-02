import os
import sys
import argparse
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from PIL import Image, ImageEnhance, ImageFilter
from pillow_heif import register_heif_opener
import pillow_heif
import rawpy
import numpy as np

# Habilita o suporte a arquivos HEIF/HEIC no Pillow
register_heif_opener()

@dataclass
class ParametrosConversao:
    """Classe para armazenar parâmetros de conversão de imagem."""
    resolucao: Optional[Tuple[int, int]] = None
    megapixels: Optional[float] = None
    qualidade: int = 95
    otimizar: bool = True
    progressivo: bool = False
    comprimir_nivel: int = 6
    transparencia: bool = True
    
    # Ajustes de imagem
    brilho: float = 1.0
    contraste: float = 1.0
    saturacao: float = 1.0
    nitidez: float = 1.0
    
    # Parâmetros HSV
    matiz: int = 0
    saturacao_hsv: int = 0
    valor_hsv: int = 0

class ProcessadorImagem:
    """Classe para processar e ajustar imagens."""
    
    @staticmethod
    def aplicar_ajustes(imagem: Image.Image, params: ParametrosConversao) -> Image.Image:
        """Aplica ajustes de brilho, contraste, saturação e nitidez."""
        if params.brilho != 1.0:
            enhancer = ImageEnhance.Brightness(imagem)
            imagem = enhancer.enhance(params.brilho)
        
        if params.contraste != 1.0:
            enhancer = ImageEnhance.Contrast(imagem)
            imagem = enhancer.enhance(params.contraste)
        
        if params.saturacao != 1.0:
            enhancer = ImageEnhance.Color(imagem)
            imagem = enhancer.enhance(params.saturacao)
        
        if params.nitidez != 1.0:
            enhancer = ImageEnhance.Sharpness(imagem)
            imagem = enhancer.enhance(params.nitidez)
        
        return imagem
    
    @staticmethod
    def ajustar_hsv(imagem: Image.Image, params: ParametrosConversao) -> Image.Image:
        """Ajusta valores HSV da imagem."""
        if params.matiz == 0 and params.saturacao_hsv == 0 and params.valor_hsv == 0:
            return imagem
        
        # Converte para HSV
        hsv = imagem.convert('HSV')
        h, s, v = hsv.split()
        
        # Aplica ajustes
        if params.matiz != 0:
            h = h.point(lambda x: (x + params.matiz) % 256)
        
        if params.saturacao_hsv != 0:
            s = s.point(lambda x: max(0, min(255, x + params.saturacao_hsv)))
        
        if params.valor_hsv != 0:
            v = v.point(lambda x: max(0, min(255, x + params.valor_hsv)))
        
        # Reconstroi a imagem
        hsv_ajustada = Image.merge('HSV', (h, s, v))
        return hsv_ajustada.convert('RGB')
    
    @staticmethod
    def redimensionar_imagem(imagem: Image.Image, params: ParametrosConversao) -> Image.Image:
        """Redimensiona a imagem conforme os parâmetros especificados."""
        if params.resolucao:
            return imagem.resize(params.resolucao, Image.Resampling.LANCZOS)
        
        if params.megapixels:
            largura, altura = imagem.size
            megapixels_atual = (largura * altura) / 1_000_000
            
            if megapixels_atual > params.megapixels:
                fator = (params.megapixels / megapixels_atual) ** 0.5
                nova_largura = int(largura * fator)
                nova_altura = int(altura * fator)
                return imagem.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)
        
        return imagem

class ConversorImagem:
    """Classe principal para conversão de imagens entre diversos formatos."""
    
    FORMATOS_SUPORTADOS = {
        '.jpg', '.jpeg', '.jpe', '.png', '.bmp', '.gif', '.ico', '.jp2',
        '.webp', '.tif', '.tiff', '.heic', '.heif', '.raw', '.cr2', '.nef', '.dng'
    }
    
    PARAMETROS_PADRAO = {
        'jpeg': {'quality': 95, 'optimize': True, 'progressive': True},
        'png': {'optimize': True, 'compress_level': 6},
        'webp': {'quality': 95, 'method': 6, 'lossless': False},
        'tiff': {'compression': 'lzw', 'quality': 95},
        'bmp': {},
        'gif': {'optimize': True, 'save_all': True},
        'ico': {'sizes': [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128)]},
        'jp2': {'quality_mode': 'rates', 'quality_layers': [95]},
        'heic': {'quality': 95},
        'heif': {'quality': 95}
    }
    
    def __init__(self):
        self.processador = ProcessadorImagem()
        self.arquivos_convertidos = 0
        self.arquivos_com_erro = 0
    
    def obter_extensoes_formato(self, formato_origem: str) -> List[str]:
        """Retorna lista de extensões para um formato específico."""
        formato_origem = formato_origem.lower().strip('.')
        
        mapeamento = {
            'jpeg': ['.jpg', '.jpeg', '.jpe'],
            'jpg': ['.jpg', '.jpeg', '.jpe'],
            'tiff': ['.tif', '.tiff'],
            'tif': ['.tif', '.tiff'],
            'heic': ['.heic', '.heif'],
            'heif': ['.heic', '.heif'],
            'raw': ['.raw', '.cr2', '.nef', '.dng']
        }
        
        return mapeamento.get(formato_origem, [f'.{formato_origem}'])
    
    def eh_arquivo_suportado(self, caminho_arquivo: str, extensoes_origem: List[str]) -> bool:
        """Verifica se o arquivo é de um formato suportado."""
        extensao = os.path.splitext(caminho_arquivo)[1].lower()
        return extensao in extensoes_origem
    
    def listar_arquivos(self, pasta_origem: str, extensoes_origem: List[str], incluir_subpastas: bool = False) -> List[str]:
        """Lista todos os arquivos com as extensões especificadas."""
        arquivos = []
        
        if incluir_subpastas:
            for root, dirs, files in os.walk(pasta_origem):
                for arquivo in files:
                    caminho_completo = os.path.join(root, arquivo)
                    if self.eh_arquivo_suportado(caminho_completo, extensoes_origem):
                        arquivos.append(caminho_completo)
        else:
            for arquivo in os.listdir(pasta_origem):
                caminho_completo = os.path.join(pasta_origem, arquivo)
                if os.path.isfile(caminho_completo) and self.eh_arquivo_suportado(caminho_completo, extensoes_origem):
                    arquivos.append(caminho_completo)
        
        return arquivos
    
    def carregar_imagem_raw(self, caminho_arquivo: str) -> Image.Image:
        """Carrega arquivo RAW usando rawpy."""
        with rawpy.imread(caminho_arquivo) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,
                half_size=False,
                no_auto_bright=True,
                output_bps=16
            )
        return Image.fromarray(rgb)
    
    def carregar_imagem(self, caminho_arquivo: str) -> Image.Image:
        """Carrega uma imagem de qualquer formato suportado."""
        extensao = os.path.splitext(caminho_arquivo)[1].lower()
        
        if extensao in ['.raw', '.cr2', '.nef', '.dng']:
            return self.carregar_imagem_raw(caminho_arquivo)
        else:
            return Image.open(caminho_arquivo)
    
    def obter_parametros_salvamento(self, formato_destino: str, params: ParametrosConversao) -> Dict:
        """Obtém parâmetros de salvamento específicos para cada formato."""
        formato = formato_destino.lower().replace('.', '')
        parametros_base = self.PARAMETROS_PADRAO.get(formato, {}).copy()
        
        # Aplica parâmetros personalizados
        if formato in ['jpeg', 'jpg', 'webp', 'heic', 'heif']:
            parametros_base['quality'] = params.qualidade
        
        if formato == 'png':
            parametros_base['optimize'] = params.otimizar
            parametros_base['compress_level'] = params.comprimir_nivel
        
        if formato in ['jpeg', 'jpg']:
            parametros_base['progressive'] = params.progressivo
            parametros_base['optimize'] = params.otimizar
        
        return parametros_base
    
    def obter_formato_salvamento(self, formato_destino: str) -> str:
        """Obtém o formato correto para salvamento no Pillow."""
        formato = formato_destino.lower().replace('.', '')
        
        mapeamento_formatos = {
            'jpg': 'JPEG',
            'jpeg': 'JPEG',
            'jpe': 'JPEG',
            'png': 'PNG',
            'bmp': 'BMP',
            'gif': 'GIF',
            'webp': 'WEBP',
            'tiff': 'TIFF',
            'tif': 'TIFF',
            'ico': 'ICO',
            'jp2': 'JPEG2000',
            'heic': 'HEIF',
            'heif': 'HEIF'
        }
        
        return mapeamento_formatos.get(formato, formato.upper())
    
    def verificar_suporte_formato(self, formato_destino: str) -> bool:
        """Verifica se o formato de destino é suportado para salvamento."""
        # Para HEIC/HEIF, verifica se pillow_heif está disponível
        if formato_destino.lower() in ['.heic', '.heif']:
            return True  # pillow_heif suporta salvamento
        
        try:
            # Cria uma imagem de teste pequena
            test_image = Image.new('RGB', (1, 1), color='white')
            formato_pil = self.obter_formato_salvamento(formato_destino)
            
            # Tenta salvar em um buffer para verificar suporte
            import io
            buffer = io.BytesIO()
            test_image.save(buffer, format=formato_pil)
            return True
        except Exception:
            return False
    
    def salvar_heif(self, imagem: Image.Image, caminho_destino: str, params: ParametrosConversao) -> None:
        """Salva imagem no formato HEIF/HEIC usando pillow_heif diretamente."""
        # Converte PIL Image para pillow_heif
        if imagem.mode not in ['RGB', 'RGBA']:
            if imagem.mode == 'P':
                imagem = imagem.convert('RGBA')
            else:
                imagem = imagem.convert('RGB')
        
        # Cria HeifFile a partir da imagem PIL
        heif_file = pillow_heif.from_pillow(imagem)
        
        # Configura parâmetros de qualidade
        if hasattr(heif_file, 'encoders') and heif_file.encoders:
            for encoder in heif_file.encoders:
                if hasattr(encoder, 'set_quality'):
                    encoder.set_quality(params.qualidade)
        
        # Salva o arquivo
        heif_file.save(caminho_destino, quality=params.qualidade)
    
    def converter_arquivo(
        self, 
        caminho_origem: str, 
        caminho_destino: str, 
        formato_destino: str, 
        params: ParametrosConversao = None
    ) -> bool:
        """Converte um único arquivo de imagem."""
        if params is None:
            params = ParametrosConversao()
        
        try:
            # Carrega a imagem
            imagem = self.carregar_imagem(caminho_origem)
            
            # Aplica redimensionamento
            imagem = self.processador.redimensionar_imagem(imagem, params)
            
            # Aplica ajustes de imagem
            imagem = self.processador.aplicar_ajustes(imagem, params)
            
            # Aplica ajustes HSV
            imagem = self.processador.ajustar_hsv(imagem, params)
            
            # Cria diretório de destino se não existir
            os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)
            
            # Tratamento especial para HEIC/HEIF
            if formato_destino.lower() in ['.heic', '.heif']:
                self.salvar_heif(imagem, caminho_destino, params)
            else:
                # Obtém o formato de destino
                formato_pil = self.obter_formato_salvamento(formato_destino)
                
                # Converte para RGB se necessário (exceto para PNG com transparência)
                if formato_destino.lower() not in ['.png', '.gif', '.ico'] and imagem.mode in ['RGBA', 'LA', 'P']:
                    if imagem.mode == 'P':
                        imagem = imagem.convert('RGBA')
                    
                    if params.transparencia and imagem.mode == 'RGBA':
                        # Cria fundo branco para transparência
                        fundo = Image.new('RGB', imagem.size, (255, 255, 255))
                        fundo.paste(imagem, mask=imagem.split()[-1])
                        imagem = fundo
                    else:
                        imagem = imagem.convert('RGB')
                
                # Obtém parâmetros de salvamento
                parametros_salvamento = self.obter_parametros_salvamento(formato_destino, params)
                
                # Salva a imagem usando Pillow
                imagem.save(caminho_destino, formato_pil, **parametros_salvamento)
            
            self.arquivos_convertidos += 1
            return True
            
        except Exception as e:
            print(f"[ERRO] Falha ao converter {os.path.basename(caminho_origem)}: {e}")
            self.arquivos_com_erro += 1
            return False
    
    def converter_pasta(
        self,
        pasta_origem: str,
        pasta_destino: str,
        formato_origem: str,
        formato_destino: str,
        incluir_subpastas: bool = False,
        params: ParametrosConversao = None
    ) -> Tuple[int, int]:
        """Converte todos os arquivos de uma pasta."""
        if not os.path.exists(pasta_origem):
            raise FileNotFoundError(f"Pasta de origem '{pasta_origem}' não existe.")
        
        if params is None:
            params = ParametrosConversao()
        
        # Verifica se o formato de destino é suportado
        if not self.verificar_suporte_formato(formato_destino):
            print(f"[AVISO] Formato {formato_destino.upper()} pode não ser totalmente suportado para salvamento.")
        
        # Reset contadores
        self.arquivos_convertidos = 0
        self.arquivos_com_erro = 0
        
        # Obtém extensões do formato de origem
        extensoes_origem = self.obter_extensoes_formato(formato_origem)
        
        # Lista arquivos para conversão
        arquivos = self.listar_arquivos(pasta_origem, extensoes_origem, incluir_subpastas)
        
        if not arquivos:
            print(f"Nenhum arquivo {formato_origem.upper()} encontrado na pasta de origem.")
            return 0, 0
        
        # Cria pasta de destino
        os.makedirs(pasta_destino, exist_ok=True)
        
        print(f"Iniciando conversão de {len(arquivos)} arquivos de {formato_origem.upper()} para {formato_destino.upper()}...")
        
        # Converte cada arquivo
        for caminho_origem in arquivos:
            nome_base = os.path.splitext(os.path.basename(caminho_origem))[0]
            nome_destino = f"{nome_base}{formato_destino}"
            
            if incluir_subpastas:
                # Mantém estrutura de subpastas
                caminho_relativo = os.path.relpath(os.path.dirname(caminho_origem), pasta_origem)
                pasta_destino_arquivo = os.path.join(pasta_destino, caminho_relativo)
                caminho_destino = os.path.join(pasta_destino_arquivo, nome_destino)
            else:
                caminho_destino = os.path.join(pasta_destino, nome_destino)
            
            sucesso = self.converter_arquivo(caminho_origem, caminho_destino, formato_destino, params)
            
            if sucesso:
                print(f"[OK] {os.path.basename(caminho_origem)} -> {nome_destino}")
        
        print(f"\nConversão concluída: {self.arquivos_convertidos} sucessos, {self.arquivos_com_erro} erros")
        return self.arquivos_convertidos, self.arquivos_com_erro

def main():
    """Função principal com interface de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Conversor universal de imagens - Suporte a múltiplos formatos"
    )
    
    # Parâmetros obrigatórios
    parser.add_argument("origem", help="Caminho do arquivo ou pasta de origem")
    parser.add_argument("destino", help="Caminho do arquivo ou pasta de destino")
    parser.add_argument("formato_origem", help="Formato de origem (ex: heic, jpg, png)")
    parser.add_argument("formato_destino", help="Formato de destino (ex: jpg, png, webp)")
    
    # Parâmetros opcionais - qualidade e compressão
    parser.add_argument("--qualidade", type=int, default=95, help="Qualidade (1-100). Padrão: 95")
    parser.add_argument("--subpastas", action="store_true", help="Incluir subpastas na conversão")
    
    # Parâmetros de redimensionamento
    parser.add_argument("--resolucao", nargs=2, type=int, metavar=('LARGURA', 'ALTURA'), 
                       help="Resolução de saída (largura altura)")
    parser.add_argument("--megapixels", type=float, help="Máximo de megapixels na saída")
    
    # Ajustes de imagem
    parser.add_argument("--brilho", type=float, default=1.0, help="Ajuste de brilho (0.5-2.0). Padrão: 1.0")
    parser.add_argument("--contraste", type=float, default=1.0, help="Ajuste de contraste (0.5-2.0). Padrão: 1.0")
    parser.add_argument("--saturacao", type=float, default=1.0, help="Ajuste de saturação (0.0-2.0). Padrão: 1.0")
    parser.add_argument("--nitidez", type=float, default=1.0, help="Ajuste de nitidez (0.0-2.0). Padrão: 1.0")
    
    # Ajustes HSV
    parser.add_argument("--matiz", type=int, default=0, help="Ajuste de matiz (-180 a 180). Padrão: 0")
    parser.add_argument("--saturacao-hsv", type=int, default=0, help="Ajuste de saturação HSV (-100 a 100). Padrão: 0")
    parser.add_argument("--valor-hsv", type=int, default=0, help="Ajuste de valor HSV (-100 a 100). Padrão: 0")

    args = parser.parse_args()
    
    # Configura parâmetros de conversão
    params = ParametrosConversao(
        resolucao=tuple(args.resolucao) if args.resolucao else None,
        megapixels=args.megapixels,
        qualidade=args.qualidade,
        brilho=args.brilho,
        contraste=args.contraste,
        saturacao=args.saturacao,
        nitidez=args.nitidez,
        matiz=args.matiz,
        saturacao_hsv=args.saturacao_hsv,
        valor_hsv=args.valor_hsv
    )
    
    # Inicializa conversor
    conversor = ConversorImagem()
    
    # Normaliza formatos (adiciona ponto se necessário)
    if not args.formato_destino.startswith('.'):
        args.formato_destino = f".{args.formato_destino}"
    
    try:
        if os.path.isfile(args.origem):
            # Converte um único arquivo
            nome_base = os.path.splitext(os.path.basename(args.origem))[0]
            if os.path.isdir(args.destino):
                # Destino é pasta
                caminho_destino = os.path.join(args.destino, f"{nome_base}{args.formato_destino}")
            else:
                # Destino é arquivo específico
                caminho_destino = args.destino
            
            sucesso = conversor.converter_arquivo(args.origem, caminho_destino, args.formato_destino, params)
            if sucesso:
                print(f"[OK] Arquivo convertido: {os.path.basename(args.origem)} -> {os.path.basename(caminho_destino)}")
        
        elif os.path.isdir(args.origem):
            # Converte pasta inteira
            conversor.converter_pasta(
                args.origem, 
                args.destino, 
                args.formato_origem, 
                args.formato_destino, 
                args.subpastas, 
                params
            )
        else:
            print(f"Erro: '{args.origem}' não é um arquivo ou pasta válida.")
            sys.exit(1)
    
    except Exception as e:
        print(f"Erro durante a conversão: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()