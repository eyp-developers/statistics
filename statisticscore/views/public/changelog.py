import os
import mistune
from django.shortcuts import render
from django.conf import settings


CHANGELOG_URL = os.path.join(settings.BASE_DIR, "CHANGELOG.md")


def changelog(request):

    # Get the raw markdown from GitHub
    raw_markdown = open(CHANGELOG_URL).read()

    # Render the markdown
    rendered_markdown = mistune.markdown(raw_markdown)

    # Pass the rendered markdown on to the template, where it will be inserted
    context = {'changelog': rendered_markdown}

    return render(request, 'statisticscore/changelog.html', context)
