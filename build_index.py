"""
Script to build the FAISS vector index from the crime dataset.
Run this script whenever you update the crime.csv file or want to rebuild the index.
"""

import faiss
import pandas as pd
import numpy as np
from embeddings import generate_embeddings
from config import CSV_FILE, INDEX_FILE
import pickle

print("📊 Loading crime dataset...")
df = pd.read_csv(CSV_FILE)

print(f"✅ Loaded {len(df)} crime records")
print(f"📋 Columns: {df.columns.tolist()}")

# Combine columns into one text for better search
print("\n🔄 Creating combined text for embeddings...")
df["combined_text"] = df.apply(
    lambda row: f"DR Number: {row['DR_NO']}, Crime: {row['Crm Cd Desc']}, "
    f"Location: {row['LOCATION']}, Area: {row['AREA NAME']}, "
    f"Date Occurred: {row['DATE OCC']}, Time: {row['TIME OCC']}, "
    f"Victim Age: {row['Vict Age']}, Victim Sex: {row['Vict Sex']}, "
    f"Premises: {row['Premis Desc']}, Status: {row['Status Desc']}",
    axis=1,
)

texts = df["combined_text"].tolist()

print(f"\n🧠 Generating embeddings for {len(texts)} records...")
print("⏳ This may take a while for large datasets...")
embeddings = generate_embeddings(texts)

print(f"✅ Generated embeddings with shape: {embeddings.shape}")

# Create FAISS index
print("\n🔨 Building FAISS index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

print(f"✅ Index created with {index.ntotal} vectors")

# Save the index
print(f"\n💾 Saving index to {INDEX_FILE}...")
faiss.write_index(index, INDEX_FILE)

# Save the texts for retrieval
print("💾 Saving texts for retrieval...")
with open("crime_texts.pkl", "wb") as f:
    pickle.dump(texts, f)

print("\n✨ Vector store created successfully!")
print(f"📍 Index file: {INDEX_FILE}")
print(f"📍 Texts file: crime_texts.pkl")
