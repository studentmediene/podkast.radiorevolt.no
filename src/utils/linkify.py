import re


# Regex used in Linkify to identify text which looks like a URL
_urlfinderregex = re.compile(r'http([^\.\s]+\.[^\.\s<>]*)+[^\.\s<>]{2,}')


def linkify(text: str, maxlinklength: int=50):
    """Utility for creating links out of plain text.

    This will look for text which looks like a URL and create an HTML link
    out of it.

    Args:
        text: The plain text to create links in.
        maxlinklength: Maximum chars a link will take in final text.

    Returns:
        The text with HTML links.
    """
    def replacewithlink(matchobj):
        url = matchobj.group(0)
        text = str(url)
        if text.startswith('http://'):
            text = text.replace('http://', '', 1)
        elif text.startswith('https://'):
            text = text.replace('https://', '', 1)

        if text.startswith('www.'):
            text = text.replace('www.', '', 1)

        if len(text) > maxlinklength:
            halflength = maxlinklength // 2
            text = text[0:halflength] + '...' + text[len(text) - halflength:]

        return '<a href="' + url + '">' + text + '</a>'

    if text is not None and text != '':
        return _urlfinderregex.sub(replacewithlink, text)
    else:
        return ''
