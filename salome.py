import os
import requests
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv


load_dotenv()





# Email parametrebi .env
IES_INFO_EMAIL_ADDRESS = os.getenv('IES_INFO_EMAIL_ADDRESS')
IES_INFO_EMAIL_PASSWORD = os.getenv('IES_INFO_EMAIL_PASSWORD')  
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_SERVER_PORT = int(os.getenv('SMTP_SERVER_PORT'))

# HTTP status code
http_status_codes = {
    200: "OK - წარმატებული მოთხოვნა.",
    201: "Created - ახალი რესურსი შექმნილია.",
    202: "Accepted - მოთხოვნა მიღებულია, მაგრამ ჯერ არ შესრულებულა.",
    204: "No Content - მოთხოვნა წარმატებით შესრულდა, მაგრამ არაფერია დაბრუნებული.",
    304: "Not Modified - რესურსი არ არის შეცვლილი.",
    400: "Bad Request - მომსახურება ვერ ამუშავებს მოთხოვნას.",
    401: "Unauthorized - ავტორიზაცია საჭიროა.",
    403: "Forbidden - მოთხოვნა აღიარებულია, მაგრამ უარის თქმა.",
    404: "Not Found - რესურსი ვერ მოიძებნა.",
    500: "Internal Server Error - ზოგადი შეცდომა.",
    503: "Service Unavailable - მომსახურება არ არის ხელმისაწვდომი.",
}

def print_and_log(message, level='info'):
    log_file_path = "email_sender_log"
    pid = os.getpid()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] [{pid}] [{level.upper()}] {message}"
   
    print(log_message)
   
    with open(log_file_path, "a") as log_file:
        log_file.write(log_message + "\n")


#mail sender
def send_mail(recipients, subject, message, status_code=None):
    msg = MIMEMultipart()
    msg['From'] = IES_INFO_EMAIL_ADDRESS
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject

    if status_code is not None:
        message += f"\n\nMagti URL სტატუს კოდი: {status_code}"

    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP(host=SMTP_SERVER, port=SMTP_SERVER_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(IES_INFO_EMAIL_ADDRESS, IES_INFO_EMAIL_PASSWORD)
            server.sendmail(IES_INFO_EMAIL_ADDRESS, recipients, msg.as_string())
            print(f"Email sent to {recipients} with subject: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        print_and_log(f"Failed to send email: {e}", level='error')


#magti url shemowmeba
def check_magti_url():
    magti_url = os.getenv('MAGTI_URL')  # Get the Magti URL from .env

    params = {
        'request': 'oneway',
        'type': 'document'  
    }
   
    try:
        response = requests.get(magti_url, params=params, timeout=15)
        status_code = response.status_code
        response.raise_for_status() 
       
        return status_code, response.text

    except requests.exceptions.HTTPError as http_err:
        status_code = response.status_code
        error_message = f"HTTP შეცდომა: {http_err}, სტატუს კოდი: {status_code}"
        print_and_log(error_message, level='error')
        return status_code, error_message
        
    except requests.exceptions.ConnectionError:
        error_message = "კავშირი ვერ შედგა."
        print_and_log(error_message, level='error')
        return None, error_message
   
    except requests.exceptions.Timeout:
        error_message = "მოთხოვნა დროში ამოიწურა."
        print_and_log(error_message, level='error')
        return None, error_message
   
    except Exception as e:
        error_message = f"შეცდომა: {str(e)}"
        print_and_log(error_message, level='error')
        return None, error_message

def main():
    recipients = os.getenv('RECIPIENTS').split(',')
    magti_status_code, magti_response = check_magti_url()

    if magti_status_code == 200:
        message = f"Magti URL სტატუს კოდი: {magti_status_code}"
        print_and_log(message, level='info')
        send_mail(recipients, "Magti URL წარმატებით შევიდა", message)

    elif magti_status_code in [201, 400, 403, 500]:
        status_description = http_status_codes.get(magti_status_code, "უცნობი სტატუსი")
        message = f"Magti URL სტატუს კოდი: {magti_status_code} - {status_description}.\n\nპასუხი: {magti_response}"
        print_and_log(message, level='info')
        send_mail(recipients, f"Magti URL Status: {magti_status_code} {magti_response}", message, magti_status_code)

    elif magti_status_code is None:
        print_and_log(magti_response, level='error')
        send_mail(recipients, "Magti URL არ მუშაობს", magti_response)

    else:
        success_message = f"Magti URL სტატუს კოდი: {magti_status_code}, პასუხი: {magti_response}"
        print_and_log(success_message)

if __name__ == "__main__":
    main()