"""Generate fresh Ethereal email test account credentials"""
import requests

print("\n🔧 Generating fresh test email credentials...\n")

try:
    response = requests.post('https://api.nodemailer.com/user', timeout=10)
    if response.ok:
        account = response.json()
        print("✅ Test email account created!")
        print("\n📧 Add these to your .env file:\n")
        print(f"MAIL_SERVER={account['smtp']['host']}")
        print(f"MAIL_PORT={account['smtp']['port']}")
        print(f"MAIL_USE_TLS=True")
        print(f"MAIL_USE_SSL=False")
        print(f"MAIL_USERNAME={account['user']}")
        print(f"MAIL_PASSWORD={account['pass']}")
        print(f"MAIL_DEFAULT_SENDER=Tradzy Orders <noreply@tradzy.com>")
        print(f"\n🌐 View sent emails at: https://ethereal.email/login")
        print(f"   Username: {account['user']}")
        print(f"   Password: {account['pass']}")
        print("\n💡 These credentials work for testing - emails are captured but not actually sent!")
    else:
        print(f"❌ Failed to create account: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Alternative: Just use Gmail with an App Password")
    print("   See: https://myaccount.google.com/apppasswords")
