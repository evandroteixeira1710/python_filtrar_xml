import lxml.html

# --- Configuração ---

# 1. O arquivo HTML local que você quer ler
arquivo_entrada = "dependency-check-report.html"

# 2. O arquivo HTML que você quer criar com o resultado
arquivo_saida = "resultado.html"

# 3. Sua consulta XPath.
#    Esta consulta continua a mesma: ela seleciona a *tabela inteira*.
xpath_query = "//*[@id='summaryTable']"


# --------------------

try:
    # 4. Analisa (parse) o arquivo HTML de entrada
    tree = lxml.html.parse(arquivo_entrada)

    # 5. Executa a consulta XPath
    resultados = tree.xpath(xpath_query)

    if not resultados:
        print(f"Aviso: Nenhum elemento encontrado com o XPath: {xpath_query}")
    else:
        # 6. Pega o *primeiro* resultado encontrado (a tabela)
        elemento_extraido = resultados[0]

        # --- INÍCIO DA MODIFICAÇÃO (NOVO FILTRO) ---
        
        # 6a. Define o XPath para encontrar linhas (tr) ONDE a 7ª célula (td)
        #     tem o texto "0" (ignorando espaços em branco).
        #     O '.' no início ('.//tr') é crucial: significa "procure DENTRO do elemento_extraido".
        xpath_filtro_linhas = ".//tr[td[5][normalize-space(.) = '0']]"
        
        # 6b. Encontra todas as linhas que correspondem ao filtro de remoção
        linhas_para_remover = elemento_extraido.xpath(xpath_filtro_linhas)
        
        print(f"Encontradas {len(linhas_para_remover)} linhas com '0' na coluna 7. Removendo...")

        # 6c. Itera sobre as linhas e as remove da árvore HTML
        for linha in linhas_para_remover:
            # Pega o elemento 'pai' da linha (ex: <tbody> ou <table>)
            pai = linha.getparent()
            # Remove a linha do seu pai
            if pai is not None:
                pai.remove(linha)
                
        # --- FIM DA MODIFICAÇÃO ---

        # 7. Converte o elemento *modificado* de volta para uma string HTML
        html_extraido = lxml.html.tostring(elemento_extraido, encoding="unicode", pretty_print=True)

        # 8. (Opcional) Cria um HTML 'completo' para o arquivo de saída
        html_final = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Resultado da Extração Filtrada</title>
    <style>
      body {{ font-family: sans-serif; }}
      table {{ border-collapse: collapse; margin: 10px; }}
      th, td {{ border: 1px solid #ccc; padding: 4px 8px; }}
      tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Elemento Extraído (com linhas filtradas):</h1>
    {html_extraido}
</body>
</html>
"""

        # 9. Escreve o HTML final no arquivo de saída
        with open(arquivo_saida, "w", encoding="utf-8") as f:
            f.write(html_final)
        
        print(f"Sucesso! Elemento filtrado e salvo em '{arquivo_saida}'")

except IOError:
    print(f"Erro: Não foi possível encontrar ou ler o arquivo '{arquivo_entrada}'")
except lxml.etree.XPathError as e:
    print(f"Erro: O XPath fornecido é inválido: {e}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")