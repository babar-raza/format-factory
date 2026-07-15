"""MaterialX (.mtlx) graph connection resolution.

Turns the ``nodename``/``interfacename`` string references produced by
``load_mtlx()`` into real, traversable structure: given a node graph dict
and a node + input name, callers can look up the actual upstream node
object a connection points to instead of handling a bare string.

Spec reference: FACT-MTLX-102 -- node graph connections (nodename/
interfacename attributes on ``<input>`` elements referencing another
node, or a nodegraph-level interface parameter, by name).
"""
from __future__ import annotations

from typing import Any

from mtlx.exceptions import MtlxConnectionError

__all__ = ["resolve_connections", "get_connected_node"]


def _node_index(node_graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return a name -> node dict index for the nodes in a node graph."""
    return {
        node.get("name", ""): node
        for node in node_graph.get("nodes", [])
        if node.get("name")
    }


def _connection_target(inp: dict[str, str]) -> str:
    """Return the upstream name an input references, preferring nodename."""
    return inp.get("nodename") or inp.get("interfacename") or ""


def resolve_connections(node_graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Resolve every node's input connections within ``node_graph``.

    Returns a mapping of node name -> ``{"node": <node dict>, "resolved_inputs":
    [...]}`` where each resolved input is
    ``{"input_name", "upstream_name", "upstream_node"}`` for every input that
    declares a ``nodename``/``interfacename`` connection. ``upstream_node`` is
    the actual node dict the reference points to, or ``None`` when the
    reference is dangling (points at a name absent from the graph). Unlike
    ``get_connected_node``, this bulk form never raises -- it is meant for
    graph-wide inspection/analytics where a caller wants to see every
    connection (including dangling ones) rather than fail on the first one.
    """
    index = _node_index(node_graph)
    resolved: dict[str, dict[str, Any]] = {}
    for name, node in index.items():
        resolved_inputs: list[dict[str, Any]] = []
        for inp in node.get("inputs", []):
            upstream_name = _connection_target(inp)
            if not upstream_name:
                continue
            resolved_inputs.append({
                "input_name": inp.get("name", ""),
                "upstream_name": upstream_name,
                "upstream_node": index.get(upstream_name),
            })
        resolved[name] = {"node": node, "resolved_inputs": resolved_inputs}
    return resolved


def get_connected_node(
    node_graph: dict[str, Any], node_name: str, input_name: str
) -> dict[str, Any] | None:
    """Return the upstream node dict that ``node_name``'s ``input_name`` connects to.

    Returns ``None`` when the input exists but carries no
    ``nodename``/``interfacename`` connection (a literal value or an
    unconnected input) -- this is a legitimate, non-error state.

    Raises ``MtlxConnectionError`` when:
      - ``node_name`` does not exist in ``node_graph``,
      - ``node_name`` exists but has no input named ``input_name``, or
      - the input's ``nodename``/``interfacename`` references a node that
        does not exist in the graph (a dangling connection).

    These three cases are deliberately distinguished from "no connection"
    (``None``) because they represent a malformed query or a corrupt graph,
    not a valid unconnected input.
    """
    index = _node_index(node_graph)
    if node_name not in index:
        raise MtlxConnectionError(
            f"No node named '{node_name}' in node graph '{node_graph.get('name', '')}'"
        )

    node = index[node_name]
    for inp in node.get("inputs", []):
        if inp.get("name") != input_name:
            continue
        upstream_name = _connection_target(inp)
        if not upstream_name:
            return None
        if upstream_name not in index:
            raise MtlxConnectionError(
                f"Input '{input_name}' of node '{node_name}' references "
                f"unknown upstream node '{upstream_name}'"
            )
        return index[upstream_name]

    raise MtlxConnectionError(
        f"Node '{node_name}' has no input named '{input_name}'"
    )
