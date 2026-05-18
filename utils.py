def formato_pesos(valor):
    """Formatea valores como moneda colombiana."""
    return f"${valor:,.0f}".replace(",", ".")
