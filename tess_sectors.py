'''
    Criado em 17 de Novembro de 2024

    Descrição: Busca por quais setores do TESS as estrelas foram observadas e quais deles possuem curvas de luz

    Autores: João Aires (UFRN)
             Leonardo Andrade de Almeida (ECT/UFRN)
             
    Universidade Federal do Rio Grande do Norte
'''


# Bibliotecas
import numpy as np
from astroquery.mast import Catalogs, Tesscut
from astropy.coordinates import SkyCoord
import os
import urllib.request as urllib2
from IPython.display import clear_output

# Função que faz busca nos setores do TESS a partir do TIC 
def get_tess_sectors(tbl, lc=False):
    '''
    A partir do TIC da estrela, busca nos setores do TESS aqueles
    que fizeram observações desta.


    Parametros:
    ------------
    tbl: astropy.table.Table
        Tabela contendo as informações (especialmente o TIC) das
        estrelas.
    lc: bool, opcional
        Procurar, dentro dos setores do TESS, aqueles que possuem
        curvas de luz produzidas pela pipeline do instrumento.
        default: False


    Retorna:
    ------------
    tbl: astropy.table.Table
        Tabela inicial acrescida das colunas contendo os setores do 
        TESS que possuem observações das estrelas hospedeiras
    '''

    # Criando colunas para guardar os setores
    tbl['tess_setores']    = np.zeros(len(tbl))
    tbl['tess_setores']    = tbl['tess_setores'].astype('str')
    tbl['tess_setores_lc'] = np.zeros(len(tbl))
    tbl['tess_setores_lc'] = tbl['tess_setores_lc'].astype('str')

    # Loop para buscar os setores a partir do TIC
    for i,ticid in enumerate(tbl['TIC']):
        print(f'Processando ... {i+1}/{len(tbl)}')

        # Procurando a estrela na base de dados do TESS
        starID = f'TIC {ticid}'
        catalogTIC = Catalogs.query_object(starID, radius=0.02, catalog='tic')
        nearest_pos = np.argmin(catalogTIC['dstArcSec'])

        # Pegando os setores em que a estrela foi achada
        ID = (catalogTIC['ID'][nearest_pos])
        ra_list, dec_list = catalogTIC['ra'][nearest_pos], catalogTIC['dec'][nearest_pos]
        coord = SkyCoord(ra_list, dec_list, unit="deg")
        sectors = Tesscut.get_sectors(coordinates=coord)

        # Cria string com os setores e salva na tabela
        sectors_str = ''
        for i,s in enumerate(sectors['sector'].value):
            if i+1 < len(sectors['sector'].value):
                sectors_str = sectors_str + f'{s}, '
            else:
                sectors_str = sectors_str + f'{s}'

        tbl['tess_setores'][i] = sectors_str

        # Procurando os setores que possuem curva de luz
        if lc==True:
            sctr = []
            for sec in sectors['sector']:
                sec = str(sec)
                sctr.append('s'+sec.zfill(4))
            tid = ID.zfill(16)
            tid1 = tid[:4]
            tid2 = tid[4:8]
            tid3 = tid[8:12]
            tid4 = tid[12:]
            tess_folder = '/'+str(tid1)+'/'+str(tid2)+'/'+str(tid3)+'/'+str(tid4)+'/'
    
            gat = 0
            lc_sectors = np.array([])
            for sec in sctr:
                url = 'https://archive.stsci.edu/missions/tess/tid/'+str(sec)+tess_folder
                try:
                    page = urllib2.urlopen(url)
                    doc = str(page.read())
                    indexin = doc.find('href="tess')
                    indexout = doc.find('lc.fits')
                    
                    fileID = doc[indexin+6:indexout+7]
                    url_ = url + fileID
                    
                    gat = 1
                    lc_sectors = np.append(lc_sectors, sec[3:])
                except:
                    continue

            # Cria string com os setores que possuem curva de luz e salva na tabela
            lc_sectors_str = ''
            for i,s in enumerate(lc_sectors):
                if i+1 < len(lc_sectors):
                    lc_sectors_str = lc_sectors_str + f'{s}, '
                else:
                    lc_sectors_str = lc_sectors_str + f'{s}'
            
            tbl['tess_setores_lc'][i] = lc_sectors_str
        
        # Limpa o output para reduzir a poluição visual
        clear_output(wait=False)
    
    return tbl