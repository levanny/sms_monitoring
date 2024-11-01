# ფუნქცია ფაილში ჩაწერილ ტელეფონის ნომრებსა და მეილებს გადაიტანს ლისტებში და დააბრუნებს მათ.
# filename_p არის ტელეფონის ნომრების ფაილის მისამართი, ხოლო filename_m არის მეილების.
def get_numbers_and_mails(filename_p,filename_m):
    with open(filename_p,'r') as f:
        f = f.read().strip()
    numbers = f.split('\n')

    with open(filename_m,'r') as f:
        f = f.read().strip()
    mails = f.split('\n')


    return numbers, mails

# ფუნქცია გააგზავნის შეტყობინებებს მეილებსა და ტელეფონის ნომრებზე.
def send_warnings(message):
    from ies_mail_sender import send_mail
    from ies_sms_sender import send_sms

    numbers, emails = get_numbers_and_mails('phone_numbers.txt','emails.txt')
    subject = "ყურადღება!"
    
    send_mail(emails,subject,message)
    send_sms(message=message, numbers=numbers)

def check_if_magti_url_is_alive():
    import requests
    import os
    from dotenv import load_dotenv

    load_dotenv()
    magti_url = os.getenv('MAGTI_URL')

    try:
        response = requests.get(magti_url)
        if not response.ok:
            print("მაგთის ლინკი გათიშულია!")
            send_warnings(message = f"მაგთის ლინკი გათიშულია\nStatus code: {response.status_code}")
        else:
            print("მაგთის ლინკი მუშაობს!")
            pass
    except Exception as err:
        print("მაგთის ლინკითან დაკავშირება ვერ მოხერხდა!")
        send_warnings(message = f"მაგთის ლინკი გათიშულია\nError: "+f"{err}"[:18])

 
# check_if_magti_url_is_alive()
print(get_numbers_and_mails('phone_numbers.txt','emails.txt'))
