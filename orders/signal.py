from django.core.mail import send_mail

def create_send_mail(email, first_name, last_name, token):
    subject = "Сообщение от  Сервиса заказа товаров для розничных сетей "
    message = f"Уважаемый {first_name} {last_name},\nВы получили это письмо т.к. создали нового пользователя в нашем сервисе.\nДля дальнейшего взаимодействия с нашим сервисом используйте" \
              f" токен:\n{token}"
    send_mail(subject, message, from_email=None, recipient_list=[email])

def update_send_mail(email, first_name, last_name, token):
    subject = "Сообщение от  Сервиса заказа товаров для розничных сетей "
    message = f"Уважаемый {first_name} {last_name},\nВы получили это письмо т.к. изменили учетные данные пользователя в нашем сервисе." \
              f"\nДля дальнейшего взаимодействия с нашим сервисом используйте новый " \
              f" токен:\n{token}"
    send_mail(subject, message, from_email=None, recipient_list=[email])