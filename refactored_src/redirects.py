from flask import abort, redirect, Flask


SOUND_REDIRECT_ENDPOINT = "redirect_episode"
ARTICLE_REDIRECT_ENDPOINT = "redirect_article"


def redirect_episode(show, episode, title, url_service):
    try:
        url = redirect(url_service.get_original_sound(episode))
        if not url:
            raise ValueError("No episode with the given ID was found")
        return url
    except ValueError:
        abort(404)


def redirect_article(show, article, url_service):
    try:
        url = redirect(url_service.get_original_article(article))
        if not url:
            raise ValueError("No article with the given ID was found")
        return url
    except ValueError:
        abort(404)


def register_episode_redirect(app: Flask, settings, get_global):
    def do_redirect_episode(*args, **kwargs):
        kwargs['url_service'] = get_global('url_service')
        return redirect_episode(*args, **kwargs)

    app.add_url_rule(
        "/episode/<show>/<episode>/<title>",
        SOUND_REDIRECT_ENDPOINT,
        do_redirect_episode
    )


def register_article_redirect(app: Flask, settings, get_global):
    def do_redirect_article(*args, **kwargs):
        kwargs['url_service'] = get_global('url_service')
        return redirect_article(*args, **kwargs)

    app.add_url_rule(
        "/artikkel/<show>/<article>",
        ARTICLE_REDIRECT_ENDPOINT,
        do_redirect_article
    )