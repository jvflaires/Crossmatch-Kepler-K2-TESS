'''
    Criado em 17 de Novembro de 2024

    Descrição: Seleção dos dados dos exoplanetas disponíveis na base de dados do 
               NASA Exoplanet Archive que foram detectados pelas missões K2, Kepler e TESS.

    Autores: João Aires (UFRN)
             Leonardo Andrade de Almeida (ECT/UFRN)
             
    Universidade Federal do Rio Grande do Norte
'''


# Bibliotecas
from astropy.io import ascii
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
from datetime import datetime
import os
import glob

# Data do dia de compilação
query_date = datetime.now().strftime('%Y%m%d')

# Colunas padrão para inicialização da função
colnames     = ['pl_name', 'hostname', 'disc_pubdate', 'disc_year', 'disc_facility', 'disc_refname', 'ra', 'dec']
colnames_new = ['nome_planeta', 'nome_estrela', 'data_publicacao', 'ano_deteccao', 'missao', 'referencia', 'ra', 'dec']

# Função que faz a busca e download da base de dados
def download_kepler_k2_tess(colnames=colnames, colnames_new=colnames_new, delete=True, save=False):
    '''
    Busca remotamente na base do NASA Exoplanet Archive os exoplanetas detectados
    pelo Kepler, K2 e TESS, salvando-os em arquivos .dat

    
    Parametros
    -----------
    colnames: array(str)
        Nomes das colunas (conforme o NASA Exoplanet Archive) a serem buscadas.
    colnames_new: array(str) (opcional)
        Nomes novos para as colunas.


    Retorna:
    -----------
    k2: astropy.table.Table
        Planetas detectados pelo K2
    kepler: astropy.table.Table
        Planetas detectados pelo Kepler
    tess: astropy.table.Table
        Planetas detectados pelo TESS
    '''
    

    # Exclui todos os arquivos já existentes que foram gerados pelo código
    if delete==True:
        list_files = glob.glob('*_exoplanets_*.dat')
        for f in list_files:
            os.remove(f)

    # Loop para criar a string utilizada no query para selecionar as colunas que serão salvas
    col_string = ''
    for i,col in enumerate(colnames):
        if i+1 < len(colnames):
            col_string = col_string + f'{col},'
        else:
            col_string = col_string + f'{col}'

    # Fazendo o download dos exoplanetas descobertos pelo K2
    k2     = NasaExoplanetArchive.query_criteria(table="ps", select=col_string, where="disc_facility like '%K2%' and default_flag=1")
    for co,cn in zip(colnames, colnames_new):
        k2[co].name = cn
    
    # Fazendo o download dos exoplanetas descobertos pelo Kepler
    kepler = NasaExoplanetArchive.query_criteria(table="ps", select=col_string, where="disc_facility like '%Kepler%' and default_flag=1")
    for co,cn in zip(colnames, colnames_new):
        kepler[co].name = cn
    
    # Fazendo o download dos exoplanetas descobertos pelo TESS
    tess   = NasaExoplanetArchive.query_criteria(table="ps", select=col_string, where="disc_facility like '%TESS%' and default_flag=1")
    for co,cn in zip(colnames, colnames_new):
        tess[co].name = cn

    # Salvando arquivos com os planetas detectados por cada missão
    if save==True:
        # K2
        filename = 'K2_exoplanets_'+query_date+'.dat'
        ascii.write(k2, filename, overwrite=True)
        print(f'Exoplanetas do K2 foram salvos em: \t\t {filename}')   

        # Kepler
        filename = 'Kepler_exoplanets_'+query_date+'.dat'
        ascii.write(kepler, filename, overwrite=True)
        print(f'Exoplanetas do Kepler foram salvos em: \t\t {filename}')

        #TESS
        filename = 'TESS_exoplanets_'+query_date+'.dat'
        ascii.write(tess, filename, overwrite=True)
        print(f'Exoplanetas do TESS foram salvos em: \t\t {filename}')    
    
    
    print('Resumo dos dados')
    print('(NASA Exoplanet Archive)')
    print('-----------------------------------------')
    print(f'Kepler: \t\t {len(kepler)} planetas')
    print(f'K2: \t\t\t {len(k2)} planetas')
    print(f'TESS: \t\t\t {len(tess)} planetas')
    print('-----------------------------------------')
    print(f'Total: \t\t\t {len(kepler) + len(k2) + len(tess)} planetas')

    return kepler, k2, tess