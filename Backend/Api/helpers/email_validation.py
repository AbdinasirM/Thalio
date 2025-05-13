from email_validator import validate_email, EmailNotValidError


def validate_emails(email_address):
    try:
        email_info = validate_email(email_address, check_deliverability=True)
        # Return the normalized email address
        return email_info.normalized
    except EmailNotValidError as e:
        return f"Error: {str(e)}"

# email = "my+address@gmail.com"
# print(validate_emails(email))