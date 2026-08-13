"""
AI-powered job matching using NLP
"""
import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class JobMatcher:
    """Matches jobs based on skills and preferences"""
    
    def __init__(self):
        self.skill_synonyms = {
            'python': ['python', 'django', 'flask', 'fastapi'],
            'java': ['java', 'spring', 'hibernate', 'j2ee'],
            'react': ['react', 'reactjs', 'redux', 'nextjs'],
            'javascript': ['javascript', 'js', 'node', 'nodejs'],
            'sql': ['sql', 'mysql', 'postgresql', 'mongodb', 'database'],
            'cloud': ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes'],
            'ml': ['machine learning', 'ml', 'ai', 'artificial intelligence']
        }
    
    def match_job(self, job: Dict, profile: Dict) -> float:
        """Calculate match percentage between job and profile"""
        score = 0
        max_score = 100
        
        # Check skills match
        job_skills = self._extract_skills(job.get('title', '') + ' ' + job.get('description', ''))
        profile_skills = profile.get('skills', [])
        
        if profile_skills and job_skills:
            matched = self._calculate_skill_match(profile_skills, job_skills)
            score += matched * 40  # 40% weight
        
        # Check experience match
        req_exp = self._extract_experience(job.get('description', ''))
        profile_exp = profile.get('experience_years', 0)
        if req_exp and profile_exp:
            if profile_exp >= req_exp:
                score += 30  # 30% weight
            elif profile_exp >= req_exp - 2:
                score += 15
        
        # Check location match
        if job.get('location', '').lower() in str(profile.get('preferred_locations', [])).lower():
            score += 15  # 15% weight
        
        # Check title match
        if any(skill.lower() in job.get('title', '').lower() for skill in profile_skills[:3]):
            score += 15  # 15% weight
        
        return min(score, max_score)
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        text = text.lower()
        skills = []
        for skill, synonyms in self.skill_synonyms.items():
            for syn in synonyms:
                if syn in text:
                    skills.append(skill)
                    break
        return skills
    
    def _extract_experience(self, text: str) -> int:
        """Extract required experience from text"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)',
            r'(?:experience|exp)\s*[:.]?\s*(\d+)\+?\s*(?:years?|yrs?)?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        return 0
    
    def _calculate_skill_match(self, profile_skills: List[str], job_skills: List[str]) -> float:
        """Calculate skill match percentage"""
        if not job_skills:
            return 1.0
        
        matched = 0
        for skill in profile_skills:
            if skill.lower() in job_skills:
                matched += 1
        
        return matched / len(job_skills) if job_skills else 0