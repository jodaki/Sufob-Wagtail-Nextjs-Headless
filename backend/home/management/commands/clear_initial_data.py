from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wagtail.models import Page
from home.models import HomePage
from blog.models import BlogPageIndex, BlogPage, BlogCategory, BlogTag
from sufob_comments.models import Comment

User = get_user_model()

class Command(BaseCommand):
    help = 'Clear all initial data from the project'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of data',
        )
        parser.add_argument(
            '--keep-users',
            action='store_true',
            help='Keep user accounts',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This command will delete data. Use --confirm to proceed.'
                )
            )
            return

        self.stdout.write(self.style.WARNING('Starting data cleanup...'))
        
        # Delete comments
        comment_count = Comment.objects.count()
        Comment.objects.all().delete()
        self.stdout.write(f'Deleted {comment_count} comments')
        
        # Delete blog pages
        blog_page_count = BlogPage.objects.count()
        BlogPage.objects.all().delete()
        self.stdout.write(f'Deleted {blog_page_count} blog pages')
        
        # Delete blog categories and tags
        category_count = BlogCategory.objects.count()
        tag_count = BlogTag.objects.count()
        BlogCategory.objects.all().delete()
        BlogTag.objects.all().delete()
        self.stdout.write(f'Deleted {category_count} categories and {tag_count} tags')
        
        # Delete blog index
        blog_index_count = BlogPageIndex.objects.count()
        BlogPageIndex.objects.all().delete()
        self.stdout.write(f'Deleted {blog_index_count} blog index pages')
        
        # Delete home pages (except root)
        home_page_count = HomePage.objects.count()
        HomePage.objects.all().delete()
        self.stdout.write(f'Deleted {home_page_count} home pages')
        
        # Delete users if not keeping them
        if not options['keep_users']:
            user_count = User.objects.exclude(is_superuser=True).count()
            User.objects.exclude(is_superuser=True).delete()
            self.stdout.write(f'Deleted {user_count} users (kept superusers)')
        
        self.stdout.write(self.style.SUCCESS('Data cleanup completed!'))
