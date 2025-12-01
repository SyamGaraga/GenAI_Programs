import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🛍️ Fake Store Dashboard")

# 1. Fetch Data directly into Pandas
url = "https://fakestoreapi.com/products"
df = pd.read_json(url)

# 2. Add filters (Optional but cool)
category = st.selectbox("Select Category", ["All"] + list(df['category'].unique()))

if category != "All":
    df = df[df['category'] == category]

# 3. Display Data
# Option A: Simple Table
st.write(f"Showing {len(df)} products:")
st.dataframe(df)

# Option B: Visual Grid (Like a website)
st.subheader("Product Gallery")
cols = st.columns(4) # Create 4 columns

for index, row in df.iterrows():
    with cols[index % 4]: # Cycle through columns
        st.image(row['image'], width=150)
        st.write(f"**{row['title'][:30]}...**") # Shorten title
        st.write(f"💲{row['price']}")
        st.write("---")