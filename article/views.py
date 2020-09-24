from django.shortcuts import render, redirect
from article.models import ArticlePost
import markdown
# 引入刚才定义的ArticlePostForm表单类
from article.forms import ArticlePostForm
from django.http import HttpResponse
# 引入User模型
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# 引入分页模块
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
from article.models import ArticleColumn
# 引入评论表单
from comment.forms import CommentForm
# Create your views here.

@login_required(login_url='/userprofile/login/')
def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    if search:
        try:
            author_id = User.objects.get(username=search)
            if order == 'total_views':
                # 用 Q对象 进行联合搜索
                # Q(title__icontains=search)意思是在模型的title字段查询，
                # icontains是不区分大小写的包含，中间用两个下划线隔开。search
                # 是需要查询的文本。多个Q对象用管道符|隔开，就达到了联合查询的目的。

                article_list = ArticlePost.objects.filter(
                    Q(title__icontains=search) |
                    Q(body__icontains=search) |
                    Q(author_id=author_id)
                ).order_by('-total_views')
            else:
                article_list = ArticlePost.objects.filter(
                    Q(title__icontains=search) |
                    Q(body__icontains=search) |
                    Q(author_id=author_id)
                )
        except:
            if order == 'total_views':
                # 用 Q对象 进行联合搜索
                # Q(title__icontains=search)意思是在模型的title字段查询，
                # icontains是不区分大小写的包含，中间用两个下划线隔开。search
                # 是需要查询的文本。多个Q对象用管道符|隔开，就达到了联合查询的目的。

                article_list = ArticlePost.objects.filter(
                    Q(title__icontains=search) |
                    Q(body__icontains=search)
                ).order_by('-total_views')
            else:
                article_list = ArticlePost.objects.filter(
                    Q(title__icontains=search) |
                    Q(body__icontains=search)
                )

    else:
        # 将 search 参数重置为空
        search = ''
        if order == 'total_views':
            article_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            article_list = ArticlePost.objects.all()
    paginator = Paginator(article_list, 4)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    context = {'articles': articles, 'order': order, 'search': search}
    return render(request, 'article/list.html', context)

# @login_required(login_url='/userprofile/login/')
# def article_mylist(request, id):
#     user_id = User.objects.get(id=id)
#     user_list = ArticlePost.objects.get(author_id=user_id)
#     return render(request, 'article/list.html', {'articles': user_list})



def article_detail(request, id):
    # 取出文章
    article = ArticlePost.objects.get(id=id)
    # 取出文章评论
    comments = Comment.objects.filter(article=id)
    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    md = markdown.Markdown(extensions=[
                                         # 包含 缩写、表格等常用扩展
                                         'markdown.extensions.extra',
                                         # 语法高亮扩展
                                         'markdown.extensions.codehilite',
                                         # 目录扩展
                                         'markdown.extensions.toc',
                                     ])
    article.body = md.convert(article.body)
    # 引入评论表单
    comment_form = CommentForm()
    # 新增了md.toc对象
    context = {'article': article, 'toc': md.toc, 'comments': comments, 'comment_form': comment_form,}
    # 为了能将toc单独提取出来，我们先将Markdown类赋值给一个临时变量md，然后用convert()方法
    # 将正文渲染为html页面。通过md.toc将目录传递给模板。
    # 载入模板，返回context对象
    return render(request, 'article/detail.html', context)
# 检查登录
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户，并传入此用户的id
            new_article.author = User.objects.get(id=request.user.id)
            # 新增的代码
            if request.FILES.get('avatar'):
                new_article.avatar = request.FILES.get('avatar')
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 将新文章保存到数据库中
            new_article.save()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 新增及修改的代码
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = {'article_post_form': article_post_form, 'columns': columns }
        # 返回模板
        return render(request, 'article/create.html', context)

# def article_delete(request, id):
#     article = ArticlePost.objects.get(id=id)
#     article.delete()
#     return redirect("article:article_list")
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")

# 提醒用户登录
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    if request.method == 'POST':
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            # 新增的代码
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:article_detail", id=id)
            # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

            # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 新增及修改的代码
        columns = ArticleColumn.objects.all()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = {'article': article, 'article_post_form': article_post_form, 'columns': columns,}
        # 将响应返回到模板中
        return render(request, 'article/update.html', context)
