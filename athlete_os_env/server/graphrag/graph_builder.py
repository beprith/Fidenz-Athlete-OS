"""
In-memory property graph — replaces Neo4j / Zep Cloud.
Dict-of-dicts structure with add/query/traverse helpers.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import numpy as np

from server.graphrag.ontology import GraphEdge


class InMemoryGraph:
    """
    Lightweight property graph stored entirely in RAM.
    Nodes are dicts keyed by node_id; edges stored in adjacency lists.
    """

    def __init__(self):
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: List[GraphEdge] = []
        self._adj: Dict[str, List[GraphEdge]] = {}  # source -> [edges]
        self._rev_adj: Dict[str, List[GraphEdge]] = {}  # target -> [edges]
        self._embeddings: Dict[str, np.ndarray] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_node(
        self,
        node_id: str,
        entity_type: str,
        properties: Dict[str, Any] | None = None,
        embedding: list[float] | np.ndarray | None = None,
    ) -> None:
        self._nodes[node_id] = {
            "id": node_id,
            "entity_type": entity_type,
            **(properties or {}),
        }
        if node_id not in self._adj:
            self._adj[node_id] = []
        if node_id not in self._rev_adj:
            self._rev_adj[node_id] = []
        if embedding is not None:
            self._embeddings[node_id] = np.asarray(embedding, dtype=np.float32)

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation: str,
        properties: Dict[str, Any] | None = None,
    ) -> None:
        edge = GraphEdge(
            source_id=source_id,
            target_id=target_id,
            relation=relation,
            properties=properties or {},
        )
        self._edges.append(edge)
        self._adj.setdefault(source_id, []).append(edge)
        self._rev_adj.setdefault(target_id, []).append(edge)

    def set_embedding(self, node_id: str, embedding: list[float] | np.ndarray) -> None:
        self._embeddings[node_id] = np.asarray(embedding, dtype=np.float32)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_node(self, node_id: str) -> Dict[str, Any] | None:
        return self._nodes.get(node_id)

    def get_nodes_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        return [n for n in self._nodes.values() if n.get("entity_type") == entity_type]

    def get_edges_from(self, node_id: str, relation: str | None = None) -> List[GraphEdge]:
        edges = self._adj.get(node_id, [])
        if relation:
            return [e for e in edges if e.relation == relation]
        return edges

    def get_edges_to(self, node_id: str, relation: str | None = None) -> List[GraphEdge]:
        edges = self._rev_adj.get(node_id, [])
        if relation:
            return [e for e in edges if e.relation == relation]
        return edges

    # ------------------------------------------------------------------
    # Traversal
    # ------------------------------------------------------------------

    def traverse(
        self,
        start_id: str,
        max_hops: int = 2,
        relation_filter: str | None = None,
    ) -> List[Dict[str, Any]]:
        """BFS traversal from start_id up to max_hops. Returns visited nodes."""
        visited: Set[str] = set()
        frontier = [start_id]
        results: List[Dict[str, Any]] = []

        for _ in range(max_hops + 1):
            next_frontier: list[str] = []
            for nid in frontier:
                if nid in visited:
                    continue
                visited.add(nid)
                node = self._nodes.get(nid)
                if node:
                    results.append(node)
                for edge in self.get_edges_from(nid, relation_filter):
                    if edge.target_id not in visited:
                        next_frontier.append(edge.target_id)
            frontier = next_frontier
            if not frontier:
                break

        return results

    def query(
        self,
        entity_type: str | None = None,
        predicate: Callable[[Dict[str, Any]], bool] | None = None,
    ) -> List[Dict[str, Any]]:
        """Simple filtered query over all nodes."""
        results = list(self._nodes.values())
        if entity_type:
            results = [n for n in results if n.get("entity_type") == entity_type]
        if predicate:
            results = [n for n in results if predicate(n)]
        return results

    # ------------------------------------------------------------------
    # Vector similarity
    # ------------------------------------------------------------------

    def vector_search(
        self, query_embedding: np.ndarray | list[float], top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """Cosine similarity search over stored embeddings."""
        q = np.asarray(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm < 1e-8:
            return []

        scores: list[Tuple[str, float]] = []
        for node_id, emb in self._embeddings.items():
            e_norm = np.linalg.norm(emb)
            if e_norm < 1e-8:
                continue
            sim = float(np.dot(q, emb) / (q_norm * e_norm))
            scores.append((node_id, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    # ------------------------------------------------------------------
    # Episode memory (Zep-style)
    # ------------------------------------------------------------------

    def add_episode_memory(
        self, player_id: str, content: str, metadata: Dict[str, Any] | None = None
    ) -> str:
        """Append an episode memory node linked to the player."""
        mem_id = f"{player_id}_mem_{len(self._edges)}"
        self.add_node(mem_id, "EpisodeMemory", {"content": content, **(metadata or {})})
        self.add_edge(player_id, mem_id, "HAS_MEMORY", metadata or {})
        return mem_id

    def get_episode_memories(self, player_id: str) -> List[Dict[str, Any]]:
        edges = self.get_edges_from(player_id, "HAS_MEMORY")
        memories = []
        for e in edges:
            node = self.get_node(e.target_id)
            if node:
                memories.append(node)
        return memories

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    def summary(self) -> str:
        type_counts: Dict[str, int] = {}
        for n in self._nodes.values():
            t = n.get("entity_type", "Unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        parts = [f"{t}: {c}" for t, c in sorted(type_counts.items())]
        return f"Graph({self.node_count} nodes, {self.edge_count} edges) — {', '.join(parts)}"

    def clear(self) -> None:
        self._nodes.clear()
        self._edges.clear()
        self._adj.clear()
        self._rev_adj.clear()
        self._embeddings.clear()
