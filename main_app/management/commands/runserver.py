import webbrowser
from django.core.management.commands.runserver import Command as RunServerCommand


class Command(RunServerCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--nothreaded', action='store_true', dest='nothreaded',
                            help='Disable threading in the development server.')

    def handle(self, *args, **options):
        print("\n✓ Starting Django development server...")
        print("Opening browser to home page...\n")
        
        # Open browser after a short delay to let the server start
        import threading
        import time
        
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://127.0.0.1:8000/')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        super().handle(*args, **options)
