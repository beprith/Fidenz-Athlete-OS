"""
Dual-path retriever — structured query + vector similarity.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

from server.graphrag.graph_builder import InMemoryGraph


class GraphRetriever:
    """
    Retrieves relevant graph context for a player in the simulation.
    Dual-path: structured traversal + vector cosine search.
    """

    def __init__(self, graph: InMemoryGraph, top_k: int = 3):
        self.graph = graph
        self.top_k = top_k
        self._cache: Dict[str, str] = {}

    def retrieve(
        self,
        player_id: str,
        query_text: str | None = None,
        query_embedding: list[float] | None = None,
        use_cache: bool = True,
    ) -> str:
        cache_key = f"{player_id}:{query_text or 'default'}"
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        parts: list[str] = []

        # Path 1: Structured graph traversal (2-hop from player)
        neighbourhood = self.graph.traverse(player_id, max_hops=2)
        if neighbourhood:
            struct_lines = []
            for node in neighbourhood[:self.top_k * 2]:
                etype = node.get("entity_type", "")
                name = node.get("name", node.get("id", ""))
                struct_lines.append(f"[{etype}] {name}")
            parts.append("Graph context:\n" + "\n".join(struct_lines))

        # Path 2: Vector similarity search
        if query_embedding:
            vec_results = self.graph.vector_search(query_embedding, self.top_k)
            if vec_results:
                vec_lines = []
                for nid, score in vec_results:
                    node = self.graph.get_node(nid)
                    if node:
                        name = node.get("name", nid)
                        vec_lines.append(f"{name} (sim={score:.2f})")
                parts.append("Similar entities:\n" + "\n".join(vec_lines))

        # Path 3: Episode memories
        memories = self.graph.get_episode_memories(player_id)
        if memories:
            mem_lines = [m.get("content", "") for m in memories[-self.top_k:]]
            parts.append("Recent memory:\n" + "\n".join(mem_lines))

        result = "\n\n".join(parts) if parts else "No graph context available."
        self._cache[cache_key] = result
        return result

    def retrieve_for_squad(self, player_ids: List[str]) -> Dict[str, str]:
        return {pid: self.retrieve(pid) for pid in player_ids}

    def invalidate_cache(self, player_id: str | None = None) -> None:
        if player_id:
            keys_to_drop = [k for k in self._cache if k.startswith(f"{player_id}:")]
            for k in keys_to_drop:
                del self._cache[k]
        else:
            self._cache.clear()
