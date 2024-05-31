import yaml
from common.database.db_setup import setup_database
from common.database.db_operations import save_or_update_resume
from common.utils.file_utils import get_file_extension
from common.utils.data_utils import extract_information
from parser.pdf_parser import parse_pdf
from parser.doc_parser import parse_doc

def main(file_path):
    ext = get_file_extension(file_path)
    
    if ext == '.pdf':
        text = parse_pdf(file_path)
    elif ext == '.doc' or ext == '.docx':
        text = parse_doc(file_path)
    else:
        raise ValueError('Unsupported file format')
    
    resume_data = extract_information(text)

    with open("config/config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    
    engine = setup_database(config['database']['connection_string'])
    save_or_update_resume(engine, resume_data)

if __name__ == "__main__":
    file_path = 'F:\\Job-Search\\VedikaSrivastava_Resume_May2024.pdf'
    main(file_path)
