from django.contrib import admin

# Register your models here.







from django.apps import apps
from django.contrib import admin

# Registering all models?
class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        if 'created' in self.list_display:
            self.ordering = ['-created']
        
        super(ListAdminMixin, self).__init__(model, admin_site)


models = apps.get_models()
# print('# models: ', models)
for model in models:
    admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass