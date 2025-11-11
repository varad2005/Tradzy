"""Email utility functions for sending order confirmations and receipts."""
from __future__ import annotations

from typing import Any
from datetime import datetime
from flask import current_app
from flask_mail import Mail, Message

mail = Mail()


def init_mail(app: Any) -> None:
    """Initialize Flask-Mail with the Flask app."""
    mail.init_app(app)


def create_ethereal_test_account() -> dict[str, str]:
    """
    Create a temporary test email account using Ethereal.
    Returns credentials that can be used for testing.
    """
    import requests
    try:
        response = requests.post('https://api.nodemailer.com/user')
        if response.ok:
            account = response.json()
            return {
                'user': account['user'],
                'pass': account['pass'],
                'smtp_host': account['smtp']['host'],
                'smtp_port': account['smtp']['port'],
                'web_url': f"https://ethereal.email/messages"
            }
    except:
        pass
    
    # Fallback to default test credentials
    return {
        'user': 'test@ethereal.email',
        'pass': 'test',
        'smtp_host': 'smtp.ethereal.email',
        'smtp_port': 587,
        'web_url': 'https://ethereal.email'
    }


def generate_order_receipt_html(order_data: dict[str, Any], user_email: str, username: str) -> str:
    """Generate HTML receipt for an order."""
    items_html = ""
    for item in order_data.get("items", []):
        item_total = item["price"] * item["quantity"]
        product_name = item.get("name", f"Product #{item['product_id']}")
        items_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #eee;">{product_name}</td>
            <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: center;">{item['quantity']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: right;">₹{item['price']:.2f}</td>
            <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: right;">₹{item_total:.2f}</td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Order Confirmation - Tradzy</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 28px;">Order Confirmed!</h1>
            <p style="color: #f0f0f0; margin: 10px 0 0 0;">Thank you for your order</p>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px;">
            <p style="font-size: 16px; margin-bottom: 20px;">Hi <strong>{username}</strong>,</p>
            
            <p style="font-size: 14px; margin-bottom: 25px;">
                Your order has been successfully placed and is being processed. Here are your order details:
            </p>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="color: #667eea; font-size: 18px; margin-top: 0; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                    Order Details
                </h2>
                <table style="width: 100%; margin-bottom: 15px;">
                    <tr>
                        <td style="padding: 8px 0;"><strong>Order ID:</strong></td>
                        <td style="padding: 8px 0; text-align: right;">#{order_data['id']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Order Date:</strong></td>
                        <td style="padding: 8px 0; text-align: right;">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Status:</strong></td>
                        <td style="padding: 8px 0; text-align: right;">
                            <span style="background: #ffc107; color: #333; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                                {order_data.get('status', 'pending').upper()}
                            </span>
                        </td>
                    </tr>
                </table>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="color: #667eea; font-size: 18px; margin-top: 0; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                    Items Ordered
                </h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #f5f5f5;">
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #667eea;">Item</th>
                            <th style="padding: 12px; text-align: center; border-bottom: 2px solid #667eea;">Qty</th>
                            <th style="padding: 12px; text-align: right; border-bottom: 2px solid #667eea;">Price</th>
                            <th style="padding: 12px; text-align: right; border-bottom: 2px solid #667eea;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colspan="3" style="padding: 15px 12px 12px 12px; text-align: right; font-size: 18px; font-weight: bold; border-top: 2px solid #667eea;">
                                Total Amount:
                            </td>
                            <td style="padding: 15px 12px 12px 12px; text-align: right; font-size: 18px; font-weight: bold; color: #667eea; border-top: 2px solid #667eea;">
                                ₹{order_data['total_amount']:.2f}
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196f3; margin-bottom: 20px;">
                <p style="margin: 0; font-size: 14px;">
                    <strong>📧 Questions?</strong> Reply to this email or contact our support team.
                </p>
            </div>
            
            <p style="font-size: 14px; color: #666; margin-top: 25px;">
                Thank you for choosing Tradzy!<br>
                <strong>The Tradzy Team</strong>
            </p>
        </div>
        
        <div style="text-align: center; padding: 20px; font-size: 12px; color: #999;">
            <p>This is an automated email. Please do not reply directly to this email.</p>
            <p>&copy; {datetime.now().year} Tradzy. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    return html


def generate_order_receipt_text(order_data: dict[str, Any], user_email: str, username: str) -> str:
    """Generate plain text receipt for an order."""
    items_text = ""
    for item in order_data.get("items", []):
        item_total = item["price"] * item["quantity"]
        product_name = item.get("name", f"Product #{item['product_id']}")
        items_text += f"\n  - {product_name} x {item['quantity']} @ ₹{item['price']:.2f} = ₹{item_total:.2f}"
    
    text = f"""
ORDER CONFIRMATION - TRADZY
{'=' * 60}

Hi {username},

Your order has been successfully placed and is being processed!

ORDER DETAILS
{'=' * 60}
Order ID: #{order_data['id']}
Order Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Status: {order_data.get('status', 'pending').upper()}

ITEMS ORDERED
{'=' * 60}{items_text}

{'=' * 60}
TOTAL AMOUNT: ₹{order_data['total_amount']:.2f}
{'=' * 60}

Thank you for choosing Tradzy!

Questions? Reply to this email or contact our support team.

Best regards,
The Tradzy Team

---
This is an automated email. Please do not reply directly to this email.
© {datetime.now().year} Tradzy. All rights reserved.
    """
    return text


def send_order_confirmation_email(
    to_email: str,
    username: str,
    order_data: dict[str, Any],
) -> bool:
    """
    Send order confirmation email with receipt to the customer.
    
    Args:
        to_email: Recipient email address
        username: Username of the customer
        order_data: Dictionary containing order details (id, total_amount, status, items)
        
    Returns:
        True if email was sent successfully, False otherwise
    """
    try:
        # Skip sending if email configuration is not set
        mail_username = current_app.config.get("MAIL_USERNAME", "")
        if not mail_username:
            current_app.logger.warning("Email not configured. Skipping email send.")
            return False
        
        # Console mode - just log the email instead of sending
        if mail_username.lower() == 'console':
            current_app.logger.info("=" * 60)
            current_app.logger.info("📧 EMAIL WOULD BE SENT (Console Mode)")
            current_app.logger.info("=" * 60)
            current_app.logger.info(f"To: {to_email}")
            current_app.logger.info(f"Subject: Order Confirmation #{order_data['id']} - Tradzy")
            current_app.logger.info(f"Order ID: {order_data['id']}")
            current_app.logger.info(f"Total: ₹{order_data['total_amount']:.2f}")
            current_app.logger.info(f"Status: {order_data.get('status', 'pending').upper()}")
            current_app.logger.info(f"Items: {len(order_data.get('items', []))}")
            current_app.logger.info("=" * 60)
            current_app.logger.info("✅ Email logged successfully (not actually sent - console mode)")
            return True
            
        subject = f"Order Confirmation #{order_data['id']} - Tradzy"
        
        html_body = generate_order_receipt_html(order_data, to_email, username)
        text_body = generate_order_receipt_text(order_data, to_email, username)
        
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=text_body,
            html=html_body,
        )
        
        mail.send(msg)
        current_app.logger.info(f"Order confirmation email sent to {to_email} for order #{order_data['id']}")
        
        # If using Ethereal/test email, log the preview URL
        if 'ethereal' in current_app.config.get("MAIL_SERVER", "").lower():
            current_app.logger.info("📧 Using test email server - emails are captured but not actually delivered")
            current_app.logger.info("🔗 View emails at: https://ethereal.email/messages")
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send order confirmation email: {str(e)}")
        return False
