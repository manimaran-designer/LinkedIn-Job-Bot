import yaml
from models.schemas import ConfigData

def parse_config(file_path: str) -> ConfigData:
    """Parses the YAML configuration file and returns a ConfigData model."""
    with open(file_path, 'r') as f:
        raw_config = yaml.safe_load(f)
        
    return ConfigData(
        interested_roles=raw_config.get('interested_roles', []),
        need_company_research=raw_config.get('need_company_research', False),
        prepare_mock_questions=raw_config.get('prepare_mock_questions', False),
        auto_apply=raw_config.get('auto_apply', False),
        modify_resume=raw_config.get('modify_resume', False),
        skill_threshold=raw_config.get('skill_threshold', 70),
        search_keywords=raw_config.get('search_keywords', []),
        location_filter=raw_config.get('location_filter', 'Remote'),
        salary_min=raw_config.get('salary_min', None),
        blacklist_companies=raw_config.get('blacklist_companies', [])
    )
