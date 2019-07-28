# -*- coding:utf-8 -*-
# !/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: create_articles.py
@time: 2017/3/11 上午1:58
"""
import os
import time
import pprint

from django.conf import settings
from django.core.management.base import BaseCommand
from blog.models import Article, Tag, Category
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
import datetime


category_dir = settings.UPLOAD_ARTICLES_ROOT
# category_dir = '/Users/zhenwenlei/PycharmProjects/django_blog_dzreal/uploads/articles'
category_li = os.listdir(category_dir)
article_dict = {}

for category_name in category_li:
    article_dict.setdefault(category_name,[])
    article_dir = os.path.join(category_dir, category_name)
    article_li = os.listdir(article_dir)
    for article_name in article_li:
        article_filepath = os.path.join(article_dir, article_name)
        article_dict[category_name].append(article_filepath)

# pprint.pprint(article_dict)



class Command(BaseCommand):
    help = 'bulk create article'

    def handle(self, *args, **options):
        save_article_list = set()

        # 存文章
        for category_name, article_fliepath_li in article_dict.items():
            for article_filepath in article_fliepath_li:
                article_name = article_filepath.split('/')[-1]
                article_name_no_tail = article_name.split('.')[0]
                # 不允许存在相同标题的文章
                if(article_name_no_tail in save_article_list):
                    self.stdout.write(self.style.ERROR('{} 存储失败，因为有重复的文章\n'.format(article_name_no_tail)))
                    continue
                with open(article_filepath, 'r', encoding='utf-8') as fp:
                    body = fp.read()
                    user = get_user_model().objects.get_or_create(email='dzreal_93@126.com', username='Editor',
                                                                  password='test!q@w#eTYU')[0]
                    category = Category.objects.get_or_create(name=category_name, parent_category=None)[0]
                    category.save()
                    article = Article.objects.get_or_create(category=category,
                                                            title=article_name_no_tail,
                                                            body=body,
                                                            author=user
                                                            )[0]
                    article.save()
                    self.stdout.write(self.style.SUCCESS('{} 文章保存成功 \n'.format(article_name_no_tail)))
                    save_article_list.add(article_name_no_tail)
                    from DjangoBlog.utils import cache
                    cache.clear()
        self.stdout.write(self.style.SUCCESS('请确认需要保存的文章 {}\n'.format(save_article_list)))
