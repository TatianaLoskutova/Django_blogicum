from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .constants import NUMBER_OF_POSTS
from .forms import PostForm, CommentForm, UserForm
from .models import Post, Category, Comment


class PublishedPostsMixin:
    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            pub_date__lte=datetime.now(),
        )


class ProfileQuerysetMixin:
    def get_queryset(self):
        return super().get_queryset().select_related(
            'author',
            'location',
            'category'
        ).order_by(
            '-pub_date'
        ).annotate(
            comment_count=Count('comments')
        )


class IndexListView(PublishedPostsMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    ordering = ('-pub_date')
    paginate_by = NUMBER_OF_POSTS

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()
        queryset = queryset.annotate(comment_count=Count('comments'))
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context

    def get_queryset(self):
        return super().get_queryset().filter(
            category__is_published=True,
        )


class PostDetailView(PublishedPostsMixin, DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = get_object_or_404(
            self.model.objects.select_related(
                'location', 'author', 'category'
            ), id=self.kwargs['post_id']
        )
        if not (post.is_published or post.author == self.request.user):
            raise Http404('Страница не найдена')
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related(
                'author'
            )
        )
        return context

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if not (post.is_published or post.author == self.request.user):
            raise Http404('Страница не найдена')
        return super().dispatch(request, *args, **kwargs)


class CategoryPostsListView(PublishedPostsMixin, ListView):
    model = Post
    context_object_name = 'page_obj'
    template_name = 'blog/category.html'
    ordering = ('-pub_date')
    paginate_by = NUMBER_OF_POSTS

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(slug=self.kwargs['category_slug'])
        context['category'] = category
        return context

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        return super().get_queryset().filter(
            category__slug=category_slug,
            category__is_published=True,
        )

    def dispatch(self, request, *args, **kwargs):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True,
        )

        if not category.is_published:
            return Http404('Страница не найдена')
        return super().dispatch(request, *args, **kwargs)


class ProfileListView(ProfileQuerysetMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = NUMBER_OF_POSTS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        if self.author != self.request.user:
            queryset = super().get_queryset().filter(
                author=self.author,
                is_published=True,
            )
            return queryset
        return super().get_queryset().filter(author=self.author)


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.object:
            return context
        context['title'] = self.object.title
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.object:
            return context
        context['form'] = self.get_form()
        return context

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if user != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, id=kwargs['post_id'])
        if instance.author != request.user:
            return redirect(
                'blog:post_detail',
                post_id=instance.id
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.id},
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Post, id=kwargs['post_id'])
        if comment.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentForm
    template_name = 'blog/comments.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(
            Post,
            id=kwargs['post_id'],
            pub_date__lte=datetime.now(),
            is_published=True,
            category__is_published=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.post_obj.id},
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        if comment.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.post_id},
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        if comment.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.post_id},
        )
