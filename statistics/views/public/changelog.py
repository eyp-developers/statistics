import urllib.request, urllib.error, urllib.parse
import mistune
from django.shortcuts import render

CHANGELOG_URL = "https://raw.githubusercontent.com/" \
                "eyp-developers/statistics/master/CHANGELOG.md"


def changelog(request):

    # Get the raw markdown from GitHub
    raw_markdown = urllib.request.urlopen(CHANGELOG_URL).read()

    # Render the markdown
    rendered_markdown = mistune.markdown(raw_markdown)

    # Pass the rendered markdown on to the template, where it will be inserted
    context = {'changelog': rendered_markdown}

    return render(request, 'statistics/changelog.html', context)
