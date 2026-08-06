import tkinter as tk
import pandas as pd
import numpy as np
import math

luft = pd.read_csv("Stoffdaten_Luft.csv")

luft = luft.rename(columns={
    "T (K) ↑": "T_K",
    "T (°C)": "T_C",
    "Ρ (KG/M³)": "rho",
    "CP (KJ/KG·K)": "c_p",
    "Ν×10⁻⁶ (M²/S)": "nu",
    "K×10⁻³ (W/M·K)": "k",
    "PR": "Pr"
})

luft["k"] = luft["k"] / 1000
luft["nu"] = luft["nu"] / 1000000
luft["c_p"] = luft["c_p"] * 1000


def stoffwerte(T_f):

    # interp braucht immer 3 Informationen:
    #1. Der gewünschte Wert (in diesem Fall die Temperatur in K)
    #2. Von wo die T-Werte abgelesen werden sollen
    #3. Der Ort um den zum T-Wert dazugehörigen gewünschten Wert (in diesem Fall nu, k und Pr) abzulesen

    nu = np.interp(
        T_f,
        luft["T_K"],
        luft["nu"]
    )

    k = np.interp(
        T_f,
        luft["T_K"],
        luft["k"]
    )

    Pr = np.interp(
        T_f,
        luft["T_K"],
        luft["Pr"]
    )

    return nu, k, Pr

def c_p_Wert(T_f):

    c_p = np.interp(
        T_f,
        luft["T_K"],
        luft["c_p"]

        
    )

    return c_p

#################################################

def dichte_rho(T_f):

    rho = np.interp(
        T_f,
        luft["T_K"],
        luft["rho"]
    )

    return rho

######################################

def eingaben_einlesen_allgemein():

    T_umgebung = float(T_umgebung_entry.get()) + 273.15
    T_wand = float(T_wand_entry.get()) + 273.15
    r_zylinder = float(r_zylinder_entry.get())
    h_zylinder = float(h_zylinder_entry.get())

    return T_umgebung, T_wand, r_zylinder, h_zylinder

######################################################

def eingaben_einlesen_erzwungen():

    w = float(w_entry.get())

    return w

###############################################################

def T_f_berechnen(T_ab, T_wand):

    T_f = (T_wand + T_ab) / 2

    return T_f

##############################################

def K_berechnen(T_f, T_wand):

    K = (T_f / T_wand)**0.12

    return K

##############################################

# Für einen quer angeströmten Zylinder ist l_char = Durchmesser
def l_char_erzwungen_berechnen(r_zylinder):

    l_char_erzwungen = 2 * r_zylinder

    return l_char_erzwungen

################################################

def l_char_frei_berechnen(h_zylinder):

    l_char_frei = h_zylinder

    return l_char_frei

###################################################

def Re_berechnen(w, l_char_erzwungen, nu):

    Re = (w * l_char_erzwungen) / nu

    return Re

####################################################

def m_berechnen(rho, w, r_zylinder, h_zylinder):

    m = rho * w * 2 * r_zylinder * h_zylinder

    return m

#####################################################

def Nu_erzwungen_berechnen(Re, K, Pr):

    konvektion = auswahl_Konvektion.get()

    if Re < 10:

        Nu_erzwungen = 0.664 * ((Re)**0.5) * ((Pr)**(2/3)) * K

    elif Re >= 10:

        Nu_erzwungen = (0.037 * ((Re)**(0.8)) * Pr * K) / (1 + 2.443 * ((Re)**(-0.1)) * ((Pr)**(2/3) - 1))

    return Nu_erzwungen

######################################################################

def Nu_frei_berechnen(Ra, f_3):

    konvektion = auswahl_Konvektion.get()

    Nu_frei = (0.752 + 0.387 * (Ra * f_3)**(1 / 6))**2

    return Nu_frei

#########################################################

def beta_berechnen(T_f):

    beta = 1 / T_f

    return beta

#####################################################################

def Gr_berechnen(T_f, T_umgebung, T_wand, g, nu, beta, l_char_frei):

    Gr = (g * ((l_char_frei)**3) * beta * (T_wand - T_umgebung)) / nu**2

    return Gr

######################################################################

def Ra_berechnen(Gr, Pr):

    Ra = Gr * Pr

    return Ra

###################################################################


def h_frei_berechnen(Nu_frei, k, l_char_frei):

    h_frei = (Nu_frei * k) / l_char_frei

    return h_frei

####################################################################

def h_erzwungen_berechnen(Nu_erzwungen, k, l_null):

    h_erzwungen = (Nu_erzwungen * k) / l_null

    return h_erzwungen

######################################################################

def f_3_berechnen(Pr):

    f_3 = 1 / (1 + ((0.559 / Pr)**(9 /16)))**(16 / 9)

    return f_3

########################################################################

def Q_erzwungen_berechnen(h_erzwungen, r_zylinder, h_zylinder, T_wand, T_umgebung):

    Q_erzwungen = h_erzwungen * 2 * math.pi * r_zylinder * h_zylinder * (T_wand - T_umgebung)

    return Q_erzwungen

#######################################################################

def T_neu_berechnen(m, c_p, T_umgebung, Q_erzwungen):

    T_neu = (Q_erzwungen / (m * c_p)) + T_umgebung

    return T_neu

#########################################################################

def Fehler_berechnen(T_neu, T_ab):
    
    Fehler = abs(T_neu - T_ab)
    
    return Fehler

######################################################################

def l_null(r_zylinder):

    l_null = math.pi * r_zylinder

    return l_null

###################################################################


# Strömungsgeschwindigkeit ausgrauen bei freier Konvektion

def konvektion_aktualisieren():

    konvektion = auswahl_Konvektion.get()

    if konvektion == "frei":

        w_entry.config(state="disabled")

    elif konvektion == "erzwungen":

        w_entry.config(state="normal")

##################################################################

#Schleife/Iteration

def ganze_berechnung():

    Fehler = 100
    max_iteration = 100
    g = 9.81
    i = 0

    T_umgebung, T_wand, r_zylinder, h_zylinder = eingaben_einlesen_allgemein()

    T_ab = T_umgebung + 10

    while Fehler > 0.00001 and i < 100:

        T_f = T_f_berechnen(T_ab, T_wand)
        
        nu, k, Pr =stoffwerte(T_f)
        
        rho = dichte_rho(T_f)
        
        c_p = c_p_Wert(T_f)
        
        konvektion = auswahl_Konvektion.get()
        
        if konvektion == "erzwungen":

            l_char_erzwungen = l_char_erzwungen_berechnen(r_zylinder)

            l_null = l_char_erzwungen_berechnen(r_zylinder)
        
            w = eingaben_einlesen_erzwungen()
        
            K = K_berechnen(T_f, T_wand)
        
            Re = Re_berechnen(w, l_char_erzwungen, nu)
        
            m = m_berechnen(rho, w, r_zylinder, h_zylinder)
        
            Nu_erzwungen = Nu_erzwungen_berechnen(Re, K, Pr)
        
            h_erzwungen = h_erzwungen_berechnen(Nu_erzwungen, k, l_null)
        
            Q_erzwungen = Q_erzwungen_berechnen(h_erzwungen, r_zylinder, h_zylinder, T_wand, T_umgebung)
        
            T_neu = T_neu_berechnen(m, c_p, T_umgebung, Q_erzwungen)

            h = h_erzwungen

            T_ab_fertig.config(text=f"{T_neu-273.15:.2f} °C")

        
        elif konvektion == "frei":

            l_char_frei = l_char_frei_berechnen(h_zylinder)
        
            f_3 = f_3_berechnen(Pr)
        
            beta = beta_berechnen(T_f)
        
            Gr = Gr_berechnen(T_f, T_umgebung, T_wand, g, nu, beta, l_char_frei)
        
            Ra = Ra_berechnen(Gr, Pr)
        
            Nu_frei = Nu_frei_berechnen(Ra, f_3)

            h_frei = h_frei_berechnen(Nu_frei, k, l_char_frei)

            h = h_frei

            T_neu = T_wand

        
        Fehler = Fehler_berechnen(T_neu, T_ab)

        T_ab = T_neu

        i = i + 1

    h_fertig.config(text=f"{h:.2f}")
    

# GUI Code


fenster = tk.Tk()
fenster.title("WÜ-Rechner")
fenster.geometry("800x600")
fenster.columnconfigure(0, weight=1)
fenster.rowconfigure(0, weight=1)
fenster.rowconfigure(1, weight=1)
fenster.rowconfigure(2, weight=1)

frame_1 = tk.Frame(fenster)
frame_1.grid(row=0, column=0, sticky="news")

konvektion_frame= tk.LabelFrame(frame_1, text="Art der Konvektion")
konvektion_frame.grid(row=0 , column=0, padx=10, pady=5, sticky="ew")


# Radiobuttons um auszuwählen, ob Konvektion frei oder erzwungen ist
auswahl_Konvektion = tk.StringVar(value= "erzwungen",)

tk.Radiobutton(konvektion_frame, text= "erzwungen", variable= auswahl_Konvektion, value= "erzwungen", command=konvektion_aktualisieren).grid(row=0, column=0, padx= 10, pady= 10, sticky="w")

tk.Radiobutton(konvektion_frame, text= "frei", variable= auswahl_Konvektion, value="frei", command=konvektion_aktualisieren).grid(row=0, column=1, padx= 10, pady= 10, sticky="w")


# Datenerfassung vom Anwender
datenerfassung_frame = tk.LabelFrame(frame_1, text= "Datenerfassung")
datenerfassung_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

tk.Label(datenerfassung_frame, text="Umgebungstemperatur [°C]").grid(row=0, column=0, padx=5)
T_umgebung_entry = tk.Entry(datenerfassung_frame)
T_umgebung_entry.grid(row=0, column=1)

tk.Label(datenerfassung_frame, text="Wandtemperatur [°C]").grid(row=0, column=3, padx=5)
T_wand_entry = tk.Entry(datenerfassung_frame)
T_wand_entry.grid(row=0, column=4)

tk.Label(datenerfassung_frame, text= "Zylinderradius [m]").grid(row=1, column=0, padx=5, pady=5)
r_zylinder_entry = tk.Entry(datenerfassung_frame)
r_zylinder_entry.grid(row=1, column=1, pady=5)

tk.Label(datenerfassung_frame, text= "Zylinderhöhe [m]").grid(row=1, column=3, padx=5, pady=5)
h_zylinder_entry = tk.Entry(datenerfassung_frame)
h_zylinder_entry.grid(row=1, column=4, pady=5)

# Datenerfassung für erzwungene Konvektion

datenerfassung_erzwungene_Konvektion = tk.LabelFrame(frame_1, text= "Datenerfassung für erzwungene Konvektion")
datenerfassung_erzwungene_Konvektion.grid(row=2, column=0,padx=10, pady=10, sticky="ew")

tk.Label(datenerfassung_erzwungene_Konvektion, text="Stromüngsgesschwindigkeit [m/s]").grid(row=0, column=0, padx=5,pady=5)
w_entry = tk.Entry(datenerfassung_erzwungene_Konvektion)
w_entry.grid(row=0, column=1)

# Button zum berechnen

button_frame = tk.LabelFrame(frame_1, text="Abgabe der Daten")
button_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

button = tk.Button(button_frame, text="berechnen",command= ganze_berechnung)
button.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

# Ausgabefeld für die Ergebnisse

ergebnisse_frame = tk.LabelFrame(frame_1, text= "Ergebnisse")
ergebnisse_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

h_ergebniss = tk.Label(ergebnisse_frame, text="h [W/m\u00B2K]:")
h_ergebniss.grid(row=0, column=0, padx=5, pady=5)

h_fertig = tk.Label(ergebnisse_frame, text="noch nicht berechnet")
h_fertig.grid(row=0, column=1, pady=5)

T_ab_ergebniss = tk.Label(ergebnisse_frame, text="Abströmtemperatur [°C]:")
T_ab_ergebniss.grid(row=0, column=3, padx=5, pady=5)

T_ab_fertig = tk.Label(ergebnisse_frame, text="noch nicht berechnet")
T_ab_fertig.grid(row=0, column=4, pady=5)


fenster.mainloop()