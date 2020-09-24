from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# timezone 用于处理时间相关事务。
from django.utils import timezone
from PIL import Image
# Create your models here.

class ArticleColumn(models.Model):
    """
    栏目的 Model
    """
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    # 文章更新时间。参数 auto_now=True 指定每次数据更新时自动写入当前时间
    update = models.DateTimeField(auto_now=True)
    # 正整数
    total_views = models.PositiveIntegerField(default=0)
    # 文章标题图
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )

    def save(self, *args, **kwargs):
        # 调用原有的 save() 的功能
        article = super(ArticlePost, self).save(*args, **kwargs)

        # 固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)

        return article

    def __str__(self):
        return self.title
    class Meta:
        # '-created' 表明数据应该以倒序排列
        ordering = ('-created',)

        # 获取文章地址
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])



