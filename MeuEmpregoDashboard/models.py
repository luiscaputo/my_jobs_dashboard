from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator, URLValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name.strip():
            raise ValidationError({'name': 'O nome do grupo não pode estar vazio.'})


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, on_delete=models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)

    def clean(self):
        if not self.group:
            raise ValidationError({'group': 'O grupo deve ser especificado.'})
        if not self.permission:
            raise ValidationError({'permission': 'A permissão deve ser especificada.'})


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', on_delete=models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name.strip():
            raise ValidationError({'name': 'O nome da permissão não pode estar vazio.'})
        if not self.codename.strip():
            raise ValidationError({'codename': 'O codename da permissão não pode estar vazio.'})


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254, blank=True, null=True)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'

    def __str__(self):
        return self.username

    def clean(self):
        # Validação dos campos booleanos representados como inteiros
        for field in ['is_superuser', 'is_staff', 'is_active']:
            value = getattr(self, field)
            if value not in [0, 1]:
                raise ValidationError({field: f'O campo {field} deve ser 0 ou 1.'})
        
        # Validação do email
        if self.email:
            EmailValidator()(self.email)


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)

    def clean(self):
        if not self.user:
            raise ValidationError({'user': 'O usuário deve ser especificado.'})
        if not self.group:
            raise ValidationError({'group': 'O grupo deve ser especificado.'})


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)

    def clean(self):
        if not self.user:
            raise ValidationError({'user': 'O usuário deve ser especificado.'})
        if not self.permission:
            raise ValidationError({'permission': 'A permissão deve ser especificada.'})


class Blogs(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author_id = models.CharField(max_length=500, blank=True, null=True)
    published_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'blogs'

    def __str__(self):
        return self.title

    def clean(self):
        # Validação das datas
        if self.published_at and self.updated_at:
            if self.updated_at < self.published_at:
                raise ValidationError({'updated_at': 'A data de atualização deve ser posterior à data de publicação.'})


class Categories(models.Model):
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categories'

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name.strip():
            raise ValidationError({'name': 'O nome da categoria não pode estar vazio.'})


class CommentReplies(models.Model):
    comment = models.ForeignKey('Comments', on_delete=models.DO_NOTHING, blank=True, null=True)
    author_id = models.CharField(max_length=500, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'comment_replies'

    def __str__(self):
        return self.author_id if self.author_id else "Resposta"

    def clean(self):
        if self.content and not self.content.strip():
            raise ValidationError({'content': 'O conteúdo da resposta não pode estar vazio.'})


class Comments(models.Model):
    blog = models.ForeignKey(Blogs, on_delete=models.DO_NOTHING, blank=True, null=True)
    author_id = models.CharField(max_length=500, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comments'

    def __str__(self):
        return f"Comentário em {self.blog} por {self.author_id}"

    def clean(self):
        if self.content and not self.content.strip():
            raise ValidationError({'content': 'O conteúdo do comentário não pode estar vazio.'})
        if self.created_at and self.updated_at:
            if self.updated_at < self.created_at:
                raise ValidationError({'updated_at': 'A data de atualização não pode ser anterior à data de criação.'})


class Companies(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'companies'

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name.strip():
            raise ValidationError({'name': 'O nome da empresa não pode estar vazio.'})
        if self.website:
            URLValidator()(self.website)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', on_delete=models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'

    def clean(self):
        # Exemplo de validação: action_flag deve estar dentro de um conjunto válido
        if self.action_flag not in [0, 1, 2, 3, 4]:  # Ajuste conforme necessário
            raise ValidationError({'action_flag': 'O action_flag deve ser um valor válido.'})


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)

    def __str__(self):
        return f"{self.app_label}.{self.model}"

    def clean(self):
        if not self.app_label.strip():
            raise ValidationError({'app_label': 'O app_label não pode estar vazio.'})
        if not self.model.strip():
            raise ValidationError({'model': 'O model não pode estar vazio.'})


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'

    def clean(self):
        if not self.app.strip():
            raise ValidationError({'app': 'O campo app não pode estar vazio.'})
        if not self.name.strip():
            raise ValidationError({'name': 'O campo name não pode estar vazio.'})


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'

    def clean(self):
        if self.expire_date and self.expire_date < timezone.now():
            raise ValidationError({'expire_date': 'A data de expiração da sessão não pode ser no passado.'})


class Jobs(models.Model):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    type_work = models.CharField(max_length=255, blank=True, null=True)
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)]
    )
    responsibilities = models.TextField(blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    total_vagancy = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    published_at = models.DateTimeField()
    due_date_to_apply = models.DateField(blank=True, null=True)
    is_closed = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    is_approved = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    company_name = models.CharField(max_length=255, blank=True, null=True)
    email_to_apply = models.EmailField(max_length=255, blank=True, null=True)
    website_to_apply = models.URLField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Categories, on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(db_column='updated_At', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jobs'

    def __str__(self):
        return self.title

    def clean(self):
        # Validação das datas
        if self.published_at and self.due_date_to_apply:
            if self.published_at.date() > self.due_date_to_apply:
                raise ValidationError({'due_date_to_apply': 'A data de encerramento para candidatura deve ser posterior à data de publicação.'})

        # Validação de total_vagancy
        if self.total_vagancy is not None and self.total_vagancy <= 0:
            raise ValidationError({'total_vagancy': 'O número total de vagas deve ser positivo.'})

        # Validação de salary
        if self.salary is not None and self.salary < 0:
            raise ValidationError({'salary': 'O salário deve ser um valor positivo.'})

        # Validação de is_closed e is_approved
        for field in ['is_closed', 'is_approved']:
            value = getattr(self, field)
            if value not in [0, 1, None]:
                raise ValidationError({field: f'O campo {field} deve ser 0 ou 1.'})

        # Validar email_to_apply
        if self.email_to_apply:
            EmailValidator()(self.email_to_apply)

        # Validar website_to_apply
        if self.website_to_apply:
            URLValidator()(self.website_to_apply)

        # Garantir que title não esteja vazio
        if not self.title.strip():
            raise ValidationError({'title': 'O título da vaga não pode estar vazio.'})


class Users(models.Model):
    username = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users'

    def __str__(self):
        return self.username

    def clean(self):
        # Validar email
        if self.email:
            EmailValidator()(self.email)

        # Garantir que username não contenha espaços
        if ' ' in self.username:
            raise ValidationError({'username': 'O nome de usuário não deve conter espaços.'})

        # Garantir que password tenha pelo menos 8 caracteres
        if len(self.password) < 8:
            raise ValidationError({'password': 'A senha deve ter pelo menos 8 caracteres.'})
