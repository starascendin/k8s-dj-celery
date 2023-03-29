from django.apps import apps
from django.contrib import admin


class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        if model._meta.model_name == 'ContentSource':
            print("#DEBUG excluding raw_content_json_blob from ContentSource model...")
            self.list_display.remove('raw_content_json_blob')
        super(ListAdminMixin, self).__init__(model, admin_site)


models = apps.get_models()
for model in models:
    admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        print("#DEBUG registering all admin models...")
        if model._meta.model_name == 'ContentSource':
            admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {'exclude': ['raw_content_json_blob']})
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        print(f"#DEBUG model {model._meta.model_name} has already registered admin model...")
        pass