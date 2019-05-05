"""
From bitprophet/releases (BSD 2-clause)

https://github.com/bitprophet/releases/blob/35157fa/releases/__init__.py

Also looking at: https://github.com/bitprophet/releases/blob/master/releases/util.py
"""
import re

from docutils import nodes

year_arg_re = re.compile(r'^(.+?)\s*(?<!\x00)<(.*?)>$', re.DOTALL)


class Release(nodes.Element):
    @property
    def number(self):
        return self['number']

    @property
    def minor(self):
        return '.'.join(self.number.split('.')[:-1])

    @property
    def family(self):
        return int(self.number.split('.')[0])

    def __repr__(self):
        return '<release {}>'.format(self.number)


def release_nodes(text, slug, date, config):
    # Doesn't seem possible to do this "cleanly" (i.e. just say "make me a
    # title and give it these HTML attributes during render time) so...fuckit.
    # We were already doing fully raw elements elsewhere anyway. And who cares
    # about a PDF of a changelog? :x
    uri = None
    if config.releases_release_uri:
        # TODO: % vs .format()
        uri = config.releases_release_uri % slug
    elif config.releases_github_path:
        uri = "https://github.com/{}/tree/{}".format(config.releases_github_path, slug)
    # Only construct link tag if user actually configured release URIs somehow
    if uri:
        link = '<a class="reference external" href="{}">{}</a>'.format(uri, text)
    else:
        link = text
    datespan = ''
    if date:
        datespan = ' <span style="font-size: 75%;">{}</span>'.format(date)
    header = '<h2 style="margin-bottom: 0.3em;">{}{}</h2>'.format(link, datespan)
    return nodes.section(
        '', nodes.raw(rawtext='', text=header, format='html'), ids=[text]
    )


def release_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Invoked as :release:`N.N.N <YYYY-MM-DD>`.
    Turns into useful release header + link to GH tree for the tag.
    """
    # Make sure year has been specified
    match = year_arg_re.match(text)
    if not match:
        msg = inliner.reporter.error("Must specify release date!")
        return [inliner.problematic(rawtext, rawtext, msg)], [msg]
    number, date = match.group(1), match.group(2)
    # Lol @ access back to Sphinx
    config = inliner.document.settings.env.app.config
    nodelist = [release_nodes(number, number, date, config)]
    # Return intermediate node
    node = Release(number=number, date=date, nodelist=nodelist)
    return [node], []


def setup(app):
    for key, default in (
        # Issue base URI setting: releases_issue_uri
        # E.g. 'https://github.com/fabric/fabric/issues/'
        ('issue_uri', None),
        # Release-tag base URI setting: releases_release_uri
        # E.g. 'https://github.com/fabric/fabric/tree/'
        ('release_uri', None),
        # Convenience Github version of above
        ('github_path', None),
    ):
        app.add_config_value(
            name='releases_{}'.format(key), default=default, rebuild='html'
        )
    app.add_role('release', release_role)
