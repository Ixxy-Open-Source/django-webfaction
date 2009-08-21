import xmlrpclib

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache

from forms import EmailForm
from utils import generate_mailbox_name
from utils import generate_targets
from utils import get_email_accounts

from models import Log

@never_cache
@staff_member_required
def email_changelist(request):
    email_accounts = get_email_accounts()
    return render_to_response(
        'email_changelist.html',
        {
            'emails': email_accounts,
        },
        RequestContext(request),
    )

@never_cache
@staff_member_required
def email_changeform(request, id=None):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            server = xmlrpclib.Server('https://api.webfaction.com/')
            session_id, account = server.login(settings.WEBFACTION_USERNAME, settings.WEBFACTION_PASSWORD)
            if id == None:
                change = False
                if f['create_mailbox']:
                    mailbox_name = generate_mailbox_name(f['email_address'])
                    targets = generate_targets(mailbox_name, f['redirect'])
                    if not(settings.WEBFACTION_TEST):
                        password = server.create_mailbox(session_id, mailbox_name, f['enable_spam_protection'])['password']
                    else:
                        password = 'test'
                else:
                    targets = generate_targets(None, f['redirect'])
                if not(settings.WEBFACTION_TEST):
                    server.create_email(session_id, f['email_address'], targets, f['autoresponder_on'], f['autoresponder_subject'], f['autoresponder_message'])
                email_msg = "Created email address %s" % f['email_address']
                l = Log(user=request.user, action=email_msg)
                l.save()
                request.user.message_set.create(message=email_msg)
                if f['create_mailbox']:
                    mailbox_msg = "Created mailbox %s" % mailbox_name
                    password_msg = mailbox_msg +" with password %s" % password
                    if settings.WEBFACTION_LOG_PASSWORD:
                        l = Log(user=request.user, action=password_msg)
                    else:
                        l = Log(user=request.user, action=mailbox_msg)
                    l.save()
                    request.user.message_set.create(message=password_msg)
            else:
                change = True
                messages = []
                update_email = False
                if f['autoresponder_on']!=f['autoresponder_on_prev']:
                    messages.append("Autoresponder Status for %s changed to %s" % (f['email_address'], f['autoresponder_on']))
                    update_email = True
                if f['autoresponder_subject']!=f['autoresponder_subject_prev']:
                    messages.append("Autoresponder Subject for %s changed from '%s' to '%s'" % (f['email_address'], f['autoresponder_subject_prev'], f['autoresponder_subject']))
                    update_email = True
                if f['autoresponder_message']!=f['autoresponder_message_prev']:
                    messages.append("Autoresponder Message for %s changed from '%s' to '%s'" % (f['email_address'], f['autoresponder_message_prev'], f['autoresponder_message']))
                    update_email = True
                if f['redirect']!=f['redirect_prev']:
                    messages.append("Redirect Address for %s changed from '%s' to '%s'" % (f['email_address'], f['redirect_prev'], f['redirect']))
                    update_email = True
                if update_email:
                    mailbox_name = generate_mailbox_name(f['email_address'])
                    targets = generate_targets(mailbox_name, f['redirect'])
                    if not(settings.WEBFACTION_TEST):
                        server.update_email(session_id, f['email_address'], targets, f['autoresponder_on'], f['autoresponder_subject'], f['autoresponder_message'])
                if f['enable_spam_protection']!=f['enable_spam_protection_prev']:
                    mailbox_name = generate_mailbox_name(f['email_address'])
                    if not(settings.WEBFACTION_TEST):
                        try:
                            server.update_mailbox(session_id, mailbox_name, f['enable_spam_protection'])
                            messages.append("Spam Protection Status for %s changed to %s" % (f['enable_spam_protection'], f['email_address']))
                        except xmlrpclib.Fault: #Probably means this is a redirect only address
                            messages.append("Error. Can only change spam protection status on addresses with their own mailbox")
                for msg in messages:
                    request.user.message_set.create(message=msg)
                    l = Log(user=request.user, action=msg)
                    l.save()
            return HttpResponseRedirect('..')
    else:
        if id==None: # We are creating
            change = False
            form = EmailForm()
        else: # We are updating
            change = True
            email_accounts = get_email_accounts()
            email_account = [x for x in email_accounts if x['id']==int(id)][0] # Assume only one match
            if email_account.get('mailbox', None):
                enable_spam_protection = email_account['mailbox']['enable_spam_protection']
            else:
                enable_spam_protection = False
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
                'redirect': email_account.get('redirect', ''),
                'redirect_prev': email_account.get('redirect', ''),
            })
            del form.fields['create_mailbox']
    return render_to_response('email_changeform.html', {
        'change': change,
        'form': form,
        },
        RequestContext(request),
    )
