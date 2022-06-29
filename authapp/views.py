from django.db import transaction
from django.shortcuts import render, HttpResponseRedirect
from authapp.forms import ShopUserLoginForm, ShopUserRegisterForm, ShopUserProfileEditForm
from django.contrib import auth
from django.urls import reverse

from authapp.models import ShopUser
from geekshop import settings
from django.core.mail import send_mail

from authapp.forms import ShopUserEditForm


def login(request):
    title = 'вход'

    login_form = ShopUserLoginForm(data=request.POST or None)
    next = request.GET['next'] if 'next' in request.GET.keys() else ''
    #print('next', next)

    if request.method == 'POST' and login_form.is_valid():
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            if 'next' in request.POST.keys():
                #print('redirect next', request.POST['next'])
                return HttpResponseRedirect(request.POST['next'])
            else:
                return HttpResponseRedirect(reverse('main'))

    content = {
        'title': title,
        'login_form': login_form,
        'next': next
    }

    return render(request, 'authapp/login.html', content)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('main'))


def register(request):
    title = 'регистрация'
    if request.method == 'POST':
        register_form = ShopUserRegisterForm(request.POST, request.FILES)

        if register_form.is_valid():
            user = register_form.save()  # user is inactive
            if send_verify_mail(user):
                print('Сообщение подтверждения отправлено')
            else:
                print('Ошибка отправки сообщения')
            return HttpResponseRedirect(reverse('auth:login'))

    else:
        register_form = ShopUserRegisterForm()
        content = {'title': title, 'register_form': register_form}
        return render(request, 'authapp/register.html', content)


# декоратор для целостности данных (транзакция все или ничего)
# две связанные таблицы в рамках одной транзакции
@transaction.atomic
def edit(request):
    title = 'редактирование'
    if request.method == 'POST':
        edit_form = ShopUserEditForm(request.POST, request.FILES,
                                     instance=request.user)
        profile_form = ShopUserProfileEditForm(request.POST,
                                               instance=request.user.shopuserprofile)
        if edit_form.is_valid() and profile_form.is_valid():
            edit_form.save()  # сработает сигнал для ShopUserProfile
            return HttpResponseRedirect(reverse('auth:edit'))
    else:
        edit_form = ShopUserEditForm(instance=request.user)
        profile_form = ShopUserProfileEditForm(
            instance=request.user.shopuserprofile
            )
        content = {
            'title': title,
            'edit_form': edit_form,
            'profile_form': profile_form
            }
        return render(request, 'authapp/edit.html', content)


def send_verify_mail(user):
    verify_link = reverse('auth:verify', args=[user.email, user.activation_key])
    title = f'Подтверждение учетной записи {user.username}'
    message = f'Для подтверждения учетной записи {user.username} на портале {settings.DOMAIN_NAME} ' \
              f'пройдите по ссылке: \n{settings.DOMAIN_NAME}{verify_link}'
    # [user.email] - list of receivers:
    return send_mail(title, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)


def verify(request, email, activation_key):
    try:
        user = ShopUser.objects.get(email=email)
        if user.activation_key == activation_key and not user.is_activation_key_expired():
            user.is_active = True
            user.save()
            # auth.login(request, user)
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return render(request, 'authapp/verification.html')
        else:
            print(f'error activation user: {user}')
            return render(request, 'authapp/verification.html')
    except Exception as e:
        print(f'error activation user : {e.args}')
        return HttpResponseRedirect(reverse('main'))
