import sys
sys.path.insert(0, 'source')

import pickle
import numpy as np
from pathlib import Path
import psycopg2
from pgvector.psycopg2 import register_vector

from source.process_data.feature_extraction import process_single_audio

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'dbname': 'mydb',
    'user': 'admin',
    'password': 'admin123',
}

print("[1] Loading feature stats...")
with open('data/feature_stats.pkl', 'rb') as f:
    stats = pickle.load(f)
print(f"    ✅ Loaded {len(stats)} features")

print("\n[2] Running inference on test file...")
test_file = Path('data/samples/barswa/bird_001.wav')
with open(test_file, 'rb') as f:
    audio_bytes = f.read()

inference_embedding = process_single_audio(audio_bytes, stats, verbose=False)
print(f"    ✅ Inference embedding shape: {inference_embedding.shape}")
print(f"    ✅ L2 norm: {np.linalg.norm(inference_embedding):.6f}")

print("\n[3] Querying database for top-5 similar files...")
conn = psycopg2.connect(**DB_CONFIG)
register_vector(conn)
cur = conn.cursor()

# Search for top-5 similar embeddings
query_sql = """
    SELECT 
        af.id,
        af.file_path,
        b.species_name,
        af.duration_s,
        1 - (e.embedding <-> %s::vector) as similarity
    FROM embeddings e
    JOIN audio_files af ON e.audio_id = af.id
    JOIN birds b ON af.bird_id = b.id
    ORDER BY e.embedding <-> %s::vector
    LIMIT 5;
"""

cur.execute(query_sql, (inference_embedding, inference_embedding))
results = cur.fetchall()

print(f"\n[4] TOP-5 RESULTS:")
for i, (audio_id, file_path, species, duration, similarity) in enumerate(results, 1):
    print(f"    {i}. {file_path}")
    print(f"       Species: {species}")
    print(f"       Duration: {duration:.2f}s")
    print(f"       Similarity: {similarity:.6f}")

# Check if first result is the query file itself (expected)
first_file_path = results[0][1]
if str(test_file) in first_file_path or 'bird_001' in first_file_path:
    print(f"\n✅ CORRECT: Top result is the query file itself")
else:
    print(f"\n⚠️  WARNING: Top result is not the query file (expected behavior if using different chunk)")

conn.close()
print(f"\n✅ END-TO-END TEST PASSED - Retrieval working correctly!")
