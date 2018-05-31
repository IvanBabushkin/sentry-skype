# coding: utf-8
import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from sentry.plugins.bases import notify
from sentry.http import safe_urlopen
from sentry.utils.safe import safe_execute

from . import __version__, __doc__ as package_doc


class TelegramNotificationsOptionsForm(notify.NotificationConfigurationForm):
    api_id = forms.CharField(
        label=_('BotAPI id'),
        widget=forms.TextInput(attrs={'placeholder': ''}),
        help_text=_(''),
    )
    api_secret = forms.CharField(
        label=_('BotAPI secret'),
        widget=forms.TextInput(attrs={'placeholder': ''}),
        help_text=_(''),
    )
    receivers = forms.CharField(
        label=_('Receivers'),
        widget=forms.Textarea(attrs={'class': 'span6'}),
        help_text=_('Enter receivers IDs (one per line). Personal messages, group chats and channels also available.'))

    message_template = forms.CharField(
        label=_('Message template'),
        widget=forms.Textarea(attrs={'class': 'span4'}),
        help_text=_('Set in standard python\'s {}-format convention, available names are: '
                    '{project_name}, {url}, {title}, {message}, {tag[%your_tag%]}'),
        initial='(yotfr)\nProject:<b> {project_name}</b>\n{tag[level]}: <b>{title}</b>\n{message}\n{url}\n(yotfr)'
    )

class SkypeNotificationsPlugin(notify.NotificationPlugin):
    title = 'Skype Notifications'
    slug = 'sentry_skype'
    description = package_doc
    version = __version__
    author = 'Ivan Babushkin'
    author_url = 'https://github.com'
    resource_links = [
        ('Bug Tracker', 'https://github.com//issues'),
        ('Source', 'https://github.com'),
    ]

    conf_key = 'sentry_skype'
    conf_title = title

    project_conf_form = TelegramNotificationsOptionsForm

    logger = logging.getLogger('sentry.plugins.sentry_telegram')

    def is_configured(self, project, **kwargs):
        return bool(self.get_option('api_id', project) and self.get_option('api_secret', project) and self.get_option('receivers', project))

    def get_config(self, project, **kwargs):
        return [
            {
                'name': 'api_id',
                'label': 'BotAPI id',
                'type': 'text',
                'help': '',
                'placeholder': '',
                'validators': [],
                'required': True,
            },
            {
                'name': 'api_secret',
                'label': 'BotAPI secret',
                'type': 'text',
                'help': '',
                'placeholder': '',
                'validators': [],
                'required': True,
            },
            {
                'name': 'receivers',
                'label': 'Receivers',
                'type': 'textarea',
                'help': 'Enter receivers IDs (one per line). Personal messages, group chats',
                'validators': [],
                'required': True,
            },
            {
                'name': 'message_template',
                'label': 'Message Template',
                'type': 'textarea',
                'help': 'Set in standard python\'s {}-format convention, available names are: '
                    '{project_name}, {url}, {title}, {message}, {tag[%your_tag%]}',
                'validators': [],
                'required': True,
                'default': '(yotfr)\nProject:<b> {project_name}</b>\n{tag[level]}: <b>{title}</b>\n{message}\n{url}\n(yotfr)'
            },
        ]

    def build_message(self, group, event):
        names = {
            'title': event.title,
            'tag': {k:v for k, v in event.tags},
            'message': event.message,
            'project_name': group.project.name,
            'url': group.get_absolute_url(),
        }

        template = self.get_message_template(group.project)
        text = template.format(**names)
        return text


    def get_message_template(self, project):
        return self.get_option('message_template', project)

    def get_receivers(self, project):
        receivers = self.get_option('receivers', project)
        if not receivers:
            return []
        return filter(bool, receivers.strip().splitlines())

    def send_message(self, message, receiver, api_id, api_secret):
        url = 'https://apis.skype.com/v2/conversations/' + receiver + '/activities'
        token = self.get_access_token(client_id=api_id, client_secret=api_secret)
        headers = {'Authorization':'Bearer ' + token}
        payload = {'message':{'content': message}}
        self.logger.debug('Sending message to %s ' % receiver)
        response = safe_urlopen(
            method='POST',
            headers=headers,
            url=url,
            json=payload,
        )
        self.logger.debug('Response code: %s, content: %s' % (response.status_code, response.content))


    def notify_users(self, group, event, fail_silently=False):
        self.logger.debug('Received notification for event: %s' % event)
        receivers = self.get_receivers(group.project)
        self.logger.debug('for receivers: %s' % ', '.join(receivers or ()))
        message = self.build_message(group, event)
        self.logger.debug('Built message: %s' % message)

        api_id = self.get_option('api_id', group.project)
        api_secret = self.get_option('api_secret', group.project)

        #url = self.build_url(group.project)
        #self.logger.debug('Built url: %s' % url)
        for receiver in receivers:
            safe_execute(self.send_message, message, receiver, api_id, api_secret, _with_transaction=False)
