from django.conf import settings
from django import forms

from utils import generate_mailbox_name

class EmailForm(forms.Form):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    #email_address = ReadOnlyField()
    email_address = forms.EmailField()
    email_address_prev = forms.EmailField(required=False, widget=forms.HiddenInput)
    create_mailbox = forms.BooleanField(initial=True, required=False, help_text="Uncheck this if you only want to redirect and not access this account directly.")
    redirect = forms.EmailField(required=False, label="Address to redirect mail to", help_text="Forward all email sent to this address to another address")
    redirect_prev = forms.EmailField(required=False, widget=forms.HiddenInput)
    autoresponder_on = forms.BooleanField(required=False, label="Turn auto-responder on", help_text="Automatically reply to all emails with the message below")
    autoresponder_on_prev = forms.BooleanField(required=False, widget=forms.HiddenInput)
    autoresponder_subject = forms.CharField(required=False, help_text="The subject line for the automatic reply")
    autoresponder_subject_prev = forms.CharField(required=False, widget=forms.HiddenInput)
    autoresponder_message = forms.CharField(required=False, widget=forms.widgets.Textarea(), help_text="The actual message for the automatic reply")
    autoresponder_message_prev = forms.CharField(required=False, widget=forms.HiddenInput)
    enable_spam_protection = forms.BooleanField(required=False, help_text="Mark suspected spam with a hidden tag that you can use to filter the messages in your email software. Only works via a mailbox - not redirected mail.")
    enable_spam_protection_prev = forms.BooleanField(required=False, widget=forms.HiddenInput)
    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        if self.data.get('email_address', None): # If this field already exists it should be readonly
            self.fields['email_address'].widget.attrs['readonly'] = True # Note that this is insecure as the field can still be tampered with.
            self.fields['email_address'].widget.attrs['style'] = 'border: 0; color: #888;' # Naughty - mixing CSS with Python...
    def clean_email_address(self):
        data = self.cleaned_data['email_address']
        if not(data.split('@')[1] in settings.WEBFACTION_DOMAINS.keys()):
            raise forms.ValidationError("Domain name not recognized") #TODO email address should be just the prefix and domain should be a ChoiceField
        mailbox_name_length = len(generate_mailbox_name(data))
        if mailbox_name_length>32:
            raise forms.ValidationError("Email address is %s character(s) too long" % mailbox_name_length-32) # We could truncate the address so that it produces a valid mailbox name instead but then we would have to check for duplicate mailbox names.
        return data
    #TODO check for duplicate emails addresses and mailboxes

