from typing import Dict, List, Any, Optional
import math


class VectorCollection:
    """
    A simple in-memory "Collection" with NAMED partitions.

    - partitions is a dict:
        partition_name (str) -> { id -> {"vector": [...], "metadata": {...}} }
    """

    def __init__(
        self,
        name: str,
        dim: int,
        partition_names: Optional[List[str]] = None,
        default_num_partitions: int = 2
    ):
        """
        :param name:            Collection name (e.g., "products").
        :param dim:             Vector dimension (e.g., 4, 384, 768).
        :param partition_names: Optional list of custom partition names.
                                Example: ["fruits", "juices", "others"]
        :param default_num_partitions: Used only if partition_names is None.
        """
        self.name = name
        self.dim = dim

        # If user provides custom names, use them.
        if partition_names is not None and len(partition_names) > 0:
            self.partition_names = partition_names
        else:
            # Fall back to generic names if no names are provided
            self.partition_names = [
                f"partition_{i}" for i in range(default_num_partitions)
            ]

        # Map of partition_name -> {vector_id -> record}
        self.partitions: Dict[str, Dict[str, Dict[str, Any]]] = {
            pname: {} for pname in self.partition_names
        }

    # -----------------------------
    # Helper Methods
    # -----------------------------

    def _validate_vector(self, vector: List[float]) -> None:
        """Ensure that the vector has the correct dimension."""
        if len(vector) != self.dim:
            raise ValueError(
                f"Vector dimension mismatch. Expected {self.dim}, got {len(vector)}"
            )

    def _choose_partition_automatically(self, vector_id: str) -> str:
        """
        Simple automatic partitioning rule:
        - Use hash-based partitioning: hash(id) % number_of_partitions

        This is used ONLY when caller does NOT specify a partition_name.
        """
        idx = hash(vector_id) % len(self.partition_names)
        return self.partition_names[idx]

    # -----------------------------
    # Core Operations
    # -----------------------------

    def upsert_vector(
        self,
        vector_id: str,
        vector: List[float],
        metadata: Dict[str, Any],
        partition_name: Optional[str] = None
    ):
        """
        UPSERT operation with optional named partition:

        - If vector_id already exists in any partition → UPDATE it in that partition.
        - Else:
            * If partition_name is given → INSERT into that partition.
            * If partition_name is None → use automatic partitioning.
        """
        self._validate_vector(vector)

        # 1) Check if the ID already exists anywhere
        for p_name, store in self.partitions.items():
            if vector_id in store:
                store[vector_id]["vector"] = vector
                store[vector_id]["metadata"] = metadata
                print(f"[UPSERT] Updated ID '{vector_id}' in partition '{p_name}'")
                return

        # 2) INSERT case
        if partition_name is not None:
            if partition_name not in self.partitions:
                raise ValueError(
                    f"Partition '{partition_name}' does not exist. "
                    f"Available: {list(self.partitions.keys())}"
                )
            target_partition = partition_name
        else:
            target_partition = self._choose_partition_automatically(vector_id)

        self.partitions[target_partition][vector_id] = {
            "vector": vector,
            "metadata": metadata
        }
        print(f"[UPSERT] Inserted ID '{vector_id}' into partition '{target_partition}'")

    def get_vector(self, vector_id: str):
        """Retrieve a vector by ID (searches all partitions)."""
        for p_name, store in self.partitions.items():
            if vector_id in store:
                return p_name, store[vector_id]
        return None, None

    def get_partition(self, partition_name: str) -> Dict[str, Dict[str, Any]]:
        """Return the raw dictionary for a specific partition."""
        if partition_name not in self.partitions:
            raise ValueError(
                f"Partition '{partition_name}' does not exist. "
                f"Available: {list(self.partitions.keys())}"
            )
        return self.partitions[partition_name]

    def print_collection_summary(self):
        """Print the number of vectors in each partition."""
        print(f"\n=== Collection Summary: '{self.name}' ===")
        total = 0
        for p_name, store in self.partitions.items():
            count = len(store)
            total += count
            print(f"  {p_name}: {count} vectors")
        print(f"  TOTAL: {total} vectors\n")

    def search_in_partition(
        self,
        partition_name: str,
        query_vector: List[float],
        top_k: int = 3
    ):
        """Brute-force L2 search inside ONE partition."""
        self._validate_vector(query_vector)

        if partition_name not in self.partitions:
            raise ValueError(
                f"Partition '{partition_name}' does not exist. "
                f"Available: {list(self.partitions.keys())}"
            )

        store = self.partitions[partition_name]
        results = []

        for vec_id, record in store.items():
            dist = math.dist(query_vector, record["vector"])
            results.append((vec_id, dist))

        results.sort(key=lambda x: x[1])  # sort by distance ascending
        return results[:top_k]


# -------------------------------------------------------------
# DEMO
# -------------------------------------------------------------
if __name__ == "__main__":

    collection = VectorCollection(
        name="products",
        dim=4,
        partition_names=["fruits", "juices", "others"]
    )

    collection.upsert_vector("p1", [0.9, 0.1, 0.0, 0.0],
                             {"name": "Red apple", "category": "fruit"},
                             partition_name="fruits")

    collection.upsert_vector("p2", [0.85, 0.15, 0.0, 0.0],
                             {"name": "Green apple", "category": "fruit"},
                             partition_name="fruits")

    collection.upsert_vector("p3", [0.0, 0.1, 0.9, 0.1],
                             {"name": "Orange juice", "category": "juice"},
                             partition_name="juices")

    collection.upsert_vector("p4", [0.1, 0.9, 0.0, 0.0],
                             {"name": "Banana", "category": "fruit"})

    collection.print_collection_summary()

    fruits_partition = collection.get_partition("fruits")
    print("Contents of 'fruits' partition:")
    for vid, rec in fruits_partition.items():
        print(f"  ID={vid}, name={rec['metadata']['name']}")

    query = [0.88, 0.12, 0.0, 0.0]
    results = collection.search_in_partition("fruits", query, top_k=2)

    print("\nTop-2 nearest neighbors in 'fruits':")
    for vid, dist in results:
        _, rec = collection.get_vector(vid)
        print(f"  ID={vid}, dist={dist:.4f}, name={rec['metadata']['name']}")
