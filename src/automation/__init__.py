"""
Automation components for job portals
"""
from src.automation.naukri_applier import NaukriApplier
from src.automation.form_filler import FormFiller
from src.automation.resume_uploader import ResumeUploader
from src.automation.question_handler import QuestionHandler
from src.automation.naukri_login import NaukriLogin
from src.automation.naukri_search import NaukriSearch
from src.automation.naukri_apply import NaukriApply

__all__ = [
    'NaukriApplier',
    'FormFiller',
    'ResumeUploader',
    'QuestionHandler',
    'NaukriLogin',
    'NaukriSearch',
    'NaukriApply'
]