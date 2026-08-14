"""
Form filling automation for Naukri.com applications
"""
import logging
import time

logger = logging.getLogger(__name__)

class FormFiller:
    """Handles form filling for Naukri job applications"""
    
    def __init__(self, browser):
        self.browser = browser
        self.page = browser.page
        
        # Lazy import to avoid circular dependency
        self._resume_uploader = None
        self._question_handler = None
    
    @property
    def resume_uploader(self):
        """Lazy load resume uploader"""
        if self._resume_uploader is None:
            from src.automation.resume_uploader import ResumeUploader
            self._resume_uploader = ResumeUploader(self.browser)
        return self._resume_uploader
    
    @property
    def question_handler(self):
        """Lazy load question handler"""
        if self._question_handler is None:
            from src.automation.question_handler import QuestionHandler
            self._question_handler = QuestionHandler(self.browser)
        return self._question_handler
    
    def fill_and_submit(self) -> bool:
        """Fill the application form and submit"""
        try:
            logger.info("📝 Filling application form...")
            self.browser.human_delay(2, 3)

            # Naukri's native apply sometimes opens a chat-style screening
            # question panel (single question, "Type message here..." box,
            # its own Save button) instead of a traditional form. This has
            # no "Submit" button at all, so it must be handled before
            # falling through to the traditional-form path below.
            if self._is_chat_panel_open():
                return self._handle_chat_panel()

            # Handle any popup questions
            self._handle_popups()

            # Handle resume upload (smart detection)
            if not self.resume_uploader.upload_resume():
                logger.warning("⚠️ Resume upload failed, but continuing...")

            # Handle recruiter questions
            if not self.question_handler.handle_questions():
                logger.warning("⚠️ Some questions may not have been answered")

            # Fill text inputs
            self._fill_text_inputs()

            # Fill dropdowns
            self._fill_dropdowns()

            # Handle radio buttons
            self._fill_radios()

            # Check if there's a "Next" or "Continue" before submit
            self._handle_multi_step_form()

            # If clicking through the multi-step form revealed a chat
            # panel as the final step, hand off to that handler too.
            if self._is_chat_panel_open():
                return self._handle_chat_panel()

            # No form fields and no chat panel appeared at all — this can
            # mean the native apply click was itself the complete
            # submission (common for jobs with no screening questions),
            # but it can just as easily mean the click silently failed to
            # do anything. Absence of a form is not proof of success, so
            # verify against the page's actual post-apply state (the
            # button turns into a disabled green "Applied" pill) rather
            # than assuming success by default.
            if not self._has_any_form_fields():
                if self._is_apply_confirmed():
                    logger.info("✅ Apply button now shows 'Applied' — submission confirmed")
                    return True
                logger.warning("⚠️ No form/questions appeared, but 'Applied' state not confirmed either")
                return False

            # Submit the application
            return self._submit()

        except Exception as e:
            logger.error(f"Form filling failed: {str(e)}")
            return False

    def _is_apply_confirmed(self) -> bool:
        """Check whether the page shows Naukri's post-apply confirmation
        state — the Apply button turning into a non-clickable 'Applied'
        pill — rather than inferring success from the mere absence of a
        form, which is also what an apply click that silently no-opped
        would look like.
        """
        try:
            applied_btn = self.page.locator("button:has-text('Applied')").first
            if applied_btn.count() and applied_btn.is_visible():
                return True

            page_text = self.page.content().lower()
            return any(phrase in page_text for phrase in [
                "already applied", "application submitted", "you have applied"
            ])
        except Exception:
            return False

    def _is_chat_panel_open(self) -> bool:
        """Detect Naukri's chat-style screening question panel"""
        try:
            return self.page.get_by_placeholder("Type message here...").first.is_visible()
        except Exception:
            return False

    def _has_any_form_fields(self) -> bool:
        """Check whether any traditional form field is present/visible"""
        try:
            for selector in ["input[type='text']", "input:not([type])", "select", "input[type='radio']"]:
                if self.page.locator(selector).first.is_visible():
                    return True
            return False
        except Exception:
            return False

    def _handle_chat_panel(self) -> bool:
        """Answer and submit Naukri's chat-style screening question panel.

        The panel asks one question at a time via a text box (placeholder
        "Type message here...") with its own Save button that only
        activates once text is entered. It can repeat for multiple
        questions in sequence, so this loops until the panel closes or a
        safety cap is hit.
        """
        try:
            max_questions = 10
            for _ in range(max_questions):
                chat_input = self.page.get_by_placeholder("Type message here...").first
                if not chat_input.is_visible():
                    # The panel closing is necessary but not sufficient —
                    # it also closes if something went wrong. Confirm the
                    # actual post-apply page state before calling it a
                    # success.
                    if self._is_apply_confirmed():
                        logger.info("✅ Chat panel closed and 'Applied' state confirmed")
                        return True
                    logger.warning("⚠️ Chat panel closed but 'Applied' state not confirmed")
                    return False

                question_text = self._get_chat_question_text()
                answer = self.question_handler.get_answer_for_text(question_text)

                chat_input.click()
                chat_input.fill(answer)
                self.browser.human_delay(0.5, 1)

                # The Save button lives in the same panel as the input and
                # is disabled/inert until text is entered — locate it by
                # walking up from the input rather than a bare
                # "button:has-text('Save')", which also matches the
                # unrelated job-bookmark Save button elsewhere on the page.
                save_btn = chat_input.locator(
                    "xpath=ancestor::*[self::div or self::section][1]//button[contains(., 'Save')]"
                ).first
                if not save_btn.count():
                    # Fall back to nearest Save button on the page —
                    # still preferable to giving up outright.
                    save_btn = self.page.locator("button:has-text('Save')").last

                save_btn.click()
                self.browser.human_delay(1.5, 2.5)

            logger.warning("⚠️ Chat panel still open after max question attempts")
            return False

        except Exception as e:
            logger.warning(f"Chat panel handling failed: {str(e)}")
            return False

    def _get_chat_question_text(self) -> str:
        """Extract the current question text shown in the chat panel"""
        try:
            chat_input = self.page.get_by_placeholder("Type message here...").first
            question_bubble = chat_input.locator(
                "xpath=ancestor::*[self::div or self::section][2]//*[contains(@class, 'chatbot')][1]"
            ).first
            if question_bubble.count():
                text = question_bubble.text_content()
                if text:
                    return text.strip()
        except Exception:
            pass
        return ""
    
    def _handle_popups(self):
        """Handle popup dialogs in application form"""
        try:
            # Look for popup containers
            popups = self.page.locator(".popup, .modal, .dialog, .overlay").all()
            
            for popup in popups:
                if popup.is_visible():
                    # Check if it's a question popup
                    question_text = popup.text_content() if popup.count() else ""
                    if "question" in question_text.lower() or "answer" in question_text.lower():
                        # Use question handler
                        self.question_handler.handle_questions()
                        continue
                    
                    # Fill salary expectation
                    salary_input = popup.locator("input[placeholder*='salary'], input[placeholder*='expectation']").first
                    if salary_input.count():
                        salary_input.fill("10-15 LPA")
                        self.browser.human_delay(0.5, 1)
                    
                    # Fill notice period
                    notice_input = popup.locator("input[placeholder*='notice']").first
                    if notice_input.count():
                        notice_input.fill("30 days")
                        self.browser.human_delay(0.5, 1)
                    
                    # Fill experience
                    exp_input = popup.locator("input[placeholder*='experience'], input[placeholder*='exp']").first
                    if exp_input.count():
                        exp_input.fill("3-5 years")
                        self.browser.human_delay(0.5, 1)
                    
                    # Click continue/next
                    next_btn = popup.locator(
                        "button:has-text('Next'), "
                        "button:has-text('Continue'), "
                        "button:has-text('Save'), "
                        "button:has-text('Submit')"
                    ).first
                    
                    if next_btn.count():
                        next_btn.click()
                        self.browser.human_delay(1, 2)
                        
        except Exception as e:
            logger.warning(f"Popup handling warning: {str(e)}")
    
    def _fill_text_inputs(self):
        """Fill text input fields"""
        try:
            inputs = self.page.locator("input[type='text'], input:not([type])").all()
            
            for inp in inputs:
                if inp.is_visible() and not inp.is_disabled():
                    placeholder = inp.get_attribute("placeholder") or ""
                    name = inp.get_attribute("name") or ""
                    value = inp.get_attribute("value") or ""
                    
                    if not value and not inp.get_attribute("type") == "file":
                        if "experience" in placeholder.lower() or "exp" in name.lower():
                            inp.fill("3-5 years")
                            self.browser.human_delay(0.3, 0.8)
                        elif "salary" in placeholder.lower() or "expect" in placeholder.lower():
                            inp.fill("15 LPA")
                            self.browser.human_delay(0.3, 0.8)
                        elif "notice" in placeholder.lower():
                            inp.fill("30 days")
                            self.browser.human_delay(0.3, 0.8)
                        elif "location" in placeholder.lower() or "city" in placeholder.lower():
                            inp.fill("Bangalore")
                            self.browser.human_delay(0.3, 0.8)
                    
        except Exception as e:
            logger.warning(f"Text input fill warning: {str(e)}")
    
    def _fill_dropdowns(self):
        """Fill dropdown/select fields"""
        try:
            selects = self.page.locator("select").all()
            
            for select in selects:
                if select.is_visible():
                    options = select.locator("option").all()
                    for opt in options:
                        text = opt.text_content().lower() if opt.count() else ""
                        if "experienced" in text or "3-5" in text or "yes" in text:
                            opt.click()
                            self.browser.human_delay(0.5, 1)
                            break
                        elif text and "select" not in text and "choose" not in text:
                            opt.click()
                            self.browser.human_delay(0.5, 1)
                            break
                    
        except Exception as e:
            logger.warning(f"Dropdown fill warning: {str(e)}")
    
    def _fill_radios(self):
        """Fill radio button fields"""
        try:
            radios = self.page.locator("input[type='radio']").all()
            
            for radio in radios:
                if radio.is_visible() and not radio.is_checked():
                    value = radio.get_attribute("value") or ""
                    if "yes" in value.lower() or "available" in value.lower():
                        radio.click()
                        self.browser.human_delay(0.3, 0.8)
                    elif "experienced" in value.lower() or "professional" in value.lower():
                        radio.click()
                        self.browser.human_delay(0.3, 0.8)
                    
        except Exception as e:
            logger.warning(f"Radio fill warning: {str(e)}")
    
    def _handle_multi_step_form(self):
        """Handle multi-step application forms"""
        try:
            # Check for "Next" or "Continue" button
            next_selectors = [
                "button:has-text('Next')",
                "button:has-text('Continue')",
                "button:has-text('Next Step')",
                "button:has-text('Proceed')"
            ]
            
            for selector in next_selectors:
                next_btn = self.page.locator(selector).first
                if next_btn.count() and next_btn.is_visible():
                    logger.info("📋 Moving to next step...")
                    next_btn.click()
                    self.browser.human_delay(2, 3)
                    # Recursively handle next steps
                    self._handle_multi_step_form()
                    break
                    
        except Exception as e:
            logger.warning(f"Multi-step handling warning: {str(e)}")
    
    def _submit(self) -> bool:
        """Submit the application"""
        try:
            submit_selectors = [
                "button:has-text('Submit')",
                "button:has-text('Apply')",
                "button:has-text('Finish')",
                "button:has-text('Submit Application')",
                "button:has-text('Send Application')",
                "button:has-text('Send')",
                "input[value='Submit']",
                "input[value='Apply']",
                ".submit-btn",
                ".apply-btn",
                "button[class*='submit']"
            ]
            
            for selector in submit_selectors:
                submit_btn = self.page.locator(selector).first
                if submit_btn.count() and submit_btn.is_visible():
                    submit_btn.click()
                    self.browser.human_delay(3, 5)
                    
                    # Check for confirmation
                    confirmation = self._check_submission_confirmation()
                    if confirmation:
                        logger.info("✅ Application submitted successfully!")
                        return True
                    else:
                        logger.warning("⚠️ Submission may have failed")
                        return False
            
            logger.warning("Submit button not found")
            return False
            
        except Exception as e:
            logger.error(f"Submit failed: {str(e)}")
            return False
    
    def _check_submission_confirmation(self) -> bool:
        """Check if submission was successful"""
        try:
            page_text = self.page.content().lower()
            confirmation_indicators = [
                "application submitted",
                "applied successfully",
                "thank you",
                "confirmation",
                "successfully applied"
            ]
            
            for indicator in confirmation_indicators:
                if indicator in page_text:
                    return True
            
            # Check for success message elements
            success_selectors = [
                ".success",
                ".thank-you",
                ".confirmation",
                ".applied",
                ".submitted"
            ]
            
            for selector in success_selectors:
                elem = self.page.locator(selector).first
                if elem.count() and elem.is_visible():
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Confirmation check warning: {str(e)}")
            return False