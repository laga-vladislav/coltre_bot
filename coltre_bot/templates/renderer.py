import jinja2

from coltre_bot.config import TEMPLATES_DIR

def render_template(template_name: str, data: dict | None = None) -> str:
    if data is None:
        data = {}
    if template_name[-3::] != '.j2':
        template_name += '.j2'
    template = _get_template_env().get_template(template_name)
    rendered = template.render(**data).replace("\n", " ")
    rendered = rendered.replace("<br>", "\n")
    rendered = rendered.replace("<b>", "*")
    rendered = rendered.replace("</b>", "*")
    rendered = "\n".join(line.strip() for line in rendered.split("\n"))
    return rendered

def _get_template_env():
    if not getattr(_get_template_env, "template_env", None):
        template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATES_DIR)
        env = jinja2.Environment(
            loader=template_loader,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )

        _get_template_env.template_env = env
    return _get_template_env.template_env

if __name__ == '__main__':
    print(render_template('start.j2'))
