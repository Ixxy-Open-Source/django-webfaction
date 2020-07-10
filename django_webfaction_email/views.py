import xmlrpc.client

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from .forms import EmailForm
from .utils import generate_mailbox_name
from .utils import generate_targets
from .utils import get_email_accounts

from .models import Log


@never_cache
@staff_member_required
def email_changelist(request):
    email_accounts = get_email_accounts()
    return render_to_response(
        'email_changelist.html',
        {'emails': email_accounts},
        RequestContext(request),
    )


@never_cache
@staff_member_required
def email_changeform(request, id=None):

    if request.method == 'POST':

        # Submitting the form
        form = EmailForm(request.POST)
        change = False

        if form.is_valid():

            f = form.cleaned_data
            server = xmlrpc.client.Server('https://api.webfaction.com/')
            session_id, account = server.login(settings.WEBFACTION_USERNAME, settings.WEBFACTION_PASSWORD)

            if id is None:

                # Creating a new email
                if f['create_mailbox']:
                    mailbox_name = generate_mailbox_name(f['email_address'])
                    password = server.create_mailbox(
                        session_id,
                        mailbox_name,
                        f['enable_spam_protection'])['password']
                    targets = generate_targets(mailbox_name, f['redirect'])
                else:
                    targets = generate_targets(None, f['redirect'])

                server.create_email(
                    session_id,
                    f['email_address'],
                    targets,
                    f['autoresponder_on'],
                    f['autoresponder_subject'],
                    f['autoresponder_message'],
                )
                email_msg = "Created email address {}".format(f['email_address'])
                l = Log(user=request.user, action=email_msg)
                l.save()
                messages.info(request, email_msg)

                if f['create_mailbox']:
                    mailbox_msg = "Created mailbox {}".format(mailbox_name)
                    password_msg = mailbox_msg + " with password {}".format(password)
                    if settings.WEBFACTION_LOG_PASSWORD:
                        l = Log(user=request.user, action=password_msg)
                    else:
                        l = Log(user=request.user, action=mailbox_msg)
                    l.save()
                    messages.info(request, password_msg)
            else:

                # Editing an existing email
                change = True
                message_list = []
                update_email = False

                if f['autoresponder_on'] != f['autoresponder_on_prev']:
                    message_list.append("Autoresponder Status for {} changed to {}".format(
                        f['email_address'],
                        f['autoresponder_on']),
                    )
                    update_email = True

                if f['autoresponder_subject'] != f['autoresponder_subject_prev']:
                    message_list.append("Autoresponder Subject for {} changed from '{}' to '{}'".format(
                        f['email_address'],
                        f['autoresponder_subject_prev'],
                        f['autoresponder_subject']),
                    )
                    update_email = True

                if f['autoresponder_message'] != f['autoresponder_message_prev']:
                    message_list.append("Autoresponder Message for {} changed from '{}' to '{}'".format(
                        f['email_address'],
                        f['autoresponder_message_prev'],
                        f['autoresponder_message']),
                    )
                    update_email = True

                if f['redirect'] != f['redirect_prev']:
                    message_list.append("Redirect Address for {} changed from '{}' to '{}'".format(
                        f['email_address'],
                        f['redirect_prev'],
                        f['redirect']),
                    )
                    update_email = True

                if update_email:
                    mailbox_name = f.get('mailbox_prev', None)
                    targets = generate_targets(mailbox_name, f['redirect'])
                    server.update_email(
                        session_id,
                        f['email_address'],
                        targets,
                        f['autoresponder_on'],
                        f['autoresponder_subject'],
                        f['autoresponder_message'],
                        f['email_address'],
                    )

                if f['enable_spam_protection'] != f['enable_spam_protection_prev']:
                    mailbox_name = f.get('mailbox_prev', None)
                    try:
                        server.update_mailbox(session_id, mailbox_name, f['enable_spam_protection'])
                        message_list.append("Spam Protection Status for {} changed to {}".format(
                            f['enable_spam_protection'],
                            f['email_address']),
                        )

                    except xmlrpc.client.Fault:  # Probably means this is a redirect only address

                        message_list.append(
                            "Error. Can only change spam protection status on addresses with their own mailbox"
                        )

                for msg in message_list:
                    messages.info(request, msg)
                    l = Log(user=request.user, action=msg)
                    l.save()

            return HttpResponseRedirect('..')
    else:

        # Blank form
        if id is None:  # We are creating
            change = False
            form = EmailForm()

        else:  # We are updating

            change = True
            email_accounts = get_email_accounts()
            email_account = [x for x in email_accounts if x['id'] == int(id)][0]  # Assume only one match

            if email_account.get('mailbox', None):

                # Has a mailbox
                enable_spam_protection = email_account['mailbox']['enable_spam_protection']
            else:

                # Is just a redirect
                enable_spam_protection = False

            if email_account.get('mailbox', False):
                mailbox_name = email_account['mailbox']['mailbox']
            else:
                mailbox_name = ''

            form = EmailForm({
                'email_address': email_account['email_address'],
                'email_address_prev': email_account['email_address'],
                'autoresponder_on': email_account['autoresponder_on'],
                'autoresponder_on_prev': email_account['autoresponder_on'],
                'autoresponder_subject': email_account['autoresponder_subject'],
                'autoresponder_subject_prev': email_account['autoresponder_subject'],
                'autoresponder_message': email_account['autoresponder_message'],
                'autoresponder_message_prev': email_account['autoresponder_message'],
                'enable_spam_protection': enable_spam_protection,
                'enable_spam_protection_prev': enable_spam_protection ,
                'create_mailbox': email_account.get('mailbox', False),
                'mailbox_prev': mailbox_name,
                'redirect': email_account.get('redirect', ''),
                'redirect_prev': email_account.get('redirect', ''),
            })
            del form.fields['create_mailbox']

    context = {'change': change, 'form': form}
    template = 'email_changeform.html'
    return TemplateResponse(
        request,
        template,
        context,
    )
