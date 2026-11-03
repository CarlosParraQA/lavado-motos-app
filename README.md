# App Registro Lavado de Motos

Aplicación sencilla en Python + Streamlit para registrar lavadas de motos por lavador.

## Funcionalidades

- Registrar lavadas por lavador.
- Seleccionar y administrar los precios de las lavadas.
- Calcular automáticamente el 40% para el lavador.
- Calcular automáticamente el 60% para el negocio.
- Administrar lavadores desde la cuenta de administrador.
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

## Configuración de precios en Supabase

Antes de usar la administración de precios, ejecuta el contenido de
[`supabase_precios_lavada.sql`](./supabase_precios_lavada.sql) en el SQL Editor
de Supabase. Esto crea la tabla de precios y agrega los valores iniciales:
$8.000, $15.000, $20.000, $30.000, $35.000 y $50.000.

## Ejecución

```bash
streamlit run app.py
```

La base de datos `lavado_motos.db` se crea automáticamente cuando se ejecuta la app.
