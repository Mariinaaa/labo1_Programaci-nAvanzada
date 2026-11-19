from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "processed" / "libros.csv"

st.set_page_config(page_title="Catálogo de libros", page_icon="📚", layout="wide")
st.title("📚 Catálogo de libros")
st.caption("Exploración del catálogo de books.toscrape.com")

if not DATA_PATH.exists():
    st.error(
        "No se encuentra data/processed/libros.csv. Ejecuta las celdas del "
        "notebook para descargar y procesar el catálogo."
    )
    st.stop()

books = pd.read_csv(DATA_PATH)
books["rating"] = books["rating"].astype(int)

with st.sidebar:
    st.header("Filtros")
    categories = sorted(books["category"].dropna().unique())
    selected_categories = st.multiselect(
        "Categorías", categories, default=categories
    )
    ratings = st.multiselect(
        "Valoración (estrellas)", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5]
    )
    maximum_price = float(books["price_gbp"].max())
    price_limit = st.slider(
        "Precio máximo (£)", 0.0, maximum_price, maximum_price, step=0.5
    )

filtered = books[
    books["category"].isin(selected_categories)
    & books["rating"].isin(ratings)
    & (books["price_gbp"] <= price_limit)
]

metric1, metric2, metric3 = st.columns(3)
metric1.metric("Libros", f"{len(filtered):,}")
metric2.metric(
    "Precio medio", f"£{filtered['price_gbp'].mean():.2f}" if len(filtered) else "—"
)
metric3.metric(
    "Valoración media", f"{filtered['rating'].mean():.2f}/5" if len(filtered) else "—"
)

left, right = st.columns(2)
with left:
    st.subheader("Libros por categoría")
    category_counts = (
        filtered["category"].value_counts().rename_axis("Categoría").to_frame("Libros")
    )
    st.bar_chart(category_counts)
with right:
    st.subheader("Precio y valoración")
    st.scatter_chart(filtered, x="rating", y="price_gbp", color="category")

st.subheader("Resultados")
st.dataframe(
    filtered.sort_values("title")[
        ["title", "category", "price_gbp", "rating", "available"]
    ],
    width="stretch",
    hide_index=True,
)
