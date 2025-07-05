import os
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox
import warnings

from loguru import logger

warnings.filterwarnings("ignore")



def extract_pdf(pdf_file:str,output_folder:str= './data/temp/'):
    try:
        logger.debug(f'starting pdf extraction for the file -> {pdf_file}')
        file_folder_name = pdf_file.split('/')[-1]
        os.makedirs(f'{output_folder+file_folder_name}',exist_ok=True)
        text = ''
        for page_layout in extract_pages(pdf_file):
            for element in page_layout:
                #go through every element in page, and append text to text
                if isinstance(element, LTTextBox):
                    #logger.debug(element.get_text())
                    text += element.get_text()

        # Save the text in a file
        #logger.debug(output_folder+file_folder_name +'/' + pdf_file.split('\\')[-1].replace('.pdf','.txt'))
        logger.debug(f'writing text file for file -> {pdf_file}')
        with open(output_folder+file_folder_name+'/' + pdf_file.split('/')[-1].replace('.pdf','.txt'), 'w', encoding='utf-8') as f:
            f.write(text)
        logger.debug(f'writing text file for file -> {pdf_file} completed!')
    except Exception as e:
        logger.debug(f'inside the exception block of {__name__}, exception is -> {e}')
        #print(e)
        raise Exception(e)
