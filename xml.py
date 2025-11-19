import lxml.html
import socket
import re # Usaremos 're' para garantir um nome de arquivo seguro.

# --- Configuração ---

# 1. O arquivo HTML local que você quer ler
arquivo_entrada = "dependency-check-report.html"

# 2. Obtém o nome do computador local (hostname)
try:
    hostname_raw = socket.gethostname()
except socket.error:
    hostname_raw = "local_maquina" # Fallback em caso de erro

# 3. Sanitiza o nome do host para uso no nome do arquivo:
#    - Converte para minúsculas.
#    - Substitui qualquer caractere que não seja letra, número, hífen ou underscore por um hífen.
hostname_sanitized = re.sub(r'[^a-z0-9-_]', '-', hostname_raw.lower())

# 4. O arquivo HTML que você quer criar com o resultado.
#    Agora ele incluirá o hostname. Exemplo: "meu-pc-resultado-filtrado.html"
arquivo_saida = f"{hostname_sanitized}-resultado-filtrado.html"

# 5. Sua consulta XPath.
#    Esta consulta continua a mesma: ela seleciona a *tabela inteira*.
xpath_query = "//*[@id='summaryTable']"


# --------------------

print(f"Nome do Host Detectado: {hostname_raw}")
print(f"Arquivo de Saída Gerado: {arquivo_saida}")


try:
    # 6. Analisa (parse) o arquivo HTML de entrada
    tree = lxml.html.parse(arquivo_entrada)

    # 7. Executa a consulta XPath
    resultados = tree.xpath(xpath_query)

    if not resultados:
        print(f"Aviso: Nenhum elemento encontrado com o XPath: {xpath_query}")
    else:
        # 8. Pega o *primeiro* resultado encontrado (a tabela)
        elemento_extraido = resultados[0]

        # --- FILTRO DE LINHAS (Remove linhas com '0' na 5ª coluna de td) ---

        # 8a. Define o XPath para encontrar linhas (tr) ONDE a 5ª célula (td)
        #     tem o texto "0" (ignorando espaços em branco).
        xpath_filtro_linhas = ".//tr[td[5][normalize-space(.) = '0']]"

        # 8b. Encontra todas as linhas que correspondem ao filtro de remoção
        linhas_para_remover = elemento_extraido.xpath(xpath_filtro_linhas)

        print(f"Encontradas {len(linhas_para_remover)} linhas com '0' na coluna 5. Removendo...")

        # 8c. Itera sobre as linhas e as remove da árvore HTML
        for linha in linhas_para_remover:
            # Pega o elemento 'pai' da linha (ex: <tbody> ou <table>)
            pai = linha.getparent()
            # Remove a linha do seu pai
            if pai is not None:
                pai.remove(linha)

        # --- FIM DO FILTRO ---

        # 9. Converte o elemento *modificado* de volta para uma string HTML
        html_extraido = lxml.html.tostring(elemento_extraido, encoding="unicode", pretty_print=True)

        # 10. (Opcional) Cria um HTML 'completo' para o arquivo de saída
        html_final = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Resultado da Extração Filtrada ({hostname_raw})</title>
    <style>
      body {{ font-family: sans-serif; margin: 20px; }}
      h1 {{ color: #1e40af; border-bottom: 2px solid #bfdbfe; padding-bottom: 5px; }}
      table {{ 
        border-collapse: collapse; 
        width: 100%; 
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 15px;
      }}
      th, td {{ 
        border: 1px solid #e5e7eb; 
        padding: 8px 12px; 
        text-align: left;
      }}
      th {{ 
        background-color: #eff6ff; 
        color: #1e40af; 
        font-weight: bold;
      }}
      tr:nth-child(even) {{ background-color: #f9fafb; }}
      tr:hover {{ background-color: #f3f4f6; }}
    </style>
</head>
<body>
    <h1>Relatório de Dependência Filtrado (Host: {hostname_raw})</h1>
    {html_extraido}
</body>
</html>
"""

        # 11. Escreve o HTML final no arquivo de saída
        with open(arquivo_saida, "w", encoding="utf-8") as f:
            f.write(html_final)

        print(f"Sucesso! Elemento filtrado e salvo em '{arquivo_saida}'")

except IOError:
    print(f"Erro: Não foi possível encontrar ou ler o arquivo de entrada '{arquivo_entrada}'")
except lxml.etree.XPathError as e:
    print(f"Erro: O XPath fornecido é inválido: {e}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")