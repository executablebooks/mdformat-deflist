from typing import Mapping

from markdown_it import MarkdownIt
from mdformat.renderer import RenderContext, RenderTreeNode
from mdformat.renderer.typing import Render
from mdit_py_plugins.deflist import deflist_plugin


def update_mdit(mdit: MarkdownIt) -> None:
    """Update the parser, e.g. by adding a plugin: `mdit.use(myplugin)`"""
    mdit.use(deflist_plugin)


def make_render_children(separator: str) -> Render:
    def render_children(
        node: RenderTreeNode,
        context: RenderContext,
    ) -> str:
        return separator.join(child.render(context) for child in node.children)

    return render_children


def _render_dl(node: RenderTreeNode, context: RenderContext) -> str:
    """Render the definition list."""
    return make_render_children("\n")(node, context)


def _render_dt(node: RenderTreeNode, context: RenderContext) -> str:
    """Render the definition term."""
    return make_render_children("\n")(node, context)


def _render_dd(node: RenderTreeNode, context: RenderContext) -> str:
    """Render the definition body."""
    tight_list = all(
        child.type != "paragraph" or child.hidden for child in node.children
    )
    marker = ": "
    indent_width = len(marker)
    context.env["indent_width"] += indent_width
    try:
        text = make_render_children("\n\n")(node, context)
        lines = text.splitlines()
        if not lines:
            return ":"
        indented_lines = [f"{marker}{lines[0]}"] + [
            f"{' '*indent_width}{line}" if line else "" for line in lines[1:]
        ]
        indented_lines = ("" if tight_list else "\n") + "\n".join(indented_lines)
        next_sibling = node.next_sibling
        return indented_lines + (
            "\n" if (next_sibling and next_sibling.type == "dt") else ""
        )
    finally:
        context.env["indent_width"] -= indent_width


# A mapping from syntax tree node type to a function that renders it.
# This can be used to overwrite renderer functions of existing syntax
# or add support for new syntax.
RENDERERS: Mapping[str, Render] = {"dl": _render_dl, "dt": _render_dt, "dd": _render_dd}
