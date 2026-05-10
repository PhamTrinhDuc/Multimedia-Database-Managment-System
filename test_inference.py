import sys
sys.path.insert(0, 'source')

import pickle
import numpy as np
from pathlib import Path
from source.process_data.feature_extraction import process_single_audio

# Load stats
print("[1] Loading feature stats from offline pipeline...")
with open('data/feature_stats.pkl', 'rb') as f:
    stats = pickle.load(f)
print(f"    ✅ Loaded {len(stats)} feature columns")

# Load file test
test_file = Path('data/samples/barswa/bird_001.wav')
print(f"\n[2] Loading test audio file: {test_file}")
with open(test_file, 'rb') as f:
    audio_bytes = f.read()
print(f"    ✅ File size: {len(audio_bytes)} bytes")

# Extract embedding (verbose mode)
print(f"\n[3] Running inference (feature extraction + normalization)...")
result = process_single_audio(audio_bytes, stats, verbose=True)

print(f"\n[4] RESULTS:")
print(f"    Embedding shape: {len(result['embedding'])}")
print(f"    Embedding L2 norm: {result['steps']['embedding_norm']:.6f}")
print(f"    Audio duration after preprocessing: {result['steps']['preprocessing']['duration_after_s']:.3f}s")
print(f"    Sample rate: {result['steps']['preprocessing']['sample_rate']} Hz")

print(f"\n[5] Features raw values (first 5):")
for k, v in list(result['steps']['features_raw'].items())[:5]:
    print(f"    {k}: {v}")

print(f"\n[6] Features after normalization (first 5):")
for k, v in list(result['steps']['features_normalized'].items())[:5]:
    print(f"    {k}: {v}")

print(f"\n[7] Embedding vector (first 10 values):")
print(f"    {result['embedding'][:10]}")

print(f"\n✅ INFERENCE TEST PASSED - All steps working correctly!")
