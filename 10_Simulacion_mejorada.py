import pandas as pd
import random
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
import os

# ==========================================
# 1. LOGICA DE GENERACIÓN (MEJORADA - SIN REPETIDOS)
# ==========================================
def generar_data_equipo(nombre_equipo):
    posiciones = ["Portero", "Defensa", "Defensa", "Defensa", "Defensa", 
                  "Medio", "Medio", "Medio", "Delantero", "Delantero", "Delantero", 
                  "Defensa", "Medio", "Delantero"]
    
    # Banco de nombres ampliado
    banco_nombres = [
        "Alexia", "Betota", "Carla", "Dani", "Edy", "Fer", "Gaby", "Hana", "Ivana", 
        "Juanita", "Kenia", "Luisa", "Manuela", "Nico", "Olga", "Pachita", "Quini", 
        "Rafaela", "Santina", "Tonia", "Uri", "Victoria", "Wilma", "Xavi", "Yago", 
        "Zac", "Leo", "Messi", "Cristiano", "Neymar", "Mbappe", "Haaland", "Vinicius",
        "Modric", "Kroos", "Benzema", "Lewandowski", "Salah", "De Bruyne", "Courtois",
        "Ter Stegen", "Oblak", "Alisson", "Ederson", "Casemiro", "Pedri", "Gavi"
    ]
    
    # --- Cor
    # corregimos aquí ---
    # Usamos random.sample en lugar de random.choice
    # random.sample extrae 14 nombres ÚNICOS sin reemplazo
    if len(banco_nombres) < 14:
        # Por seguridad, si faltan nombres, permitimos repetición
        nombres_base = [random.choice(banco_nombres) for _ in range(14)]
    else:
        nombres_base = random.sample(banco_nombres, 14)

    # Agregamos el número aleatorio, pero el nombre base ya es único
    nombres = [f"{nombre} {random.randint(1,99)}" for nombre in nombres_base]
    
    ofensiva = []
    defensiva = []
    resistencia = []
    
    for pos in posiciones:
        resistencia.append(random.randint(75, 98))
        if pos == "Portero":
            ofensiva.append(random.randint(5, 20))
            defensiva.append(random.randint(85, 99))
        elif pos == "Defensa":
            ofensiva.append(random.randint(30, 60))
            defensiva.append(random.randint(75, 90))
        elif pos == "Medio":
            ofensiva.append(random.randint(60, 85))
            defensiva.append(random.randint(60, 85))
        elif pos == "Delantero":
            ofensiva.append(random.randint(80, 98))
            defensiva.append(random.randint(20, 50))
            
    data = {
        "Equipo": [nombre_equipo] * 14,
        "Nombre": nombres,
        "Posicion": posiciones,
        "Rating_Ofensivo": ofensiva,
        "Rating_Defensivo": defensiva,
        "Resistencia": resistencia
    }
    return data

def crear_datos_iniciales():
    if not os.path.exists("equipo_A.csv"):
        pd.DataFrame(generar_data_equipo("Pink Warriors")).to_csv("equipo_A.csv", index=False)
    if not os.path.exists("equipo_B.csv"):
        pd.DataFrame(generar_data_equipo("Rival FC")).to_csv("equipo_B.csv", index=False)

crear_datos_iniciales()

# ==========================================
# 2. CLASES DEL JUEGO
# ==========================================
class Jugador:
    def __init__(self, nombre, posicion, r_of, r_def, resistencia):
        self.nombre = nombre
        self.posicion = posicion
        self.r_of = int(r_of)
        self.r_def = int(r_def)
        self.resistencia = int(resistencia)

class Equipo:
    def __init__(self, ruta_csv):
        self.ruta = ruta_csv
        self.nombre = "Desconocido"
        self.titulares = []
        self.banca = []
        self.cargar_datos()
        
    def cargar_datos(self):
        try:
            df = pd.read_csv(self.ruta)
            self.nombre = df.iloc[0]['Equipo'] 
            for _, row in df.iterrows():
                j = Jugador(row['Nombre'], row['Posicion'], row['Rating_Ofensivo'], row['Rating_Defensivo'], row['Resistencia'])
                if len(self.titulares) < 11:
                    self.titulares.append(j)
                else:
                    self.banca.append(j)
        except Exception as e:
            messagebox.showerror("Error", f"Error leyendo {self.ruta}\n{e}")

    def obtener_estrategia(self):
        if not self.titulares: return "Sin datos"
        prom_of = sum(j.r_of for j in self.titulares) / 11
        prom_def = sum(j.r_def for j in self.titulares) / 11
        if prom_def > prom_of + 10: return "Defensiva (Autobús)"
        if prom_of > prom_def + 10: return "Ofensiva (Ataque Total)"
        return "Equilibrada"

    def promedio_ofensivo(self):
        return sum(j.r_of * (j.resistencia/100) for j in self.titulares) / 11
        
    def hacer_cambio(self):
        # Lógica mejorada: Sale el más cansado, entra uno fresco
        if self.banca:
            cansado = min(self.titulares, key=lambda x: x.resistencia)
            # Intentamos buscar alguien de la misma posición
            sustituto = next((s for s in self.banca if s.posicion == cansado.posicion), None)
            
            # Si no hay de la misma posición, mete al primero que haya
            if not sustituto: 
                sustituto = self.banca[0]

            self.titulares.remove(cansado)
            self.titulares.append(sustituto)
            self.banca.remove(sustituto)
            
            # Retornamos el texto exacto del cambio para la bitácora
            return f" CAMBIO en {self.nombre}: Sale {cansado.nombre} (Cansado) -> Entra {sustituto.nombre} (Fresco)"
        return None

class SimuladorPartido:
    def __init__(self, ruta_local, ruta_visita):
        self.local = Equipo(ruta_local)
        self.visita = Equipo(ruta_visita)
        self.bitacora = [] # Aquí guardaremos TODO lo que pase en orden
        self.marcador = {self.local.nombre: 0, self.visita.nombre: 0}

    def simular(self):
        self.bitacora.append(f" INICIO DEL PARTIDO: {self.local.nombre} vs {self.visita.nombre}")
        self.bitacora.append(f" Estrategia Inicial -> Local: {self.local.obtener_estrategia()} | Visita: {self.visita.obtener_estrategia()}")
        self.bitacora.append("-" * 40)

        for m in range(1, 91):
            
            # --- MEDIO TIEMPO ---
            if m == 45:
                self.bitacora.append("\n  MEDIO TIEMPO")
                self.bitacora.append(f" Estrategia Actual -> Local: {self.local.obtener_estrategia()} | Visita: {self.visita.obtener_estrategia()}")
                self.bitacora.append("-" * 40)

            # --- INTENTO GOL LOCAL ---
            prob_gol_local = 2 + (self.local.promedio_ofensivo() / 20)
            if random.randint(0, 1000) < prob_gol_local:
                autor = random.choice([j.nombre for j in self.local.titulares if j.posicion != "Portero"])
                self.marcador[self.local.nombre] += 1
                self.bitacora.append(f"Min {m}: ¡GOOOL DE {self.local.nombre}! Anotó: {autor}")
                self.bitacora.append(f"      (Marcador: {self.local.nombre} {self.marcador[self.local.nombre]} - {self.marcador[self.visita.nombre]} {self.visita.nombre})")

            # --- INTENTO GOL VISITA ---
            prob_gol_visita = 2 + (self.visita.promedio_ofensivo() / 20)
            if random.randint(0, 1000) < prob_gol_visita:
                autor = random.choice([j.nombre for j in self.visita.titulares if j.posicion != "Portero"])
                self.marcador[self.visita.nombre] += 1
                self.bitacora.append(f"Min {m}: ¡GOOOL DE {self.visita.nombre}! Anotó: {autor}")
                self.bitacora.append(f"      (Marcador: {self.local.nombre} {self.marcador[self.local.nombre]} - {self.marcador[self.visita.nombre]} {self.visita.nombre})")

            # --- DESGASTE (MODIFICADO PARA SER DINÁMICO) ---
            for j in self.local.titulares + self.visita.titulares:
                # Un valor aleatorio entre 0.4 y 0.9 para variedad
                desgaste = random.uniform(0.4, 0.9)
                j.resistencia -= desgaste
            
            # --- CAMBIOS (Ocurren en el min 60 y 75) ---
            if m == 60 or m == 75:
                # Cambio Local
                evento_cambio = self.local.hacer_cambio()
                if evento_cambio: 
                    self.bitacora.append(f"Min {m}: {evento_cambio}")
                
                # Cambio Visita
                evento_cambio_v = self.visita.hacer_cambio()
                if evento_cambio_v: 
                    self.bitacora.append(f"Min {m}: {evento_cambio_v}")

        # --- FINAL ---
        self.bitacora.append("\n SILBATAZO FINAL")
        self.bitacora.append(f"Estrategia Final -> Local: {self.local.obtener_estrategia()} | Visita: {self.visita.obtener_estrategia()}")

# ==========================================
# 3. INTERFAZ GRÁFICA
# ==========================================
class AplicacionFutbol:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador PRO - Minuto a Minuto")
        self.root.geometry("650x750")

        self.ruta_a = tk.StringVar()
        self.ruta_b = tk.StringVar()

        # --- CREADOR DE EQUIPOS ---
        frame_creador = tk.LabelFrame(root, text="1. Creador de Equipos (Fábrica)", padx=10, pady=10, fg="blue")
        frame_creador.pack(pady=5, fill="x", padx=10)
        
        tk.Button(frame_creador, text=" Crear Nuevo Equipo CSV", command=self.crear_nuevo_equipo, bg="#ADD8E6").pack(fill="x")

        # --- CARGA DE ARCHIVOS ---
        frame_carga = tk.LabelFrame(root, text="2. Configuración del Partido", padx=10, pady=10)
        frame_carga.pack(pady=5, fill="x", padx=10)

        tk.Button(frame_carga, text="Cargar Local", command=self.cargar_local).grid(row=0, column=0, padx=5, sticky="ew")
        tk.Label(frame_carga, textvariable=self.ruta_a, fg="blue").grid(row=0, column=1, sticky="w")

        tk.Button(frame_carga, text="Cargar Visitante", command=self.cargar_visita).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        tk.Label(frame_carga, textvariable=self.ruta_b, fg="red").grid(row=1, column=1, sticky="w")
        
        tk.Button(frame_carga, text=" Ver Plantillas Cargadas", command=self.ver_datos_csv).grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        # --- JUGAR ---
        tk.Button(root, text=" JUGAR PARTIDO (Ver Minuto a Miuto) ", bg="green", fg="white", font=("Arial", 12, "bold"), command=self.ejecutar_simulacion).pack(pady=10)

        # --- RESULTADOS ---
        self.txt_resultados = scrolledtext.ScrolledText(root, width=75, height=22)
        self.txt_resultados.pack(padx=10, pady=5)

    # --- MISMAS FUNCIONES DE APOYO ---
    def crear_nuevo_equipo(self):
        nombre = simpledialog.askstring("Nuevo Equipo", "Nombre del equipo:")
        if not nombre: return
        archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not archivo: return
        try:
            pd.DataFrame(generar_data_equipo(nombre)).to_csv(archivo, index=False)
            messagebox.showinfo("Éxito", f"Equipo '{nombre}' guardado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cargar_local(self):
        f = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if f: self.ruta_a.set(f)

    def cargar_visita(self):
        f = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if f: self.ruta_b.set(f)

    def ver_datos_csv(self):
        if not self.ruta_a.get() or not self.ruta_b.get(): return
        top = tk.Toplevel(self.root)
        top.geometry("600x400")
        txt = scrolledtext.ScrolledText(top, width=70, height=20)
        txt.pack()
        try:
            df_a = pd.read_csv(self.ruta_a.get())
            df_b = pd.read_csv(self.ruta_b.get())
            txt.insert(tk.END, f"LOCAL: {df_a.iloc[0]['Equipo']}\n{df_a[['Nombre', 'Rating_Ofensivo']].to_string(index=False)}\n\n")
            txt.insert(tk.END, f"VISITA: {df_b.iloc[0]['Equipo']}\n{df_b[['Nombre', 'Rating_Ofensivo']].to_string(index=False)}")
        except: pass

    # --- SIMULACIÓN CORREGIDA (Salida Cronológica) ---
    def ejecutar_simulacion(self):
        if not self.ruta_a.get() or not self.ruta_b.get():
            messagebox.showwarning("Error", "Carga ambos equipos.")
            return

        self.txt_resultados.delete(1.0, tk.END)
        self.root.update()

        partido = SimuladorPartido(self.ruta_a.get(), self.ruta_b.get())
        partido.simular()
        
        # AHORA IMPRIMIMOS LA BITÁCORA EN ORDEN
        for evento in partido.bitacora:
            self.txt_resultados.insert(tk.END, evento + "\n")
            # Un pequeño efecto visual de scroll automático
            self.txt_resultados.see(tk.END)
            
        # Resultado final grande
        m_local = partido.marcador[partido.local.nombre]
        m_visita = partido.marcador[partido.visita.nombre]
        
        res_final = f"\n MARCADOR FINAL: {partido.local.nombre} {m_local} - {m_visita} {partido.visita.nombre}\n"
        self.txt_resultados.insert(tk.END, res_final)

if __name__ == "__main__":
    ventana = tk.Tk()
    app = AplicacionFutbol(ventana)
    ventana.mainloop()