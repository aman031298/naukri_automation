"""
Question & Answer Handler for Recruiter Questions
Supports JSON-based Q&A database with 1000+ questions
Handles: MCQ, Text, Number, Yes/No, Dropdown questions
"""
import logging
import json
import re
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class QuestionHandler:
    """Handles recruiter questions during application"""
    
    def __init__(self, browser):
        self.browser = browser
        self.page = browser.page
        
        # Load Q&A database
        self.qa_database = self._load_qa_database()
        
        # Load profile answers
        self.profile_answers = self._load_profile_answers()
        
        # Track answered questions
        self.answered_questions = []
        self.skipped_questions = []
        
        # Question type handlers
        self.type_handlers = {
            'mcq': self._handle_mcq,
            'text': self._handle_text,
            'number': self._handle_number,
            'yes_no': self._handle_yes_no,
            'dropdown': self._handle_dropdown
        }
    
    def _load_qa_database(self) -> Dict:
        """Load Q&A database from JSON file"""
        try:
            # Try multiple paths
            db_paths = [
                Path("data/qa_database.json"),
                Path("../data/qa_database.json"),
                Path("qa_database.json"),
                Path("src/data/qa_database.json")
            ]
            
            for db_path in db_paths:
                if db_path.exists():
                    with open(db_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    total = data.get('metadata', {}).get('total_questions', 0)
                    logger.info(f"✅ Loaded Q&A database: {total} questions from {db_path}")
                    return data
            
            logger.warning("⚠️ Q&A database not found, using fallback")
            return self._create_fallback_database()
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {str(e)}")
            return self._create_fallback_database()
        except Exception as e:
            logger.error(f"❌ Failed to load Q&A database: {str(e)}")
            return self._create_fallback_database()
    
    def _create_fallback_database(self) -> Dict:
        """Create fallback Q&A database if file not found"""
        return {
            "metadata": {
                "total_questions": 20,
                "question_types": {"text": 10, "yes_no": 5, "mcq": 5}
            },
            "questions": {
                "ctc_salary": [
                    {"id": "F001", "type": "text", "question": "What is your current CTC?", "answer": "8-10 LPA"},
                    {"id": "F002", "type": "text", "question": "What is your expected CTC?", "answer": "15-20 LPA"}
                ],
                "experience": [
                    {"id": "F003", "type": "text", "question": "What is your total experience?", "answer": "3-5 years"}
                ],
                "personal": [
                    {"id": "F004", "type": "text", "question": "What is your name?", "answer": "Sachin Chakrawarti"}
                ],
                "internship": [
                    {"id": "F005", "type": "yes_no", "question": "Can you work unpaid internship?", "answer": "No"}
                ]
            },
            "contextual_answers": {}
        }
    
    def _load_profile_answers(self) -> Dict:
        """Load answers from user profile"""
        try:
            from src.utils.file_handler import load_user_profile
            profile = load_user_profile()
            
            answers = {
                'current_ctc': profile.get('form_data', {}).get('current_salary', '8-10 LPA'),
                'expected_ctc': profile.get('form_data', {}).get('expected_salary', '15-20 LPA'),
                'notice_period': profile.get('form_data', {}).get('notice_period', '30 days'),
                'experience': profile.get('form_data', {}).get('total_experience', '3-5 years'),
                'current_location': profile.get('personal_info', {}).get('city', 'Bangalore'),
                'highest_education': profile.get('form_data', {}).get('highest_education', 'M.Tech in Data Science'),
                'skills': profile.get('form_data', {}).get('skills_string', 'Python, Java, React, Spring Boot'),
                'full_name': profile.get('personal_info', {}).get('first_name', 'Sachin'),
                'last_name': profile.get('personal_info', {}).get('last_name', 'Chakrawarti'),
                'email': profile.get('personal_info', {}).get('email', ''),
                'phone': profile.get('personal_info', {}).get('phone', ''),
                'gender': profile.get('personal_info', {}).get('gender', 'Male'),
                'date_of_birth': profile.get('personal_info', {}).get('date_of_birth', '2001-03-20'),
            }
            logger.info("✅ Loaded profile answers")
            return answers
        except Exception as e:
            logger.warning(f"⚠️ Could not load profile: {str(e)}")
            return {}
    
    def handle_questions(self) -> bool:
        """Main method to handle all questions on page"""
        try:
            logger.info("📋 Checking for recruiter questions...")
            
            # Detect questions on page
            questions = self._detect_questions()
            
            if not questions:
                logger.info("ℹ️ No questions detected")
                return True
            
            logger.info(f"📋 Found {len(questions)} questions")
            
            # Process each question
            answered_count = 0
            for question_data in questions:
                if self._process_question(question_data):
                    answered_count += 1
            
            # Get statistics
            stats = self.get_statistics()
            logger.info(f"✅ Answered: {stats['total_answered']}, Skipped: {stats['total_skipped']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Question handling failed: {str(e)}")
            return False
    
    def _detect_questions(self) -> List[Dict]:
        """Detect questions on the page"""
        questions = []
        try:
            # Get all visible inputs
            inputs = self.page.locator("input, select, textarea").all()
            
            for inp in inputs:
                if inp.is_visible():
                    # Get label/placeholder
                    label = self._get_input_label(inp)
                    if label and self._is_question(label):
                        question_data = {
                            'element': inp,
                            'label': label,
                            'type': self._detect_question_type(inp),
                            'options': self._get_options(inp) if inp.get_attribute('type') == 'select' else []
                        }
                        questions.append(question_data)
            
            # Also check for explicit question containers
            question_containers = self.page.locator(".question, .form-group, .field-group, .question-group").all()
            for container in question_containers:
                if container.is_visible():
                    text = container.text_content() or ""
                    if self._is_question(text):
                        inp = container.locator("input, select, textarea").first
                        if inp.count():
                            questions.append({
                                'element': inp,
                                'label': text[:200],  # Limit label length
                                'type': self._detect_question_type(inp),
                                'options': []
                            })
            
            return questions
            
        except Exception as e:
            logger.warning(f"⚠️ Question detection failed: {str(e)}")
            return []
    
    def _is_question(self, text: str) -> bool:
        """Check if text contains a question"""
        if not text:
            return False
        
        question_indicators = [
            '?', 'what', 'why', 'how', 'when', 'where', 'who', 
            'which', 'please', 'select', 'choose', 'enter', 
            'provide', 'describe', 'explain', 'tell', 'share',
            'current', 'expected', 'experience', 'skills', 'notice',
            'available', 'preferred', 'willing', 'open to'
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in question_indicators)
    
    def _detect_question_type(self, element) -> str:
        """Detect question type from element"""
        try:
            input_type = element.get_attribute('type') or ''
            tag_name = element.evaluate('el => el.tagName.toLowerCase()')
            
            if tag_name == 'select':
                return 'dropdown'
            elif input_type == 'radio':
                return 'mcq'
            elif input_type == 'checkbox':
                return 'mcq'
            elif input_type == 'number':
                return 'number'
            elif input_type == 'text':
                return 'text'
            elif input_type == 'email' or input_type == 'tel':
                return 'text'
            elif input_type == 'textarea':
                return 'text'
            else:
                return 'text'
        except:
            return 'text'
    
    def _get_input_label(self, element) -> str:
        """Get label for an input element"""
        try:
            # Check for for attribute
            input_id = element.get_attribute('id')
            if input_id:
                label = self.page.locator(f"label[for='{input_id}']").first
                if label.count():
                    text = label.text_content()
                    if text:
                        return text.strip()
            
            # Check for placeholder
            placeholder = element.get_attribute('placeholder')
            if placeholder:
                return placeholder.strip()
            
            # Check for aria-label
            aria_label = element.get_attribute('aria-label')
            if aria_label:
                return aria_label.strip()
            
            # Check for name attribute
            name = element.get_attribute('name')
            if name:
                return name.replace('_', ' ').replace('-', ' ').strip()
            
            # Check for title attribute
            title = element.get_attribute('title')
            if title:
                return title.strip()
            
            return ""
            
        except Exception as e:
            logger.warning(f"Could not get label: {str(e)}")
            return ""
    
    def _get_options(self, element) -> List[str]:
        """Get options for select/dropdown"""
        try:
            options = []
            option_elements = element.locator("option").all()
            for opt in option_elements:
                if opt.count():
                    text = opt.text_content()
                    if text and text.strip() and text.strip() != "Select" and text.strip() != "Choose":
                        options.append(text.strip())
            return options
        except:
            return []
    
    def _find_question_in_db(self, label: str) -> Optional[Dict]:
        """Find question in database by matching label"""
        if not label:
            return None
        
        label_lower = label.lower()
        
        # Search through all categories
        for category, questions in self.qa_database.get('questions', {}).items():
            for q in questions:
                # Check main question
                q_text = q.get('question', '').lower()
                if q_text and (q_text in label_lower or label_lower in q_text):
                    return q
                
                # Check variations
                for variation in q.get('variations', []):
                    if variation.lower() in label_lower or label_lower in variation.lower():
                        return q
        return None
    
    def _process_question(self, question_data: Dict) -> bool:
        """Process a single question"""
        try:
            element = question_data['element']
            label = question_data['label']
            q_type = question_data['type']
            options = question_data.get('options', [])
            
            logger.info(f"📝 Processing: {label[:50]}... (Type: {q_type})")
            
            # --- SPECIAL HANDLER FOR UNPAID INTERNSHIP ---
            if 'unpaid' in label.lower() and 'internship' in label.lower():
                logger.info("💼 Detected unpaid internship question")
                return self._handle_unpaid_internship_question(element, label)
            # ----------------------------------------------
            
            # Find in database
            q_db = self._find_question_in_db(label)
            
            # Get answer based on type
            if q_db:
                answer = self._get_answer_from_db(q_db, label)
                logger.debug(f"   Found in DB: {q_db.get('id')}")
            else:
                answer = self._get_answer_from_profile(label)
                logger.debug("   Using profile answer")
            
            if answer:
                # Use appropriate handler
                handler = self.type_handlers.get(q_type, self._handle_text)
                if handler(element, answer, options):
                    self.answered_questions.append({
                        'question': label[:100],
                        'answer': answer[:100],
                        'type': q_type,
                        'db_id': q_db.get('id') if q_db else None
                    })
                    logger.info(f"✅ Answered: {label[:30]}... -> {answer[:30]}...")
                    return True
                else:
                    # Try fallback handlers
                    logger.warning(f"⚠️ Primary handler failed, trying fallback")
                    return self._try_fallback_handlers(element, label, q_type, options)
            else:
                # Try to skip
                logger.warning(f"⚠️ No answer found, trying to skip")
                return self._skip_question(element)
            
        except Exception as e:
            logger.warning(f"⚠️ Question processing failed: {str(e)}")
            return self._skip_question(question_data['element'])
    
    def _get_answer_from_db(self, q_db: Dict, label: str) -> Optional[str]:
        """Get answer from database"""
        try:
            # Get answer
            answer = q_db.get('answer')
            
            # Check for unpaid internship special handling
            if q_db.get('id', '').startswith('INT') and 'unpaid' in q_db.get('question', '').lower():
                logger.info("   Unpaid internship detected - returning 'No'")
                return "No"
            
            # Return answer or fallback
            if answer:
                return answer
            elif q_db.get('fallback_answers'):
                return random.choice(q_db['fallback_answers'])
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not get answer from DB: {str(e)}")
            return None
    
    def _get_answer_from_profile(self, label: str) -> Optional[str]:
        """Get answer from profile based on label"""
        if not label:
            return None
        
        label_lower = label.lower()
        
        mappings = {
            'ctc': 'current_ctc',
            'salary': 'current_ctc',
            'experience': 'experience',
            'notice': 'notice_period',
            'location': 'current_location',
            'education': 'highest_education',
            'skills': 'skills',
            'name': 'full_name',
            'first name': 'full_name',
            'last name': 'last_name',
            'email': 'email',
            'phone': 'phone',
            'mobile': 'phone',
            'gender': 'gender',
            'dob': 'date_of_birth',
            'birth': 'date_of_birth'
        }
        
        for key, profile_key in mappings.items():
            if key in label_lower:
                return self.profile_answers.get(profile_key)
        
        return None
    
    def _handle_unpaid_internship_question(self, element, label: str) -> bool:
        """Special handler for unpaid internship questions"""
        try:
            logger.info("💼 Handling unpaid internship question...")
            
            # Get element type
            element_type = element.get_attribute('type') or ''
            tag_name = element.evaluate('el => el.tagName.toLowerCase()')
            
            # For radio buttons (Yes/No)
            if element_type == 'radio':
                name = element.get_attribute('name')
                if name:
                    radios = self.page.locator(f"input[name='{name}']").all()
                    for radio in radios:
                        if radio.is_visible():
                            value = radio.get_attribute('value') or ""
                            if 'no' in value.lower() or 'not' in value.lower() or 'cannot' in value.lower():
                                radio.click()
                                self.browser.human_delay(0.5, 1)
                                self.answered_questions.append({
                                    'question': label[:100],
                                    'answer': 'No',
                                    'type': 'yes_no',
                                    'db_id': 'INT001'
                                })
                                logger.info("✅ Selected 'No' for unpaid internship")
                                return True
            
            # For text input
            elif element_type == 'text' or element_type == 'textarea' or tag_name == 'textarea':
                responses = [
                    "I appreciate the opportunity, but I am looking for paid positions.",
                    "Thank you for the offer, but I need a paid internship at this point.",
                    "I am interested in the role, but I require a stipend/internship pay.",
                    "While I'm very interested in this position, I am seeking paid opportunities."
                ]
                answer = random.choice(responses)
                element.click()
                element.fill("")
                self.browser.human_delay(0.3, 0.8)
                element.fill(answer)
                self.browser.human_delay(0.3, 0.8)
                self.answered_questions.append({
                    'question': label[:100],
                    'answer': answer[:100],
                    'type': 'text',
                    'db_id': 'INT001'
                })
                logger.info(f"✅ Entered professional decline: {answer[:50]}...")
                return True
            
            # For dropdown
            elif tag_name == 'select':
                options = element.locator("option").all()
                for opt in options:
                    if opt.count():
                        opt_text = opt.text_content() or ""
                        if 'no' in opt_text.lower() or 'not interested' in opt_text.lower():
                            opt.click()
                            self.browser.human_delay(0.5, 1)
                            self.answered_questions.append({
                                'question': label[:100],
                                'answer': 'No',
                                'type': 'dropdown',
                                'db_id': 'INT001'
                            })
                            logger.info("✅ Selected 'No' from dropdown")
                            return True
            
            # Try to skip
            logger.info("Could not handle unpaid internship, trying to skip...")
            return self._skip_question(element)
            
        except Exception as e:
            logger.warning(f"Unpaid internship handling failed: {str(e)}")
            return self._skip_question(element)
    
    def _handle_mcq(self, element, answer: str, options: List[str]) -> bool:
        """Handle multiple choice questions"""
        try:
            # For radio buttons
            if element.get_attribute('type') == 'radio':
                name = element.get_attribute('name')
                if name:
                    radios = self.page.locator(f"input[name='{name}']").all()
                    for radio in radios:
                        if radio.is_visible():
                            value = radio.get_attribute('value') or ""
                            # Match answer with option
                            if answer.lower() in value.lower() or value.lower() in answer.lower():
                                radio.click()
                                self.browser.human_delay(0.5, 1)
                                return True
                    
                    # If no match, try first non-empty option
                    for radio in radios:
                        if radio.is_visible():
                            value = radio.get_attribute('value') or ""
                            if value and value.strip():
                                radio.click()
                                self.browser.human_delay(0.5, 1)
                                return True
                
                return False
            
            # For checkboxes
            elif element.get_attribute('type') == 'checkbox':
                # For checkboxes, just check it if it's not checked
                if not element.is_checked():
                    element.click()
                    self.browser.human_delay(0.5, 1)
                    return True
                return True
            
            # For select dropdowns (treated as MCQ)
            elif element.evaluate('el => el.tagName.toLowerCase()') == 'select':
                return self._handle_dropdown(element, answer, options)
            
            return False
            
        except Exception as e:
            logger.warning(f"MCQ handling failed: {str(e)}")
            return False
    
    def _handle_text(self, element, answer: str, options: List[str] = None) -> bool:
        """Handle text input questions"""
        try:
            if element.is_visible() and not element.is_disabled():
                # Clear and fill
                element.click()
                element.fill("")
                self.browser.human_delay(0.3, 0.8)
                element.fill(answer)
                self.browser.human_delay(0.3, 0.8)
                return True
            return False
        except Exception as e:
            logger.warning(f"Text handling failed: {str(e)}")
            return False
    
    def _handle_number(self, element, answer: str, options: List[str] = None) -> bool:
        """Handle number input questions"""
        try:
            if element.is_visible() and not element.is_disabled():
                # Extract number from answer
                numbers = re.findall(r'\d+', answer)
                if numbers:
                    number = numbers[0]
                else:
                    number = answer
                
                element.click()
                element.fill("")
                self.browser.human_delay(0.3, 0.8)
                element.fill(number)
                self.browser.human_delay(0.3, 0.8)
                return True
            return False
        except Exception as e:
            logger.warning(f"Number handling failed: {str(e)}")
            return False
    
    def _handle_yes_no(self, element, answer: str, options: List[str] = None) -> bool:
        """Handle Yes/No questions"""
        try:
            # For radio buttons
            if element.get_attribute('type') == 'radio':
                name = element.get_attribute('name')
                if name:
                    radios = self.page.locator(f"input[name='{name}']").all()
                    for radio in radios:
                        if radio.is_visible():
                            value = radio.get_attribute('value') or ""
                            # Match Yes/No
                            if (answer.lower() == 'yes' and 'yes' in value.lower()) or \
                               (answer.lower() == 'no' and 'no' in value.lower()):
                                radio.click()
                                self.browser.human_delay(0.5, 1)
                                return True
                            
                            # If we can't find exact match, try first option
                            if value and value.strip():
                                radio.click()
                                self.browser.human_delay(0.5, 1)
                                return True
            
            # For text input
            elif element.get_attribute('type') == 'text' or element.get_attribute('type') == 'textarea':
                return self._handle_text(element, answer)
            
            # For dropdown
            elif element.evaluate('el => el.tagName.toLowerCase()') == 'select':
                return self._handle_dropdown(element, answer, options or [])
            
            return False
            
        except Exception as e:
            logger.warning(f"Yes/No handling failed: {str(e)}")
            return False
    
    def _handle_dropdown(self, element, answer: str, options: List[str]) -> bool:
        """Handle dropdown questions"""
        try:
            if element.is_visible():
                # Try to select by text matching
                option_elements = element.locator("option").all()
                
                # First try exact or partial match
                for opt in option_elements:
                    if opt.count():
                        opt_text = opt.text_content() or ""
                        if answer.lower() in opt_text.lower() or opt_text.lower() in answer.lower():
                            opt.click()
                            self.browser.human_delay(0.5, 1)
                            return True
                
                # If no match, try first non-empty option
                for opt in option_elements:
                    if opt.count():
                        opt_text = opt.text_content() or ""
                        if opt_text.strip() and opt_text.strip() != "Select" and opt_text.strip() != "Choose":
                            opt.click()
                            self.browser.human_delay(0.5, 1)
                            return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Dropdown handling failed: {str(e)}")
            return False
    
    def _try_fallback_handlers(self, element, label: str, q_type: str, options: List[str]) -> bool:
        """Try fallback handlers if primary handler fails"""
        try:
            # Try generic text for any input
            if q_type != 'text':
                answer = self._get_answer_from_profile(label)
                if answer:
                    return self._handle_text(element, answer)
            
            # Try clicking the element and using keyboard
            element.click()
            self.browser.human_delay(0.5, 1)
            
            # Try to enter a default answer
            default_answers = {
                'text': 'Not applicable',
                'number': '0',
                'yes_no': 'No'
            }
            default = default_answers.get(q_type, 'N/A')
            element.fill(default)
            self.browser.human_delay(0.5, 1)
            return True
            
        except:
            return False
    
    def _skip_question(self, element) -> bool:
        """Skip a question"""
        try:
            # Look for skip button
            skip_selectors = [
                "button:has-text('Skip')",
                "button:has-text('Skip this question')",
                "button:has-text('I\\'ll do it later')",
                "button:has-text('Later')",
                "button:has-text('Not applicable')",
                "button:has-text('N/A')",
                "a:has-text('Skip')",
                ".skip-btn",
                ".skip",
                ".close",
                ".crossIcon",
                ".modal-close"
            ]
            
            for selector in skip_selectors:
                skip_btn = self.page.locator(selector).first
                if skip_btn.count() and skip_btn.is_visible():
                    skip_btn.click()
                    self.browser.human_delay(0.5, 1)
                    self.skipped_questions.append({
                        'question': 'Unknown',
                        'reason': 'Skip button clicked'
                    })
                    logger.info("✅ Skipped question")
                    return True
            
            # Try pressing Escape
            self.page.keyboard.press("Escape")
            self.browser.human_delay(0.5, 1)
            self.skipped_questions.append({
                'question': 'Unknown',
                'reason': 'Escape key pressed'
            })
            logger.info("✅ Pressed Escape to skip")
            return True
            
        except Exception as e:
            logger.warning(f"Skip failed: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get statistics about answered/skipped questions"""
        return {
            'total_answered': len(self.answered_questions),
            'total_skipped': len(self.skipped_questions),
            'answered_questions': self.answered_questions,
            'skipped_questions': self.skipped_questions
        }
    
    def get_summary(self) -> str:
        """Get a summary of question handling"""
        stats = self.get_statistics()
        summary = f"""
        Question Handling Summary:
        ============================
        Total Answered: {stats['total_answered']}
        Total Skipped: {stats['total_skipped']}
        
        Answered Questions:
        {self._format_questions(stats['answered_questions'])}
        
        Skipped Questions:
        {self._format_questions(stats['skipped_questions'], show_answer=False)}
        """
        return summary
    
    def _format_questions(self, questions: List[Dict], show_answer: bool = True) -> str:
        """Format questions for summary"""
        if not questions:
            return "   None"
        
        lines = []
        for i, q in enumerate(questions[:10], 1):
            question = q.get('question', 'Unknown')[:50]
            if show_answer:
                answer = q.get('answer', 'N/A')[:50]
                lines.append(f"   {i}. {question} -> {answer}")
            else:
                lines.append(f"   {i}. {question}")
        
        if len(questions) > 10:
            lines.append(f"   ... and {len(questions) - 10} more")
        
        return "\n".join(lines)