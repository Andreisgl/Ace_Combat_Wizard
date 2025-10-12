import re
import csv

def convert_with_specific_delimiter(input_txt_file, output_csv_file):
    """
    Converte um arquivo de texto para CSV, usando uma sequência de 5 ou mais
    espaços como o delimitador de coluna.

    Args:
        input_txt_file (str): O caminho para o arquivo de texto de entrada.
        output_csv_file (str): O caminho para o arquivo CSV de saída a ser criado.
    """
    processed_data = []
    
    # Regex para encontrar 5 ou mais espaços seguidos. Este será nosso separador.
    delimiter_regex = re.compile(r'\s{5,}')

    print(f"Lendo o arquivo de entrada: {input_txt_file}")
    try:
        with open(input_txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Ignora linhas de cabeçalho, separadores ou linhas vazias
                if not line.strip() or line.startswith("=") or line.startswith("AIRCRAFT"):
                    continue

                # Usa o regex para dividir a linha em colunas
                columns = delimiter_regex.split(line.strip())
                
                # Remove espaços extras no início/fim de cada coluna resultante
                cleaned_columns = [col.strip() for col in columns]

                # Garante que a linha tenha o número esperado de colunas antes de adicionar
                if len(cleaned_columns) == 4:
                    processed_data.append(cleaned_columns)
                else:
                    print(f"Aviso: Linha ignorada por não ter 4 colunas após a divisão: '{line.strip()}'")

    except FileNotFoundError:
        print(f"Erro: O arquivo de entrada '{input_txt_file}' não foi encontrado.")
        return

    if not processed_data:
        print("Nenhum dado foi processado. O arquivo de saída não será criado.")
        return

    print(f"Processamento concluído. {len(processed_data)} linhas de dados extraídas.")

    # Escreve os dados processados no arquivo CSV
    try:
        with open(output_csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escreve o cabeçalho original
            writer.writerow(['AIRCRAFT GAMEPLAY MODEL FILE', 'AIRCRAFT HANGAR MODEL FILE', 'AIRCRAFT ID', 'COLOR'])
            
            # Escreve todas as linhas de dados processadas
            writer.writerows(processed_data)
            
        print(f"Sucesso! Arquivo '{output_csv_file}' criado.")

    except IOError:
        print(f"Erro: Não foi possível escrever no arquivo de saída '{output_csv_file}'.")


# --- Como usar o script ---
if __name__ == '__main__':
    # Nome do seu arquivo de texto original
    input_filename = 'aircraft IDs\\ACZ file aircraft ID.txt'
    
    # Nome que você quer para o arquivo CSV de saída
    output_filename = 'aircraft_list_final.csv'
    
    # Chama a função de conversão
    convert_with_specific_delimiter(input_filename, output_filename)
