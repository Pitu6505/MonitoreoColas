import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. VISUAL CONFIGURATION FOR THE PAPER (IEEE/Springer Style)
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.2)

# ==========================================
# 2. DATA LOADING AND CLEANING
# ==========================================
print("\n" + "="*50)
print(" STATISTICAL SUMMARY - 11 DAYS OF TELEMETRY")
print("="*50)

# --- IBM QUEUES ---
df_colas_ibm = pd.read_csv('registro_colas_ibm.csv', sep=';')
df_colas_ibm['Timestamp'] = pd.to_datetime(df_colas_ibm['Timestamp'])
print("\n[+] IBM QUEUES (Pending Jobs):")
print(df_colas_ibm.groupby('Backend')['Pending_Jobs'].describe()[['count', 'mean', 'max']])

# --- AWS QUEUES ---
df_colas_aws = pd.read_csv('registro_colas_aws.csv', sep=';')
df_colas_aws['Timestamp'] = pd.to_datetime(df_colas_aws['Timestamp'])
df_colas_aws['Tareas_Normales_Cola'] = pd.to_numeric(df_colas_aws['Tareas_Normales_Cola'], errors='coerce')
print("\n[+] AWS QUEUES (Tasks in Queue):")
print(df_colas_aws.groupby('QPU_Name')['Tareas_Normales_Cola'].describe()[['count', 'mean', 'max']])

# --- IBM NOISE ---
df_ruido_ibm = pd.read_csv('registro_ruido_ibm.csv', sep=';')
df_ruido_ibm['Timestamp'] = pd.to_datetime(df_ruido_ibm['Timestamp'])
print("\n[+] IBM NOISE (Average T1 and Readout Error):")
print(df_ruido_ibm.groupby('Backend')[['T1_Medio_us', 'Error_Lectura_Medio_%']].mean().round(2))

# --- AWS NOISE (Standardization) ---
# Transform "Readout Fidelity" to "Readout Error" (100 - Fidelity)
# to compare directly with IBM in the same format.
df_ruido_aws = pd.read_csv('registro_ruido_aws.csv', sep=';')
df_ruido_aws['Timestamp'] = pd.to_datetime(df_ruido_aws['Timestamp'])
df_ruido_aws['Error_Lectura_%'] = 100 - df_ruido_aws['Fid_Lectura_%']
print("\n[+] AWS NOISE (Equivalent Readout Error):")
print(df_ruido_aws.groupby('QPU')[['Error_Lectura_%']].mean().round(2))

# Paletas consistentes y de alto contraste por proveedor.
ibm_palette = {
    'ibm_fez': '#1f77b4',
    'ibm_kingston': '#ff7f0e',
    'ibm_marrakesh': '#2ca02c',
}

aws_palette = {
    'Cepheus-1-108Q': '#d62728',
    'Garnet': '#9467bd',
    'Forte 1': '#8c564b',
}

# ==========================================
# 3. GRAPH GENERATION
# ==========================================
print("\nGenerating graphs at high resolution (300 DPI)...")

# --- GRAPH 1: IBM Queue Evolution ---
plt.figure(figsize=(10, 5))

sns.lineplot(data=df_colas_ibm, x='Timestamp', y='Pending_Jobs', hue='Backend', 
             marker='o', markersize=4, palette=ibm_palette)

plt.title('IBM Queue Evolution - Pending Jobs', fontweight='bold')
plt.ylabel('Pending Jobs')
plt.xlabel('Timestamp')
plt.xticks(rotation=45)
plt.legend(title="IBM Backend", loc='best')
plt.tight_layout()
plt.savefig('grafica_colas_ibm.png', dpi=300)

# --- GRAPH 2: AWS Queue Evolution ---
plt.figure(figsize=(10, 5))

sns.lineplot(data=df_colas_aws, x='Timestamp', y='Tareas_Normales_Cola', hue='QPU_Name', 
             marker='s', markersize=4, palette=aws_palette)

plt.title('AWS Queue Evolution - Pending Tasks', fontweight='bold')
plt.ylabel('Pending Tasks')
plt.xlabel('Timestamp')
plt.xticks(rotation=45)
plt.legend(title="AWS QPU", loc='best')
plt.tight_layout()
plt.savefig('grafica_colas_aws.png', dpi=300)

# --- GRAPH 2: Temporal Drift of Readout Error ---
fig, axes = plt.subplots(2, 1, figsize=(10, 12), sharex=True)

sns.lineplot(data=df_ruido_ibm, x='Timestamp', y='Error_Lectura_Medio_%', 
             hue='Backend', marker='^', markersize=6, ax=axes[0], palette=ibm_palette)
axes[0].set_title('A: Readout Error Rate (IBM Quantum)', fontweight='bold')
axes[0].set_ylabel('Readout Error (%)')
axes[0].legend(title="IBM Backend", loc='upper left')

sns.lineplot(data=df_ruido_aws, x='Timestamp', y='Error_Lectura_%', 
             hue='QPU', marker='o', markersize=6, ax=axes[1], palette=aws_palette)
axes[1].set_title('B: Readout Error Rate (AWS Braket)', fontweight='bold')
axes[1].set_ylabel('Readout Error (%)')
axes[1].set_xlabel('Timestamp')
axes[1].legend(title="AWS QPU", loc='upper left')

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('grafica_ruido_error_lectura.png', dpi=300)

# --- GRAPH 3: Temporal Drift of T1 (IBM) ---
plt.figure(figsize=(10, 5))

sns.lineplot(data=df_ruido_ibm, x='Timestamp', y='T1_Medio_us', 
             hue='Backend', marker='s', markersize=6, palette=ibm_palette)

plt.title('Temporal Drift of Average T1 (IBM Quantum)', fontweight='bold')
plt.ylabel('Average T1 (μs)')
plt.xlabel('Timestamp')
plt.xticks(rotation=45)
plt.legend(title="IBM Backend", loc='best')
plt.tight_layout()
plt.savefig('grafica_ruido_t1.png', dpi=300)

# --- GRAPH 4: Temporal Drift of T2 (IBM) ---
plt.figure(figsize=(10, 5))

sns.lineplot(data=df_ruido_ibm, x='Timestamp', y='T2_Medio_us', 
             hue='Backend', marker='D', markersize=6, palette=ibm_palette)

plt.title('Temporal Drift of Average T2 (IBM Quantum)', fontweight='bold')
plt.ylabel('Average T2 (μs)')
plt.xlabel('Timestamp')
plt.xticks(rotation=45)
plt.legend(title="IBM Backend", loc='best')
plt.tight_layout()
plt.savefig('grafica_ruido_t2.png', dpi=300)

# --- GRAPH 5: Qubit Error Probability W(q) ---
# W(q) = α·ε_readout(q) + β·(1/T1(q)) + γ·(1/T2(q))
# where α=0.3, β=0.35, γ=0.35
alpha = 0.3
beta = 0.35
gamma = 0.35

df_w_q = df_ruido_ibm.copy()
df_w_q['W_q'] = (alpha * (df_w_q['Error_Lectura_Medio_%'] / 100) + 
                 beta * (1 / df_w_q['T1_Medio_us']) + 
                 gamma * (1 / df_w_q['T2_Medio_us'])) * 1000  # Scale for visibility

plt.figure(figsize=(10, 6))

sns.lineplot(data=df_w_q, x='Timestamp', y='W_q', 
             hue='Backend', marker='o', markersize=6, palette=ibm_palette, linewidth=2.5)

plt.title('Qubit Error Probability W(q) Over Time (IBM Quantum)\nW(q) = 0.3·ε_readout(q) + 0.35·(1/T₁) + 0.35·(1/T₂)', fontweight='bold')
plt.ylabel('W(q) [×10⁻³]')
plt.xlabel('Timestamp')
plt.xticks(rotation=45)
plt.legend(title="IBM Backend", loc='best')
plt.tight_layout()
plt.savefig('grafica_w_q.png', dpi=300)

print("Process completed! The following images have been created:")
print("  - grafica_colas_ibm.png")
print("  - grafica_colas_aws.png")
print("  - grafica_ruido_error_lectura.png")
print("  - grafica_ruido_t1.png")
print("  - grafica_ruido_t2.png")
print("  - grafica_w_q.png")