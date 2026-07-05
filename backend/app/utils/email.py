import logging
import resend
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_address = settings.FROM_EMAIL or "Cognora <noreply@cognora.app>"
        self.base_url = (settings.APP_URL or "http://localhost:3000").rstrip("/")
        if self.api_key:
            resend.api_key = self.api_key

    def send_email(self, to: str, subject: str, html_body: str) -> bool:
        if not self.api_key:
            logger.warning(f"No RESEND_API_KEY configured. Email not sent to {to}")
            return False
        try:
            params = {
                "from": self.from_address,
                "to": [to],
                "subject": subject,
                "html": html_body,
            }
            response = resend.Emails.send(params)
            logger.info(f"Email sent to {to} — response: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False

    def send_verification_email(self, to: str, token: str) -> bool:
        verification_url = f"{self.base_url}/verify-email?token={token}"

        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px 24px;">
            <div style="text-align: center; margin-bottom: 32px;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 12px; background: #2563EB;">
                    <span style="color: white; font-size: 24px;">✦</span>
                </div>
                <h1 style="margin: 16px 0 4px; font-size: 24px; color: #0F172A;">Verify your email</h1>
                <p style="margin: 0; color: #64748B; font-size: 14px;">Welcome to Cognora! Click the button below to verify your email address.</p>
            </div>
            <div style="text-align: center; margin: 32px 0;">
                <a href="{verification_url}" style="display: inline-block; padding: 12px 32px; background: #2563EB; color: white; text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: 500;">Verify Email</a>
            </div>
            <p style="color: #64748B; font-size: 12px; text-align: center;">Or copy this link: <br><a href="{verification_url}" style="color: #2563EB;">{verification_url}</a></p>
            <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 32px 0;">
            <p style="color: #94A3B8; font-size: 12px; text-align: center;">If you didn't create an account, you can safely ignore this email.</p>
        </div>
        """
        return self.send_email(to, "Verify your email", html)

    def send_password_reset_email(self, to: str, token: str) -> bool:
        reset_url = f"{self.base_url}/reset-password?token={token}"

        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px 24px;">
            <div style="text-align: center; margin-bottom: 32px;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 12px; background: #2563EB;">
                    <span style="color: white; font-size: 24px;">✦</span>
                </div>
                <h1 style="margin: 16px 0 4px; font-size: 24px; color: #0F172A;">Reset your password</h1>
                <p style="margin: 0; color: #64748B; font-size: 14px;">Click the button below to reset your password. This link expires in 1 hour.</p>
            </div>
            <div style="text-align: center; margin: 32px 0;">
                <a href="{reset_url}" style="display: inline-block; padding: 12px 32px; background: #2563EB; color: white; text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: 500;">Reset Password</a>
            </div>
            <p style="color: #64748B; font-size: 12px; text-align: center;">Or copy this link: <br><a href="{reset_url}" style="color: #2563EB;">{reset_url}</a></p>
            <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 32px 0;">
            <p style="color: #94A3B8; font-size: 12px; text-align: center;">If you didn't request this, you can safely ignore this email.</p>
        </div>
        """
        return self.send_email(to, "Reset your password", html)
