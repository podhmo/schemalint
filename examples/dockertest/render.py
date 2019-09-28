import jinja2

t = """
{{xxx}}
"""

t = jinja2.Template(t, undefined=jinja2.StrictUndefined)
print(t.render(xxx="yyy"))
