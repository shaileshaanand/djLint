"""Djlint tests specific to django.

run::

   pytest tests/test_django.py --cov=src/djlint --cov-branch \
          --cov-report xml:coverage.xml --cov-report term-missing

for a single test, run::

   pytest tests/test_django.py::test_single_line_tag --cov=src/djlint \
     --cov-branch --cov-report xml:coverage.xml --cov-report term-missing

"""
# pylint: disable=C0116

from typing import TextIO

from click.testing import CliRunner

from .conftest import reformat


def test_dj_comments_tag(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file, runner, b"{# comment #}\n{% if this %}<div></div>{% endif %}"
    )
    assert output["text"] == """{# comment #}\n{% if this %}<div></div>{% endif %}\n"""
    # no change was required
    assert output["exit_code"] == 0


def test_reformat_asset_tag(runner: CliRunner, tmp_file: TextIO) -> None:
    # pylint: disable=C0301
    output = reformat(
        tmp_file,
        runner,
        b"""{% block css %}{% assets "css_error" %}<link type="text/css" rel="stylesheet" href="{{ ASSET_URL }}" />{% endassets %}{% endblock css %}""",
    )  # noqa: E501
    assert (
        output["text"]
        == """{% block css %}
    {% assets "css_error" %}
        <link type="text/css" rel="stylesheet" href="{{ ASSET_URL }}" />
    {% endassets %}
{% endblock css %}
"""
    )
    assert output["exit_code"] == 1


def test_autoescape(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file, runner, b"{% autoescape on %}{{ body }}{% endautoescape %}"
    )
    assert output["exit_code"] == 1
    assert (
        output["text"]
        == r"""{% autoescape on %}
    {{ body }}
{% endautoescape %}
"""
    )


def test_comment(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file, runner, b"""{% comment "Optional note" %}{{ body }}{% endcomment %}"""
    )
    assert output["exit_code"] == 0
    # too short to put on multiple lines
    assert (
        output["text"]
        == r"""{% comment "Optional note" %}{{ body }}{% endcomment %}
"""
    )


def test_for_loop(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file,
        runner,
        b"""<ul>{% for athlete in athlete_list %}<li>{{ athlete.name }}</li>{% empty %}<li>Sorry, no athletes in this list.</li>{% endfor %}</ul>""",
    )
    assert output["exit_code"] == 1
    assert (
        output["text"]
        == r"""<ul>
    {% for athlete in athlete_list %}
        <li>{{ athlete.name }}</li>
    {% empty %}
        <li>Sorry, no athletes in this list.</li>
    {% endfor %}
</ul>
"""
    )


def test_filter(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file,
        runner,
        b"""{% filter force_escape|lower %}This text will be HTML-escaped, and will appear in all lowercase.{% endfilter %}""",
    )
    assert output["exit_code"] == 1
    assert (
        output["text"]
        == r"""{% filter force_escape|lower %}
    This text will be HTML-escaped, and will appear in all lowercase.
{% endfilter %}
"""
    )


def test_if(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file,
        runner,
        b"""{% if athlete_list %}Number of athletes: {{ athlete_list|length }}{% elif athlete_in_locker_room_list %}Athletes should be out of the locker room soon!{% else %}No athletes.{% endif %}""",
    )
    assert output["exit_code"] == 1
    assert (
        output["text"]
        == r"""{% if athlete_list %}
    Number of athletes: {{ athlete_list|length }}
{% elif athlete_in_locker_room_list %}
    Athletes should be out of the locker room soon!
{% else %}
    No athletes.
{% endif %}
"""
    )


def test_ifchanged(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file,
        runner,
        b"""{% for match in matches %}<div style="background-color:"pink">{% ifchanged match.ballot_id %}{% cycle "red" "blue" %}{% else %}gray{% endifchanged %}{{ match }}</div>{% endfor %}""",
    )
    assert output["exit_code"] == 1
    assert (
        output["text"]
        == r"""{% for match in matches %}
    <div style="background-color:"pink">
        {% ifchanged match.ballot_id %}
            {% cycle "red" "blue" %}
        {% else %}
            gray
        {% endifchanged %}
        {{ match }}
    </div>
{% endfor %}
"""
    )


def test_include(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(tmp_file, runner, b"""{% include "this" %}{% include "that"%}""")
    assert output["exit_code"] == 1
    assert (
        output["text"]
        == r"""{% include "this" %}
{% include "that" %}
"""
    )


def test_spaceless(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file,
        runner,
        b"""{% spaceless %}<p><a href="foo/">Foo</a></p>{% endspaceless %}""",
    )
    assert output["exit_code"] == 1
    assert (
        output["text"]
        == r"""{% spaceless %}
    <p>
        <a href="foo/">Foo</a>
    </p>
{% endspaceless %}
"""
    )


def test_templatetag(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file,
        runner,
        b"""{% templatetag openblock %} url 'entry_list' {% templatetag closeblock %}""",
    )
    assert output["exit_code"] == 0
    assert (
        output["text"]
        == r"""{% templatetag openblock %} url 'entry_list' {% templatetag closeblock %}
"""
    )


def test_verbatim(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file, runner, b"""{% verbatim %}Still alive.{% endverbatim %}"""
    )
    assert output["exit_code"] == 1
    assert (
        output["text"]
        == r"""{% verbatim %}
    Still alive.
{% endverbatim %}
"""
    )


def test_blocktranslate(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file,
        runner,
        b"""{% blocktranslate %}The width is: {{ width }}{% endblocktranslate %}""",
    )
    assert output["exit_code"] == 1
    assert (
        output["text"]
        == r"""{% blocktranslate %}
    The width is: {{ width }}
{% endblocktranslate %}
"""
    )


def test_with(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file,
        runner,
        b"""{% with total=business.employees.count %}{{ total }} employee{{ total|pluralize }}{% endwith %}""",
    )
    assert output["exit_code"] == 1
    assert (
        output["text"]
        == r"""{% with total=business.employees.count %}
    {{ total }} employee{{ total|pluralize }}
{% endwith %}
"""
    )


def test_single_line_tag(runner: CliRunner, tmp_file: TextIO) -> None:
    output = reformat(
        tmp_file,
        runner,
        b"""{% if messages|length %}{% for message in messages %}{{ message }}{% endfor %}{% endif %}""",
    )
    assert output["exit_code"] == 1
    assert (
        output["text"]
        == r"""{% if messages|length %}
    {% for message in messages %}{{ message }}{% endfor %}
{% endif %}
"""
    )
