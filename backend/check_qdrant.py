import qdrant_client
from qdrant_client import QdrantClient
import inspect

print(f"Qdrant Client Version: {qdrant_client.__version__ if hasattr(qdrant_client, '__version__') else 'unknown'}")
client = QdrantClient(location=":memory:")
print("Methods in QdrantClient:")
methods = [m for m, _ in inspect.getmembers(client, predicate=inspect.ismethod)]
print(", ".join(methods))

if "search" in methods:
    print("SUCCESS: 'search' method found.")
else:
    print("FAILURE: 'search' method NOT found.")
    # Show search-like methods
    search_likes = [m for m in methods if "search" in m.lower() or "query" in m.lower()]
    print(f"Similar methods: {', '.join(search_likes)}")
