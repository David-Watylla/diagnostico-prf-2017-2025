import os
import glob
import shutil
import zipfile

def descompactar_e_organizar(pasta_origem, pasta_destino="./dados_prf_brutos"):
    """
    Busca arquivos .zip na pasta_origem, extrai todos os CSVs encontrados
    e os consolida na pasta_destino.
    """
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Localiza arquivos .zip na pasta de origem indicada
    arquivos_zip = glob.glob(os.path.join(pasta_origem, "*acidentes*.zip")) + \
               glob.glob(os.path.join(pasta_origem, "*datatran*.zip"))
    
    if not arquivos_zip:
        print(f"[!] Nenhum arquivo .zip encontrado no diretório: '{os.path.abspath(pasta_origem)}'")
        return

    print(f"[*] Encontrados {len(arquivos_zip)} arquivos .zip para processar...\n")
    temp_dir = os.path.join(pasta_destino, "_temp_extract")

    for caminho_zip in arquivos_zip:
        nome_zip = os.path.basename(caminho_zip)
        print(f"Extraindo: {nome_zip}...")
        
        try:
            with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                
                # Procura todos os CSVs extraídos dentro da pasta temporária
                for raiz, _, arquivos in os.walk(temp_dir):
                    for arquivo in arquivos:
                        if arquivo.lower().endswith(".csv"):
                            origem_csv = os.path.join(raiz, arquivo)
                            destino_csv = os.path.join(pasta_destino, arquivo)
                            
                            # Move o CSV para a pasta dados_prf_brutos
                            shutil.move(origem_csv, destino_csv)
                            print(f"  -> Movido com sucesso: {arquivo}")
        except Exception as e:
            print(f"  [X] Erro ao extrair {nome_zip}: {e}")
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    print("\n[✓] Descompactação concluída!")
    print(f"[✓] Todos os arquivos CSV estão salvos em: {os.path.abspath(pasta_destino)}")

if __name__ == "__main__":
    # Ajuste o caminho da pasta de Downloads do seu usuário no Windows:
    # Use r"..." para o Python aceitar barras do Windows sem dar warning
    PASTA_DOWNLOADS = r"C:\Users\watyl\Downloads"
    
    descompactar_e_organizar(pasta_origem=PASTA_DOWNLOADS, pasta_destino="./dados_prf_brutos")