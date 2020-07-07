import pathlib

from uiflows import UiflowAction, UiflowDotWriter, UiflowNode, UiflowSee, UiflowYamlParser

current_dir = pathlib.Path(__file__).parent


# noinspection SpellCheckingInspection
def test_write_dot_01():
    dot = current_dir / "sample_test_write_dot_01.dot"
    node1 = UiflowNode("hoge", [UiflowSee("hoge"), UiflowSee("uge")])
    node1.action = [UiflowAction(node1.id, "fuga"), UiflowAction(node1.id, "muga", "hage")]
    node2 = UiflowNode("hage", [UiflowSee("hoge"), UiflowSee("uga")], )
    node2.action = [UiflowAction(node2.id, "fuga"), UiflowAction(node2.id, "muga", "hoge")]
    node_list = [node1, node2]
    writer = UiflowDotWriter()
    writer.write(node_list)
    writer.to_dot(dot)
    writer.to_png(dot.with_suffix(".png"))


def write_dot(dot, yaml):
    parser = UiflowYamlParser()
    nodes = parser.parse(yaml)
    writer = UiflowDotWriter()
    writer.write(nodes)
    writer.to_dot(dot)
    writer.to_png(dot.with_suffix(".png"))


def test_write_dot_02():
    dot = current_dir / "sample_test_write_dot_02.dot"
    yaml = current_dir / "sample1.yml"
    write_dot(dot, yaml)


def test_write_dot_03():
    dot = current_dir / "sample_test_write_dot_03.dot"
    yaml = current_dir / "sample2.yml"
    write_dot(dot, yaml)


def test_write_dot_04():
    dot = current_dir / "sample_test_write_dot_04.dot"
    yaml = current_dir / "sample3.yml"
    write_dot(dot, yaml)
