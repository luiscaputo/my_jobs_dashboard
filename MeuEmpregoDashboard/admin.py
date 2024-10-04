from django.contrib import admin

from .models import Categories, Blogs, Companies, CommentReplies, Comments, Jobs, Users

admin.site.site_header = 'Meu Emprego Dashboard'
admin.site.site_title = 'Painel Administrativo'
admin.site.index_title = 'Painel Administrativo'

admin.site.register(Categories)
admin.site.register(Blogs)
admin.site.register(Companies)
admin.site.register(CommentReplies)
admin.site.register(Comments)
admin.site.register(Jobs)
admin.site.register(Users)
