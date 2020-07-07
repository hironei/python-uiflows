import hashlib
import pathlib
from dataclasses import dataclass
from typing import Callable, List

import pydot as dt
import yaml

TOP_BG_COLOR = "#87CEEB"
SEE_COLOR = "#8B0000"
ACTION_COLOR = "#4FBC92"

GRAPH_DEFAULTS = dict(
    charset="UTF-8",
    style="filled",
    rankdir="LR",
)
NODE_DEFAULTS = dict(
    style="solid",
    fontsize=11,
    margin="0.1,0.1",
    fontname="M+ 1m,Osaka-Mono,ＭＳ ゴシック",
)
EDGE_DEFAULTS = dict(
    fontsize=9,
    fontname="M+ 1m,Osaka-Mono,ＭＳ ゴシック",
    color="#777777"
)


class FormatError(Exception):
    pass


@dataclass
class UiflowSee:
    label: str


@dataclass
class UiflowAction:
    parent_id: str
    event: str
    node: str = None
    meta: dict = None

    @property
    def port(self):
        d = self.parent_id + self.event + (self.node or "")
        return "p" + hashlib.sha256(d.encode("utf-8")).hexdigest()


@dataclass
class UiflowNode:
    name: str
    see: List[UiflowSee] = list
    action: List[UiflowAction] = list
    meta: dict = None

    @property
    def id(self):
        d = self.name
        return "i" + hashlib.sha256(d.encode("utf-8")).hexdigest()

    @property
    def is_no_actions(self):
        if not self.action:
            return False

        if any([True for x in self.action if x.node]):
            return False
        else:
            return True


class UiflowYamlParser:
    def __init__(self):
        pass

    def parse(self, path: [pathlib.Path, str], encoding: str = "utf-8"):
        if isinstance(path, str):
            path = pathlib.Path(path)

        with path.open(encoding=encoding) as f:
            config = yaml.safe_load(f)

        result = []
        for node_config in config:
            name = node_config.pop("name")
            node = UiflowNode(name)
            node.see = self._parse_see(node_config)
            node.action = self._parse_action(node.id, node_config)
            node.meta = node_config
            result.append(node)

        return result

    @classmethod
    def _parse_action(cls, node_id, node_config):
        node_actions = node_config.pop("action", [])
        action = []
        for node_action in node_actions:
            if isinstance(node_action, dict):
                if len(node_action) == 1:
                    event, node = list(node_action.items())[0]
                    action.append(UiflowAction(node_id, event, node))
                else:
                    event = node_action.pop("event")
                    node = node_action.pop("node")
                    params = node_action
                    action.append(UiflowAction(node_id, event, node, params))
            else:
                action.append(UiflowAction(node_id, node_action))
        return action

    @classmethod
    def _parse_see(cls, node_config):
        node_see = node_config.pop("see", [])
        see = []
        for node_see in node_see:
            see.append(UiflowSee(node_see))

        return see


class UiflowDotWriter:
    def __init__(self, **kwargs):
        self.dot = dt.Dot(**kwargs)
        self.dot.set_node_defaults(**NODE_DEFAULTS)
        self.dot.set_graph_defaults(**GRAPH_DEFAULTS)
        self.dot.set_edge_defaults(**EDGE_DEFAULTS)

    def _write_header(self):
        pass

    def _write_footer(self):
        pass

    def _write_node(self, node: UiflowNode):
        params = node.meta or {}
        top_bg_color = params.pop("top_bg_color", TOP_BG_COLOR)
        see_color = params.pop("see_color", SEE_COLOR)
        action_color = params.pop("action_color", ACTION_COLOR)

        see_rows = self._create_rows_from_see(node.see, see_color)
        action_rows = self._create_rows_from_action(node.action, action_color)
        header = [
            "<", '<table border="0" cellborder="1" cellspacing="0">',
            f'<tr><td port="top" bgcolor="{top_bg_color}"><B>{node.name}</B></td></tr>'
        ]
        footer = ["</table>", ">"]
        data = '\n\t\t'.join(header + see_rows + action_rows + footer)
        n = dt.Node(node.id, label=data, shape="plaintext", **params)
        self.dot.add_node(n)
        return n

    @classmethod
    def _create_rows_from_see(cls, see: List[UiflowSee], see_color: str):
        result = []
        for s in see:
            see_data = f'<tr><td><font color="{see_color}"><B>{s.label}</B></font></td></tr>'
            result.append(see_data)

        return result

    @classmethod
    def _create_rows_from_action(cls, action: List[UiflowAction], action_color: str):
        result = []
        for s in action:
            action_data = f'<tr><td port="{s.port}"><font color="{action_color}"><B>{s.event}</B></font></td></tr>'
            result.append(action_data)

        return result

    def _write_edge(self, node: UiflowNode, node_dic: dict):
        for action in node.action:
            if action.node:
                src = f"{action.parent_id}:{action.port}"
                fk = node_dic.get(action.node) or action.node
                params = action.meta or {}
                dst = f"{fk}:top"
                e = dt.Edge(src, dst, **params)
                self.dot.add_edge(e)

    def _write_no_action_edge(self, src_node: UiflowNode, dst_node: UiflowNode):
        src = f"{src_node.id}:top"
        dst = f"{dst_node.id}:top"
        e = dt.Edge(src, dst)
        self.dot.add_edge(e)

    @staticmethod
    def prev_anc_current(node_list):
        it = iter(node_list)
        last = next(it)
        # 2番目の値から開始して反復子を使い果たすまで実行
        for val in it:
            # 一つ前の値を返す
            yield last, val
            last = val  # 値の更新
        # 最後の一つは返さない

    def write(self, node_list: List[UiflowNode]):
        self._write_header()
        node_dic = {x.name: x.id for x in node_list}
        for node in node_list:
            self._write_node(node)
        for node in node_list:
            self._write_edge(node, node_dic)
        for prev, current in self.prev_anc_current(node_list):
            if prev.is_no_actions:
                self._write_no_action_edge(prev, current)
        self._write_footer()

    def to_dot(self, path: pathlib.Path):
        # noinspection PyUnresolvedReferences
        self.dot.write_dot(path, encoding="utf-8")

    def to_png(self, path: pathlib.Path):
        # noinspection PyUnresolvedReferences
        self.dot.write_png(path, encoding="utf-8")

    def to_svg(self, path: pathlib.Path):
        # noinspection PyUnresolvedReferences
        self.dot.write_svg(path, encoding="utf-8")


def uiflows():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input yaml file", required=True)
    parser.add_argument("-o", "--output", help="Output file", required=True)
    parser.add_argument("-f", "--format", help="Output format", choices=("dot", "png", "svg"), default="dot")

    args = parser.parse_args()
    yml = args.input
    fmt = args.format
    out = pathlib.Path(args.output)

    parser = UiflowYamlParser()
    nodes = parser.parse(yml)
    writer = UiflowDotWriter()
    writer.write(nodes)

    format_dic = {
        "dot": writer.to_dot,
        "png": writer.to_png,
        "svg": writer.to_svg,
    }
    write: Callable[[pathlib.Path], None] = format_dic[fmt]
    write(out)


if __name__ == '__main__':
    uiflows()
