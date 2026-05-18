# App Registro Lavado de Motos

Aplicación sencilla en Python + Streamlit para registrar lavadas de motos por gamusero.

## Funcionalidades

- Registrar lavadas por gamusero.
- Seleccionar valores de $15.000, $20.000, $30.000 y $35.000.
- Calcular automáticamente el 40% para el gamusero.
- Calcular automáticamente el 60% para el negocio.
- Ver lavadas del día.
- Realizar cierre diario.
- Exportar cierres e historial a Excel.

## Estructura

```text
lavado_motos_app/
│
├── app.py
├── database.py
├── utils.py
├── requirements.txt
├── README.md
│
├── pages/
│   ├── 1_Registrar_Lavada.py
│   ├── 2_Lavadas_Del_Dia.py
│   ├── 3_Cierre_Del_Dia.py
│   └── 4_Historial_General.py
│
└── exports/
```

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

La base de datos `lavado_motos.db` se crea automáticamente cuando se ejecuta la app.
